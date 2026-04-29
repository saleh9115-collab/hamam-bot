import requests
import time
import json

# ==================== الإعدادات ====================
TELEGRAM_TOKEN = "8702387334:AAF-Wcw3bSmJlnoRg33Dnna9kmGECOy8u0U"
CHAT_ID = "675363562"

PRODUCTS = [
    {
        "name": "منتج 1 - أصل الحمام",
        "url": "https://salla.sa/asl-al7mam/lGyBxbD",
        "api_url": "https://api.salla.dev/store/v2/products/lGyBxbD"
    },
    {
        "name": "منتج 2 - أصل الحمام",
        "url": "https://salla.sa/asl-al7mam/nEvwRrK",
        "api_url": "https://api.salla.dev/store/v2/products/nEvwRrK"
    }
]

CHECK_INTERVAL = 60  # فحص كل 60 ثانية
# =====================================================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"خطأ في إرسال تيليغرام: {e}")
        return False

def check_product(product):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ar,en;q=0.9",
    }
    try:
        response = requests.get(product["url"], headers=headers, timeout=15)
        page_text = response.text.lower()

        # علامات النفاد
        out_of_stock_keywords = [
            "نفذ", "نفد", "غير متاح", "out of stock", "sold out",
            "unavailable", "نفذت الكمية", "انتهى المخزون"
        ]

        # علامات التوفر
        in_stock_keywords = [
            "أضف إلى السلة", "اضف للسلة", "add to cart", "اشتري الآن",
            "buy now", "متاح", "in stock", "أضف للسلة"
        ]

        is_out = any(kw in page_text for kw in out_of_stock_keywords)
        is_in = any(kw in page_text for kw in in_stock_keywords)

        if is_in and not is_out:
            return "available"
        elif is_out:
            return "out_of_stock"
        else:
            return "unknown"

    except Exception as e:
        print(f"خطأ في الفحص: {e}")
        return "error"

def main():
    print("🚀 بدأ البوت... يراقب المنتجات")
    send_telegram("✅ <b>بوت أصل الحمام شغّال!</b>\n\nسأرسل لك فور توفر المنتجات 👇\n" +
                  "\n".join([f"• {p['name']}" for p in PRODUCTS]))

    # حالة كل منتج
    last_status = {p["url"]: None for p in PRODUCTS}

    while True:
        for product in PRODUCTS:
            status = check_product(product)
            prev = last_status[product["url"]]

            print(f"[{product['name']}] الحالة: {status}")

            # إذا تغيرت الحالة إلى متاح
            if status == "available" and prev != "available":
                msg = (
                    f"🟢 <b>المنتج متاح الآن!</b>\n\n"
                    f"🛒 {product['name']}\n"
                    f"🔗 {product['url']}\n\n"
                    f"⚡ اطلب بسرعة قبل ما ينفد!"
                )
                send_telegram(msg)
                print(f"✅ تم إرسال تنبيه: {product['name']}")

            # إذا نفد بعد توفر
            elif status == "out_of_stock" and prev == "available":
                msg = (
                    f"🔴 <b>نفد المنتج</b>\n\n"
                    f"😔 {product['name']}\n"
                    f"سأنبهك فور توفره مجدداً."
                )
                send_telegram(msg)

            last_status[product["url"]] = status

        print(f"⏳ انتظار {CHECK_INTERVAL} ثانية...\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
