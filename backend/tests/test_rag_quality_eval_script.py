from app.scripts.rag_quality_eval import (
    EvaluationCase,
    evaluate_cases,
    format_report,
    load_default_cases,
)
from app.services.retrieval_service import LocalDocumentRetriever


def test_evaluate_cases_passes_when_expected_category_and_terms_are_found() -> None:
    retriever = LocalDocumentRetriever(
        [
            {
                "source_type": "wiki_page",
                "title": "트랙 안내",
                "source": "Mini LLM Wiki",
                "category": "track",
                "heading_path": "AI 트랙",
                "content": "AI 관심 학생은 빅데이터와 머신러닝 트랙을 먼저 확인한다.",
                "metadata": {"path": "data/wiki/track.md"},
            }
        ]
    )
    cases = [
        EvaluationCase(
            question="AI 관심 있으면 어떤 트랙을 보면 좋아?",
            expected_categories=("track",),
            required_terms=("AI", "트랙"),
        )
    ]

    results = evaluate_cases(retriever, cases)

    assert results[0].passed is True
    assert results[0].source_count == 1
    assert results[0].matched_categories == ["track"]
    assert results[0].missing_terms == []


def test_evaluate_cases_reports_missing_sources_for_demo_question() -> None:
    retriever = LocalDocumentRetriever([])
    cases = [
        EvaluationCase(
            question="수강신청 전에 뭘 확인해야 해?",
            expected_categories=("freshman", "system"),
            required_terms=("수강신청",),
        )
    ]

    result = evaluate_cases(retriever, cases)[0]

    assert result.passed is False
    assert result.reason == "expected evidence was not found"


def test_evaluate_cases_can_expect_no_sources_for_out_of_scope_question() -> None:
    retriever = LocalDocumentRetriever(
        [
            {
                "source_type": "wiki_page",
                "title": "트랙 안내",
                "source": "Mini LLM Wiki",
                "category": "track",
                "heading_path": "",
                "content": "AI 트랙 안내",
                "metadata": {},
            }
        ]
    )
    cases = [
        EvaluationCase(
            question="의과대학 편입 장학금 알려줘",
            expected_categories=(),
            required_terms=(),
            expect_no_sources=True,
        )
    ]

    result = evaluate_cases(retriever, cases)[0]

    assert result.passed is True
    assert result.reason == "no internal evidence expected"


def test_format_report_summarizes_pass_fail_counts() -> None:
    retriever = LocalDocumentRetriever([])
    results = evaluate_cases(
        retriever,
        [
            EvaluationCase(
                question="수강신청 전에 뭘 확인해야 해?",
                expected_categories=("freshman",),
                required_terms=("수강신청",),
            )
        ],
    )

    report = format_report(results)

    assert "RAG quality evaluation: passed=0 failed=1 total=1" in report
    assert "[FAIL] 수강신청 전에 뭘 확인해야 해?" in report


def test_load_default_cases_match_documented_demo_questions() -> None:
    cases = load_default_cases()

    questions = [case.question for case in cases]

    assert "AI에 관심 있으면 어떤 트랙을 보면 좋을까?" in questions
    assert "신입생이 수강신청 전에 뭘 확인해야 해?" in questions
    assert "교학팀 문의는 어디로 하면 돼?" in questions
    assert any(case.expect_no_sources for case in cases)
