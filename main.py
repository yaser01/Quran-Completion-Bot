import datetime
import json
import logging
import os

import pytz
import telegram
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup
from telegram.constants import ChatType, ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, CallbackContext, \
    MessageHandler, filters
from telegram.request import HTTPXRequest

from Database import db
from Startup.Global_Files import Daily_Page_Quran_File
from Packges.Global_Functions import get_user_object_date_from_update_object, send_missing_data_message, clear_user_data
from Packges.MainMenu.about_bot import about_bot_pressed
from Packges.MainMenu.browse_quran import browse_quran_pressed, browse_quran_by_chapter_pressed, \
    browse_quran_by_chapter_browsing, close_quran_pressed, browse_quran_by_page_no_entered, \
    browse_quran_by_page_no_browsing, browse_quran_by_page_no_pressed, browse_quran_book_pressed, \
    browse_quran_by_surah_pressed, send_quran_chapter_file_pressed, send_quran_book_file_pressed
from Packges.MainMenu.contribute_to_khatma import contribute_to_public_khatma_options_pressed, \
    contribute_to_public_khatma_pressed, contribute_to_private_khatma_pressed, view_khatma_from_contribute_parts, \
    view_public_khatma_pressed
from Packges.MainMenu.current_contribution import current_contribution_pressed, current_contribution_parts_pressed, \
    options_khatma_part_pressed, mark_part_as_cancel_pressed, mark_part_as_done_pressed, time_remaining_pressed, \
    current_contribution_khatmas_pressed
from Packges.MainMenu.main_menu import main_menu, back_to_main_menu, start
from Packges.MainMenu.manage_khatma import manage_khatma_pressed, manage_khatma_properties_pressed, \
    manage_khatma_update_name_pressed, manage_khatma_update_type_to_public_pressed, \
    manage_khatma_update_type_to_private_pressed, manage_khatma_update_type_pressed, \
    manage_khatma_update_part_duration_pressed, manage_khatma_update_intention_pressed, \
    manage_khatma_parts_options_pressed, manage_khatma_part_option_pressed, \
    mark_part_as_cancel_occupied_by_admin_pressed, mark_part_as_occupied_by_admin_pressed, \
    mark_part_as_done_by_admin_pressed, mark_part_as_cancel_read_by_admin_pressed, \
    mark_khatma_as_cancel_by_admin_pressed, mark_khatma_as_cancel_by_admin_confirmed_pressed, \
    mark_khatma_as_done_by_admin_pressed, mark_khatma_as_done_by_admin_confirmed_pressed
from Packges.MainMenu.new_khatma import new_khatma_confirmation_pressed, new_khatma_pressed, cancel_mission, \
    new_khatma_type_pressed
from Packges.MainMenu.view_khatma import show_khatma_info, khatma_refresh_pressed, khatma_part_pressed
from Packges.Schedule_Jobs import check_booked_parts_deadline, check_booked_parts_next_notification, \
    upload_daily_quran_page_to_channel, upload_quran_files, backup_database_daily
from Startup.CallBackData import CallBackData
from Startup.Keyboards import Keyboards
from Startup.KhatmaStatus import KhatmaStatus
from Startup.Text import Text
from Startup.UserStates import UserStates

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_LISTEN_HOST = os.getenv('WEBHOOK_LISTEN_HOST')
WEBHOOK_LISTEN_PORT = os.getenv('WEBHOOK_LISTEN_PORT')
SECRET_TOKEN = os.getenv('SECRET_TOKEN')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
CERT = os.getenv('CERT')


