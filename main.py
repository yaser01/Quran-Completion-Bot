import datetime
import json
import logging
import os

import pytz
import telegram
from dotenv import load_dotenv

load_dotenv()  # must run before project imports that read env vars at module level

from telegram import Update
from telegram.constants import ChatType
from telegram.ext import Application, ContextTypes
from telegram.request import HTTPXRequest

from db import db
from bot import state_dispatcher
from config.Global_Files import Daily_Page_Quran_File, Logs_Folder
from bot.Global_Functions import get_user_object_date_from_update_object
from bot.MainMenu.view_khatma import show_khatma_info
from bot.Schedule_Jobs import check_booked_parts_deadline, check_booked_parts_next_notification, \
    upload_daily_quran_page_to_channel, upload_quran_files, backup_database_daily, check_expired_khatmas
from bot.router import register_handlers
from config.Text import Text

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_LISTEN_HOST = os.getenv('WEBHOOK_LISTEN_HOST')
WEBHOOK_LISTEN_PORT = os.getenv('WEBHOOK_LISTEN_PORT')
SECRET_TOKEN = os.getenv('SECRET_TOKEN')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
CERT = os.getenv('CERT')



async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text.startswith("show_khatma_info_"):
        await show_khatma_info(update=update, context=context)
        return
    if update.message.chat.type != ChatType.PRIVATE:
        return
    telegram_user = get_user_object_date_from_update_object(update)
    chat_id = update.message.from_user.id
    is_blocked = await db.insert_new_user(telegram_user=telegram_user)
    if is_blocked:
        await context.bot.send_message(chat_id=chat_id, text=Text.Blocked_User)
        return
    state = context.user_data.get("state")
    if state is None:
        return
    await state_dispatcher.dispatch(state, update, context)


async def _post_init(application: Application) -> None:
    await db.warm_file_id_cache()


def main():
    application = Application.builder().token(BOT_TOKEN).get_updates_request(HTTPXRequest(http_version="1.1")) \
        .request(HTTPXRequest(http_version="1.1", read_timeout=1000, write_timeout=1000, connect_timeout=1000,
                              connection_pool_size=10,
                              pool_timeout=1000)).post_init(_post_init).build()
    register_handlers(application, message)
    job_queue = application.job_queue
    job_check_booked_parts_deadline = job_queue.run_repeating(check_booked_parts_deadline, interval=60, first=10)
    job_check_booked_parts_next_notification = job_queue.run_repeating(check_booked_parts_next_notification,
                                                                       interval=60, first=10)
    job_upload_daily_quran_page_to_channel = job_queue.run_daily(upload_daily_quran_page_to_channel,
                                                                 datetime.time(hour=8, minute=0,
                                                                               tzinfo=pytz.timezone('Asia/Baghdad')))
    job_upload_daily_backup_to_drive = job_queue.run_daily(backup_database_daily,
                                                           datetime.time(hour=9, minute=0,
                                                                         tzinfo=pytz.timezone('Asia/Baghdad')))
    job_upload_quran_files = job_queue.run_once(upload_quran_files, when=5)
    job_check_expired_khatmas = job_queue.run_repeating(check_expired_khatmas, interval=60 * 60 * 24 * 7, first=3)
    application.run_webhook(
        listen=WEBHOOK_LISTEN_HOST,
        port=WEBHOOK_LISTEN_PORT,
        secret_token=SECRET_TOKEN,
        key=PRIVATE_KEY,
        cert=CERT,
        webhook_url=WEBHOOK_URL
    )


def setup_startup_files():
    os.makedirs(Logs_Folder, exist_ok=True)
    os.makedirs(os.path.dirname(Daily_Page_Quran_File), exist_ok=True)
    if not os.path.isfile(Daily_Page_Quran_File):
        data = {}
        with open(Daily_Page_Quran_File, "a+", encoding="UTF-8") as f:
            data["page_no"] = 1
            json.dump(data, f)


if __name__ == "__main__":
    import asyncio
    logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    setup_startup_files()
    asyncio.run(db.create_schema_only())
    main()
