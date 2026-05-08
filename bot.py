import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
import pytz
import time
from telegram import Bot
from telegram.constants import ParseMode

BOT_TOKEN   = os.environ.get("BOT_TOKEN", "")
CHANNEL_ID  = os.environ.get("CHANNEL_ID", "")
NOTIFY_HOUR = int(os.environ.get("NOTIFY_HOUR", "9"))
TIMEZONE    = "Asia/Baghdad"

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)


def load_days():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "days.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_events_for_date(month, day):
    data = load_days()
    events = []
    for category in ["international_days", "iraqi_national_days", "custom_days"]:
        for item in data.get(category, []):
            if item["month"] == month and item["day"] == day:
                item["_category"] = category
                events.append(item)
    return events


def build_message(events, event_date):
    month_map = {
        1:"يناير", 2:"فبراير", 3:"مارس",    4:"ابريل",
        5:"مايو",  6:"يونيو",  7:"يوليو",   8:"اغسطس",
        9:"سبتمبر",10:"اكتوبر",11:"نوفمبر",12:"ديسمبر"
    }
    day_str   = str(event_date.day)
    month_str = month_map[event_date.month]

    lines = ["تذكير - غدا " + day_str + " " + month_str + "\n"]

    for ev in events:
        cat = ev.get("_category", "")
        if cat == "international_days":
            tag = "يوم عالمي"
        elif cat == "iraqi_national_days":
            tag = "يوم وطني عراقي"
        else:
            tag = "مناسبة خاصة"
        lines.append(ev['emoji'] + " " + ev['name'])
        lines.append("   " + tag + "\n")

    lines.append("──────────────")
    lines.append("@mr_alsafi")
    return "\n".join(lines)


async def send_notification():
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    tomorrow = now + timedelta(days=1)
    events = get_events_for_date(tomorrow.month, tomorrow.day)

    if not events:
        log.info(f"لا توجد احداث غدا ({tomorrow.day}/{tomorrow.month})")
        return

    message = build_message(events, tomorrow)
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=message)
        log.info(f"تم الارسال - {len(events)} حدث")
    except Exception as e:
        log.error(f"خطا في الارسال: {e}")


def run_scheduler():
    tz = pytz.timezone(TIMEZONE)
    log.info(f"البوت شغال - ينتظر الساعة {NOTIFY_HOUR:02d}:00 بتوقيت بغداد")
    sent_today = False
    last_day = -1

    while True:
        now = datetime.now(tz)

        if now.day != last_day:
            sent_today = False
            last_day = now.day
            log.info(f"يوم جديد: {now.strftime('%Y-%m-%d')}")

        if now.hour == NOTIFY_HOUR and not sent_today:
            log.info(f"الساعة {NOTIFY_HOUR} - جاري الارسال...")
            asyncio.run(send_notification())
            sent_today = True

        log.info(f"الوقت: {now.strftime('%H:%M')} - انتظر الساعة {NOTIFY_HOUR:02d}:00")
        time.sleep(60)


if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN غير موجود")
    if not CHANNEL_ID:
        raise ValueError("CHANNEL_ID غير موجود")
    log.info("البوت يبدا...")
    run_scheduler()
