from __future__ import annotations

from pathlib import Path

from app.scripts.check_env import read_env_file


def default_repo_root() -> Path:
    cwd = Path.cwd()
    return cwd.parent if cwd.name == "backend" else cwd


def read_root_smoke_env(repo_root: Path | None = None) -> dict[str, str]:
    root = repo_root or default_repo_root()
    return read_env_file(root / ".env")


def resolve_smoke_value(name: str, env_value: str | None = None) -> str:
    return (env_value or read_root_smoke_env().get(name) or "").strip()


def upsert_env_values(path: Path, values: dict[str, str]) -> None:
    existing_lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    remaining = dict(values)
    output_lines: list[str] = []

    for line in existing_lines:
        key, separator, _value = line.partition("=")
        normalized_key = key.strip()
        if separator and normalized_key in remaining:
            output_lines.append(f"{normalized_key}={remaining.pop(normalized_key)}")
        else:
            output_lines.append(line)

    if remaining and output_lines and output_lines[-1].strip():
        output_lines.append("")
    for key, value in remaining.items():
        output_lines.append(f"{key}={value}")

    path.write_text("\n".join(output_lines).rstrip() + "\n", encoding="utf-8")
