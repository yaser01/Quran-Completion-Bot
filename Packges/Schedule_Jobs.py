import logging
import os.path
from datetime import datetime

from dotenv import load_dotenv
from telegram.ext import ContextTypes

from Database import db
from Startup.Global_Files import Quran_Hafs_Pages_Images_Folder, Quran_Hafs_Tajwid_Pages_Images_Folder, \
    Quran_Hafs_Chapters_Folder, Quran_Hafs_Tajwid_Chapters_Folder
from Packges.Global_Functions import QURAN_BOOK_ID, get_current_page_no_daily_page_quran, \
    set_next_page_no_daily_page_quran
from Startup.Keyboards import part_no_dict
from Startup.Text import Text

load_dotenv()
QURAN_FILES_CHANNEL_ID = os.getenv('QURAN_FILES_CHANNEL_ID')
QURAN_DAILY_PAGE_CHANNEL_ID = os.getenv('QURAN_DAILY_PAGE_CHANNEL_ID')


async def check_booked_parts_deadline(context: ContextTypes.DEFAULT_TYPE):
    expired_parts = await db.cancel_reservation_of_all_expired_booked_parts()
    for expired_part in expired_parts:
        expired_part_message_text = Text.create_expired_khatma_part_text(khatma_id=expired_part.khatma_id,
                                                                         part_no=expired_part.part_no,
                                                                         khatma_intention=expired_part.khatma_intention,
                                                                         khatma_part_duration=expired_part.khatma_part_duration,
                                                                         khatma_opener_name=expired_part.khatma_opener_name
                                                                         )
        try:
            await context.bot.send_message(chat_id=expired_part.telegram_user_id,
                                           text=expired_part_message_text,
                                           parse_mode="MarkDownV2")
        except Exception as e:
            logging.error(e)


async def check_booked_parts_next_notification(context: ContextTypes.DEFAULT_TYPE):
    notification_parts = await db.get_send_notification_of_booked_parts()
    for notification_part in notification_parts:
        remain_time = (notification_part.deadline - datetime.utcnow()).total_seconds()
        notification_part_message_text = Text.create_notification_khatma_part_text(
            khatma_id=notification_part.khatma_id,
            part_no=notification_part.part_no,
            khatma_intention=notification_part.khatma_intention,
            khatma_opener_name=notification_part.khatma_opener_name,
            remain_time=remain_time
        )
        try:
            await context.bot.send_message(chat_id=notification_part.telegram_user_id,
                                           text=notification_part_message_text,
                                           parse_mode="MarkDownV2")
        except Exception as e:
            logging.error(e)


