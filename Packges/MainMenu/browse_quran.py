import logging

from telegram import Update, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CallbackContext

from Database import db
from Packges.Global_Functions import QURAN_BOOK_ID
from Startup.Keyboards import Keyboards
from Startup.Text import Text
from Startup.UserStates import UserStates


async def browse_quran_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data.split("_")
    book_id = int(data[2])
    browse_quran_text = Text.get_quran_description_by_book_id(book_id=book_id)
    browse_quran_keyboard = InlineKeyboardMarkup(Keyboards.get_quran_browse_ways_main_keyboard(book_id=book_id))
    await query.edit_message_text(text=browse_quran_text,
                                  reply_markup=browse_quran_keyboard)
    context.user_data["state"] = UserStates.Nothing
    await query.answer()


async def browse_quran_book_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    browse_quran_text = Text.Quran_Browse_Text
    browse_quran_keyboard = InlineKeyboardMarkup(Keyboards.get_quran_browse_books_main_keyboard())
    await query.edit_message_text(text=browse_quran_text,
                                  reply_markup=browse_quran_keyboard)
    context.user_data["state"] = UserStates.Nothing
    await query.answer()


async def browse_quran_by_chapter_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data.split("_")
    book_id = int(data[2])
    browse_quran_by_chapter_text = Text.Quran_Browse_By_Chapter_Text
    browse_quran_by_chapter_keyboard = InlineKeyboardMarkup(
        Keyboards.get_quran_browse_by_chapter_keyboard(book_id=book_id))
    await query.edit_message_text(text=browse_quran_by_chapter_text,
                                  reply_markup=browse_quran_by_chapter_keyboard)
    context.user_data["state"] = UserStates.Nothing
    await query.answer()


async def browse_quran_by_chapter_browsing(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data.split("_")
    book_id = int(data[2])
    chapter_no = int(data[3])
    start_range = int(data[4])
    end_range = int(data[5])
    total_pages = end_range - start_range + 1

    page = int(data[6])
    page_in_chapter = page - start_range + 1
    page_file_id = await db.get_quran_page_link(page_no=page, book_id=book_id)
    browse_quran_by_chapter_page_text = Text.get_quran_page_description_by_chapter(book_id=book_id,
                                                                                   chapter_no=chapter_no,
                                                                                   total_pages=total_pages,
                                                                                   current_page=page_in_chapter)
    browse_quran_by_chapter_keyboard = InlineKeyboardMarkup(Keyboards.get_quran_browse_by_chapter_browsing_keyboard(
        book_id=book_id,
        range_start=start_range,
        chapter_no=chapter_no,
        range_end=end_range,
        current_page=page
    ))
    await query.answer()
    if query.message.photo == ():
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=page_file_id,
            caption=browse_quran_by_chapter_page_text,
            reply_markup=browse_quran_by_chapter_keyboard
        )
    else:
        await query.edit_message_media(
            media=InputMediaPhoto(media=page_file_id, caption=browse_quran_by_chapter_page_text),
            reply_markup=browse_quran_by_chapter_keyboard
        )
    context.user_data["state"] = UserStates.Nothing


async def browse_quran_by_page_no_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data.split("_")
    book_id = int(data[2])
    browse_quran_by_page_no_text = Text.Quran_Browse_By_Page_Text
    browse_quran_by_page_no_keyboard = InlineKeyboardMarkup(Keyboards.get_cancel_keyboard())
    message_to_delete = await context.bot.send_message(chat_id=chat_id, text=browse_quran_by_page_no_text,
                                                       reply_markup=browse_quran_by_page_no_keyboard)
    context.user_data["state"] = UserStates.Browse_Quran_Waiting_For_Page_No
    context.user_data["Book_id"] = book_id
    context.user_data["bot_message_to_delete"] = message_to_delete.message_id
    await query.answer()


