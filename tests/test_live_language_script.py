from __future__ import annotations

from pathlib import Path

from scripts.check_live_language import find_live_language_violations


def test_live_language_checks_current_active_docs() -> None:
    assert find_live_language_violations(Path.cwd()) == []


def test_live_language_detects_non_live_terms(tmp_path: Path) -> None:
    product_dir = tmp_path / "docs" / "product"
    product_dir.mkdir(parents=True)
    (product_dir / "live-scenario.md").write_text(
        "발표 데모에서는 mock fallback을 사용한다.\n",
        encoding="utf-8",
    )

    matches = find_live_language_violations(tmp_path)

    assert [(match.path.as_posix(), match.term) for match in matches] == [
        ("docs/product/live-scenario.md", "mock"),
        ("docs/product/live-scenario.md", "데모"),
    ]