async def nothing_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    await query.answer()


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text.startswith("show_khatma_info_"):
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
    state = context.user_data.get("state", None)

    if state is None:
        return
    if state == UserStates.Contribute_Private_Khatma_Waiting_ID:
        khatma_id = text
        if not khatma_id.isdigit():
            logging.error(f"entered private_khatma_id is not a number ({khatma_id})")
            khatma_private_id_request_message_text = Text.Please_Enter_Correct_Number
            back_main_menu_keyboard = InlineKeyboardMarkup(
                Keyboards.get_back_to_main_menu())
            khatma_info_request_message_object = await context.bot.send_message(chat_id=chat_id,
                                                                                reply_markup=back_main_menu_keyboard,
                                                                                text=khatma_private_id_request_message_text)
            context.user_data["khatma_private_id_request_message_id"] = khatma_info_request_message_object.id
            return
        if int(khatma_id) <= 0:
            logging.error(f"entered private_khatma_id is not a natural number ({khatma_id})")
            khatma_private_id_request_message_text = Text.Please_Enter_Correct_Number
            back_main_menu_keyboard = InlineKeyboardMarkup(
                Keyboards.get_back_to_main_menu())
            khatma_info_request_message_object = await context.bot.send_message(chat_id=chat_id,
                                                                                reply_markup=back_main_menu_keyboard,
                                                                                text=khatma_private_id_request_message_text)
            context.user_data["khatma_private_id_request_message_id"] = khatma_info_request_message_object.id
            return
        if "temp_message_id" in context.user_data.keys():
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=context.user_data["temp_message_id"])
                context.user_data.pop("temp_message_id")
            except Exception as e:
                pass
        khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
        if khatma_status == KhatmaStatus.Not_Found:
            back_main_menu_keyboard = InlineKeyboardMarkup(
                Keyboards.get_back_to_main_menu())
            await context.bot.send_message(chat_id=chat_id, text=Text.Khatma_Not_Found
                                           , reply_markup=back_main_menu_keyboard)
            return
        if khatma_status == KhatmaStatus.Opened:
            khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                               intention=khatma_data.description,
                                                               duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                               start_date=khatma_data.time)
            khatma_info_message_keyboard = InlineKeyboardMarkup(Keyboards.get_khatma_parts_keyboard(khatma_id=khatma_id,
                                                                                                    khatma_parts=khatma_parts_data))
        elif khatma_status == KhatmaStatus.Done:
            khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                               intention=khatma_data.description,
                                                               duration_in_days=0,
                                                               start_date=khatma_data.start_date,
                                                               end_date=khatma_data.end_date,
                                                               is_finished=True,
                                                               is_canceled=False)
            khatma_info_message_keyboard = InlineKeyboardMarkup(
                Keyboards.get_back_to_main_menu())
        else:
            khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                               intention=khatma_data.description,
                                                               duration_in_days=0,
                                                               start_date=khatma_data.start_date,
                                                               end_date=khatma_data.end_date,
                                                               is_finished=False,
                                                               is_canceled=True)
            khatma_info_message_keyboard = InlineKeyboardMarkup(
                Keyboards.get_back_to_main_menu())
        await context.bot.send_message(chat_id=chat_id, reply_markup=khatma_info_message_keyboard,
                                       text=khatma_info_message_text,
                                       parse_mode=ParseMode.MARKDOWN_V2)
        clear_user_data(context.user_data)
        context.user_data["state"] = UserStates.Nothing
    elif state == UserStates.New_Khatma_Waiting_For_Opener_Name:
        if not {"new_khatma_message_id", "khatma_info_request_message_id"}.issubset(context.user_data.keys()):
            logging.error("Not enough data")
            await send_missing_data_message(telegram_user=telegram_user, context=context)
            return
        opener_name = text
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
            await context.bot.delete_message(chat_id=chat_id,
                                             message_id=context.user_data["khatma_info_request_message_id"])
        except Exception as e:
            logging.error(e)
        new_khatma_info_text = Text.create_new_khatma_info_with_name(name=opener_name)
        khatma_info_request_message_text = Text.Please_Enter_Intention
        khatma_info_request_message_keyboard = InlineKeyboardMarkup(Keyboards.get_cancel_keyboard())
        khatma_info_request_message_object = await context.bot.send_message(chat_id=chat_id,
                                                                            text=khatma_info_request_message_text,
                                                                            )
        await context.bot.edit_message_text(chat_id=chat_id, message_id=context.user_data["new_khatma_message_id"]
                                            , text=new_khatma_info_text,
                                            reply_markup=khatma_info_request_message_keyboard,
                                            parse_mode=ParseMode.MARKDOWN_V2)
        context.user_data["state"] = UserStates.New_Khatma_Waiting_For_Intention
        context.user_data["khatma_info_request_message_id"] = khatma_info_request_message_object.id
        context.user_data["khatma_info_opener_name"] = opener_name
    elif state == UserStates.New_Khatma_Waiting_For_Intention:
        if not {"new_khatma_message_id", "khatma_info_request_message_id",
                "khatma_info_opener_name"}.issubset(context.user_data.keys()):
            logging.error("Not enough data")
            await send_missing_data_message(telegram_user=telegram_user, context=context)
            return
        opener_name = context.user_data["khatma_info_opener_name"]
        intention = text
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
            await context.bot.delete_message(chat_id=chat_id,
                                             message_id=context.user_data["khatma_info_request_message_id"])
        except Exception as e:
            logging.error(e)
        new_khatma_info_text = Text.create_new_khatma_info_with_name_and_intention(name=opener_name,
                                                                                   intention=intention)
        khatma_info_request_message_text = Text.Please_Enter_Duration_In_Days
        khatma_info_request_message_keyboard = InlineKeyboardMarkup(Keyboards.get_cancel_keyboard())
        khatma_info_request_message_object = await context.bot.send_message(chat_id=chat_id,
                                                                            text=khatma_info_request_message_text
                                                                            )
        await context.bot.edit_message_text(chat_id=chat_id, message_id=context.user_data["new_khatma_message_id"]
                                            , text=new_khatma_info_text,
                                            reply_markup=khatma_info_request_message_keyboard,
                                            parse_mode=ParseMode.MARKDOWN_V2
                                            )
        context.user_data["state"] = UserStates.New_Khatma_Waiting_For_Part_Duration
        context.user_data["khatma_info_request_message_id"] = khatma_info_request_message_object.id
        context.user_data["khatma_info_intention"] = intention
    elif state == UserStates.New_Khatma_Waiting_For_Part_Duration:
        if not {"new_khatma_message_id", "khatma_info_request_message_id",
                "khatma_info_opener_name", "khatma_info_intention"}.issubset(context.user_data.keys()):
            logging.error("Not enough data")
            await send_missing_data_message(telegram_user=telegram_user, context=context)
            return
        opener_name = context.user_data["khatma_info_opener_name"]
        intention = context.user_data["khatma_info_intention"]
        duration = text
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
            await context.bot.delete_message(chat_id=chat_id,
                                             message_id=context.user_data["khatma_info_request_message_id"])
        except Exception as e:
            logging.error(e)
        if not duration.isdigit():
            logging.error(f"entered duration is not a number ({duration})")
            khatma_info_request_message_text = Text.Please_Enter_Duration_In_Days
            khatma_info_request_message_text += "\n"
            khatma_info_request_message_text += Text.Please_Enter_Correct_Number
            khatma_info_request_message_object = await context.bot.send_message(chat_id=chat_id,
                                                                                text=khatma_info_request_message_text)
            context.user_data["khatma_info_request_message_id"] = khatma_info_request_message_object.id
            return
        if int(duration) <= 0:
            logging.error(f"entered duration is not a number ({duration})")
            khatma_info_request_message_text = Text.Please_Enter_Duration_In_Days
            khatma_info_request_message_text += "\n"
            khatma_info_request_message_text += Text.Please_Enter_Correct_Number
            khatma_info_request_message_object = await context.bot.send_message(chat_id=chat_id,
                                                                                text=khatma_info_request_message_text)
            context.user_data["khatma_info_request_message_id"] = khatma_info_request_message_object.id
            return
        duration = int(duration)
        new_khatma_info_text = Text.create_new_khatma_info_with_all(name=opener_name,
                                                                    intention=intention,
                                                                    duration_in_days=duration)
        khatma_info_request_message_text = Text.Please_Confirm_Information
        khatma_info_request_message_keyboard = InlineKeyboardMarkup(Keyboards.get_new_khatma_confirmation_keyboard())
        khatma_info_request_message_object = await context.bot.send_message(chat_id=chat_id,
                                                                            text=khatma_info_request_message_text,
                                                                            reply_markup=khatma_info_request_message_keyboard)
        await context.bot.edit_message_text(chat_id=chat_id, message_id=context.user_data["new_khatma_message_id"]
                                            , text=new_khatma_info_text, parse_mode=ParseMode.MARKDOWN_V2)
        context.user_data["state"] = UserStates.New_Khatma_Waiting_For_Khatma_Confirmation
        context.user_data["khatma_info_request_message_id"] = khatma_info_request_message_object.id
        context.user_data["khatma_info_duration"] = duration
    elif state == UserStates.Update_Khatma_Waiting_For_Opener_Name:
        opener_name = text
        if not {"khatma_id"}.issubset(context.user_data.keys()):
            logging.error("Not enough data")
            await send_missing_data_message(telegram_user=telegram_user, context=context)
            return
        khatma_id = int(context.user_data["khatma_id"])
        result = await db.update_khatma_opener_name(khatma_id, new_opener_name=opener_name)
        if result:
            await context.bot.send_message(chat_id=chat_id, text=Text.Update_Khatma_Info_Done)
        else:
            await context.bot.send_message(chat_id=chat_id, text=Text.Unknown_Error_Text)
        context.user_data["state"] = UserStates.Nothing
        context.user_data.pop("khatma_id")
        try:
            if context.user_data.get("temp_message_id", None) is not None:
                await context.bot.delete_message(chat_id=chat_id, message_id=context.user_data["temp_message_id"])
        except Exception as e:
            logging.error(e)
    elif state == UserStates.Update_Khatma_Waiting_For_Intention:
        intention = text
        if not {"khatma_id"}.issubset(context.user_data.keys()):
            logging.error("Not enough data")
            await send_missing_data_message(telegram_user=telegram_user, context=context)
            return
        khatma_id = int(context.user_data["khatma_id"])
        result = await db.update_khatma_intention(khatma_id, new_intention=intention)
        if result:
            await context.bot.send_message(chat_id=chat_id, text=Text.Update_Khatma_Info_Done)
        else:
            await context.bot.send_message(chat_id=chat_id, text=Text.Unknown_Error_Text)
        context.user_data["state"] = UserStates.Nothing
        context.user_data.pop("khatma_id")
        try:
            if context.user_data.get("temp_message_id", None) is not None:
                await context.bot.delete_message(chat_id=chat_id, message_id=context.user_data["temp_message_id"])
        except Exception as e:
            logging.error(e)
    elif state == UserStates.Update_Khatma_Waiting_For_Part_Duration:
        reading_part_duration = text
        if not {"khatma_id"}.issubset(context.user_data.keys()):
            logging.error("Not enough data")
            await send_missing_data_message(telegram_user=telegram_user, context=context)
            return
        if not reading_part_duration.isdigit():
            logging.error(f"entered update duration is not a number ({reading_part_duration})")
            khatma_info_request_message_text = Text.Please_Enter_Correct_Number
            await context.bot.send_message(chat_id=chat_id,
                                           text=khatma_info_request_message_text)
            return
        if int(reading_part_duration) <= 0:
            logging.error(f"entered update duration is not a number ({reading_part_duration})")
            khatma_info_request_message_text = Text.Please_Enter_Correct_Number
            await context.bot.send_message(chat_id=chat_id,
                                           text=khatma_info_request_message_text)
            return
        reading_part_duration = int(reading_part_duration)
        khatma_id = int(context.user_data["khatma_id"])
        result = await db.update_khatma_reservation_part_duration(khatma_id,
                                                                  new_reservation_part_duration=reading_part_duration)
        if result:
            await context.bot.send_message(chat_id=chat_id, text=Text.Update_Khatma_Info_Done)
        else:
            await context.bot.send_message(chat_id=chat_id, text=Text.Unknown_Error_Text)
        context.user_data["state"] = UserStates.Nothing
        context.user_data.pop("khatma_id")
        try:
            if context.user_data.get("temp_message_id", None) is not None:
                await context.bot.delete_message(chat_id=chat_id, message_id=context.user_data["temp_message_id"])
        except Exception as e:
            logging.error(e)
    elif state == UserStates.Browse_Quran_Waiting_For_Page_No:
        page_no = text
        if not page_no.isdigit():
            logging.error(f"entered quran browse page no is not a number ({page_no})")
            error_message_text = Text.Wrong_Input_Browse_Quran
            await context.bot.send_message(chat_id=chat_id, text=error_message_text)
            return
        page_no = int(page_no)
        if page_no < 1 or page_no > 604:
            logging.error(f"entered quran browse page no is not a number in range (1-604) ({page_no})")
            error_message_text = Text.Wrong_Range_Browse_Quran
            await context.bot.send_message(chat_id=chat_id, text=error_message_text)
            return
        context.user_data["state"] = UserStates.Nothing
        await browse_quran_by_page_no_entered(update=update, context=context, chat_id=chat_id, page_no=page_no,
                                              message_id_to_delete=update.message.message_id)


