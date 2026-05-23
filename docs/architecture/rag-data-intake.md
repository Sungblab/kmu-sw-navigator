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

가능하면 자료마다 원본 파일이나 URL과 함께 “이 자료로 답해야 하는 질문”을 2-3개 적는다. 예를 들어 “AI 전공 1학년이 먼저 들어야 할 과목은?”, “개발 동아리는 어떤 학생에게 맞나?”처럼 실제 상담 질문을 같이 받으면 chunk 제목, heading, category를 RAG 검색 우선순위에 맞춰 정리할 수 있다.

사용자가 파일이나 사진으로 넘길 때는 아래 정보가 있으면 정형화가 빠르다.

| 필요 정보 | 이유 |
| --- | --- |
| 원본 파일/사진/PDF 또는 공식 URL | 답변 근거에 표시할 출처와 최신성 확인에 사용 |
| 자료명 | `title`, wiki heading, 검색 결과 chip에 사용 |
| 학부/대상 학년 | 소프트웨어학부/인공지능학부, 1학년/2학년 등 개인화 필터에 사용 |
| 자료 유형 | curriculum, track, club, system, career, startup, freshman 중 하나로 분류 |
| 수집일/적용 연도 | 교과과정과 졸업요건처럼 연도별로 바뀌는 자료를 구분 |
| 상담 질문 2-3개 | RAG chunk를 실제 사용자의 질문 형태에 맞게 나누는 기준 |
| 확실하지 않은 부분 표시 | 답변에서 단정하지 않고 “공식 확인 필요”로 처리 |

사진, 캡처, PDF도 가능하다. Codex가 OCR/전사 결과를 사람이 읽을 수 있는 Markdown으로 정리하고, 필요하면 중간 JSON으로 변환한 뒤 `data/raw/*.md`, `data/wiki/*.md`, Supabase `document_chunks`로 이어지게 만든다. 최종 live RAG 기준은 JSON 파일 자체가 아니라 출처가 남은 Markdown과 Supabase chunk다.

## 정형화 흐름

1. 원본 파일을 `data/inbox/`에 둔다.
2. 원본 파일명 기준으로 `pnpm rag:intake-stub -- --file <파일명> --title "<자료 제목>" --category <category> --source "<공식 출처명>"`를 실행해 접수 Markdown stub을 만든다.
3. 생성된 stub에 출처, 대상 학부/학년, category, 핵심 필드를 채운다.
4. 개인정보나 학생 개인 자료가 섞였는지 확인하고 제거한다.
5. 텍스트/Markdown으로 바꾼다.
6. `pnpm rag:intake-check`로 필수 출처/category, placeholder 잔존 여부, 개인정보 위험을 검사한다. `확인 필요`, `TODO`, 기본 전사 안내문이 남아 있으면 blocked 처리하고, 통과한 접수 파일만 `pnpm rag:prepare-raw ...` 명령을 함께 출력한다.
7. `pnpm rag:prepare-raw`로 frontmatter가 있는 raw 문서를 만든다.
8. `pnpm wiki:build`로 `data/wiki`를 재생성한다.
9. `pnpm rag:ingest:dry`로 chunk 수와 category 구성을 확인한다.
10. Supabase schema가 준비되면 `pnpm rag:ingest:embeddings`로 live DB에 넣는다.

예시:

```powershell
pnpm rag:intake-stub -- --file ai-curriculum.pdf --title "인공지능학부 교과과정" --category curriculum --source "국민대학교 학부 홈페이지"
pnpm rag:intake-check
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

## 자료별 필수 메타데이터

| 자료 유형 | 반드시 남길 필드 |
| --- | --- |
| 교과과정/트랙 | 과목명, 학년/학기, 이수구분, 학점, 선수과목, 연결 트랙, 추천 상황 |
| 동아리/활동 | 활동명, 분야, 모집 시기, 활동 내용, 요구 역량, 추천 대상, 신청 경로 |
| 학교 시스템/학사 | 제도명, 사용 시점, 신청/확인 경로, 준비물, 마감, 문의처 |
| 진로/취업/창업 | 프로그램명, 대상, 신청 기간, 얻을 수 있는 결과, 추천 준비, 연결 과목/프로젝트 |

이 필드는 JSON 파일로 바로 저장하지 않아도 된다. 먼저 사람이 읽을 수 있는 Markdown으로 정리하고, ingest 단계에서 `category`, `source_type`, `title`, `heading_path`, `chunk_index`, `content_hash`와 함께 Supabase chunk로 변환한다.

필요하면 정형화 중간 산출물을 JSON으로도 만들 수 있다. 단, live RAG에 넣는 기준 데이터는 최종적으로 `data/raw/*.md`, `data/wiki/*.md`, Supabase `document_chunks`와 출처 URL/파일명이 서로 맞아야 한다.

```json
{
  "title": "소프트웨어학부 1학년 권장 수강",
  "department": "소프트웨어학부",
  "category": "curriculum",
  "audience": ["1학년"],
  "source": "국민대학교 소프트웨어융합대학 공식 페이지",
  "source_url": "https://...",
  "verified_at": "2026-05-23",
  "facts": [
    {
      "topic": "전공 기초",
      "content": "1학년은 프로그래밍 기초와 수학 기초를 우선 확인한다.",
      "answer_when": "신입생이 첫 학기 과목 선택을 질문할 때"
    }
  ]
}
```

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