async def upload_quran_files(context: ContextTypes.DEFAULT_TYPE):
    for i in range(1, 605):
        db_page_no = db.calc_file_id_with_page_no(page_no=i, book_id=QURAN_BOOK_ID.Hafs.value)
        if await db.get_quran_page_link(page_no=i, book_id=QURAN_BOOK_ID.Hafs.value) is None:
            page = os.path.join(Quran_Hafs_Pages_Images_Folder, f"{i}.jpg")
            message = await context.bot.send_photo(chat_id=QURAN_FILES_CHANNEL_ID, photo=open(page, "rb"))
            await db.update_quran_file_link(file_id=db_page_no, telegram_file_id=message.photo[-1].file_id)
            logging.warning(
                f"Update Quran Page ({QURAN_BOOK_ID.Hafs.name},{i}) Telegram File Id: {message.photo[-1].file_id}")
        else:
            logging.warning(f"Quran Page ({QURAN_BOOK_ID.Hafs.name},{i}) is already on DB.")

    for i in range(1, 605):
        db_page_no = db.calc_file_id_with_page_no(page_no=i, book_id=QURAN_BOOK_ID.Hafs_with_tajwid.value)
        if await db.get_quran_page_link(page_no=i, book_id=QURAN_BOOK_ID.Hafs_with_tajwid.value) is None:
            page = os.path.join(Quran_Hafs_Tajwid_Pages_Images_Folder, f"{i}.jpg")
            message = await context.bot.send_photo(chat_id=QURAN_FILES_CHANNEL_ID, photo=open(page, "rb"))

            await db.update_quran_file_link(file_id=db_page_no, telegram_file_id=message.photo[-1].file_id)
            logging.warning(
                f"Update Quran Page ({QURAN_BOOK_ID.Hafs_with_tajwid.name},{i}) Telegram File Id: {message.photo[-1].file_id}")
        else:
            logging.warning(f"Quran Page ({QURAN_BOOK_ID.Hafs_with_tajwid.name},{i}) is already on DB.")

    for i in range(1, 31):
        db_chapter_no = db.calc_file_id_with_chapter_no(chapter_no=i, book_id=QURAN_BOOK_ID.Hafs.value)
        if await db.get_quran_chapter_link(chapter_no=i, book_id=QURAN_BOOK_ID.Hafs.value) is None:
            chapter = os.path.join(Quran_Hafs_Chapters_Folder, f"{i}.pdf")
            chapter_file_caption = Text.get_quran_chapter_file_description(chapter_no=i,
                                                                           book_id=QURAN_BOOK_ID.Hafs.value)
            file_name = part_no_dict[i]
            file_name += " برواية حفص عن عاصم"
            file_name += ".pdf"
            message = await context.bot.send_document(chat_id=QURAN_FILES_CHANNEL_ID, document=open(chapter, "rb"),
                                                      filename=file_name, caption=chapter_file_caption)
            await db.update_quran_file_link(file_id=db_chapter_no, telegram_file_id=message.document.file_id)
            logging.warning(
                f"Update Quran Chapter ({QURAN_BOOK_ID.Hafs.name},{i}) Telegram File Id: {message.document.file_id}")
        else:
            logging.warning(f"Quran Chapter ({QURAN_BOOK_ID.Hafs.name},{i}) is already on DB.")

    for i in range(1, 31):
        db_chapter_no = db.calc_file_id_with_chapter_no(chapter_no=i, book_id=QURAN_BOOK_ID.Hafs_with_tajwid.value)
        if await db.get_quran_chapter_link(chapter_no=i, book_id=QURAN_BOOK_ID.Hafs_with_tajwid.value) is None:
            chapter = os.path.join(Quran_Hafs_Tajwid_Chapters_Folder, f"{i}.pdf")
            chapter_file_caption = Text.get_quran_chapter_file_description(chapter_no=i,
                                                                           book_id=QURAN_BOOK_ID.Hafs_with_tajwid.value)
            file_name = part_no_dict[i]
            file_name += " من مصحف التجويد برواية حفص عن عاصم"
            file_name += ".pdf"
            message = await context.bot.send_document(chat_id=QURAN_FILES_CHANNEL_ID, document=open(chapter, "rb"),
                                                      filename=file_name, caption=chapter_file_caption)
            await db.update_quran_file_link(file_id=db_chapter_no, telegram_file_id=message.document.file_id)
            logging.warning(
                f"Update Quran Chapter ({QURAN_BOOK_ID.Hafs_with_tajwid.name},{i}) Telegram File Id: {message.document.file_id}")
        else:
            logging.warning(f"Quran Chapter ({QURAN_BOOK_ID.Hafs_with_tajwid.name},{i}) is already on DB.")


async def upload_daily_quran_page_to_channel(context: ContextTypes.DEFAULT_TYPE):
    book_id = QURAN_BOOK_ID.Hafs_with_tajwid.value
    current_page_no = get_current_page_no_daily_page_quran()
    browse_quran_by_page_no_page_text = Text.get_quran_page_description_by_page_no(page_no=current_page_no,
                                                                                   book_id=book_id)
    page_file_id = await db.get_quran_page_link(page_no=current_page_no, book_id=book_id)
    await context.bot.send_photo(
        chat_id=QURAN_DAILY_PAGE_CHANNEL_ID,
        photo=page_file_id,
        caption=browse_quran_by_page_no_page_text)
    set_next_page_no_daily_page_quran()


async def backup_database_daily(context: ContextTypes.DEFAULT_TYPE):
    db.add_backup_request()
