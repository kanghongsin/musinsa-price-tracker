#!/bin/bash
# Cloudflare Pages 빌드 스크립트
# 환경변수로 Supabase 설정을 index.html에 주입

set -e

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_ANON_KEY" ]; then
  echo "Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set"
  exit 1
fi

sed -i "s|__SUPABASE_URL__|${SUPABASE_URL}|g" frontend/index.html
sed -i "s|__SUPABASE_ANON_KEY__|${SUPABASE_ANON_KEY}|g" frontend/index.html

echo "Build complete"
