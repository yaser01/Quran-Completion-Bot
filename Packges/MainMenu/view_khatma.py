import logging
from datetime import datetime

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode, ChatType
from telegram.ext import ContextTypes, CallbackContext

from Database import db
from Entites.TelegramUser import TelegramUser
from Packges.Brodcast import send_completed_message_to_users
from Packges.Global_Functions import get_user_object_date_from_update_object, clear_user_data
from Startup.Keyboards import Keyboards
from Startup.KhatmaPartStatus import KhatmaPartStatus
from Startup.KhatmaStatus import KhatmaStatus
from Startup.Text import Text
from Startup.UserStates import UserStates


async def show_khatma_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_user = get_user_object_date_from_update_object(update)
    is_blocked = await db.insert_new_user(telegram_user=telegram_user)
    chat_id = update.effective_chat.id
    is_group = not (update.effective_chat.type == ChatType.PRIVATE)
    if is_blocked:
        await context.bot.send_message(chat_id=chat_id, text=Text.Blocked_User)
        return
    if len(context.args) > 0:
        khatma_id = str(context.args[0])
        if khatma_id.startswith("khatma_id_"):
            khatma_id = khatma_id.split("_")[-1]
    else:
        khatma_id = update.message.text.split("_")[-1]
    if not khatma_id.isdigit():
        return
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    if khatma_status == KhatmaStatus.Not_Found:
        await context.bot.send_message(chat_id=chat_id, reply_to_message_id=update.message.id,
                                       text=Text.Khatma_Not_Found)
        return
    if khatma_status == KhatmaStatus.Opened:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                           start_date=khatma_data.time)
        khatma_info_message_keyboard = InlineKeyboardMarkup(Keyboards.get_khatma_parts_keyboard(khatma_id=khatma_id,
                                                                                                khatma_parts=khatma_parts_data,
                                                                                                is_group=is_group))
    elif khatma_status == KhatmaStatus.Done:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=0,
                                                           start_date=khatma_data.start_date,
                                                           end_date=khatma_data.end_date,
                                                           is_canceled=False,
                                                           is_finished=True)
        khatma_info_message_keyboard = None
    else:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=0,
                                                           start_date=khatma_data.start_date,
                                                           end_date=khatma_data.end_date,
                                                           is_canceled=True,
                                                           is_finished=False)
        khatma_info_message_keyboard = None
    khatma_info_message_object = await context.bot.send_message(chat_id=chat_id,
                                                                text=khatma_info_message_text,
                                                                reply_markup=khatma_info_message_keyboard,
                                                                parse_mode=ParseMode.MARKDOWN_V2)
    clear_user_data(context.user_data)
    context.user_data["state"] = UserStates.Nothing


