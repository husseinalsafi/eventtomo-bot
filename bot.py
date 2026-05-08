import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
import pytz
import schedule
import time
import threading
from telegram import Bot
from telegram.constants import ParseMode

# ─────────────────────────────────────────
#  الإعدادات
# ─────────────────────────────────────────
BOT_TOKEN   = os.environ.get("BOT_TOKEN", "")
CHANNEL_ID  = os.environ.get("CHANNEL_ID", "")   # مثال: @my_channel أو -100xxxxxxxxxx
NOTIFY_HOUR = int(os.environ.get("NOTIFY_HOUR", "9"))   # ساعة الإرسال (صباحاً)
TIMEZONE    = "Asia/Baghdad"

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────
#  تحميل قاعدة بيانات الأيام
# ─────────────────────────────────────────
def load_days():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "days.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_events_for_date(month: int, day: int) -> list[dict]:
    """يرجع كل الأحداث اللي تنطبق على التاريخ المعطى"""
    data = load_days()
    events = []
    for category in ["international_days", "iraqi_national_days", "custom_days"]:
        for item in data.get(category, []):
            if item["month"] == month and item["day"] == day:
                item["_category"] = category
                events.append(item)
    return events

# ─────────────────────────────────────────
#  بناء رسالة الإشعار
# ─────────────────────────────────────────
def build_message(events: list[dict], event_date: datetime) -> str:
    day_str   = event_date.strftime("%-d")
    month_map = {
        1:"يناير", 2:"فبراير", 3:"مارس",    4:"أبريل",
        5:"مايو",  6:"يونيو",  7:"يوليو",   8:"أغسطس",
        9:"سبتمبر",10:"أكتوبر",11:"نوفمبر",12:"ديسمبر"
    }
    month_str = month_map[event_date.month]

    lines = [
        f"🔔 *تذكير — غداً {day_str} {month_str}*\n",
    ]

    for ev in events:
        cat = ev.get("_category", "")
        tag = ""
        if cat == "international_days":
            tag = "🌍 يوم عالمي"
        elif cat == "iraqi_national_days":
            tag = "🇮🇶 يوم وطني عراقي"
        elif cat == "iraqi_religious_days":
            tag = "☪️ مناسبة دينية"
        else:
            tag = "📌 مناسبة خاصة"

        lines.append(f"{ev['emoji']} *{ev['name']}*")
        lines.append(f"   _{tag}_\n")

    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("📅 تابعونا للمزيد من المناسبات")
    return "\n".join(lines)

# ─────────────────────────────────────────
#  إرسال الإشعار
# ─────────────────────────────────────────
async def send_notification():
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    tomorrow = now + timedelta(days=1)

    events = get_events_for_date(tomorrow.month, tomorrow.day)

    if not events:
        log.info(f"لا توجد أحداث غداً ({tomorrow.strftime('%d/%m')})")
        return

    message = build_message(events, tomorrow)
    bot = Bot(token=BOT_TOKEN)

    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )
        log.info(f"✅ تم الإرسال — {len(events)} حدث(أحداث) لـ {tomorrow.strftime('%d/%m')}")
    except Exception as e:
        log.error(f"❌ خطأ في الإرسال: {e}")

# ─────────────────────────────────────────
#  اختبار يدوي: أرسل إشعار فوراً (اختياري)
# ─────────────────────────────────────────
async def send_test():
    log.info("🧪 وضع الاختبار — إرسال إشعار الآن...")
    await send_notification()

# ─────────────────────────────────────────
#  جدول المهام اليومي
# ─────────────────────────────────────────
def run_scheduler():
    send_time = f"{NOTIFY_HOUR:02d}:00"
    log.info(f"⏰ الجدولة: كل يوم الساعة {send_time} (توقيت بغداد)")

    schedule.every().day.at(send_time).do(
        lambda: asyncio.run(send_notification())
    )

    while True:
        schedule.run_pending()
        time.sleep(30)

# ─────────────────────────────────────────
#  نقطة الدخول
# ─────────────────────────────────────────
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN غير موجود! أضفه في متغيرات البيئة.")
    if not CHANNEL_ID:
        raise ValueError("❌ CHANNEL_ID غير موجود! أضفه في متغيرات البيئة.")

    log.info("🚀 البوت شغّال...")
    run_scheduler()
