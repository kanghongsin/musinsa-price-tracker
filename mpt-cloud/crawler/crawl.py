"""
GitHub Actions용 가격 크롤러
2시간마다 등록된 상품의 가격/품절 상태를 체크해서 Supabase에 저장
"""
import os
import requests
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]  # service_role key (서버용)
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL", "")
GOODS_API = "https://goods-detail.musinsa.com/api2/goods/"
PRODUCT_URL = "https://www.musinsa.com/products/"

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
        review = g.get("goodsReview", {})
        return {
            "price": best_price,
            "original_price": gp.get("normalPrice", 0),
            "is_sold_out": is_sold_out,
            "is_soon_out_of_stock": bool(g.get("isSoonOutOfStock", False)),
            "review_count": review.get("totalCount", 0),
            "review_score": review.get("satisfactionScore", 0),
        }
    except Exception as e:
        print(f"  Error fetching {goods_no}: {e}")
        return None


def send_discord(embeds):
    """Discord 웹훅으로 알림 전송"""
    if not DISCORD_WEBHOOK or not embeds:
        return
    # Discord 웹훅은 한 번에 최대 10개 embed
    for i in range(0, len(embeds), 10):
        batch = embeds[i:i+10]
        try:
            r = requests.post(DISCORD_WEBHOOK, json={"embeds": batch}, timeout=10)
            r.raise_for_status()
        except Exception as e:
            print(f"  Discord error: {e}")


def main():
    products = supabase_get("product", "select=id,goods_no,name,current_price,lowest_price,image_url,is_sold_out,user_id")
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}] Checking {len(products)} products...")

    now = datetime.now(timezone.utc).isoformat()
    updated = 0
    changed = 0
    alerts = []

    for p in products:
        product_id = p["id"]
        goods_no = p.get("goods_no") or product_id  # 하위 호환
        old_price = p.get("current_price") or 0
        old_lowest = p.get("lowest_price") or 0
        info = fetch_goods(goods_no)
        if not info:
            continue

        price_changed = info["price"] != old_price

        # 가격 변동 시에만 이력 추가
        if price_changed:
            supabase_post("price_history", {
                "product_id": product_id,
                "price": info["price"],
                "original_price": info["original_price"],
                "checked_at": now,
            })
            changed += 1

        # 상품 정보 업데이트 (updated_at은 항상 갱신)
        new_lowest = min(old_lowest or info["price"], info["price"])
        update_data = {
            "current_price": info["price"],
            "original_price": info["original_price"],
            "lowest_price": new_lowest,
            "is_sold_out": info["is_sold_out"],
            "is_soon_out_of_stock": info["is_soon_out_of_stock"],
            "review_count": info["review_count"],
            "review_score": info["review_score"],
            "updated_at": now,
        }
        if price_changed:
            update_data["previous_price"] = old_price
        supabase_patch("product", "id", product_id, update_data)

        # 재입고 알림
        was_sold_out = p.get("is_sold_out", False)
        if was_sold_out and not info["is_sold_out"]:
            alerts.append({
                "title": f"🔔 재입고! {p.get('name', str(goods_no))}",
                "url": PRODUCT_URL + str(goods_no),
                "color": 0x2ecc71,  # 초록
                "fields": [
                    {"name": "현재 가격", "value": f"**{info['price']:,}원**", "inline": True},
                ],
                **({"thumbnail": {"url": p["image_url"]}} if p.get("image_url") else {}),
            })

        # 가격 변동 시 알림 데이터 수집 (1% 미만 변동은 무시)
        if price_changed and old_price > 0 and abs(info["price"] - old_price) / old_price >= 0.01:
            diff = info["price"] - old_price
            is_new_lowest = info["price"] < (old_lowest or info["price"])
            discount = round((1 - info["price"] / info["original_price"]) * 100) if info["original_price"] else 0

            if diff < 0:
                color = 0x3498db  # 파란색 (인하)
                emoji = "🔽"
            else:
                color = 0xe74c3c  # 빨간색 (인상)
                emoji = "🔺"

            title = f"{emoji} {p.get('name', str(goods_no))}"
            if is_new_lowest:
                title = f"🏆 역대 최저가! {p.get('name', str(goods_no))}"
                color = 0xf1c40f  # 금색

            fields = [
                {"name": "이전 가격", "value": f"{old_price:,}원", "inline": True},
                {"name": "현재 가격", "value": f"**{info['price']:,}원** ({'+' if diff > 0 else ''}{diff:,})", "inline": True},
                {"name": "할인율", "value": f"{discount}%", "inline": True},
            ]
            if is_new_lowest:
                fields.append({"name": "최저가 갱신", "value": f"~~{old_lowest:,}원~~ → **{info['price']:,}원**", "inline": False})

            embed = {
                "title": title,
                "url": PRODUCT_URL + str(goods_no),
                "color": color,
                "fields": fields,
            }
            thumb = p.get("image_url", "")
            if thumb:
                embed["thumbnail"] = {"url": thumb}

            alerts.append(embed)

        status = " [SOLD OUT]" if info["is_sold_out"] else ""
        change = ""
        if price_changed:
            diff = info["price"] - old_price
            change = f" ({'+' if diff > 0 else ''}{diff:,})"
        print(f"  {goods_no}: {info['price']:,}원{change}{status}")
        updated += 1

    # Discord 알림 전송
    if alerts:
        send_discord(alerts)
        print(f"Discord: {len(alerts)} alerts sent.")

    print(f"Done! {updated} checked, {changed} price changed.")


if __name__ == "__main__":
    main()
