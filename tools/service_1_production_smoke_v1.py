from __future__ import annotations

import json
import os
import re
import sys
from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, build_opener

from openpyxl import Workbook


BASE_URL_ENV = "PYMIA_PRODUCTION_BASE_URL"
SUPABASE_URL_ENV = "PYMIA_SUPABASE_URL"
SUPABASE_PUBLISHABLE_KEY_ENV = "PYMIA_SUPABASE_PUBLISHABLE_KEY"
SMOKE_EMAIL_ENV = "PYMIA_SMOKE_EMAIL"
SMOKE_PASSWORD_ENV = "PYMIA_SMOKE_PASSWORD"


class SmokeFailure(RuntimeError):
    pass


def _required_env(name: str) -> str:
    value = str(os.environ.get(name) or "").strip()
    if not value:
        raise SmokeFailure(f"missing required environment variable: {name}")
    return value


def _xlsx_bytes() -> bytes:
    stream = BytesIO()
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Ventas"
    sheet.append(["fecha", "venta_total", "cobrado"])
    sheet.append(["2026-08-01", 1000, 800])
    sheet.append(["2026-08-02", 2000, 1500])
    workbook.save(stream)
    return stream.getvalue()


def _request(opener, method: str, url: str, *, body: bytes = b"", headers: dict[str, str] | None = None):
    request = Request(url, data=body if method != "GET" else None, method=method, headers=headers or {})
    try:
        response = opener.open(request, timeout=30)
        return response.status, response.headers, response.read()
    except HTTPError as exc:
        return exc.code, exc.headers, exc.read()
    except URLError as exc:
        raise SmokeFailure(f"network failure for {url}: {exc.reason}") from None


def _supabase_access_token(opener, *, url: str, publishable_key: str, email: str, password: str) -> str:
    endpoint = url.rstrip("/") + "/auth/v1/token?grant_type=password"
    payload = json.dumps({"email": email, "password": password}).encode("utf-8")
    status, _, content = _request(
        opener,
        "POST",
        endpoint,
        body=payload,
        headers={
            "apikey": publishable_key,
            "Authorization": f"Bearer {publishable_key}",
            "Content-Type": "application/json",
        },
    )
    if status != 200:
        raise SmokeFailure(f"Supabase login failed with HTTP {status}")
    try:
        token = str(json.loads(content.decode("utf-8"))["access_token"]).strip()
    except Exception:
        raise SmokeFailure("Supabase login response did not contain access_token") from None
    if not token:
        raise SmokeFailure("Supabase returned an empty access_token")
    return token


def _multipart(filename: str, content: bytes, *, launch_review: str) -> tuple[bytes, str]:
    boundary = "PymIAProductionSmokeBoundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="launch_review"\r\n\r\n'
        f"{launch_review}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n"
    ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode("utf-8")
    return body, f"multipart/form-data; boundary={boundary}"


def _cookie(headers) -> str:
    raw = headers.get("Set-Cookie")
    if not raw:
        raise SmokeFailure("application did not issue service session cookie")
    return raw.split(";", 1)[0]


