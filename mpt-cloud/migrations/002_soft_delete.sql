-- 소프트 삭제 지원: 삭제해도 DB에 데이터 보존
-- product 삭제 시 is_deleted = TRUE로만 변경, price_history는 그대로 유지

-- 소프트 삭제 컬럼 추가
ALTER TABLE product ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE product ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- ON DELETE CASCADE 제거 → 상품 삭제해도 이력 보존
-- 기존 FK 제거 후 RESTRICT로 재생성
ALTER TABLE price_history DROP CONSTRAINT IF EXISTS price_history_product_id_fkey;
ALTER TABLE price_history ADD CONSTRAINT price_history_product_id_fkey
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE RESTRICT;
