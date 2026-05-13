# RAG / Mini LLM Wiki 자료 폴더

이 폴더에는 RAG 검색과 Mini LLM Wiki 생성에 사용할 국민대/소프트웨어학부 관련 Markdown 자료를 둡니다.

## 구조

```txt
data/raw/
  팀원이 직접 정리하거나 출처를 표시한 원문 markdown

data/wiki/
  Python wiki compiler가 생성한 신입생용 wiki markdown
```

## raw 문서 frontmatter

자료를 추가할 때는 문서 상단에 아래 값을 적습니다.

```md
---
title: 문서 제목
category: freshman | track | club | roadmap | system | general
source: 출처 또는 팀 정리
collected_at: 2026-05-13
---
```

## 위키 생성

```powershell
cd backend
uv run python -m app.scripts.build_wiki --raw-dir ..\data\raw --wiki-dir ..\data\wiki
```

생성된 `data/wiki/_index.md`는 RAG 검색의 우선 자료 카탈로그로 사용합니다.
