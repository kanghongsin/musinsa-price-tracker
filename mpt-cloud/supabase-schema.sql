-- Supabase에서 SQL Editor로 실행할 스키마

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 상품 테이블 (id = goodsNo_userId)
CREATE TABLE IF NOT EXISTS product (
    id TEXT PRIMARY KEY,                  -- goodsNo_userId 형태
    goods_no BIGINT,                      -- 무신사 상품번호
    user_id TEXT DEFAULT 'default' REFERENCES users(id),
    name TEXT NOT NULL,
    image_url TEXT,
    product_url TEXT,
    brand_name TEXT,
    category TEXT,                        -- 상의, 바지, 아우터 등
    current_price INTEGER,
    original_price INTEGER,
    lowest_price INTEGER,
    initial_price INTEGER,                -- 등록 시점 가격
    previous_price INTEGER,               -- 직전 가격 (변동률 계산용)
    is_sold_out BOOLEAN DEFAULT FALSE,
    is_soon_out_of_stock BOOLEAN DEFAULT FALSE,
    is_unliked BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    review_count INTEGER DEFAULT 0,
    review_score NUMERIC(2,1) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 마이그레이션 자동 실행용 함수 (GitHub Actions에서 사용)
CREATE OR REPLACE FUNCTION exec_sql(query TEXT)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER
AS $$ BEGIN EXECUTE query; END; $$;

-- 가격 이력 테이블
CREATE TABLE IF NOT EXISTS price_history (
    id BIGSERIAL PRIMARY KEY,
    product_id TEXT REFERENCES product(id) ON DELETE RESTRICT,
    price INTEGER,
    original_price INTEGER,
    checked_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_price_history_product ON price_history(product_id, checked_at);

-- RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE product ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all on users" ON users FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on product" ON product FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on price_history" ON price_history FOR ALL USING (true) WITH CHECK (true);

-- 기본 사용자
INSERT INTO users (id, name) VALUES ('default', '기본 사용자') ON CONFLICT DO NOTHING;
