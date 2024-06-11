import logging
from datetime import datetime

from telegram import Update, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from Database import db
from Entites.TelegramUser import TelegramUser
from Packges.Global_Functions import send_missing_data_message, delete_old_khatma_opening_request, clear_user_data
from Startup.CallBackData import CallBackData
from Startup.Keyboards import Keyboards
from Startup.Text import Text
from Startup.UserStates import UserStates


async def new_khatma_confirmation_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    state = context.user_data.get("state", None)
    telegram_user = TelegramUser(telegram_id=query.from_user.id, telegram_username=query.from_user.username,
                                 telegram_fullname=query.from_user.full_name)
    if not {"new_khatma_message_id", "khatma_info_request_message_id",
            "khatma_info_opener_name", "khatma_info_intention", "khatma_info_duration"} \
            .issubset(context.user_data.keys()):
        logging.error("Not enough data")
        await query.answer()
        await send_missing_data_message(telegram_user=telegram_user, context=context)
        return
    opener_name = context.user_data["khatma_info_opener_name"]
    intention = context.user_data["khatma_info_intention"]
    duration = context.user_data["khatma_info_duration"]
    confirmation_answer = query.data
    await query.answer()
    await query.delete_message()
    if state != UserStates.New_Khatma_Waiting_For_Khatma_Confirmation:
        logging.error("Error in workflow")
        try:
            await query.delete_message()
        except Exception as e:
            logging.error(e)
        await send_missing_data_message(telegram_user=telegram_user, context=context)
        return
    if confirmation_answer == CallBackData.New_Khatma_Confirm_No:
        khatma_cancel_message_text = Text.Operation_Canceled
        khatma_cancel_message_object = await context.bot.send_message(chat_id=chat_id,
                                                                      text=khatma_cancel_message_text)
        try:
            await query.delete_message()
            await context.bot.delete_message(chat_id=chat_id,
                                             message_id=context.user_data["khatma_info_request_message_id"])
            await context.bot.delete_message(chat_id=chat_id,
                                             message_id=context.user_data["new_khatma_message_id"])
        except Exception as e:
            logging.error(e)
        return
    khatma_id = await db.create_new_khatma(telegram_id=telegram_user.id, description=intention,
                                           name_of_opener=opener_name,
                                           time=datetime.utcnow(), is_private=True,
                                           max_number_of_parts=2, number_of_days_to_finish_a_part=duration)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    khatma_started_message_text = Text.New_Khatma_Started
    khatma_started_message_object = await context.bot.send_message(chat_id=chat_id,
                                                                   text=khatma_started_message_text)
    khatma_info_message_text = Text.create_khatma_info_on_creation(khatma_id=khatma_id, name=opener_name,
                                                                   intention=intention,
                                                                   duration_in_days=duration,
                                                                   start_date=khatma_data.time)

    khatma_info_message_keyboard = InlineKeyboardMarkup(Keyboards.get_khatma_parts_keyboard(khatma_id=khatma_id,
                                                                                            khatma_parts=khatma_parts_data))
    khatma_info_message_object = await context.bot.send_message(chat_id=chat_id,
                                                                text=khatma_info_message_text,
                                                                reply_markup=khatma_info_message_keyboard,
                                                                parse_mode=ParseMode.MARKDOWN_V2)
    clear_user_data(context.user_data)
    context.user_data["state"] = UserStates.Nothing


async def new_khatma_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    new_khatma_info_message_text = Text.create_new_khatma_info_nothing()
    new_khatma_info_message_keyboard = InlineKeyboardMarkup(Keyboards.get_cancel_keyboard())
    await delete_old_khatma_opening_request(chat_id, context)
    number_of_currently_opened_khatmas_by_user = await db.count_number_of_currently_opened_khatmas_by_user(
        user_id=chat_id)
    if number_of_currently_opened_khatmas_by_user >= 5:
        await query.answer(text=Text.create_reached_limit_of_opened_khatmas(), show_alert=True)
        return
    new_khatma_message_object = await context.bot.send_message(chat_id=chat_id, text=new_khatma_info_message_text,
                                                               reply_markup=new_khatma_info_message_keyboard,
                                                               parse_mode=ParseMode.MARKDOWN_V2)
    khatma_info_request_message_text = Text.Please_Enter_Opener_Name
    khatma_info_request_message_object = await context.bot.send_message(chat_id=chat_id,
                                                                        text=khatma_info_request_message_text,
                                                                        )
    context.user_data["state"] = UserStates.New_Khatma_Waiting_For_Opener_Name
    context.user_data["new_khatma_message_id"] = new_khatma_message_object.id
    context.user_data["khatma_info_request_message_id"] = khatma_info_request_message_object.id
    await query.answer()


async def cancel_mission(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    cancel_message_text = Text.Operation_Canceled
    cancel_message_object = await context.bot.send_message(chat_id=chat_id,
                                                           text=cancel_message_text)
    try:
        await query.delete_message()
        await context.bot.delete_message(chat_id=chat_id,
                                         message_id=context.user_data["khatma_info_request_message_id"])
        await context.bot.delete_message(chat_id=chat_id,
                                         message_id=context.user_data["new_khatma_message_id"])
    except Exception as e:
        logging.error(e)
    return


async def new_khatma_type_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    state = context.user_data.get("state", None)
    telegram_user = TelegramUser(telegram_id=query.from_user.id, telegram_username=query.from_user.username,
                                 telegram_fullname=query.from_user.full_name)
    if not {"new_khatma_message_id", "khatma_info_request_message_id",
            "khatma_info_opener_name", "khatma_info_intention", "khatma_info_duration"}.issubset(
        context.user_data.keys()):
        logging.error("Not enough data")
        await send_missing_data_message(telegram_user=telegram_user, context=context)
        return
    opener_name = context.user_data["khatma_info_opener_name"]
    intention = context.user_data["khatma_info_intention"]
    duration = context.user_data["khatma_info_duration"]
    khatma_type = query.data
    if khatma_type == CallBackData.New_Khatma_Type_Private:
        khatma_type = "Private"
    else:
        khatma_type = "Public"
    await query.answer()
    if state is None:
        return
    if state != UserStates.New_Khatma_Waiting_For_Khatma_Type:
        logging.error("Error in workflow")
        try:
            await query.delete_message()
        except Exception as e:
            logging.error(e)
        await send_missing_data_message(telegram_user=telegram_user, context=context)
        return
    try:
        await query.delete_message()
    except Exception as e:
        logging.error(e)