async def khatma_refresh_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    state = context.user_data.get("state", None)
    telegram_user = TelegramUser(telegram_id=query.from_user.id, telegram_username=query.from_user.username,
                                 telegram_fullname=query.from_user.full_name)
    is_blocked = await db.insert_new_user(telegram_user=telegram_user)
    if is_blocked:
        await context.bot.send_message(chat_id=chat_id, text=Text.Blocked_User)
        return
    is_group = not (update.effective_chat.type == ChatType.PRIVATE)
    data = query.data.split("_")
    khatma_id = data[2]
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(text=Text.Khatma_Not_Found)
        return
    if khatma_status == KhatmaStatus.Opened:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                           start_date=khatma_data.time)
        if len(data) > 3:
            page_id = int(data[3])
            page_size = int(data[4])
            sort = ("asc" if data[5] == "1" else "desc")
            khatma_info_message_keyboard = InlineKeyboardMarkup(Keyboards.get_khatma_parts_keyboard(khatma_id=khatma_id,
                                                                                                    khatma_parts=khatma_parts_data,
                                                                                                    have_return_button=True,
                                                                                                    return_button_page_id=page_id,
                                                                                                    return_button_page_size=page_size,
                                                                                                    return_button_is_asc=
                                                                                                    (
                                                                                                        True if sort == "asc" else False),
                                                                                                    is_group=is_group))
        else:
            khatma_info_message_keyboard = InlineKeyboardMarkup(Keyboards.get_khatma_parts_keyboard(khatma_id=khatma_id,
                                                                                                    khatma_parts=khatma_parts_data,
                                                                                                    is_group=is_group))
    elif khatma_status == KhatmaStatus.Done:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=0,
                                                           start_date=khatma_data.start_date,
                                                           end_date=khatma_data.end_date,
                                                           is_canceled=False,
                                                           is_finished=True)
        if len(data) > 3:
            page_id = int(data[3])
            page_size = int(data[4])
            sort = ("asc" if data[5] == "1" else "desc")
            khatma_info_message_keyboard = InlineKeyboardMarkup(Keyboards.get_khatma_parts_keyboard(khatma_id=khatma_id,
                                                                                                    khatma_parts=[],
                                                                                                    have_return_button=True,
                                                                                                    have_refresh_button=False,
                                                                                                    return_button_page_id=page_id,
                                                                                                    return_button_page_size=page_size,
                                                                                                    return_button_is_asc=
                                                                                                    (
                                                                                                        True if sort == "asc" else False),
                                                                                                    is_group=is_group))
        else:
            khatma_info_message_keyboard = None
    else:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=0,
                                                           start_date=khatma_data.start_date,
                                                           end_date=khatma_data.end_date,
                                                           is_canceled=True,
                                                           is_finished=False)
        if len(data) > 3:
            page_id = int(data[3])
            page_size = int(data[4])
            sort = ("asc" if data[5] == "1" else "desc")
            khatma_info_message_keyboard = InlineKeyboardMarkup(Keyboards.get_khatma_parts_keyboard(khatma_id=khatma_id,
                                                                                                    khatma_parts=[],
                                                                                                    have_return_button=True,
                                                                                                    have_refresh_button=False,
                                                                                                    return_button_page_id=page_id,
                                                                                                    return_button_page_size=page_size,
                                                                                                    return_button_is_asc=
                                                                                                    (
                                                                                                        True if sort == "asc" else False),
                                                                                                    is_group=is_group))
        else:
            khatma_info_message_keyboard = None
    await query.answer(text=Text.Khatma_Parts_Refresh_Done, show_alert=False)
    try:
        await query.edit_message_text(text=khatma_info_message_text, reply_markup=khatma_info_message_keyboard,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)


