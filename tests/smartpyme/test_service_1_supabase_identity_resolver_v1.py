from __future__ import annotations

from types import SimpleNamespace

import pytest

from pymia.smartpyme import service_1_assisted_web_v1 as assisted_web
from pymia.smartpyme.service_1_supabase_identity_resolver_v1 import (
    Service1SupabaseIdentityErrorV1,
    Service1SupabaseIdentityResolverV1,
    load_service_1_supabase_identity_config_v1,
)


class _Headers:
    def __init__(self, auth_header: str | None) -> None:
        self._auth_header = auth_header

    def get(self, name: str):
        return self._auth_header


class _Auth:
    def __init__(self, response=None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.tokens: list[str] = []

    def get_user(self, token: str):
        self.tokens.append(token)
        if self.error is not None:
            raise self.error
        return self.response


def _handler(auth_header: str | None):
    return SimpleNamespace(headers=_Headers(auth_header))


def _resolver(*, user=None, error: Exception | None = None):
    auth = _Auth(response=SimpleNamespace(user=user), error=error)
    client = SimpleNamespace(auth=auth)
    return Service1SupabaseIdentityResolverV1(client), auth


def _user():
    return SimpleNamespace(
        id="fdb51574-c0e6-4b32-8076-5dd641164f51",
        app_metadata={
            "tenant_id": "tenant-acme",
            "cliente_id": "cliente-001",
            "owner_actor_role": "owner",
        },
        user_metadata={
            "tenant_id": "forged-tenant",
            "cliente_id": "forged-client",
            "owner_actor_role": "forged-role",
        },
    )


def test_resolver_validates_token_and_maps_verified_app_metadata() -> None:
    resolver, auth = _resolver(user=_user())

    identity = resolver(_handler("Bearer verified.jwt"))

    assert auth.tokens == ["verified.jwt"]
    assert identity == {
        "owner_actor_id": "fdb51574-c0e6-4b32-8076-5dd641164f51",
        "tenant_id": "tenant-acme",
        "cliente_id": "cliente-001",
        "owner_actor_role": "owner",
    }


@pytest.mark.parametrize(
    "auth_header",
    [None, "", "Basic abc", "Bearer", "Bearer one two"],
)
def test_resolver_rejects_missing_or_malformed_bearer_token(auth_header) -> None:
    resolver, auth = _resolver(user=_user())

    with pytest.raises(Service1SupabaseIdentityErrorV1):
        resolver(_handler(auth_header))

    assert auth.tokens == []


def test_resolver_fails_closed_when_supabase_rejects_token() -> None:
    resolver, _ = _resolver(error=RuntimeError("remote detail must not escape"))

    with pytest.raises(
        Service1SupabaseIdentityErrorV1,
        match="Supabase rejected the access token",
    ):
        resolver(_handler("Bearer invalid.jwt"))


@pytest.mark.parametrize(
    "field",
    ["tenant_id", "cliente_id", "owner_actor_role"],
)
def test_resolver_fails_closed_when_required_app_metadata_is_missing(field: str) -> None:
    user = _user()
    del user.app_metadata[field]
    resolver, _ = _resolver(user=user)

    with pytest.raises(Service1SupabaseIdentityErrorV1, match=field):
        resolver(_handler("Bearer verified.jwt"))


def test_resolver_never_uses_user_metadata_as_authority() -> None:
    user = _user()
    user.app_metadata = {}
    resolver, _ = _resolver(user=user)

    with pytest.raises(Service1SupabaseIdentityErrorV1, match="tenant_id"):
        resolver(_handler("Bearer verified.jwt"))


def test_identity_config_requires_url_and_publishable_key() -> None:
    with pytest.raises(Service1SupabaseIdentityErrorV1):
        load_service_1_supabase_identity_config_v1({})

    config = load_service_1_supabase_identity_config_v1(
        {
            "PYMIA_SUPABASE_URL": "https://example.supabase.co",
            "PYMIA_SUPABASE_PUBLISHABLE_KEY": "sb_publishable_example",
        }
    )
    assert config.url == "https://example.supabase.co"
    assert config.publishable_key == "sb_publishable_example"


def test_assisted_web_main_wires_supabase_identity_resolver(monkeypatch) -> None:
    resolver = object()
    memory_loader = object()
    prior_loader = object()
    persistence = SimpleNamespace(
        list_owner_confirmation_memory=memory_loader,
        load_current_semantic_contract=prior_loader,
    )
    calls: dict[str, object] = {}
    server = SimpleNamespace(serve_forever=lambda: calls.setdefault("served", True))

    monkeypatch.setattr(
        assisted_web,
        "Service1SupabaseIdentityResolverV1",
        SimpleNamespace(from_environment=lambda: resolver),
    )
    monkeypatch.setattr(
        assisted_web,
        "Service1SupabasePersistenceAdapterV1",
        SimpleNamespace(from_environment=lambda: persistence),
    )

    def create_server(**kwargs):
        calls["server_kwargs"] = kwargs
        return server

    monkeypatch.setattr(assisted_web, "create_assisted_web_server_v1", create_server)
    monkeypatch.setattr("sys.argv", ["service_1_assisted_web_v1"])

    assisted_web.main()

    assert calls["server_kwargs"] == {
        "host": "127.0.0.1",
        "port": 8765,
        "persist_tenant_confirmation": persistence,
        "load_tenant_memory": memory_loader,
        "load_prior_semantic_contract": prior_loader,
        "require_tenant_persistence": True,
        "tenant_identity_resolver": resolver,
    }
    assert calls["served"] is True
