from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from app.services.document_ingest import build_document_chunk_payloads, load_ingest_documents
from app.services.retrieval_service import LocalDocumentRetriever, RetrievalResult


@dataclass(frozen=True)
class EvaluationCase:
    question: str
    expected_categories: tuple[str, ...]
    required_terms: tuple[str, ...]
    expect_no_sources: bool = False
    min_sources: int = 1


@dataclass(frozen=True)
class EvaluationResult:
    question: str
    passed: bool
    reason: str
    source_count: int
    matched_categories: list[str]
    missing_terms: list[str]
    top_sources: list[str]


def load_default_cases() -> list[EvaluationCase]:
    return [
        EvaluationCase(
            question="AI에 관심 있으면 어떤 트랙을 보면 좋을까?",
            expected_categories=("track", "curriculum", "roadmap"),
            required_terms=("트랙",),
        ),
        EvaluationCase(
            question="신입생이 수강신청 전에 뭘 확인해야 해?",
            expected_categories=("freshman", "system", "curriculum"),
            required_terms=("수강신청", "신입생"),
        ),
        EvaluationCase(
            question="개발과 운동에 관심 있으면 어떤 활동이 좋을까?",
            expected_categories=("club", "roadmap"),
            required_terms=("개발",),
        ),
        EvaluationCase(
            question="교학팀 문의는 어디로 하면 돼?",
            expected_categories=("system", "freshman"),
            required_terms=("교학팀",),
        ),
        EvaluationCase(
            question="바리스타 원두 로스팅 온도 알려줘",
            expected_categories=(),
            required_terms=(),
            expect_no_sources=True,
            min_sources=0,
        ),
    ]


def evaluate_cases(
    retriever: LocalDocumentRetriever,
    cases: list[EvaluationCase],
    *,
    limit: int = 5,
) -> list[EvaluationResult]:
    return [_evaluate_case(retriever, case, limit=limit) for case in cases]


def format_report(results: list[EvaluationResult]) -> str:
    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed
    lines = [f"RAG quality evaluation: passed={passed} failed={failed} total={len(results)}"]

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"[{status}] {result.question}")
        lines.append(f"  reason={result.reason}")
        lines.append(
            "  evidence="
            f"sources={result.source_count}, "
            f"matched_categories={','.join(result.matched_categories) or '-'}, "
            f"missing_terms={','.join(result.missing_terms) or '-'}"
        )
        if result.top_sources:
            lines.append(f"  top_sources={'; '.join(result.top_sources)}")

    return "\n".join(lines)


def _evaluate_case(
    retriever: LocalDocumentRetriever,
    case: EvaluationCase,
    *,
    limit: int,
) -> EvaluationResult:
    results = retriever.search(case.question, limit=limit)
    source_count = len(results)
    matched_categories = _matched_categories(results, case.expected_categories)
    missing_terms = _missing_required_terms(results, case.required_terms)
    top_sources = _top_source_labels(results)

    if case.expect_no_sources:
        passed = source_count == 0
        return EvaluationResult(
            question=case.question,
            passed=passed,
            reason="no internal evidence expected"
            if passed
            else "unexpected internal evidence was found",
            source_count=source_count,
            matched_categories=matched_categories,
            missing_terms=missing_terms,
            top_sources=top_sources,
        )

    has_enough_sources = source_count >= case.min_sources
    has_expected_category = bool(matched_categories) if case.expected_categories else True
    has_required_terms = not missing_terms
    passed = has_enough_sources and has_expected_category and has_required_terms

    reason = "expected evidence found" if passed else "expected evidence was not found"
    return EvaluationResult(
        question=case.question,
        passed=passed,
        reason=reason,
        source_count=source_count,
        matched_categories=matched_categories,
        missing_terms=missing_terms,
        top_sources=top_sources,
    )


def _matched_categories(
    results: list[RetrievalResult],
    expected_categories: tuple[str, ...],
) -> list[str]:
    expected = set(expected_categories)
    matched: list[str] = []
    for result in results:
        if result.category in expected and result.category not in matched:
            matched.append(str(result.category))
    return matched


def _missing_required_terms(
    results: list[RetrievalResult],
    required_terms: tuple[str, ...],
) -> list[str]:
    if not required_terms:
        return []

    evidence_parts: list[str] = []
    for result in results:
        evidence_parts.extend(
            [
                result.title,
                result.category or "",
                result.heading_path,
                result.content,
            ]
        )
    evidence_text = "\n".join(evidence_parts).casefold()
    return [term for term in required_terms if term.casefold() not in evidence_text]


def _top_source_labels(results: list[RetrievalResult]) -> list[str]:
    labels: list[str] = []
    for result in results[:3]:
        category = result.category or "-"
        labels.append(f"{result.title} ({category}, score={result.score})")
    return labels


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate local RAG evidence coverage for demo questions."
    )
    parser.add_argument("--raw-dir", type=Path, default=Path("../data/raw"))
    parser.add_argument("--wiki-dir", type=Path, default=Path("../data/wiki"))
    parser.add_argument("--max-chars", type=int, default=1200)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    # Live 키 없이도 제출 시연 질문이 어떤 내부 근거를 잡는지 확인하기 위한 로컬 평가다.
    documents = load_ingest_documents(args.raw_dir, args.wiki_dir)
    payloads = build_document_chunk_payloads(documents, max_chars=args.max_chars)
    results = evaluate_cases(
        LocalDocumentRetriever(payloads),
        load_default_cases(),
        limit=args.limit,
    )
    print(format_report(results))
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