async def khatma_part_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    state = context.user_data.get("state", None)
    telegram_user = TelegramUser(telegram_id=query.from_user.id, telegram_username=query.from_user.username,
                                 telegram_fullname=query.from_user.full_name)
    is_blocked = await db.insert_new_user(telegram_user=telegram_user)
    if is_blocked:
        await context.bot.send_message(chat_id=chat_id, text=Text.Blocked_User)
        return
    is_group = not (update.effective_chat.type == ChatType.PRIVATE)
    data = query.data.split("_")
    khatma_id = data[1]
    part_no = data[2]
    khatma_part_data = await db.get_khatma_part_data(khatma_id=khatma_id, part_no=part_no)
    old_keyboard = list(query.message.reply_markup.inline_keyboard)
    last_button_text = old_keyboard[-1][0].text
    old_refresh_button = None
    old_return_button = None
    if last_button_text.find("تحديث") != -1:
        old_refresh_button = old_keyboard[-1][0]
    elif last_button_text.find("عودة") != -1:
        old_return_button = old_keyboard[-1][0]
    last_2nd_button_text = old_keyboard[-2][0].text
    if last_2nd_button_text.find("تحديث") != -1:
        old_refresh_button = old_keyboard[-2][0]
    elif last_2nd_button_text.find("عودة") != -1:
        old_return_button = old_keyboard[-2][0]
    finished_parts_dict = None
    if khatma_part_data.part_state == KhatmaPartStatus.Occupied:
        time_since_start_in_second = (datetime.utcnow() - khatma_part_data.part_start).total_seconds()
        booked_part_user = (await db.get_user_data(telegram_id=khatma_part_data.user_id))
        if int(booked_part_user.telegram_id) == int(chat_id):
            if time_since_start_in_second < 1200:
                await query.answer(text=Text.Mark_Part_As_Done_Time_Limit, show_alert=True)
                return
            part_data = await db.mark_khatma_part_as_done(khatma_id=khatma_id, part_no=part_no)
            finished_parts_dict = await db.check_if_khatma_done(khatma_id=khatma_id)
            if part_data is None:
                await query.answer(text=Text.Mark_Khatma_Part_As_Done_Text, show_alert=True)

            else:
                await query.answer(text=Text.Unknown_Error_Text, show_alert=False)
        else:
            booked_part_user_fullname = booked_part_user.telegram_fullname
            await query.answer(text=Text.create_khatma_part_booked_data(name=booked_part_user_fullname,
                                                                        time_since_start_in_second=time_since_start_in_second),
                               show_alert=True)
    elif khatma_part_data.part_state == KhatmaPartStatus.Done:
        await query.answer(text=Text.Khatma_Part_Done, show_alert=True)
    else:
        number_of_booked_part_by_this_user = await db.get_number_of_booked_parts_by_user(user_id=telegram_user.id)
        if number_of_booked_part_by_this_user >= 4:
            await query.answer(text=Text.create_reached_limit_of_booked_parts(), show_alert=True)
            return
        old_booked_data = await db.book_khatma_part(khatma_id=khatma_id, part_no=part_no, user_id=telegram_user.id,
                                                    duration_in_days=
                                                    khatma_part_data.Khatma.number_of_days_to_finish_a_part)
        if old_booked_data is None:
            await query.answer(text=Text.Khatma_Part_Occupied_Done, show_alert=False)
        else:
            booked_part_user_name = (await db.get_user_data(telegram_id=old_booked_data.user_id)).telegram_fullname
            time_since_start_in_second = (datetime.utcnow() - khatma_part_data.part_start).total_seconds()
            await query.answer(text=Text.create_khatma_part_booked_data(name=booked_part_user_name,
                                                                        time_since_start_in_second=time_since_start_in_second),
                               show_alert=True)
    try:
        await query.answer()
    except Exception as e:
        logging.error(e)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    if khatma_status == KhatmaStatus.Opened:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                           start_date=khatma_data.time)
        khatma_info_message_keyboard = Keyboards.get_khatma_parts_keyboard(khatma_id=khatma_id,
                                                                           khatma_parts=khatma_parts_data,
                                                                           have_refresh_button=False)
        if old_refresh_button is not None:
            khatma_info_message_keyboard.append([old_refresh_button])
        if old_return_button is not None:
            khatma_info_message_keyboard.append([old_return_button])
        if is_group:
            khatma_info_message_keyboard.append(
                [InlineKeyboardButton("تصفح القرآن الكريم 📖", url="https://telegram.me/QuranCompletionBot?start")])
    elif khatma_status == KhatmaStatus.Done:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=0,
                                                           start_date=khatma_data.start_date,
                                                           end_date=khatma_data.end_date,
                                                           is_canceled=False,
                                                           is_finished=True)
        khatma_info_message_keyboard = Keyboards.get_khatma_parts_keyboard(khatma_id=khatma_id,
                                                                           khatma_parts=[],
                                                                           have_refresh_button=False)
        if old_return_button is not None:
            khatma_info_message_keyboard.append([old_return_button])
        if is_group:
            khatma_info_message_keyboard.append(
                [InlineKeyboardButton("تصفح القرآن الكريم 📖", url="https://telegram.me/QuranCompletionBot?start")])
    else:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=0,
                                                           start_date=khatma_data.start_date,
                                                           end_date=khatma_data.end_date,
                                                           is_canceled=True,
                                                           is_finished=False)
        khatma_info_message_keyboard = Keyboards.get_khatma_parts_keyboard(khatma_id=khatma_id,
                                                                           khatma_parts=[],
                                                                           have_refresh_button=False)
        if old_return_button is not None:
            khatma_info_message_keyboard.append([old_return_button])
        if is_group:
            khatma_info_message_keyboard.append(
                [InlineKeyboardButton("تصفح القرآن الكريم 📖", url="https://telegram.me/QuranCompletionBot?start")])
    khatma_info_message_keyboard = InlineKeyboardMarkup(khatma_info_message_keyboard)
    try:
        await query.edit_message_text(text=khatma_info_message_text,
                                      reply_markup=khatma_info_message_keyboard,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)
    if finished_parts_dict is not None:
        await send_completed_message_to_users(finished_parts_dict=finished_parts_dict,
                                              khatma_opener_user_id=khatma_data.user_id, context=context)
