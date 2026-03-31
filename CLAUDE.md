# Musinsa Price Tracker

무신사 상품 가격을 추적하는 서비스. 좋아요 상품을 등록하면 가격/품절 변동 시 Discord로 알림.

## 구조

```
mpt-cloud/          # 운영 중인 아키텍처 (이걸 수정할 것)
  frontend/index.html   # 단일 파일 프론트엔드 (전체 UI + JS)
  crawler/crawl.py      # 가격 크롤러 (GitHub Actions 실행)
  migrations/           # Supabase DB 마이그레이션 SQL
  supabase-schema.sql   # 초기 스키마

.github/workflows/
  crawl.yml     # 크롤러 자동 실행 (KST 01/07/13/19시, 하루 4회)
  migrate.yml   # migrations/*.sql push 시 자동 Supabase 적용

mpt-new/        # 미사용 (Spring Boot + MariaDB 버전, 건드리지 말 것)
```

## 인프라

- **프론트엔드**: Cloudflare Pages (main push 시 자동 배포)
- **DB**: Supabase (PostgreSQL) — Free tier 500MB
- **크롤러**: GitHub Actions
- **알림**: Discord Webhook

## DB 핵심

- `product.id` = `goodsNo_userId`
- 삭제는 소프트 삭제 (`is_deleted = true`), 실제 row 삭제 안 함
- `price_history` FK는 `ON DELETE RESTRICT` — 상품 삭제해도 가격 이력 보존
- 기본 사용자: `id='default'`

## 무신사 API

- 상품 상세: `https://goods-detail.musinsa.com/api2/goods/{goodsNo}`
- 좋아요 목록: `https://like.musinsa.com/api2/like/like-page/v1/tab/goods`
  - 응답: `data`가 flat array, GOODS/BANNERS 타입 혼재, cursor 페이지네이션 (`link.next`)

## 배포 방법

프론트엔드/크롤러 수정 → main push → Cloudflare 자동 배포
DB 스키마 변경 → `migrations/` 에 SQL 추가 → push → `migrate.yml` 자동 실행

## 주의사항

- `mpt-cloud/`만 수정. `mpt-new/`는 건드리지 말 것
- migration SQL은 항상 `IF NOT EXISTS` / `IF EXISTS` 붙여서 멱등성 유지
- 크롤러에서 `supabase_patch`는 가격·품절 변동 있을 때만 호출 (불필요한 API 호출 절감)
