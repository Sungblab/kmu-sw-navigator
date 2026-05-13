# RAG 설계

## 목표

일반 챗봇이 아니라 국민대 소프트웨어융합대학 신입생 자료를 근거로 답변하는 도메인 특화 챗봇을 만든다. 자료가 많아질수록 원문 chunk만 검색하지 않고, Mini LLM Wiki를 우선 검색한 뒤 원문 chunk로 근거를 보강한다.

## 자료 단위

- 원문 자료는 `data/raw/` Markdown으로 정리합니다.
- 신입생용 정리본은 `data/wiki/` Mini LLM Wiki로 생성합니다.
- 각 문서는 `title`, `source`, `category`, `department`, `content`를 갖습니다.
- chunk 크기는 500-1000자 내외로 시작합니다.
- embedding은 Gemini Embedding 2의 768차원을 사용합니다.

## 검색 방식

Supabase pgvector의 cosine distance 연산자 `<=>`를 사용합니다. FastAPI는 Supabase RPC `match_document_chunks`를 호출합니다. 키워드 정확도가 중요한 동아리명, 시스템명, 과목명 검색은 `search_document_chunks_text`를 함께 사용해 hybrid 검색으로 확장할 수 있게 둡니다.

초기 설정:

| 항목 | 값 |
| --- | --- |
| embedding model | `gemini-embedding-2` |
| output dimensionality | `768` |
| 기본 검색 개수 | `5` |
| 초기 threshold | `0.0` |
| 검색 우선순위 | `wiki_page` -> `raw_document` |

## 답변 정책

- 검색 결과가 부족하면 “자료에서 충분한 근거를 찾지 못했다”고 답합니다.
- 답변에는 출처 제목과 category를 함께 제공합니다.
- 추측성 답변은 피하고, 신입생에게 확인이 필요한 내용은 “학부 공지 확인 필요”라고 표시합니다.

## 품질 확인

초기 RAG 품질은 다음 질문으로 확인합니다.

1. AI에 관심 있으면 어떤 트랙을 보면 좋을까?
2. 신입생이 수강신청 전에 뭘 확인해야 해?
3. 개발과 운동에 관심 있으면 어떤 활동이 좋을까?
4. 학교 시스템을 처음 쓰는 신입생이 알아야 할 것은?
