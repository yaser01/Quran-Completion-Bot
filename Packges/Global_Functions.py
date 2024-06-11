import json
import logging
import os
from datetime import timedelta, datetime
from enum import Enum

import pytz
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.helpers import escape_markdown

from Database.models import Khatma_Parts
from Entites.TelegramUser import TelegramUser
from Startup.Global_Files import Daily_Page_Quran_File
from Startup.UserOptionsKeys import UserOptionsKeys

load_dotenv()
ADMIN_TELEGRAM_ID = os.getenv('ADMIN_TELEGRAM_ID')


class QURAN_BOOK_ID(Enum):
    Hafs = 1
    Hafs_with_tajwid = 2


def calc_next_notification_time(deadline_time):
    time_now = datetime.utcnow()
    remain_time = deadline_time - time_now
    next_notification_time = None
    if remain_time <= timedelta(hours=1):
        next_notification_time = time_now + timedelta(minutes=30)
    elif remain_time <= timedelta(hours=2):
        next_notification_time = time_now + timedelta(hours=1)
    elif remain_time <= timedelta(hours=3):
        next_notification_time = time_now + timedelta(hours=1)
    elif remain_time <= timedelta(hours=5):
        next_notification_time = time_now + timedelta(hours=2)
    elif remain_time <= timedelta(hours=8):
        next_notification_time = time_now + timedelta(hours=3)
    elif remain_time <= timedelta(hours=12):
        next_notification_time = time_now + timedelta(hours=4)
    elif remain_time <= timedelta(hours=24):
        next_notification_time = time_now + timedelta(hours=12)
    elif remain_time <= timedelta(hours=36):
        next_notification_time = time_now + timedelta(hours=12)
    elif remain_time <= timedelta(hours=48):
        next_notification_time = time_now + timedelta(hours=12)
    else:
        next_notification_time = time_now + timedelta(hours=24)
    return next_notification_time


def build_async_db_uri(uri):
    if "+asyncpg" not in uri:
        return '+asyncpg:'.join(uri.split(":", 1))
    return uri


def format_timespan_in_arabic(total_time, max_units):
    formatted_time = ""
    total_time = int(total_time)
    number_of_days = total_time // 86400
    total_time -= (number_of_days * 86400)
    number_of_hours = total_time // 3600
    total_time -= (number_of_hours * 3600)
    number_of_minutes = total_time // 60
    total_time -= (number_of_minutes * 60)
    number_of_seconds = total_time
    total_numbers_of_units = 0
    if number_of_days != 0:
        if total_numbers_of_units >= max_units:
            return formatted_time[:-1]  # delete last space
        if 3 <= number_of_days <= 10:
            formatted_time += str(number_of_days)
            formatted_time += " "
            formatted_time += "أيام"
            formatted_time += " "
        else:
            formatted_time += str(number_of_days)
            formatted_time += " "
            formatted_time += "يوم"
            formatted_time += " "
        total_numbers_of_units += 1
    if number_of_hours != 0:
        if total_numbers_of_units >= max_units:
            return formatted_time[:-1]  # delete last space
        if len(formatted_time) > 0:
            formatted_time += "و "
        if 3 <= number_of_hours <= 10:
            formatted_time += str(number_of_hours)
            formatted_time += " "
            formatted_time += "ساعات"
            formatted_time += " "
        else:
            formatted_time += str(number_of_hours)
            formatted_time += " "
            formatted_time += "ساعة"
            formatted_time += " "
        total_numbers_of_units += 1
    if number_of_minutes != 0:
        if total_numbers_of_units >= max_units:
            return formatted_time[:-1]  # delete last space
        if len(formatted_time) > 0:
            formatted_time += "و "
        if 3 <= number_of_minutes <= 10:
            formatted_time += str(number_of_minutes)
            formatted_time += " "
            formatted_time += "دقائق"
            formatted_time += " "
        else:
            formatted_time += str(number_of_minutes)
            formatted_time += " "
            formatted_time += "دقيقة"
            formatted_time += " "
        total_numbers_of_units += 1
    if number_of_seconds != 0:
        if total_numbers_of_units >= max_units:
            return formatted_time[:-1]  # delete last space
        if len(formatted_time) > 0:
            formatted_time += "و "
        if 3 <= number_of_seconds <= 10:
            formatted_time += str(number_of_seconds)
            formatted_time += " "
            formatted_time += "ثواني"
            formatted_time += " "
        else:
            formatted_time += str(number_of_seconds)
            formatted_time += " "
            formatted_time += "ثانية"
            formatted_time += " "
        total_numbers_of_units += 1
    return formatted_time[:-1]  # delete last space


