"""Production entrypoint for bounded LLM column reception V1."""
from __future__ import annotations

import argparse

from pymia.smartpyme.service_1_assisted_web_semantic_reception_v1 import (
    create_semantic_reception_server_v1,
)
from pymia.smartpyme.service_1_radar_supabase_persistence_v1 import (
    Service1RadarSupabasePersistenceAdapterV1,
)
from pymia.smartpyme.service_1_supabase_identity_resolver_v1 import (
    Service1SupabaseIdentityResolverV1,
)
from pymia.smartpyme.service_1_supabase_persistence_v1 import (
    Service1SupabasePersistenceAdapterV1,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="PymIA Servicio 1 semantic reception web")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    tenant_identity_resolver = Service1SupabaseIdentityResolverV1.from_environment()
    tenant_persistence = Service1SupabasePersistenceAdapterV1.from_environment()
    radar_policy_store = Service1RadarSupabasePersistenceAdapterV1.from_environment()
    server = create_semantic_reception_server_v1(
        host=args.host,
        port=args.port,
        persist_tenant_confirmation=tenant_persistence,
        load_tenant_memory=tenant_persistence.list_owner_confirmation_memory,
        load_prior_semantic_contract=tenant_persistence.load_current_semantic_contract,
        load_persisted_cases=tenant_persistence.list_persisted_cases,
        load_persisted_case=tenant_persistence.load_persisted_case,
        require_tenant_persistence=True,
        tenant_identity_resolver=tenant_identity_resolver,
        radar_policy_store=radar_policy_store,
    )
    print(f"Servicio 1 semantic reception disponible en http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()


__all__ = ["main"]
