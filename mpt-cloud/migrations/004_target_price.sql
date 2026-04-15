-- 목표가 컬럼 추가
ALTER TABLE product ADD COLUMN IF NOT EXISTS target_price INT;
