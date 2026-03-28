# Musinsa Price Tracker

무신사 관심 상품의 가격 변동을 자동 추적하는 0원 클라우드 서비스.

## 구조

```
Cloudflare Pages (프론트) → Supabase (DB) ← GitHub Actions (크롤러, 2h마다)
                                            ↓
                                      Discord 알림
```

```
mpt-cloud/
├── frontend/index.html        # 프론트엔드 (단일 파일)
├── crawler/crawl.py           # 가격 크롤러 (GitHub Actions)
├── migrations/*.sql           # DB 마이그레이션 (push 시 자동 실행)
└── supabase-schema.sql        # 초기 DB 스키마
```

## 기능

- URL/상품번호로 등록, 북마클릿으로 찜 목록 일괄 등록
- 쿠폰 적용가 기준 추적, 직전가 대비 변동률 표시
- 역대 최저가 뱃지, 품절/품절임박/좋아요 해제 표시
- 검색, 카테고리/브랜드 다중 필터, 가격대 필터, 정렬
- 멀티유저 (클릭 전환), 일괄 삭제 (실행취소), 가격 차트
- Discord 알림 (가격 변동, 최저가 갱신, 재입고)

## 배포 (최초 1회)

1. **Supabase** - 프로젝트 생성 → SQL Editor에서 `supabase-schema.sql` 실행
2. **프론트엔드** - `frontend/index.html`에 Supabase URL/Key 입력
3. **Cloudflare Pages** - GitHub 연동, Root directory: `mpt-cloud/frontend`
4. **GitHub Secrets** - `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `DISCORD_WEBHOOK_URL`

## DB 마이그레이션

`mpt-cloud/migrations/`에 SQL 파일 추가 후 push → GitHub Actions가 자동 실행.

파일명 규칙: `001_설명.sql`, `002_설명.sql`, ...
