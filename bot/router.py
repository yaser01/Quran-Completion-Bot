from typing import Callable

from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

from bot.MainMenu.about_bot import about_bot_pressed
from bot.MainMenu.browse_quran import (
    browse_quran_pressed, browse_quran_by_chapter_pressed, browse_quran_by_chapter_browsing,
    close_quran_pressed, browse_quran_by_page_no_entered, browse_quran_by_page_no_browsing,
    browse_quran_by_page_no_pressed, browse_quran_book_pressed, browse_quran_by_surah_pressed,
    send_quran_chapter_file_pressed, send_quran_book_file_pressed,
)
from bot.MainMenu.contribute_to_khatma import (
    contribute_to_public_khatma_options_pressed, contribute_to_public_khatma_pressed,
    contribute_to_private_khatma_pressed, view_khatma_from_contribute_parts, view_public_khatma_pressed,
)
from bot.MainMenu.current_contribution import (
    current_contribution_pressed, current_contribution_parts_pressed, options_khatma_part_pressed,
    mark_part_as_cancel_pressed, mark_part_as_done_pressed, time_remaining_pressed,
    current_contribution_khatmas_pressed,
)
from bot.MainMenu.main_menu import main_menu, back_to_main_menu, start
from bot.MainMenu.manage_khatma import (
    manage_khatma_pressed, manage_khatma_properties_pressed, manage_khatma_update_name_pressed,
    manage_khatma_update_type_to_public_pressed, manage_khatma_update_type_to_private_pressed,
    manage_khatma_update_type_pressed, manage_khatma_update_part_duration_pressed,
    manage_khatma_update_intention_pressed, manage_khatma_parts_options_pressed,
    manage_khatma_part_option_pressed, mark_part_as_cancel_occupied_by_admin_pressed,
    mark_part_as_occupied_by_admin_pressed, mark_part_as_done_by_admin_pressed,
    mark_part_as_cancel_read_by_admin_pressed, mark_khatma_as_cancel_by_admin_pressed,
    mark_khatma_as_cancel_by_admin_confirmed_pressed, mark_khatma_as_done_by_admin_pressed,
    mark_khatma_as_done_by_admin_confirmed_pressed,
)
from bot.MainMenu.new_khatma import new_khatma_confirmation_pressed, new_khatma_pressed, cancel_mission, \
    new_khatma_type_pressed
from bot.MainMenu.view_khatma import show_khatma_info, khatma_refresh_pressed, khatma_part_pressed
from config.CallBackData import CallBackData


async def _nothing_pressed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()


def register_handlers(application: Application, message_handler: Callable) -> None:
    _register_commands(application)
    application.add_handler(MessageHandler(filters.TEXT, message_handler))
    _register_main_menu(application)
    _register_browse_quran(application)
    _register_contribute(application)
    _register_current_contribution(application)
    _register_new_khatma(application)
    _register_view_khatma(application)
    _register_manage_khatma(application)
    _register_misc(application)


def _register_commands(application: Application) -> None:
    application.add_handler(CommandHandler("start", show_khatma_info, filters.Regex("khatma_id_")))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("main_menu", main_menu))
    application.add_handler(CommandHandler("show_khatma_info", show_khatma_info, has_args=True))


def _register_main_menu(application: Application) -> None:
    application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern=CallBackData.Main_Menu))
    application.add_handler(CallbackQueryHandler(about_bot_pressed, pattern=CallBackData.Main_Menu_About))


def _register_browse_quran(application: Application) -> None:
    application.add_handler(
        CallbackQueryHandler(browse_quran_book_pressed, pattern=CallBackData.Main_Menu_Browse_Quran))
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
    application.add_handler(CallbackQueryHandler(close_quran_pressed, pattern=f"{CallBackData.Close_Quran}"))


def _register_contribute(application: Application) -> None:
    application.add_handler(
        CallbackQueryHandler(contribute_to_private_khatma_pressed, pattern=CallBackData.Main_Menu_Contribute_Khatma))
    application.add_handler(
        CallbackQueryHandler(contribute_to_private_khatma_pressed, pattern=CallBackData.Contribute_Khatma_Type_Private))
    application.add_handler(
        CallbackQueryHandler(contribute_to_public_khatma_pressed, pattern=CallBackData.Contribute_Khatma_Type_Public))
    application.add_handler(
        CallbackQueryHandler(contribute_to_public_khatma_options_pressed,
                             pattern=f"^{CallBackData.Contribute_Khatma_Public_Page_Option}_"))
    application.add_handler(
        CallbackQueryHandler(view_public_khatma_pressed, pattern=f"^{CallBackData.Contribute_Khatma_Public}_"))
    application.add_handler(
        CallbackQueryHandler(view_khatma_from_contribute_parts,
                             pattern=f"{CallBackData.Current_Contribution_Parts_View_Khatma}"))


def _register_current_contribution(application: Application) -> None:
    application.add_handler(
        CallbackQueryHandler(current_contribution_pressed, pattern=CallBackData.Main_Menu_Current_Contribution))
    application.add_handler(
        CallbackQueryHandler(current_contribution_parts_pressed, pattern=f"{CallBackData.Current_Contribution_Parts}"))
    application.add_handler(
        CallbackQueryHandler(current_contribution_khatmas_pressed,
                             pattern=f"{CallBackData.Current_Contribution_Khatmas}"))
    application.add_handler(
        CallbackQueryHandler(options_khatma_part_pressed, pattern=f"^{CallBackData.Options_Khatma_Part_By_ID}_"))
    application.add_handler(
        CallbackQueryHandler(mark_part_as_cancel_pressed, pattern=f"^{CallBackData.Mark_Part_As_Cancel}"))
    application.add_handler(
        CallbackQueryHandler(mark_part_as_done_pressed, pattern=f"^{CallBackData.Mark_Part_As_Done}"))
    application.add_handler(CallbackQueryHandler(time_remaining_pressed, pattern=f"^{CallBackData.Time_Remaining}"))


def _register_new_khatma(application: Application) -> None:
    application.add_handler(CallbackQueryHandler(new_khatma_pressed, pattern=CallBackData.Main_Menu_New_Khatma))
    application.add_handler(
        CallbackQueryHandler(new_khatma_type_pressed, pattern=f"{CallBackData.New_Khatma_Type_Public}|"
                                                              f"{CallBackData.New_Khatma_Type_Private}"))
    application.add_handler(
        CallbackQueryHandler(new_khatma_confirmation_pressed, pattern=f"{CallBackData.New_Khatma_Confirm_Yes}|"
                                                                      f"{CallBackData.New_Khatma_Confirm_No}"))
    application.add_handler(CallbackQueryHandler(cancel_mission, pattern=CallBackData.Cancel_Mission))


def _register_view_khatma(application: Application) -> None:
    application.add_handler(CallbackQueryHandler(khatma_part_pressed, pattern=f"^{CallBackData.Khatma_Part_ID}_"))
    application.add_handler(CallbackQueryHandler(khatma_refresh_pressed, pattern=f"^{CallBackData.Khatma_Refresh}_"))


def _register_manage_khatma(application: Application) -> None:
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
        CallbackQueryHandler(manage_khatma_part_option_pressed, pattern=f"^{CallBackData.Khatma_Part_Options_ID}_"))
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


def _register_misc(application: Application) -> None:
    application.add_handler(CallbackQueryHandler(_nothing_pressed, pattern=f"^{CallBackData.Nothing}"))