def _answers(page: str) -> dict[str, str]:
    answers: dict[str, str] = {}
    for question_id, option_id in re.findall(r'name="answer_([^"]+)" value="([^"]+)"', page):
        if option_id not in {"OTHER", "IGNORE", "not_sure"}:
            answers.setdefault(f"answer_{question_id}", option_id)
    if not answers:
        raise SmokeFailure("owner confirmation page exposed no acceptable semantic answers")
    return answers


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def run() -> dict[str, object]:
    base_url = _required_env(BASE_URL_ENV).rstrip("/")
    supabase_url = _required_env(SUPABASE_URL_ENV)
    publishable_key = _required_env(SUPABASE_PUBLISHABLE_KEY_ENV)
    email = _required_env(SMOKE_EMAIL_ENV)
    password = _required_env(SMOKE_PASSWORD_ENV)
    _assert(base_url.startswith("https://"), "production base URL must use HTTPS")

    opener = build_opener()
    checks: dict[str, str] = {}

    status, _, body = _request(opener, "GET", base_url + "/healthz")
    _assert(status == 200 and b'"status":"ok"' in body, f"healthz failed: HTTP {status}")
    checks["healthz"] = "PASS"

    xlsx = _xlsx_bytes()
    upload_body, content_type = _multipart("production_smoke_ventas.xlsx", xlsx, launch_review="sold_vs_collected_gap")
    status, _, _ = _request(
        opener,
        "POST",
        base_url + "/upload",
        body=upload_body,
        headers={"Content-Type": content_type},
    )
    _assert(status == 400, f"unauthenticated upload must fail closed, got HTTP {status}")
    checks["unauthenticated_fail_closed"] = "PASS"

    token = _supabase_access_token(
        opener,
        url=supabase_url,
        publishable_key=publishable_key,
        email=email,
        password=password,
    )
    auth = {"Authorization": f"Bearer {token}"}
    checks["supabase_login"] = "PASS"

    status, response_headers, content = _request(
        opener,
        "POST",
        base_url + "/upload",
        body=upload_body,
        headers={"Content-Type": content_type, **auth},
    )
    page = content.decode("utf-8", errors="replace")
    _assert(status == 200, f"authenticated upload failed: HTTP {status}")
    _assert("Confirmar qué significa cada dato" in page, "upload did not reach owner confirmation")
    cookie = _cookie(response_headers)
    checks["authenticated_upload"] = "PASS"

    confirm_body = urlencode(_answers(page)).encode("utf-8")
    status, _, content = _request(
        opener,
        "POST",
        base_url + "/confirm-meanings",
        body=confirm_body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": cookie,
            **auth,
        },
    )
    page = content.decode("utf-8", errors="replace")
    _assert(status == 200, f"owner confirmation failed: HTTP {status}")
    checks["owner_confirmation"] = "PASS"

    if "Ventas y cobranzas" not in page:
        review_body = urlencode({"review": "sold_vs_collected_gap"}).encode("utf-8")
        status, _, content = _request(
            opener,
            "POST",
            base_url + "/run-review",
            body=review_body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": cookie,
                **auth,
            },
        )
        page = content.decode("utf-8", errors="replace")
        _assert(status == 200, f"deterministic execution failed: HTTP {status}")

    _assert("Ventas y cobranzas" in page, "sellable result was not rendered")
    _assert("Total vendido" in page and "Diferencia" in page, "sellable result is incomplete")
    checks["deterministic_execution_and_persistence"] = "PASS"

    status, headers, content = _request(
        opener,
        "GET",
        base_url + "/download-sales-collections",
        headers={"Cookie": cookie},
    )
    _assert(status == 200 and content.startswith(b"PK"), f"XLSX download failed: HTTP {status}")
    disposition = str(headers.get("Content-Disposition") or "")
    _assert("service_1_liq_001_result.xlsx" in disposition, "unexpected delivery filename")
    checks["delivery_download"] = "PASS"

    status, _, content = _request(opener, "GET", base_url + "/cases", headers={"Cookie": cookie})
    cases = content.decode("utf-8", errors="replace")
    _assert(status == 200 and "Control de Cobros y Conciliación" in cases, "recent-case reentry listing failed")
    match = re.search(r'href="(/case\?case_ref=[^"]+)"', cases)
    _assert(match is not None, "recent cases exposed no reentry link")
    status, _, content = _request(opener, "GET", base_url + match.group(1), headers={"Cookie": cookie})
    reopened = content.decode("utf-8", errors="replace")
    _assert(status == 200 and "Total vendido" in reopened, "case reentry failed")
    checks["reentry_current_instance"] = "PASS"

    return {
        "verdict": "PASS",
        "base_url": base_url,
        "checks": checks,
        "non_claims": [
            "Does not prove durable case snapshots across restart.",
            "Does not expose or print access tokens or passwords.",
        ],
    }


def main() -> int:
    try:
        result = run()
    except SmokeFailure as exc:
        print(json.dumps({"verdict": "BLOCKED", "reason": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
