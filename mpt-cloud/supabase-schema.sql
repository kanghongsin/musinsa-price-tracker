-- Supabase에서 SQL Editor로 실행할 스키마

-- 상품 테이블
CREATE TABLE product (
    id BIGINT PRIMARY KEY,              -- 무신사 상품번호
    name TEXT NOT NULL,
    image_url TEXT,
    product_url TEXT,
    brand_name TEXT,
    category TEXT,                       -- 상의, 바지, 아우터 등
    current_price INTEGER,
    original_price INTEGER,
    lowest_price INTEGER,
    initial_price INTEGER,               -- 등록 시점 가격 (할인율 계산용)
    is_sold_out BOOLEAN DEFAULT FALSE,   -- 품절 여부
    is_soon_out_of_stock BOOLEAN DEFAULT FALSE, -- 품절 임박
    review_count INTEGER DEFAULT 0,
    review_score NUMERIC(2,1) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 가격 이력 테이블
CREATE TABLE price_history (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT REFERENCES product(id) ON DELETE CASCADE,
    price INTEGER,
    original_price INTEGER,
    checked_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_price_history_product ON price_history(product_id, checked_at);

-- RLS (Row Level Security) 비활성화 - 개인용이니까
ALTER TABLE product ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_history ENABLE ROW LEVEL SECURITY;

-- 누구나 읽기/쓰기 가능 (개인용)
CREATE POLICY "Allow all on product" ON product FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on price_history" ON price_history FOR ALL USING (true) WITH CHECK (true);
