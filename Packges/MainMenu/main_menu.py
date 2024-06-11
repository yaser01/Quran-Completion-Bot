from telegram import Update, InlineKeyboardMarkup
from telegram.constants import ChatType
from telegram.ext import ContextTypes

from Database import db
from Packges.Global_Functions import get_user_object_date_from_update_object, delete_old_khatma_opening_request, \
    clear_user_data
from Startup.Keyboards import Keyboards
from Startup.Text import Text
from Startup.UserStates import UserStates


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type != ChatType.PRIVATE:
        return
    telegram_user = get_user_object_date_from_update_object(update)
    chat_id = update.message.from_user.id
    is_blocked = await db.insert_new_user(telegram_user=telegram_user)
    clear_user_data(context.user_data)
    context.user_data["state"] = UserStates.Showing_Main_Menu
    if is_blocked:
        await context.bot.send_message(chat_id=chat_id, text=Text.Blocked_User)
        return
    keyboard = InlineKeyboardMarkup(Keyboards.get_main_inline_keyboard())
    await update.message.reply_text(text=Text.Welcome, reply_markup=keyboard)
    await delete_old_khatma_opening_request(chat_id, context)


async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    clear_user_data(context.user_data)
    await delete_old_khatma_opening_request(chat_id, context)
    main_menu_message_text = Text.Welcome
    main_menu_message_keyboard = InlineKeyboardMarkup(Keyboards.get_main_inline_keyboard())
    await query.answer()
    if query.message.photo == ():
        await query.edit_message_text(text=main_menu_message_text,
                                      reply_markup=main_menu_message_keyboard)

    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=main_menu_message_text,
            reply_markup=main_menu_message_keyboard
        )
        await query.delete_message()

    context.user_data["state"] = UserStates.Showing_Main_Menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type != ChatType.PRIVATE:
        return
    telegram_user = get_user_object_date_from_update_object(update)
    chat_id = update.message.from_user.id
    is_blocked = await db.insert_new_user(telegram_user=telegram_user)
    clear_user_data(context.user_data)
    context.user_data["state"] = UserStates.Showing_Main_Menu
    if is_blocked:
        await context.bot.send_message(chat_id=chat_id, text=Text.Blocked_User)
        return
    welcome_message=Text.get_welcome_by_user_message(telegram_user=telegram_user)
    keyboard = InlineKeyboardMarkup(Keyboards.get_main_inline_keyboard())
    await update.message.reply_text(text=welcome_message, reply_markup=keyboard,parse_mode="HTML")
    await delete_old_khatma_opening_request(chat_id, context)
