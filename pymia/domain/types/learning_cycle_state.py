"""
LearningCycleState — Estados del ciclo de aprendizaje organizacional.

Define la máquina de estados del ciclo de aprendizaje con transiciones
secuenciales estrictas hacia CERRADO, y ABORTADO desde cualquier estado
no terminal.

Doctrina fuente: PYMIA_ORGANIZATIONAL_LEARNING_MODEL.md
"""

from enum import Enum
from typing import FrozenSet


class LearningCycleState(Enum):
    """Estados posibles de un ciclo de aprendizaje."""

    INICIADO = "iniciado"
    RESULTADO_REGISTRADO = "resultado_registrado"
    ATRIBUCION_COMPLETADA = "atribucion_completada"
    APRENDIZAJE_EXTRAIDO = "aprendizaje_extraido"
    KI_ACTUALIZADO = "ki_actualizado"
    CERRADO = "cerrado"
    ABORTADO = "abortado"


LEARNING_CYCLE_STATE_ORDER = [
    LearningCycleState.INICIADO,
    LearningCycleState.RESULTADO_REGISTRADO,
    LearningCycleState.ATRIBUCION_COMPLETADA,
    LearningCycleState.APRENDIZAJE_EXTRAIDO,
    LearningCycleState.KI_ACTUALIZADO,
    LearningCycleState.CERRADO,
]

TERMINAL_STATES: FrozenSet[LearningCycleState] = frozenset(
    {LearningCycleState.CERRADO, LearningCycleState.ABORTADO}
)


def state_index(state: LearningCycleState) -> int:
    """Retorna el índice del estado en la secuencia ordenada."""
    try:
        return LEARNING_CYCLE_STATE_ORDER.index(state)
    except ValueError:
        return -1
