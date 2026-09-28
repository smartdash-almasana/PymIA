"""
contamination guard
"""
from pathlib import Path
from .policy import get_project_root, iter_python_files, extract_imports

FORBIDDEN_IMPORT_PREFIXES = [
    "app.",
    "factory",
    "factory_v2",
    "factory_v3",
    "mcp",
    "orchestration",
    "jobs",
    "workflows",
    "telegram",
    "telebot",
    "aiogram",
    "openai",
    "anthropic",
    "google.generativeai",
    "groq",
    "langchain",
    "bem",
    "ocr"
]

# Provider SDKs remain forbidden globally. The one governed provider boundary
# may import the OpenAI-compatible transport client used by NVIDIA/OpenCode.
IMPORT_ALLOWED_EXACT = {
    (
        "pymia/smartpyme/service_1_pydantic_ai_column_semantic_provider_v1.py",
        "openai.AsyncOpenAI",
    ),
}

def test_no_forbidden_imports():
    root = get_project_root()
    pymia_dir = root / "pymia"
    
    python_files = iter_python_files(pymia_dir)
    
    violations = []
    for fpath in python_files:
        imports = extract_imports(fpath)
        rel_path = fpath.relative_to(root).as_posix()
        for lineno, imp in imports:
            if (rel_path, imp) in IMPORT_ALLOWED_EXACT:
                continue
            for prefix in FORBIDDEN_IMPORT_PREFIXES:
                if imp == prefix or imp.startswith(f"{prefix}."):
                    violations.append(f"{fpath.relative_to(root)}:{lineno} -> {imp}")
                    
    assert not violations, "Found forbidden imports:\n" + "\n".join(violations)
