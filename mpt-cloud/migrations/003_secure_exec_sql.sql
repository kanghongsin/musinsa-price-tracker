-- exec_sql 함수를 service_role 전용으로 제한
-- anon/authenticated key로 임의 SQL 실행 불가
REVOKE EXECUTE ON FUNCTION exec_sql(text) FROM anon;
REVOKE EXECUTE ON FUNCTION exec_sql(text) FROM authenticated;
