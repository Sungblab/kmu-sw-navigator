# RAG / Mini LLM Wiki 자료 폴더

이 폴더에는 RAG 검색과 Mini LLM Wiki 생성에 사용할 국민대/소프트웨어학부 관련 Markdown 자료를 둡니다.

## 구조

```txt
data/raw/
  팀원이 직접 정리하거나 출처를 표시한 원문 markdown

data/inbox/
  사용자가 준 PDF/사진/캡처/텍스트 원본을 임시로 두는 접수 폴더

data/wiki/
  Python wiki compiler가 생성한 신입생용 wiki markdown
```

## raw 문서 frontmatter

자료를 추가할 때는 문서 상단에 아래 값을 적습니다.

```md
---
title: 문서 제목
category: freshman | track | curriculum | club | roadmap | system | career | startup | general
source: 출처 또는 팀 정리
collected_at: 2026-05-13
---
```

## 사용자 제공 자료 정형화

텍스트나 Markdown으로 받은 자료는 아래 명령으로 `data/raw` 규격에 맞춥니다.

```powershell
pnpm rag:intake-check
pnpm rag:prepare-raw --input ../data/inbox/ai-curriculum.txt --title "인공지능학부 교과과정" --category curriculum --source "국민대학교 학부 홈페이지"
```

PDF, 사진, 캡처 이미지는 먼저 텍스트로 추출하거나 사람이 읽어 `.txt`/`.md`로 정리한 뒤 같은 명령을 사용합니다. 원본은 `data/inbox/`에 두고, RAG 검색에는 `data/raw/*.md`만 사용합니다.

정형화 전에 아래 명령으로 접수 파일의 출처, category, 개인정보 위험을 확인합니다. `data/inbox`의 실제 접수 파일은 `source-intake-template.md`의 기본 정보 항목을 채운 `.md` 또는 `.txt` 파일이어야 합니다. 검사를 통과하면 바로 사용할 `pnpm rag:prepare-raw ...` 명령도 출력됩니다.

```powershell
pnpm rag:intake-check
```

권장 제공 자료:

- 소프트웨어학부/인공지능학부 교과과정, 전공필수/선택, 선수과목, 졸업 요건
- 트랙별 로드맵, 추천 과목, 관련 프로젝트/포트폴리오 예시
- 소프트웨어융합대학 동아리, 학회, 스터디, 해커톤/공모전 활동 안내
- 수강신청, 학사공지, 장학, 상담, 비교과 시스템 사용 방법
- 진로/취업/창업 지원 프로그램, 현장실습, 인턴십 안내

## 위키 생성

```powershell
cd backend
uv run python -m app.scripts.build_wiki --raw-dir ..\data\raw --wiki-dir ..\data\wiki
```

생성된 `data/wiki/_index.md`는 RAG 검색의 우선 자료 카탈로그로 사용합니다.
