# Musinsa Price Tracker

무신사 상품 가격 추적기. 관심 상품의 가격 변동을 추적하고 최저가를 기록합니다.

## 아키텍처

완전 무료(0원) 클라우드 구성:

| 역할 | 서비스 |
|------|--------|
| DB | Supabase (PostgreSQL) |
| 프론트엔드 호스팅 | Cloudflare Pages |
| 자동 크롤링 | GitHub Actions (예정) |

## 주요 기능

- 상품 번호/URL로 간편 등록
- 북마클릿으로 무신사 찜 목록 일괄 등록
- 쿠폰 적용가 기준 가격 추적
- 최저가 기록 및 가격 변동 이력
- 검색, 카테고리/브랜드 필터, 가격대 필터
- 할인율/가격/등록일 정렬
- 품절 상품 필터
- 선택 모드로 일괄 삭제 (실행취소 지원)

## 기술 스택

- Frontend: HTML/CSS/JS (단일 파일)
- DB: Supabase (supabase-js CDN)
- Hosting: Cloudflare Pages
- Chart: Chart.js

## 배포

1. Supabase 프로젝트 생성 후 `mpt-cloud/supabase-schema.sql` 실행
2. `mpt-cloud/frontend/index.html`에 Supabase URL/Key 설정
3. Cloudflare Pages에 GitHub 연동 (Root directory: `mpt-cloud/frontend`)
