insert into raw_documents (slug, title, category, source, collected_at, content)
values
  (
    'freshman-guide',
    '신입생 학교생활 안내',
    'freshman',
    '팀 정리 초안 - 공식 출처 확인 필요',
    '2026-05-13',
    '신입생은 포털, eCampus, 수강신청 시스템, 학사 공지 확인 방법을 익혀야 한다.'
  ),
  (
    'kmu-sw-tracks',
    '소프트웨어학부 트랙 안내',
    'track',
    '팀 정리 초안 - 공식 출처 확인 필요',
    '2026-05-13',
    'AI, 웹, 정보보호 관심사별로 Python, React, 네트워크, 운영체제 등을 학습한다.'
  )
on conflict (slug) do nothing;

insert into wiki_pages (slug, title, category, type, content, source_count)
values
  (
    'freshman',
    '신입생 안내',
    'freshman',
    'topic',
    '# 신입생 안내\n\n포털, eCampus, 수강신청, 학사 공지를 먼저 확인한다.',
    1
  ),
  (
    'track',
    '트랙 안내',
    'track',
    'topic',
    '# 트랙 안내\n\nAI, 웹, 정보보호 관심사에 따라 첫 학기 학습 방향을 고른다.',
    1
  )
on conflict (slug) do nothing;

insert into document_chunks (source_type, title, source, category, heading_path, chunk_index, content)
values
  (
    'wiki_page',
    '신입생 안내',
    'data/wiki/freshman.md',
    'freshman',
    '신입생 안내',
    0,
    '포털, eCampus, 수강신청, 학사 공지를 먼저 확인한다.'
  ),
  (
    'wiki_page',
    '트랙 안내',
    'data/wiki/track.md',
    'track',
    '트랙 안내',
    0,
    'AI, 웹, 정보보호 관심사에 따라 첫 학기 학습 방향을 고른다.'
  ),
  (
    'raw_document',
    '소프트웨어학부 트랙 안내',
    'data/raw/kmu-sw-tracks.md',
    'track',
    '소프트웨어학부 트랙 안내',
    0,
    'AI와 데이터 분석에 관심이 있는 학생은 Python, 수학/통계, 자료구조, 머신러닝 관련 학습 방향을 우선 탐색한다.'
  );

insert into wiki_logs (action, summary, affected_pages)
values ('build', 'seed 데이터 기준 wiki page 2개 생성', array['freshman', 'track']);
