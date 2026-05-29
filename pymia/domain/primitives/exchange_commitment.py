"""
ExchangeCommitment - Átomo de la organización

Doctrina: PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §4

Unidad mínima: Compromiso de intercambio
Definición: Acuerdo (explícito o implícito) por el cual la organización
entrega algo a cambio de algo bajo condiciones determinadas.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID


@dataclass(frozen=True)
class ExchangeCommitment:
    """
    Compromiso de intercambio - átomo de la organización.
    
    Value object inmutable que representa un acuerdo de intercambio.
    
    Invariantes de dominio:
    - Requiere al menos 2 partes
    - Objeto no puede estar vacío
    - Condiciones no pueden estar vacías
    
    Ejemplo:
        commitment = ExchangeCommitment(
            id=uuid4(),
            parties=["Textiles SA", "Cliente Mayorista"],
            object="Venta de 100 remeras",
            conditions="Pago contado, entrega 7 días",
            created_at=datetime.utcnow(),
        )
    """
    id: UUID
    parties: List[str]
    object: str
    conditions: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validación de invariantes de dominio."""
        if not self.parties or len(self.parties) < 2:
            raise ValueError(
                f"ExchangeCommitment requiere al menos 2 partes, "
                f"recibió {len(self.parties) if self.parties else 0}"
            )
        if not self.object or not self.object.strip():
            raise ValueError(
                "ExchangeCommitment requiere objeto no vacío"
            )
        if not self.conditions or not self.conditions.strip():
            raise ValueError(
                "ExchangeCommitment requiere condiciones no vacías"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialización a diccionario JSON-compatible.
        
        Returns:
            Dict con todos los campos serializados
        """
        return {
            "id": str(self.id),
            "parties": self.parties,
            "object": self.object,
            "conditions": self.conditions,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata or {},
        }