async def browse_quran_by_page_no_entered(update: Update, context: CallbackContext, chat_id, page_no: int,
                                          message_id_to_delete) -> None:
    start_range = 1
    end_range = 604
    await context.bot.delete_message(chat_id=chat_id, message_id=message_id_to_delete)
    bot_message_to_delete_id = context.user_data.get("bot_message_to_delete", 0)
    if bot_message_to_delete_id != 0:
        await context.bot.delete_message(chat_id=chat_id, message_id=bot_message_to_delete_id)
        context.user_data.pop("bot_message_to_delete")
    book_id = context.user_data.get("Book_id", QURAN_BOOK_ID.Hafs)
    page_file_id = await db.get_quran_page_link(page_no=page_no, book_id=book_id)
    browse_quran_by_page_no_page_text = Text.get_quran_page_description_by_page_no(page_no=page_no, book_id=book_id)
    browse_quran_by_page_no_keyboard = InlineKeyboardMarkup(Keyboards.get_quran_browse_by_page_no_browsing_keyboard(
        book_id=book_id,
        current_page=page_no
    ))
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=page_file_id,
        caption=browse_quran_by_page_no_page_text,
        reply_markup=browse_quran_by_page_no_keyboard
    )
    context.user_data["state"] = UserStates.Nothing


async def browse_quran_by_page_no_browsing(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data.split("_")
    book_id = int(data[2])
    page_no = int(data[3])
    page_file_id = await db.get_quran_page_link(page_no=page_no, book_id=book_id)
    browse_quran_by_page_no_page_text = Text.get_quran_page_description_by_page_no(page_no=page_no, book_id=book_id)
    browse_quran_by_page_no_keyboard = InlineKeyboardMarkup(Keyboards.get_quran_browse_by_page_no_browsing_keyboard(
        book_id=book_id,
        current_page=page_no
    ))
    await query.answer()
    if query.message.photo == ():
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=page_file_id,
            caption=browse_quran_by_page_no_page_text,
            reply_markup=browse_quran_by_page_no_keyboard
        )
    else:
        await query.edit_message_media(
            media=InputMediaPhoto(media=page_file_id, caption=browse_quran_by_page_no_page_text),
            reply_markup=browse_quran_by_page_no_keyboard
        )

    context.user_data["state"] = UserStates.Nothing


async def browse_quran_by_surah_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data.split("_")
    book_id = int(data[2])
    page_no = int(data[3])
    browse_quran_by_surah_text = Text.Quran_Browse_By_Surah_Text
    browse_quran_by_surah_keyboard = InlineKeyboardMarkup(
        Keyboards.get_quran_browse_by_surah_keyboard(book_id=book_id, page_no=page_no))
    await query.edit_message_text(text=browse_quran_by_surah_text,
                                  reply_markup=browse_quran_by_surah_keyboard)
    context.user_data["state"] = UserStates.Nothing
    await query.answer()


async def send_quran_chapter_file_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data.split("_")
    book_id = int(data[1])
    chapter_no = int(data[2])
    chapter_file_caption = Text.get_quran_chapter_file_description(chapter_no=chapter_no, book_id=book_id)
    chapter_file_id = await db.get_quran_chapter_link(chapter_no=chapter_no, book_id=book_id)
    await query.answer()
    try:
        message = await context.bot.send_document(chat_id=chat_id,
                                                  document=chapter_file_id,
                                                  caption=chapter_file_caption)
    except Exception as e:
        logging.error(e)
        message = await context.bot.send_message(chat_id=chat_id, text=Text.Unknown_Error_Text)


async def send_quran_book_file_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data.split("_")
    book_id = int(data[1])
    book_file_caption = Text.get_quran_book_file_description(book_id=book_id)
    book_file_id = await db.get_quran_book_link(book_id=book_id)
    await query.answer()
    try:
        message = await context.bot.send_document(chat_id=chat_id,
                                                  document=book_file_id,
                                                  caption=book_file_caption)
    except Exception as e:
        logging.error(e)
        message = await context.bot.send_message(chat_id=chat_id, text=Text.Unknown_Error_Text)


async def close_quran_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    await query.delete_message()
