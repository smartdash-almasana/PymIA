"""Verified Supabase identity resolver for Servicio 1 assisted web.

The bearer token is validated by Supabase before any tenant identity is accepted.
Trusted identity metadata is read only from verified app_metadata.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Mapping

SUPABASE_URL_ENV = "PYMIA_SUPABASE_URL"
SUPABASE_PUBLISHABLE_KEY_ENV = "PYMIA_SUPABASE_PUBLISHABLE_KEY"


class Service1SupabaseIdentityErrorV1(ValueError):
    """Fail-closed identity resolution error safe for the HTTP boundary."""


@dataclass(frozen=True)
class Service1SupabaseIdentityConfigV1:
    url: str
    publishable_key: str


def load_service_1_supabase_identity_config_v1(
    environ: Mapping[str, str] | None = None,
) -> Service1SupabaseIdentityConfigV1:
    env = os.environ if environ is None else environ
    url = str(env.get(SUPABASE_URL_ENV) or "").strip()
    key = str(env.get(SUPABASE_PUBLISHABLE_KEY_ENV) or "").strip()
    if not url:
        raise Service1SupabaseIdentityErrorV1(
            f"missing required configuration: {SUPABASE_URL_ENV}"
        )
    if not key:
        raise Service1SupabaseIdentityErrorV1(
            f"missing required configuration: {SUPABASE_PUBLISHABLE_KEY_ENV}"
        )
    return Service1SupabaseIdentityConfigV1(url=url, publishable_key=key)


def create_service_1_supabase_identity_client_v1(
    config: Service1SupabaseIdentityConfigV1,
) -> Any:
    try:
        from supabase import create_client
    except ImportError:
        raise Service1SupabaseIdentityErrorV1(
            "supabase package is required for the Supabase identity resolver"
        ) from None
    return create_client(config.url, config.publishable_key)


def _required_text(value: object, *, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise Service1SupabaseIdentityErrorV1(
            f"verified Supabase identity is missing {field}"
        )
    return text


def _bearer_token(handler: Any) -> str:
    auth_header = str(handler.headers.get("Authorization") or "").strip()
    scheme, separator, token = auth_header.partition(" ")
    token = token.strip()
    if scheme.lower() != "bearer" or not separator or not token or " " in token:
        raise Service1SupabaseIdentityErrorV1(
            "valid Authorization: Bearer token is required"
        )
    return token


class Service1SupabaseIdentityResolverV1:
    """Resolve trusted Servicio 1 identity from a verified Supabase user."""

    def __init__(self, client: Any) -> None:
        self._client = client

    @classmethod
    def from_environment(
        cls,
        environ: Mapping[str, str] | None = None,
    ) -> "Service1SupabaseIdentityResolverV1":
        config = load_service_1_supabase_identity_config_v1(environ)
        return cls(create_service_1_supabase_identity_client_v1(config))

    def __call__(self, handler: Any) -> dict[str, str]:
        token = _bearer_token(handler)
        try:
            response = self._client.auth.get_user(token)
        except Exception:
            raise Service1SupabaseIdentityErrorV1(
                "Supabase rejected the access token"
            ) from None

        user = getattr(response, "user", None)
        if user is None:
            raise Service1SupabaseIdentityErrorV1(
                "Supabase did not return a verified user"
            )

        app_metadata = getattr(user, "app_metadata", None)
        if not isinstance(app_metadata, Mapping):
            raise Service1SupabaseIdentityErrorV1(
                "verified Supabase identity is missing app_metadata"
            )

        return {
            "owner_actor_id": _required_text(getattr(user, "id", None), field="sub"),
            "tenant_id": _required_text(app_metadata.get("tenant_id"), field="tenant_id"),
            "cliente_id": _required_text(
                app_metadata.get("cliente_id"), field="cliente_id"
            ),
            "owner_actor_role": _required_text(
                app_metadata.get("owner_actor_role"), field="owner_actor_role"
            ),
        }


__all__ = [
    "SUPABASE_URL_ENV",
    "SUPABASE_PUBLISHABLE_KEY_ENV",
    "Service1SupabaseIdentityConfigV1",
    "Service1SupabaseIdentityErrorV1",
    "Service1SupabaseIdentityResolverV1",
    "load_service_1_supabase_identity_config_v1",
    "create_service_1_supabase_identity_client_v1",
]
