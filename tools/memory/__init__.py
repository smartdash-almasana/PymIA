"""Memory contract validation utilities."""

__all__ = [
    "REQUIRED_MEMORY_FILES",
    "MemoryValidationResult",
    "default_memory_root",
    "validate_memory",
]


def __getattr__(name: str):
    if name in __all__:
        from . import validate_memory as _validate_memory

        return getattr(_validate_memory, name)
    raise AttributeError(name)
