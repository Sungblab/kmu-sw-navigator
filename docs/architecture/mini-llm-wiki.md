# Mini LLM Wiki 아키텍처

## 목적

자료가 많아질수록 원문 chunk만 검색하는 RAG는 비효율적입니다. 동아리 목록, 트랙 안내, 수강 로드맵, 학교 시스템처럼 구조가 다른 자료는 먼저 위키 형태로 정리하고, 질문 시 위키를 우선 검색한 뒤 원문 근거를 보강합니다.

## 참고한 로컬 구현

- UnivMind: `Raw Sources -> Wiki -> Views` 3-layer 구조와 `loadIndex -> planWiki -> execute -> save -> log` 위키 에이전트 흐름
- OpenCairn: heading-aware chunking, `heading_path`, `content_hash`, vector + keyword hybrid retrieval, context packing

이 프로젝트는 과제 규모에 맞게 LangGraph, Redis, BullMQ, Docker worker를 제외하고 Python script와 Markdown 파일 중심으로 축소합니다.

## 계층 구조

```txt
data/raw/
  원본 자료. 팀원이 직접 정리하거나 출처를 표시한 markdown

data/wiki/
  _index.md
  log.md
  신입생용으로 재구성한 wiki page

Supabase
  raw_documents
  wiki_pages
  wiki_logs
  document_chunks
```

## 처리 흐름

```txt
raw markdown 수집
-> Python wiki compiler 실행
-> category별 wiki page 생성
-> _index.md와 log.md 갱신
-> raw/wiki markdown을 heading 기준으로 chunk
-> embedding 저장
-> 질문 시 wiki chunk 우선 검색
-> raw chunk로 근거 보강
-> Gemini 답변 생성
```

## 위키 페이지 형식

```md
---
slug: tracks
type: topic
category: track
status: active
sources: 2
last_touched: 2026-05-13
---

# 트랙 안내

## 핵심 요약

...

## 관련 자료

- 원문 제목 — 출처
```

## MVP 범위

- Markdown 원문만 우선 지원합니다.
- LLM 호출 없이도 실행 가능한 deterministic compiler를 먼저 만듭니다.
- Gemini 기반 요약/정제는 후속 단계에서 compiler에 옵션으로 붙입니다.
- 검색은 `wiki_page`를 우선하고 `raw_document`를 fallback 근거로 사용합니다.

## 발표 포인트

보고서와 발표에서는 “LLM이 원문을 바로 답변에 쓰는 것이 아니라, 원문을 먼저 신입생용 위키로 정리하고 그 위키를 검색한다”는 점을 차별점으로 설명합니다.

