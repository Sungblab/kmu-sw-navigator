# 자료 수집 inbox

사용자가 제공한 원본 파일을 임시로 두는 폴더입니다. 이 폴더의 파일은 바로 RAG에 들어가지 않고, 검토 후 `data/raw/*.md`로 정형화합니다.

## 받을 수 있는 자료

- 학부/전공 교과과정 PDF, 페이지 캡처, 표 이미지
- 트랙/전공 선택 안내 문서
- 동아리/학회/스터디 소개 페이지 캡처
- 학사 시스템, 수강신청, 장학, 졸업 요건 안내
- 진로/취업/창업 지원 프로그램 안내

## 정형화 기준

1. 출처와 수집일을 확인합니다.
2. 원본 PDF/사진/캡처/텍스트가 있으면 `pnpm rag:intake-stub -- --file <파일명> --title "<자료 제목>" --category <category> --source "<공식 출처명>"`로 접수 stub을 만듭니다.
3. `source-intake-template.md` 기준으로 학부/학년/category/핵심 필드를 채웁니다.
4. 표/사진/PDF는 텍스트로 추출하거나 사람이 읽어 Markdown으로 옮깁니다.
5. `확인 필요`, `TODO`, 기본 전사 안내문 같은 placeholder를 실제 내용으로 바꿉니다.
6. `pnpm rag:intake-check`로 출처/category/개인정보 위험을 먼저 확인합니다. placeholder가 남아 있으면 blocked 처리하며, 통과한 파일은 다음 단계에서 쓸 `pnpm rag:prepare-raw ...` 명령을 함께 출력합니다.
7. `pnpm rag:prepare-raw`로 frontmatter가 있는 `data/raw/*.md` 파일을 만듭니다.
8. `pnpm wiki:build`로 Mini LLM Wiki를 재생성합니다.
9. `pnpm rag:ingest:dry`로 chunk 수를 확인합니다.
10. Supabase schema가 준비된 뒤 `pnpm rag:ingest:embeddings`로 live vector 자료를 넣습니다.

## 개인정보 주의

학생 이름, 학번, 전화번호, 이메일, 성적표, 개인 상담 내용은 넣지 않습니다. 필요한 경우 개인 식별 정보를 지운 뒤 학업 안내 정보만 남깁니다.