def create_keyboard(keyboard_list, one_time_keyboard=False):
    return ReplyKeyboardMarkup(keyboard_list, resize_keyboard=True, one_time_keyboard=one_time_keyboard)


def get_text_copyable(text):
    return "`" + str(text) + "`"


def get_elided_text_version(text, limit=20):
    new_text = text[:limit]
    if len(new_text) < len(text):
        new_text += "..."
    return new_text


def get_user_object_date_from_update_object(update: Update) -> TelegramUser:
    user = TelegramUser(telegram_id=update.message.from_user.id, telegram_username=update.message.from_user.username,
                        telegram_fullname=update.message.from_user.full_name)
    return user


async def send_missing_data_message(telegram_user: TelegramUser, context):
    message_text = "الرجاء الضغط على /start"
    message_text += "\n"
    message_text += "Please click on /start"
    await context.bot.send_message(chat_id=telegram_user.id, text=message_text, reply_markup=ReplyKeyboardRemove())


def get_user_identity_string(user):
    user_identity_string = "User(ID: " + str(user.id) + ", " + "Username: " + str(
        user.username) + ", " + "Fullname: " + str(user.full_name) + "): "
    return user_identity_string


def get_user_identity_string_from_telegram_user_object(user: TelegramUser):
    user_identity_string = "User(ID: " + str(user.id) + ", " + "Username: " + str(
        user.username) + ", " + "Fullname: " + str(user.fullname) + "): "
    return user_identity_string


def compare_between_part_asc(item1: Khatma_Parts, item2: Khatma_Parts):
    if item1.Khatma.id != item2.Khatma.id:
        return item1.Khatma.id - item2.Khatma.id
    else:
        return int((item1.part_start - item2.part_start).total_seconds())


def compare_between_part_desc(item1: Khatma_Parts, item2: Khatma_Parts):
    if item1.Khatma.id != item2.Khatma.id:
        return item2.Khatma.id - item1.Khatma.id
    else:
        return int((item2.part_start - item1.part_start).total_seconds())


async def delete_old_khatma_opening_request(chat_id, context):
    if "new_khatma_message_id" in context.user_data.keys():
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=context.user_data["new_khatma_message_id"])
        except Exception as e:
            logging.error(e)
    if "khatma_info_request_message_id" in context.user_data.keys():
        try:
            await context.bot.delete_message(chat_id=chat_id,
                                             message_id=context.user_data["khatma_info_request_message_id"])
        except Exception as e:
            logging.error(e)


def get_local_date_from_utc_time(utc_time):
    from_zone = pytz.utc
    to_zone = pytz.timezone("Asia/Damascus")
    utc_time_with_zone_aware = utc_time.replace(tzinfo=from_zone)
    local_date = utc_time_with_zone_aware.astimezone(to_zone)
    return local_date.strftime("%Y/%m/%d")


def escape_markdown_v2(text):
    return escape_markdown(text, version=2)


def clear_user_data(user_data_dict: dict):
    for key in list(user_data_dict.keys()):
        if key not in UserOptionsKeys.__getattributes__():
            user_data_dict.pop(key)


def get_current_page_no_daily_page_quran():
    with open(Daily_Page_Quran_File, "r+", encoding="UTF-8") as f:
        data = json.load(f)
    page_no = int(data["page_no"])
    return page_no


def set_next_page_no_daily_page_quran():
    with open(Daily_Page_Quran_File, "r+", encoding="UTF-8") as f:
        data = json.load(f)
    page_no = data["page_no"]
    page_no = int(page_no)
    page_no += 1
    if page_no > 604:
        page_no = 1
    data["page_no"] = page_no
    with open(Daily_Page_Quran_File, "w+", encoding="UTF-8") as f:
        json.dump(data, f)
