from pathlib import Path

REQUIRED_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "docs/README.md",
    "docs/product/prd-dev-plan.md",
    "docs/architecture/mini-llm-wiki.md",
    "docs/contributing/dev-guide.md",
    "docs/contributing/roadmap.md",
    "docs/contributing/feature-registry.md",
    "docs/contributing/plans-status.md",
    "docs/collaboration/team-roles.md",
    "docs/collaboration/workflow.md",
    "docs/llm/usage-log.md",
    "docs/llm/codex-workflow.md",
    "docs/superpowers/specs/2026-05-13-kmu-freshman-ai-design.md",
    "docs/superpowers/specs/2026-05-13-mini-llm-wiki-design.md",
    "docs/superpowers/plans/2026-05-13-repo-docs-initialization.md",
    "docs/superpowers/plans/2026-05-13-mini-llm-wiki.md",
    "docs/testing/rag-evaluation.md",
]


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not Path(path).exists()]
    if missing:
        print("필수 문서 누락:")
        for path in missing:
            print(f"- {path}")
        return 1

    print(f"필수 문서 {len(REQUIRED_FILES)}개 확인 완료")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
