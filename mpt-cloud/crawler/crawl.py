"""
GitHub Actions용 가격 크롤러
2시간마다 등록된 상품의 가격/품절 상태를 체크해서 Supabase에 저장
"""
import os
import requests
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]  # service_role key (서버용)
GOODS_API = "https://goods-detail.musinsa.com/api2/goods/"

HEADERS_MUSINSA = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36",
    "Accept": "application/json",
}
HEADERS_SUPABASE = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}


def supabase_get(table, params=""):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=HEADERS_SUPABASE)
    r.raise_for_status()
    return r.json()


def supabase_patch(table, match_col, match_val, data):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{match_col}=eq.{match_val}",
        json=data, headers=HEADERS_SUPABASE,
    )
    r.raise_for_status()


def supabase_post(table, data):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        json=data, headers=HEADERS_SUPABASE,
    )
    r.raise_for_status()


def fetch_goods(goods_no):
    """무신사 API에서 상품 정보 조회"""
    try:
        r = requests.get(GOODS_API + str(goods_no), headers=HEADERS_MUSINSA, timeout=15)
        r.raise_for_status()
        d = r.json()
        if d.get("meta", {}).get("result") != "SUCCESS":
            return None
        g = d["data"]
        gp = g.get("goodsPrice", {})
        coupon = gp.get("couponPrice", 0)
        sale = gp.get("salePrice", 0)
        best_price = coupon if coupon and coupon > 0 else sale
        is_sold_out = g.get("goodsSaleType") != "SALE" or bool(g.get("isOutOfStock", False))
        return {
            "price": best_price,
            "original_price": gp.get("normalPrice", 0),
            "is_sold_out": is_sold_out,
        }
    except Exception as e:
        print(f"  Error fetching {goods_no}: {e}")
        return None


def main():
    products = supabase_get("product", "select=id,current_price,lowest_price")
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}] Checking {len(products)} products...")

    now = datetime.now(timezone.utc).isoformat()
    updated = 0
    changed = 0

    for p in products:
        goods_no = p["id"]
        old_price = p.get("current_price") or 0
        info = fetch_goods(goods_no)
        if not info:
            continue

        price_changed = info["price"] != old_price

        # 가격 변동 시에만 이력 추가
        if price_changed:
            supabase_post("price_history", {
                "product_id": goods_no,
                "price": info["price"],
                "original_price": info["original_price"],
                "checked_at": now,
            })
            changed += 1

        # 상품 정보 업데이트 (updated_at은 항상 갱신)
        new_lowest = min(p.get("lowest_price") or info["price"], info["price"])
        supabase_patch("product", "id", goods_no, {
            "current_price": info["price"],
            "original_price": info["original_price"],
            "lowest_price": new_lowest,
            "is_sold_out": info["is_sold_out"],
            "updated_at": now,
        })

        status = " [SOLD OUT]" if info["is_sold_out"] else ""
        change = ""
        if price_changed:
            diff = info["price"] - old_price
            change = f" ({'+' if diff > 0 else ''}{diff:,})"
        print(f"  {goods_no}: {info['price']:,}원{change}{status}")
        updated += 1

    print(f"Done! {updated} checked, {changed} price changed.")


if __name__ == "__main__":
    main()
