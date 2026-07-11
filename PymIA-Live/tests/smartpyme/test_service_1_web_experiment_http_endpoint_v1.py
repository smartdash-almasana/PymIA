from __future__ import annotations

import http.client
import json
import threading
from pathlib import Path
from uuid import uuid4

import pytest

from pymia.cli.service_1_web_experiment_server import (
    BLOCK_INVALID_EXTENSION,
    BLOCK_MISSING_FILE,
    BLOCK_MISSING_PAYLOAD_JSON,
    ROUTE_OWNER_QUESTIONS,
    ROUTE_RUN_EXPERIMENT,
    ROUTE_SEMANTIC_QUESTIONS,
    STATUS_BLOCKED,
    create_service_1_web_experiment_dev_server,
)
from pymia.smartpyme.service_1_web_experiment_backend_boundary_v1 import (
    STATUS_READY,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PARENT_ROOT = _REPO_ROOT.parent

_CASE_001_CANDIDATES = [
    _PARENT_ROOT / "prueba_excels" / "CASE_001_ventas_junio_2026_margin_leak.xlsx",
    _REPO_ROOT / "prueba_excels" / "CASE_001_ventas_junio_2026_margin_leak.xlsx",
]


def _first_existing(candidates: list[Path]) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    pytest.skip(f"No fixture found among: {[str(c) for c in candidates]}")


def _full_answers(columns: list[str]) -> dict[str, str]:
    return {column: f"respuesta {column}" for column in columns}


def _semantic_answers_for_gate(case_001_path: Path) -> dict[str, str]:
    from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
        build_service_1_semantic_bridge_from_canonical_ingestion_output_v1 as build_bridge,
    )
    from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
        build_service_1_canonical_ingestion_output_from_owner_confirmation_v1 as build_connector,
    )
    from pymia.smartpyme.service_1_semantic_bridge_to_controlled_execution_gate_v1 import (
        build_service_1_controlled_execution_gate_from_semantic_bridge_v1 as build_gate,
    )
    from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
        build_service_1_web_column_confirmation_intake_boundary_v1 as build_boundary,
    )

    boundary = build_boundary(local_xlsx_path=str(case_001_path))
    columns = list(boundary["columns"])
    connector = build_connector(
        owner_question_packet=boundary,
        owner_answers={column: f"r {column}" for column in columns},
    )
    gate = build_gate(
        semantic_bridge_packet=build_bridge(ingestion_output=connector["ingestion_output"])
    )
    return {question["column_name"]: f"rol {question['column_name']}" for question in gate["owner_questions"]}


def _multipart_body(
    *,
    file_name: str | None = None,
    file_bytes: bytes | None = None,
    payload: dict[str, object] | None = None,
) -> tuple[bytes, str]:
    boundary = f"codex-{uuid4().hex}"
    body = bytearray()

    if file_name is not None and file_bytes is not None:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            (
                f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
                "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n"
            ).encode("utf-8")
        )
        body.extend(file_bytes)
        body.extend(b"\r\n")

    if payload is not None:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            (
                'Content-Disposition: form-data; name="payload_json"\r\n'
                "Content-Type: application/json\r\n\r\n"
            ).encode("utf-8")
        )
        body.extend(json.dumps(payload).encode("utf-8"))
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    return bytes(body), boundary


def _post_request(
    *,
    host: str,
    port: int,
    file_name: str | None = None,
    file_bytes: bytes | None = None,
    payload: dict[str, object] | None = None,
    route: str = ROUTE_RUN_EXPERIMENT,
) -> tuple[int, dict[str, object]]:
    body, boundary = _multipart_body(
        file_name=file_name,
        file_bytes=file_bytes,
        payload=payload,
    )
    connection = http.client.HTTPConnection(host, port, timeout=60)
    try:
        connection.request(
            "POST",
            route,
            body=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Content-Length": str(len(body)),
            },
        )
        response = connection.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        return response.status, payload
    finally:
        connection.close()


