# KMU SW 공식 사이트 크롤링 요약

- 기준 URL: https://cs.kookmin.ac.kr/
- robots: 200 / User-agent: *
- sitemap URL: 58개
- 크롤링 HTML/기타 페이지: 180개, 성공 158개, 실패 22개
- PDF 링크: 15개
- 내부 이미지: 104개
- 외부 링크: 429개

## RAG 우선 후보 페이지
- https://cs.kookmin.ac.kr/ai/major | chars=14812 | topics=curriculum,graduation,track,career,activities,ai | title=전공개요 - 인공지능학부소개 | 전공개요 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/major/track_info | chars=13749 | topics=curriculum,graduation,track,career,activities,ai | title=트랙소개 - 소프트웨어학부소개 | 트랙소개 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/research/laboratory | chars=10382 | topics=curriculum,graduation,track,career,activities,ai | title=연구실 - 연구활동 | 연구실 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2779?sc=327 | chars=6264 | topics=curriculum,graduation,track,career,activities,ai | title=2026학년도 1학기 현장실습 운영안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2506?sc=327 | chars=6025 | topics=curriculum,graduation,track,career,activities,ai | title=2024학년도 동계 현장실습 운영 안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/intro/professor | chars=5775 | topics=curriculum,graduation,track,career,activities,ai | title=교수진 - 대학소개 | 교수진 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2782?sc=327 | chars=5293 | topics=curriculum,graduation,track,career,activities,ai | title=2026학년도 1학기 코호트 Class 헬퍼 선발 안내(~02.12) - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2786?sc=326 | chars=4787 | topics=curriculum,graduation,track,career,activities,ai | title=2026학년도 1학기 신(편)입생 학생증 발급 안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/kookmin/suburb | chars=4606 | topics=curriculum,graduation,track,career,activities,ai | title=교외채용 - 알림마당 | 국민대학교공지 | 교외채용 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2781?sc=327 | chars=4525 | topics=curriculum,graduation,track,career,activities,ai | title=2026학년도 2월 국민대학교 코딩 역량 인증제 신청 안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/kookmin/library | chars=4396 | topics=curriculum,graduation,track,career,activities,ai | title=도서관공지 - 알림마당 | 국민대학교공지 | 도서관공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2611 | chars=4375 | topics=curriculum,graduation,track,career,activities,ai | title=[S-TEAM] 2025학년도 1학기 '학습법 특강&워크숍' 프로그램 안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2793?sc=327 | chars=4199 | topics=curriculum,graduation,track,career,activities,ai | title=2026학년도 KMU-UCI Summer GREAT Program 선발 공지 (모집 연장) - 알림마당 | SW 학사공지 - 국민대학교 소프트웨
- https://cs.kookmin.ac.kr/news/notice/2707?sc=327 | chars=4174 | topics=curriculum,graduation,track,career,activities,ai | title=2025학년도 2학기「모각공」모집 안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2709?sc=327 | chars=4076 | topics=curriculum,graduation,track,career,activities,ai | title=2025학년도 2학기 코호트 Class 헬퍼 온라인 운영 안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2807?sc=327 | chars=4021 | topics=curriculum,graduation,track,career,activities,ai | title=2026학년도 1학기 PCCE/P 단체 응시 접수 안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2823?sc=326 | chars=4010 | topics=curriculum,graduation,track,career,activities,ai | title=★2025학년도 후기(2026년 8월) 졸업심사대상자 학부(과)인증 서류 제출 안내(~6/4(목) 16:00)★ - 알림마당 | SW 학사공지 
- https://cs.kookmin.ac.kr/news/notice/2642 | chars=3898 | topics=curriculum,graduation,track,career,activities,ai | title=★2024학년도 후기 졸업심사대상자 학부(과)인증 서류 제출 안내(~6/13(금) 16:00) - 알림마당 | SW 학사공지 - 국민대학교 소프
- https://cs.kookmin.ac.kr/news/notice/2801?sc=327 | chars=3844 | topics=curriculum,graduation,track,career,activities,ai | title=2026학년도 소프트웨어융합대학 멘토링 시스템 재개 안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2628 | chars=3612 | topics=curriculum,graduation,track,career,activities,ai | title=국민대학교 ‘AI스타펠로우십 지원사업’ 선정 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2412?sc=327 | chars=3461 | topics=curriculum,graduation,track,career,activities,ai | title=2024년 TOPCIT 제21회 정기평가 시행 안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2789?sc=326 | chars=3450 | topics=curriculum,graduation,track,career,activities,ai | title=기계공학부 학술 로봇동아리 KUDOS에서 16기를 모집합니다! - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2622 | chars=3430 | topics=curriculum,graduation,track,career,activities,ai | title=머신러닝&패턴인식 연구실 학부 연구생 모집(~5/10 23:00) - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2623 | chars=3390 | topics=curriculum,graduation,track,career,activities,ai | title=2025 ACPC 대회 안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/supervision/intro | chars=3380 | topics=curriculum,graduation,track,career,activities,ai | title=장학안내 - 입학/장학안내 | 장학안내 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/lab/ai | chars=3271 | topics=curriculum,graduation,track,career,activities,ai | title=인공지능연구소 - 연구소개 | 인공지능연구소 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2632 | chars=3253 | topics=curriculum,graduation,track,career,activities,ai | title=코딩역량인증 시험(PCCP/E) 접수 안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2632?sc=327 | chars=3208 | topics=curriculum,graduation,track,career,activities,ai | title=코딩역량인증 시험(PCCP/E) 접수 안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2629?sc=327 | chars=3185 | topics=curriculum,graduation,track,career,activities,ai | title=프로그래머스 캠퍼스 가입 안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학
- https://cs.kookmin.ac.kr/news/notice/2629 | chars=3177 | topics=curriculum,graduation,track,career,activities,ai | title=프로그래머스 캠퍼스 가입 안내 - 알림마당 | SW 학사공지 - 국민대학교 소프트웨어융합대학

