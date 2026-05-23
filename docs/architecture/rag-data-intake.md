# RAG 자료 접수와 정형화

이 문서는 국민대학교 소프트웨어융합대학 자료를 사용자가 파일, 사진, 캡처, 텍스트로 제공했을 때 RAG에 넣는 기준을 정리한다. 목표는 “일반 Gemini가 아는 듯이 답하는 앱”이 아니라, 출처가 확인된 학부 자료를 구조화해 Supabase `document_chunks`에 넣고 그 근거로 답하는 앱이다.

## 사용자가 주면 좋은 정보

| 영역 | 예시 | RAG category |
| --- | --- | --- |
| 학부 교과과정 | 소프트웨어학부/인공지능학부 전공필수, 전공선택, 학년별 권장 수강 | `curriculum` |
| 트랙/전공 로드맵 | AI, 백엔드, 보안, 데이터, 게임/그래픽스 등 트랙별 추천 과목 | `track`, `roadmap` |
| 동아리/활동 | 개발 동아리, 알고리즘 스터디, 보안/AI 학회, 해커톤, 공모전 | `club` |
| 학교 시스템 | 수강신청, K-StarTrack, eCampus, 장학, 상담, 졸업 요건 확인 | `system` |
| 진로/취업/창업 | 현장실습, 인턴십, 취업지원, 창업지원, 비교과 프로그램 | `career`, `startup` |
| 신입생 안내 | OT, 학사 일정, 학부 생활 팁, 첫 학기 준비물 | `freshman` |

파일 형식은 PDF, 이미지, 캡처, 엑셀, 텍스트 모두 받을 수 있다. 다만 현재 RAG 파이프라인의 입력은 `data/raw/*.md`이므로, PDF/사진은 텍스트로 읽어낸 뒤 Markdown으로 정리한다.

## 정형화 흐름

1. 원본 파일을 `data/inbox/`에 둔다.
2. 개인정보나 학생 개인 자료가 섞였는지 확인하고 제거한다.
3. 텍스트/Markdown으로 바꾼다.
4. `pnpm rag:prepare-raw`로 frontmatter가 있는 raw 문서를 만든다.
5. `pnpm wiki:build`로 `data/wiki`를 재생성한다.
6. `pnpm rag:ingest:dry`로 chunk 수와 category 구성을 확인한다.
7. Supabase schema가 준비되면 `pnpm rag:ingest:embeddings`로 live DB에 넣는다.

예시:

```powershell
pnpm rag:prepare-raw --input ../data/inbox/ai-curriculum.txt --title "인공지능학부 교과과정" --category curriculum --source "국민대학교 학부 홈페이지"
pnpm wiki:build
pnpm rag:ingest:dry
pnpm rag:ingest:embeddings
```

## raw 문서 규격

```md
---
title: 인공지능학부 교과과정
category: curriculum
source: 국민대학교 학부 홈페이지
collected_at: 2026-05-23
---

# 인공지능학부 교과과정

...
```

`source`는 답변 근거로 사용자에게 보일 수 있으므로 “팀 정리”라고만 쓰기보다 가능한 한 공식 페이지명, 문서명, 수집 경로를 남긴다.

## 사진과 PDF 처리 원칙

- 사진/캡처는 OCR 또는 수동 전사로 텍스트화한다.
- 표는 Markdown 표보다 항목형 리스트가 검색에 더 잘 걸릴 때가 많다.
- 과목명, 학년, 학기, 선수과목, 전공필수/선택 여부는 줄마다 반복해도 된다. RAG chunk가 잘렸을 때도 맥락이 남기 때문이다.
- 출처가 불명확한 자료는 `source`에 “사용자 제공, 공식 출처 확인 필요”라고 표시하고 답변에서는 확정 표현을 피한다.

## 넣으면 안 되는 정보

- 학생 이름, 학번, 전화번호, 이메일
- 성적표, 상담 내용, 개인 일정
- 비공개 강의자료, 저작권 문제가 있는 원문 전체
- 공식 안내와 충돌하는 개인 추측

개인화 메모리는 `user_memories`에 저장하고, 학교 지식 자료는 `document_chunks`에 저장한다. 둘을 섞지 않아야 다른 사용자의 개인 정보가 RAG 근거로 노출되지 않는다.