@pytest.fixture(scope="module")
def case_001_path() -> Path:
    return _first_existing(_CASE_001_CANDIDATES)


@pytest.fixture(scope="module")
def case_001_columns(case_001_path: Path) -> list[str]:
    from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
        build_service_1_web_column_confirmation_intake_boundary_v1 as build_boundary,
    )

    return list(build_boundary(local_xlsx_path=str(case_001_path))["columns"])


@pytest.fixture(scope="module")
def semantic_answers(case_001_path: Path) -> dict[str, str]:
    return _semantic_answers_for_gate(case_001_path)


@pytest.fixture(scope="module")
def dev_server() -> tuple[str, int]:
    server = create_service_1_web_experiment_dev_server(host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[0], server.server_address[1]
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def test_case_001_happy_path_http_endpoint(
    dev_server: tuple[str, int],
    case_001_path: Path,
    case_001_columns: list[str],
    semantic_answers: dict[str, str],
    tmp_path: Path,
) -> None:
    host, port = dev_server
    output_dir = tmp_path / "delivery"

    http_status, body = _post_request(
        host=host,
        port=port,
        file_name=case_001_path.name,
        file_bytes=case_001_path.read_bytes(),
        payload={
            "owner_column_answers": _full_answers(case_001_columns),
            "semantic_owner_answers": semantic_answers,
            "owner_authorization": "accept",
            "owner_validation": "accept",
            "delivery_authorized": True,
            "output_dir": str(output_dir),
        },
    )

    assert http_status == 200
    assert body["status"] == STATUS_READY
    assert body["blocked_reason"] is None
    refs = body["delivery_packet"]["refs"]
    assert len(refs) == 4
    assert {ref["name"] for ref in refs} == {
        "README.md",
        "manifest.json",
        "execution_result.json",
        "hashes.json",
    }
    assert all(Path(str(ref["path"])).exists() for ref in refs)
    assert body["delivery_packet"]["summary"]["deliverable_count"] == 4
    assert "uploaded_xlsx_bytes" not in json.dumps(body)


def test_missing_file_returns_400_json(
    dev_server: tuple[str, int],
    case_001_columns: list[str],
    semantic_answers: dict[str, str],
    tmp_path: Path,
) -> None:
    host, port = dev_server

    http_status, body = _post_request(
        host=host,
        port=port,
        payload={
            "owner_column_answers": _full_answers(case_001_columns),
            "semantic_owner_answers": semantic_answers,
            "owner_authorization": "accept",
            "owner_validation": "accept",
            "delivery_authorized": True,
            "output_dir": str(tmp_path / "delivery"),
        },
    )

    assert http_status == 400
    assert body["status"] == STATUS_BLOCKED
    assert body["blocked_reason"] == BLOCK_MISSING_FILE


def test_missing_payload_returns_400_json(
    dev_server: tuple[str, int],
    case_001_path: Path,
) -> None:
    host, port = dev_server

    http_status, body = _post_request(
        host=host,
        port=port,
        file_name=case_001_path.name,
        file_bytes=case_001_path.read_bytes(),
    )

    assert http_status == 400
    assert body["status"] == STATUS_BLOCKED
    assert body["blocked_reason"] == BLOCK_MISSING_PAYLOAD_JSON


def test_invalid_extension_returns_400_blocked(
    dev_server: tuple[str, int],
    case_001_path: Path,
    case_001_columns: list[str],
    semantic_answers: dict[str, str],
    tmp_path: Path,
) -> None:
    host, port = dev_server

    http_status, body = _post_request(
        host=host,
        port=port,
        file_name="CASE_001.csv",
        file_bytes=case_001_path.read_bytes(),
        payload={
            "owner_column_answers": _full_answers(case_001_columns),
            "semantic_owner_answers": semantic_answers,
            "owner_authorization": "accept",
            "owner_validation": "accept",
            "delivery_authorized": True,
            "output_dir": str(tmp_path / "delivery"),
        },
    )

    assert http_status == 400
    assert body["status"] == STATUS_BLOCKED
    assert body["blocked_reason"] == BLOCK_INVALID_EXTENSION


def test_delivery_authorized_false_blocks_without_writes(
    dev_server: tuple[str, int],
    case_001_path: Path,
    case_001_columns: list[str],
    semantic_answers: dict[str, str],
    tmp_path: Path,
) -> None:
    host, port = dev_server
    output_dir = tmp_path / "delivery"

    http_status, body = _post_request(
        host=host,
        port=port,
        file_name=case_001_path.name,
        file_bytes=case_001_path.read_bytes(),
        payload={
            "owner_column_answers": _full_answers(case_001_columns),
            "semantic_owner_answers": semantic_answers,
            "owner_authorization": "accept",
            "owner_validation": "accept",
            "delivery_authorized": False,
            "output_dir": str(output_dir),
        },
    )

    assert http_status == 200
    assert body["status"] == STATUS_BLOCKED
    assert body["blocked_reason"] == "DELIVERY_NOT_AUTHORIZED"
    assert body["delivery_packet"]["summary"]["delivery_created"] is False
    assert body["delivery_packet"]["refs"] == []
    assert not output_dir.exists()


def test_dynamic_owner_question_loop_discovers_questions_then_runs_delivery(
    dev_server: tuple[str, int],
    case_001_path: Path,
    tmp_path: Path,
) -> None:
    host, port = dev_server
    file_bytes = case_001_path.read_bytes()

    http_status, questions = _post_request(
        host=host,
        port=port,
        route=ROUTE_OWNER_QUESTIONS,
        file_name=case_001_path.name,
        file_bytes=file_bytes,
    )

    assert http_status == 200
    assert questions["status"] == "OWNER_COLUMN_QUESTIONS_READY"
    assert questions["question_count"] == 10
    assert len(questions["owner_questions"]) == 10
    owner_answers = {
        str(question["column_name"]): f"respuesta humana para {question['column_name']}"
        for question in questions["owner_questions"]
    }

    http_status, semantic = _post_request(
        host=host,
        port=port,
        route=ROUTE_SEMANTIC_QUESTIONS,
        file_name=case_001_path.name,
        file_bytes=file_bytes,
        payload={"owner_column_answers": owner_answers},
    )

    assert http_status == 200
    assert semantic["status"] == "SEMANTIC_OWNER_QUESTIONS_READY"
    assert semantic["question_count"] >= 1
    semantic_answers = {
        str(question["column_name"]): f"confirmo rol {question['column_name']}"
        for question in semantic["owner_questions"]
    }

    output_dir = tmp_path / "delivery"
    http_status, body = _post_request(
        host=host,
        port=port,
        file_name=case_001_path.name,
        file_bytes=file_bytes,
        payload={
            "owner_column_answers": owner_answers,
            "semantic_owner_answers": semantic_answers,
            "owner_authorization": "accept",
            "owner_validation": "accept",
            "delivery_authorized": True,
            "output_dir": str(output_dir),
        },
    )

    assert http_status == 200
    assert body["status"] == STATUS_READY
    assert body["blocked_reason"] is None
    assert body["delivery_packet"]["summary"]["deliverable_count"] == 4
    assert all(Path(str(ref["path"])).exists() for ref in body["delivery_packet"]["refs"])


def test_semantic_questions_require_owner_column_answers(
    dev_server: tuple[str, int],
    case_001_path: Path,
) -> None:
    host, port = dev_server

    http_status, body = _post_request(
        host=host,
        port=port,
        route=ROUTE_SEMANTIC_QUESTIONS,
        file_name=case_001_path.name,
        file_bytes=case_001_path.read_bytes(),
        payload={"owner_column_answers": {}},
    )

    assert http_status == 200
    assert body["status"] == STATUS_BLOCKED
    assert body["question_count"] == 0
