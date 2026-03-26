-- 멀티유저 마이그레이션 SQL
-- Supabase SQL Editor에서 실행

-- 1. users 테이블 생성
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "users_all" ON users FOR ALL USING (true) WITH CHECK (true);
INSERT INTO users (id, name) VALUES ('default', '기본 사용자') ON CONFLICT DO NOTHING;

-- 2. price_history FK 제거 (id 타입 변경 전)
ALTER TABLE price_history DROP CONSTRAINT IF EXISTS price_history_product_id_fkey;

-- 3. product 테이블에 새 컬럼 추가
ALTER TABLE product ADD COLUMN IF NOT EXISTS goods_no BIGINT;
ALTER TABLE product ADD COLUMN IF NOT EXISTS user_id TEXT DEFAULT 'default';
ALTER TABLE product ADD COLUMN IF NOT EXISTS previous_price INTEGER;

-- 4. goods_no 채우기 (기존 id 복사)
UPDATE product SET goods_no = id WHERE goods_no IS NULL;

-- 5. id 컬럼을 TEXT로 변경
ALTER TABLE product ALTER COLUMN id TYPE TEXT USING id::TEXT;

-- 6. id를 goodsNo_userId 형태로 변경
UPDATE product SET id = goods_no::TEXT || '_' || user_id WHERE id NOT LIKE '%_%';

-- 7. price_history.product_id도 TEXT로 변경
ALTER TABLE price_history ALTER COLUMN product_id TYPE TEXT USING product_id::TEXT;

-- 8. price_history.product_id를 새 id 형태로 변경
UPDATE price_history SET product_id = product_id || '_default' WHERE product_id NOT LIKE '%_%';

-- 9. FK 다시 추가
ALTER TABLE price_history ADD CONSTRAINT price_history_product_id_fkey
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE;

-- 10. user_id FK 추가
ALTER TABLE product ADD CONSTRAINT product_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id);