def main():
    application = Application.builder().token(BOT_TOKEN).get_updates_request(HTTPXRequest(http_version="1.1")) \
        .request(HTTPXRequest(http_version="1.1", read_timeout=1000, write_timeout=1000, connect_timeout=1000,
                              connection_pool_size=10,
                              pool_timeout=1000)).build()
    application.add_handler(CommandHandler("start", show_khatma_info, filters.Regex("khatma_id_")))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("main_menu", main_menu))
    application.add_handler(CommandHandler("show_khatma_info", show_khatma_info, has_args=True))
    application.add_handler(MessageHandler(filters.TEXT, message))
    application.add_handler(CallbackQueryHandler(new_khatma_pressed, pattern=CallBackData.Main_Menu_New_Khatma))
    application.add_handler(
        CallbackQueryHandler(browse_quran_book_pressed, pattern=CallBackData.Main_Menu_Browse_Quran))
    application.add_handler(
        CallbackQueryHandler(about_bot_pressed, pattern=CallBackData.Main_Menu_About))
    application.add_handler(
        CallbackQueryHandler(send_quran_chapter_file_pressed, pattern=f"^{CallBackData.Send_Chapter_Link}_"))
    application.add_handler(
        CallbackQueryHandler(send_quran_book_file_pressed, pattern=f"^{CallBackData.Send_Book_Link}_"))
    application.add_handler(
        CallbackQueryHandler(browse_quran_pressed, pattern=f"^{CallBackData.Browse_Quran_By_Book}_"))
    application.add_handler(
        CallbackQueryHandler(browse_quran_by_page_no_browsing, pattern=f"^{CallBackData.Browse_Quran_By_Page}_"))
    application.add_handler(
        CallbackQueryHandler(browse_quran_by_page_no_pressed, pattern=f"{CallBackData.Browse_Quran_By_Page_Main}"))
    application.add_handler(
        CallbackQueryHandler(browse_quran_by_surah_pressed, pattern=f"{CallBackData.Browse_Quran_By_Surah_Main}"))
    application.add_handler(
        CallbackQueryHandler(browse_quran_by_chapter_browsing, pattern=f"^{CallBackData.Browse_Quran_By_Chapter}_"))

    application.add_handler(
        CallbackQueryHandler(browse_quran_by_chapter_pressed, pattern=CallBackData.Browse_Quran_By_Chapter_Main))
    application.add_handler(
        CallbackQueryHandler(contribute_to_private_khatma_pressed, pattern=CallBackData.Main_Menu_Contribute_Khatma))
    application.add_handler(
        CallbackQueryHandler(current_contribution_pressed, pattern=CallBackData.Main_Menu_Current_Contribution))
    application.add_handler(
        CallbackQueryHandler(contribute_to_private_khatma_pressed, pattern=CallBackData.Contribute_Khatma_Type_Private))
    application.add_handler(
        CallbackQueryHandler(contribute_to_public_khatma_pressed, pattern=CallBackData.Contribute_Khatma_Type_Public))
    application.add_handler(
        CallbackQueryHandler(contribute_to_public_khatma_options_pressed,
                             pattern=f"^{CallBackData.Contribute_Khatma_Public_Page_Option}_"))
    application.add_handler(
        CallbackQueryHandler(view_public_khatma_pressed,
                             pattern=f"^{CallBackData.Contribute_Khatma_Public}_"))
    application.add_handler(
        CallbackQueryHandler(back_to_main_menu, pattern=CallBackData.Main_Menu))
    application.add_handler(
        CallbackQueryHandler(new_khatma_type_pressed, pattern=f"{CallBackData.New_Khatma_Type_Public}|"
                                                              f"{CallBackData.New_Khatma_Type_Private}"))
    application.add_handler(
        CallbackQueryHandler(view_khatma_from_contribute_parts,
                             pattern=f"{CallBackData.Current_Contribution_Parts_View_Khatma}"))
    application.add_handler(
        CallbackQueryHandler(current_contribution_parts_pressed, pattern=f"{CallBackData.Current_Contribution_Parts}"))
    application.add_handler(
        CallbackQueryHandler(current_contribution_khatmas_pressed,
                             pattern=f"{CallBackData.Current_Contribution_Khatmas}"))

    application.add_handler(CallbackQueryHandler(cancel_mission, pattern=CallBackData.Cancel_Mission))
    application.add_handler(
        CallbackQueryHandler(new_khatma_confirmation_pressed, pattern=f"{CallBackData.New_Khatma_Confirm_Yes}|"
                                                                      f"{CallBackData.New_Khatma_Confirm_No}"))
    application.add_handler(CallbackQueryHandler(khatma_part_pressed, pattern=f"^{CallBackData.Khatma_Part_ID}_"))
    application.add_handler(
        CallbackQueryHandler(manage_khatma_part_option_pressed, pattern=f"^{CallBackData.Khatma_Part_Options_ID}_"))
    application.add_handler(CallbackQueryHandler(khatma_refresh_pressed, pattern=f"^{CallBackData.Khatma_Refresh}_"))
    application.add_handler(
        CallbackQueryHandler(options_khatma_part_pressed, pattern=f"^{CallBackData.Options_Khatma_Part_By_ID}_"))
    application.add_handler(
        CallbackQueryHandler(mark_part_as_cancel_pressed, pattern=f"^{CallBackData.Mark_Part_As_Cancel}"))
    application.add_handler(
        CallbackQueryHandler(mark_part_as_done_pressed, pattern=f"^{CallBackData.Mark_Part_As_Done}"))
    application.add_handler(
        CallbackQueryHandler(manage_khatma_pressed, pattern=f"^{CallBackData.Khatmas_Options}"))
    application.add_handler(
        CallbackQueryHandler(manage_khatma_properties_pressed, pattern=f"^{CallBackData.Khatmas_Properties}"))
    application.add_handler(
        CallbackQueryHandler(manage_khatma_update_intention_pressed,
                             pattern=f"^{CallBackData.Khatmas_Change_Intention}"))
    application.add_handler(
        CallbackQueryHandler(manage_khatma_update_name_pressed, pattern=f"^{CallBackData.Khatmas_Change_Opener_Name}"))
    application.add_handler(
        CallbackQueryHandler(manage_khatma_update_part_duration_pressed,
                             pattern=f"^{CallBackData.Khatmas_Change_Duration}"))
    application.add_handler(
        CallbackQueryHandler(manage_khatma_update_type_pressed, pattern=f"^{CallBackData.Khatmas_Change_Type}"))
    application.add_handler(
        CallbackQueryHandler(manage_khatma_update_type_to_private_pressed,
                             pattern=f"^{CallBackData.Khatmas_Change_Type_Private}"))
    application.add_handler(
        CallbackQueryHandler(manage_khatma_update_type_to_public_pressed,
                             pattern=f"^{CallBackData.Khatmas_Change_Type_Public}"))
    application.add_handler(
        CallbackQueryHandler(manage_khatma_parts_options_pressed,
                             pattern=f"^{CallBackData.Khatmas_Parts_Manage}"))
    application.add_handler(
        CallbackQueryHandler(mark_part_as_cancel_occupied_by_admin_pressed,
                             pattern=f"^{CallBackData.Mark_Part_As_Cancel_Occupy_By_Admin}"))
    application.add_handler(
        CallbackQueryHandler(mark_part_as_occupied_by_admin_pressed,
                             pattern=f"^{CallBackData.Mark_Part_As_Occupied_By_Admin}"))
    application.add_handler(
        CallbackQueryHandler(mark_part_as_done_by_admin_pressed,
                             pattern=f"^{CallBackData.Mark_Part_As_Done_By_Admin}"))
    application.add_handler(
        CallbackQueryHandler(mark_part_as_cancel_read_by_admin_pressed,
                             pattern=f"^{CallBackData.Mark_Part_As_Cancel_Read_By_Admin}"))
    application.add_handler(
        CallbackQueryHandler(mark_khatma_as_cancel_by_admin_pressed,
                             pattern=f"^{CallBackData.Khatmas_Mark_As_Canceled}_"))
    application.add_handler(
        CallbackQueryHandler(mark_khatma_as_cancel_by_admin_confirmed_pressed,
                             pattern=f"^{CallBackData.Khatmas_Mark_As_Canceled_Confirmed}_"))
    application.add_handler(
        CallbackQueryHandler(mark_khatma_as_done_by_admin_pressed,
                             pattern=f"^{CallBackData.Khatmas_Mark_As_Done}_"))
    application.add_handler(
        CallbackQueryHandler(mark_khatma_as_done_by_admin_confirmed_pressed,
                             pattern=f"^{CallBackData.Khatmas_Mark_As_Done_Confirmed}_"))
    application.add_handler(CallbackQueryHandler(time_remaining_pressed, pattern=f"^{CallBackData.Time_Remaining}"))
    application.add_handler(CallbackQueryHandler(nothing_pressed, pattern=f"^{CallBackData.Nothing}"))
    application.add_handler(CallbackQueryHandler(close_quran_pressed, pattern=f"{CallBackData.Close_Quran}"))
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
    job_upload_quran_files = job_queue.run_once(upload_quran_files, when=1)
    application.run_webhook(
        listen=WEBHOOK_LISTEN_HOST,
        port=WEBHOOK_LISTEN_PORT,
        secret_token=SECRET_TOKEN,
        key=PRIVATE_KEY,
        cert=CERT,
        webhook_url=WEBHOOK_URL
    )


def setup_startup_files():
    if not os.path.isfile(Daily_Page_Quran_File):
        data = {}
        with open(Daily_Page_Quran_File, "a+", encoding="UTF-8") as f:
            data["page_no"] = 1
            json.dump(data, f)

if __name__ == "__main__":
    logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    setup_startup_files()
    main()