## PDF 후보
- https://cs.kookmin.ac.kr/images/major/pdf/ai_curriculum_2022.pdf | status=200 | type=application/pdf | length=88650
- https://cs.kookmin.ac.kr/images/major/pdf/ai_curriculum_2025.pdf | status=200 | type=application/pdf | length=753106
- https://cs.kookmin.ac.kr/images/major/pdf/curriculum_2018.pdf | status=200 | type=application/pdf | length=4045200
- https://cs.kookmin.ac.kr/images/major/pdf/curriculum_2019.pdf | status=404 | type= | length=None
- https://cs.kookmin.ac.kr/images/major/pdf/curriculum_2025.pdf | status=200 | type=application/pdf | length=894015
- https://cs.kookmin.ac.kr/images/major/pdf/curriculum_img_2009.pdf | status=200 | type=application/pdf | length=960729
- https://cs.kookmin.ac.kr/images/major/pdf/curriculum_img_2010.pdf | status=200 | type=application/pdf | length=911974
- https://cs.kookmin.ac.kr/images/major/pdf/curriculum_img_2011.pdf | status=200 | type=application/pdf | length=1166507
- https://cs.kookmin.ac.kr/images/major/pdf/curriculum_img_2012.pdf | status=404 | type= | length=None
- https://cs.kookmin.ac.kr/images/major/pdf/curriculum_img_2013.pdf | status=200 | type=application/pdf | length=979868
- https://cs.kookmin.ac.kr/images/major/pdf/curriculum_img_2014.pdf | status=200 | type=application/pdf | length=1010947
- https://cs.kookmin.ac.kr/images/major/pdf/curriculum_img_2015.pdf | status=200 | type=application/pdf | length=734320
- https://cs.kookmin.ac.kr/images/major/pdf/curriculum_img_2015_02.pdf | status=200 | type=application/pdf | length=734320
- https://cs.kookmin.ac.kr/images/major/pdf/graduated_1.pdf | status=200 | type=application/pdf | length=49257
- https://cs.kookmin.ac.kr/images/major/pdf/graduated_2.pdf | status=200 | type=application/pdf | length=59078

## 텍스트가 약한 페이지
- https://cs.kookmin.ac.kr/ai/graduated | chars=0 | title=

## 실패 페이지
- https://cs.kookmin.ac.kr/kookmin/ceo | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/kookmin/newsplus | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/kookmin/people | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/kookmin/press | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/kookmin/prof_library | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/kookmin/special | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/kookmin/ucc | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/major/curriculum | status=500 | error=HTTP Error 500: Internal Server Error
- https://cs.kookmin.ac.kr/news/cal | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/news/event | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/news/form | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/news/jobs | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/news/kookmin/academic | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/news/kookmin/administration | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/news/kookmin/recruit | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/news/kookmin/scholarship | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/news/kookmin/social_service | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/news/kookmin/special_lecture | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/news/notice | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/news/scholarship | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/news/notice?sc=326 | status=404 | error=HTTP Error 404: Not Found
- https://cs.kookmin.ac.kr/news/notice?sc=327 | status=404 | error=HTTP Error 404: Not Found