from builtins import staticmethod
from datetime import datetime
from math import ceil
from typing import List

from telegram import InlineKeyboardButton

from db import db
from db.models import Khatma_Parts, Khatma
from bot.Global_Functions import get_elided_text_version, format_timespan_in_arabic, QURAN_BOOK_ID
from config import SurahsData
from config.CallBackData import CallBackData

part_no_dict = {1: "الجزء (01)",
                2: "الجزء (02)",
                3: "الجزء (03)",
                4: "الجزء (04)",
                5: "الجزء (05)",
                6: "الجزء (06)",
                7: "الجزء (07)",
                8: "الجزء (08)",
                9: "الجزء (09)",
                10: "الجزء (10)",
                11: "الجزء (11)",
                12: "الجزء (12)",
                13: "الجزء (13)",
                14: "الجزء (14)",
                15: "الجزء (15)",
                16: "الجزء (16)",
                17: "الجزء (17)",
                18: "الجزء (18)",
                19: "الجزء (19)",
                20: "الجزء (20)",
                21: "الجزء (21)",
                22: "الجزء (22)",
                23: "الجزء (23)",
                24: "الجزء (24)",
                25: "الجزء (25)",
                26: "الجزء (26)",
                27: "الجزء (27)",
                28: "الجزء (28)",
                29: "الجزء (29)",
                30: "الجزء (30)",
                }
part_range_data = [
    {
        "text": "الجزء الـ(01)",
        "start": 1,
        "end": 21
    },
    {
        "text": "الجزء الـ(02)",
        "start": 22,
        "end": 41
    },
    {
        "text": "الجزء الـ(03)",
        "start": 42,
        "end": 61
    },
    {
        "text": "الجزء الـ(04)",
        "start": 62,
        "end": 81
    },
    {
        "text": "الجزء الـ(05)",
        "start": 82,
        "end": 101
    },
    {
        "text": "الجزء الـ(06)",
        "start": 102,
        "end": 120
    },
    {
        "text": "الجزء الـ(07)",
        "start": 121,
        "end": 141
    },
    {
        "text": "الجزء الـ(08)",
        "start": 142,
        "end": 161
    },
    {
        "text": "الجزء الـ(09)",
        "start": 162,
        "end": 181
    },
    {
        "text": "الجزء الـ(10)",
        "start": 182,
        "end": 200
    },
    {
        "text": "الجزء الـ(11)",
        "start": 201,
        "end": 221
    },
    {
        "text": "الجزء الـ(12)",
        "start": 222,
        "end": 241
    },
    {
        "text": "الجزء الـ(13)",
        "start": 242,
        "end": 261
    },
    {
        "text": "الجزء الـ(14)",
        "start": 262,
        "end": 281
    },
    {
        "text": "الجزء الـ(15)",
        "start": 282,
        "end": 301
    },
    {
        "text": "الجزء الـ(16)",
        "start": 302,
        "end": 321
    },
    {
        "text": "الجزء الـ(17)",
        "start": 322,
        "end": 341
    },
    {
        "text": "الجزء الـ(18)",
        "start": 342,
        "end": 361
    },
    {
        "text": "الجزء الـ(19)",
        "start": 362,
        "end": 381
    },
    {
        "text": "الجزء الـ(20)",
        "start": 382,
        "end": 401
    },
    {
        "text": "الجزء الـ(21)",
        "start": 402,
        "end": 421
    },
    {
        "text": "الجزء الـ(22)",
        "start": 422,
        "end": 441
    },
    {
        "text": "الجزء الـ(23)",
        "start": 442,
        "end": 461
    },
    {
        "text": "الجزء الـ(24)",
        "start": 462,
        "end": 481
    },
    {
        "text": "الجزء الـ(25)",
        "start": 482,
        "end": 501
    },
    {
        "text": "الجزء الـ(26)",
        "start": 502,
        "end": 521
    },
    {
        "text": "الجزء الـ(27)",
        "start": 522,
        "end": 541
    },
    {
        "text": "الجزء الـ(28)",
        "start": 542,
        "end": 561
    },
    {
        "text": "الجزء الـ(29)",
        "start": 562,
        "end": 581
    },
    {
        "text": "الجزء الـ(30)",
        "start": 582,
        "end": 604
    },
]
part_no_dict_in_details = \
    {1: "الأول (1)",
     2: "الثاني (2)",
     3: "الثالث (3)",
     4: "الرابع (4)",
     5: "الخامس (5)",
     6: "السادس (6)",
     7: "السابع (7)",
     8: "الثامن (8)",
     9: "التاسع (9)",
     10: "العاشر (10)",
     11: "الحادي عشر (11)",
     12: "الثاني عشر (12)",
     13: "الثالث عشر (13)",
     14: "الرابع عشر (14)",
     15: "الخامس عشر (15)",
     16: "السادس عشر (16)",
     17: "السابع عشر (17)",
     18: "الثامن عشر (18)",
     19: "التاسع عشر (19)",
     20: "العشرون (20)",
     21: "الحادي والعشرون (21)",
     22: "الثاني والعشرون (22)",
     23: "الثالث والعشرون (23)",
     24: "الرابع والعشرون (24)",
     25: "الخامس والعشرون (25)",
     26: "السادس والعشرون (26)",
     27: "السابع والعشرون (27)",
     28: "الثامن والعشرون (28)",
     29: "التاسع والعشرون (29)",
     30: "الثلاثون (30)",

     }
part_status_color = ["⚪", "🔵", "🟢"]
part_status_options_color = ["📕", "📖", "✅"]


class Keyboards:
    @staticmethod
    def get_main_inline_keyboard():
        return [
            [InlineKeyboardButton("مساهماتي الحالية", callback_data=CallBackData.Main_Menu_Current_Contribution)
                , InlineKeyboardButton("ختمة جديدة", callback_data=CallBackData.Main_Menu_New_Khatma)],
            [InlineKeyboardButton("تصفح القرآن الكريم", callback_data=CallBackData.Main_Menu_Browse_Quran),
             InlineKeyboardButton("المساهمة في ختمة", callback_data=CallBackData.Main_Menu_Contribute_Khatma)],
            [InlineKeyboardButton("حول البوت", callback_data=CallBackData.Main_Menu_About)], ]

    @staticmethod
    def get_new_khatma_confirmation_keyboard():
        return [
            [InlineKeyboardButton("إلغاء الأمر", callback_data=CallBackData.New_Khatma_Confirm_No),
             InlineKeyboardButton("نعم", callback_data=CallBackData.New_Khatma_Confirm_Yes)]
        ]

    @staticmethod
    def get_cancel_keyboard():
        return [
            [InlineKeyboardButton("إلغاء الأمر", callback_data=CallBackData.Cancel_Mission)]
        ]

    @staticmethod
    def get_cancel_keyboard():
        return [
            [InlineKeyboardButton("إلغاء الأمر", callback_data=CallBackData.Cancel_Mission)]
        ]

    @staticmethod
    def get_new_khatma_type_keyboard():
        return [
            [InlineKeyboardButton("خاصة", callback_data=CallBackData.New_Khatma_Type_Private),
             InlineKeyboardButton("عامة", callback_data=CallBackData.New_Khatma_Type_Public)],
            [InlineKeyboardButton("إلغاء الأمر", callback_data=CallBackData.Cancel_Mission)]
        ]

    @staticmethod
    def get_update_khatma_type_keyboard(khatma_id):
        return [
            [InlineKeyboardButton("خاصة",
                                  callback_data=CallBackData.Khatmas_Change_Type_Private + "_" + str(khatma_id)),
             InlineKeyboardButton("عامة",
                                  callback_data=CallBackData.Khatmas_Change_Type_Public + "_" + str(khatma_id))],
            [InlineKeyboardButton("إلغاء الأمر", callback_data=CallBackData.Cancel_Mission)]
        ]

    @staticmethod
    def get_contribute_khatma_type_keyboard():
        return [
            [InlineKeyboardButton("خاصة", callback_data=CallBackData.Contribute_Khatma_Type_Private),
             InlineKeyboardButton("عامة", callback_data=CallBackData.Contribute_Khatma_Type_Public)],
            [InlineKeyboardButton("عودة", callback_data=CallBackData.Main_Menu)]
        ]

    @staticmethod
    def get_quran_browse_books_main_keyboard():
        return [
            [InlineKeyboardButton("رواية حفص عن عاصم", callback_data=CallBackData.Browse_Quran_By_Book + "_" + str(
                QURAN_BOOK_ID.Hafs.value))],
            [InlineKeyboardButton("رواية حفص عن عاصم (المصحف المجود)",
                                  callback_data=CallBackData.Browse_Quran_By_Book + "_" + str(
                                      QURAN_BOOK_ID.Hafs_with_tajwid.value))],
            [InlineKeyboardButton("عودة", callback_data=CallBackData.Main_Menu)]
        ]

    @staticmethod
    def get_quran_browse_ways_main_keyboard(book_id):
        return [
            [InlineKeyboardButton("حسب السورة",
                                  callback_data=CallBackData.Browse_Quran_By_Surah_Main + "_" + str(book_id) + "_1"),
             InlineKeyboardButton("حسب الجزء",
                                  callback_data=CallBackData.Browse_Quran_By_Chapter_Main + "_" + str(book_id))],
            [InlineKeyboardButton("تحميل المصحف كاملاً 📚",
                                  callback_data=CallBackData.Send_Book_Link + "_" + str(book_id))
                ,InlineKeyboardButton("حسب رقم الصفحة",
                                  callback_data=CallBackData.Browse_Quran_By_Page_Main + "_" + str(book_id))],
            [InlineKeyboardButton("عودة", callback_data=CallBackData.Main_Menu_Browse_Quran)]
        ]

    @staticmethod
    def get_quran_browse_by_chapter_keyboard(book_id):
        keyboard = []
        for i in range(0, len(part_range_data), 3):
            temp_keyboard = [InlineKeyboardButton(part_range_data[i + 2]["text"],
                                                  callback_data=f'BQ_C_{book_id}_{i + 3}_{part_range_data[i + 2]["start"]}_{part_range_data[i + 2]["end"]}_{part_range_data[i + 2]["start"]}')
                , InlineKeyboardButton(part_range_data[i + 1]["text"],
                                       callback_data=f'BQ_C_{book_id}_{i + 2}_{part_range_data[i + 1]["start"]}_{part_range_data[i + 1]["end"]}_{part_range_data[i + 1]["start"]}')
                , InlineKeyboardButton(part_range_data[i]["text"],
                                       callback_data=f'BQ_C_{book_id}_{i + 1}_{part_range_data[i]["start"]}_{part_range_data[i]["end"]}_{part_range_data[i]["start"]}')
                             ]
            keyboard.append(temp_keyboard)
        temp_keyboard = [
            InlineKeyboardButton("عودة", callback_data=CallBackData.Browse_Quran_By_Book + "_" + str(book_id))]
        keyboard.append(temp_keyboard)
        return keyboard

    @staticmethod
    def get_quran_browse_by_surah_keyboard(book_id, page_no=1, page_size=20):
        keyboard = []
        start_id = (page_no - 1) * page_size
        end_id = min(len(SurahsData.Data), start_id + page_size)
        for i in range(start_id, end_id, 2):
            temp_keyboard = [InlineKeyboardButton(str(i + 2) + ". " + SurahsData.Data[i + 2]["arabic_name"],
                                                  callback_data=f'BQ_P_{book_id}_{SurahsData.Data[i + 2]["page_start"]}')
                , InlineKeyboardButton(str(i + 1) + ". " + SurahsData.Data[i + 1]["arabic_name"],
                                       callback_data=f'BQ_P_{book_id}_{SurahsData.Data[i + 1]["page_start"]}')
                             ]
            keyboard.append(temp_keyboard)
        temp_keyboard = []
        page_text = str(page_no)
        page_text += " من "
        page_text += str(int(ceil(114.0 / page_size)))
        if end_id < len(SurahsData.Data):
            temp_keyboard.append(InlineKeyboardButton("التالي ◀️",
                                                      callback_data=f"{CallBackData.Browse_Quran_By_Surah_Main}_{book_id}_{page_no + 1}"))
        temp_keyboard.append(InlineKeyboardButton(page_text, callback_data=CallBackData.Nothing + "_Q"))
        if start_id > 0:
            temp_keyboard.append(InlineKeyboardButton("▶️ السابق",
                                                      callback_data=f"{CallBackData.Browse_Quran_By_Surah_Main}_{book_id}_{page_no - 1}"))
        keyboard.append(temp_keyboard)
        temp_keyboard = [
            InlineKeyboardButton("عودة", callback_data=CallBackData.Browse_Quran_By_Book + "_" + str(book_id))]
        keyboard.append(temp_keyboard)
        return keyboard

    @staticmethod
    def get_quran_browse_by_chapter_browsing_keyboard(book_id, current_page, chapter_no, range_start=1, range_end=604):
        page_text = "الصفحة "
        page_text += str(current_page)
        keyboard = []
        temp_keyboard = []
        if current_page < range_end:
            temp_keyboard.append(InlineKeyboardButton("التالي ◀️",
                                                      callback_data=f"BQ_C_{book_id}_{chapter_no}_{range_start}_{range_end}_{current_page + 1}"))
        temp_keyboard.append(InlineKeyboardButton(page_text, callback_data=CallBackData.Nothing + "_Q"))
        if current_page > range_start:
            temp_keyboard.append(InlineKeyboardButton("▶️ السابق",
                                                      callback_data=f"BQ_C_{book_id}_{chapter_no}_{range_start}_{range_end}_{current_page - 1}"))
        keyboard.append(temp_keyboard)
        temp_keyboard = [InlineKeyboardButton("تحميل الجزء كملف PDF 📚", callback_data=CallBackData.Send_Chapter_Link+f"_{book_id}_{chapter_no}")]
        keyboard.append(temp_keyboard)
        temp_keyboard = [InlineKeyboardButton("إغلاق المصحف", callback_data=CallBackData.Close_Quran)]
        keyboard.append(temp_keyboard)
        return keyboard

    @staticmethod
    def get_quran_browse_by_page_no_browsing_keyboard(book_id, current_page, range_start=1, range_end=604):
        keyboard = []
        temp_keyboard = []
        temp_keyboard2 = []
        if current_page < range_end:
            max_after_10_pages = min(current_page + 10, 604)
            temp_keyboard2.append(InlineKeyboardButton("10 صفحات ⏪",
                                                       callback_data=f"BQ_P_{book_id}_{max_after_10_pages}"))
            temp_keyboard.append(InlineKeyboardButton("التالي ◀️",
                                                      callback_data=f"BQ_P_{book_id}_{current_page + 1}"))
            temp_keyboard.append(InlineKeyboardButton(str(current_page), callback_data=CallBackData.Nothing + "_PQ"))
        if current_page > range_start:
            max_before_10_pages = max(current_page - 10, 1)
            temp_keyboard.append(InlineKeyboardButton("▶️ السابق",
                                                      callback_data=f"BQ_P_{book_id}_{current_page - 1}"))
            temp_keyboard2.append(InlineKeyboardButton("⏩ 10 صفحات",
                                                       callback_data=f"BQ_P_{book_id}_{max_before_10_pages}"))
        keyboard.append(temp_keyboard)
        keyboard.append(temp_keyboard2)
        temp_keyboard = [InlineKeyboardButton("إغلاق المصحف", callback_data=CallBackData.Close_Quran)]
        keyboard.append(temp_keyboard)
        return keyboard

    @staticmethod
    def get_current_contributions_keyboard():
        return [
            [InlineKeyboardButton("إدارة ختماتي", callback_data=CallBackData.Current_Contribution_Khatmas),
             InlineKeyboardButton("إدارة أجزائي", callback_data=CallBackData.Current_Contribution_Parts)],
            [InlineKeyboardButton("عودة", callback_data=CallBackData.Main_Menu)]
        ]

    @staticmethod
    async def get_current_contributions_booked_parts_keyboard(booked_parts: List[Khatma_Parts]):
        keyboard = []
        set_of_khatmas_id = set()
        for part_data in booked_parts:
            khatma = part_data.Khatma
            if part_data.Khatma.id not in set_of_khatmas_id:
                set_of_khatmas_id.add(khatma.id)
                name_of_opener = khatma.name_of_opener
                intention = get_elided_text_version(text=khatma.description, limit=30)
                time_since_start_in_second = (datetime.utcnow() - khatma.time).total_seconds()
                number_of_finished_parts = await db.count_number_of_finished_parts_of_khatma(khatma_id=khatma.id)
                text = ""
                text = "الاسم: "
                text += str(name_of_opener)
                text += " | "
                # text += "النية: "
                text += str(intention)
                text += " | "
                # text += "منذ: "
                # text += format_timespan_in_arabic(total_time=time_since_start_in_second, max_units=1)
                # text += " | "
                # text += "الأجزاء المنتهية: "
                text += f"{number_of_finished_parts}/30"
                temp_keyboard = [
                    InlineKeyboardButton(text, callback_data=CallBackData.Current_Contribution_Parts_View_Khatma +
                                                             "_" + str(khatma.id))
                ]
                keyboard.append(temp_keyboard)
            time_until_end_in_second = int((part_data.part_deadline - datetime.utcnow()).total_seconds())
            timespan_text = ""
            timespan_text += format_timespan_in_arabic(total_time=time_until_end_in_second, max_units=1)
            timespan_text += " ⏳"
            temp_keyboard = [
                InlineKeyboardButton(f"تعديل ⚙️",
                                     callback_data=CallBackData.Options_Khatma_Part_By_ID + f"_{part_data.part_id}"),
                InlineKeyboardButton(f"{timespan_text}",
                                     callback_data=CallBackData.Time_Remaining + f"_{time_until_end_in_second}"),
                InlineKeyboardButton(f"{part_no_dict[part_data.part_no]}" + ": ",
                                     callback_data=CallBackData.Nothing + f"_Name_{khatma.id}_{part_data.part_no}")
            ]
            keyboard.append(temp_keyboard)
        if len(keyboard) == 0:
            keyboard.append([InlineKeyboardButton("لا يوجد أجزاء محجوزة", callback_data=CallBackData.Nothing + "_" +
                                                                                        CallBackData.Current_Contribution_Khatmas)])
        keyboard.append(
            [InlineKeyboardButton("عودة", callback_data=CallBackData.Main_Menu_Current_Contribution)
                ,
             InlineKeyboardButton("تحديث 🔄", callback_data=CallBackData.Current_Contribution_Parts)])
        return keyboard

    @staticmethod
    def get_manage_khatma_keyboard(khatma_id, is_opened):
        share_link = f"https://telegram.me/QuranCompletionBot?startgroup=khatma_id_{khatma_id}"
        if is_opened:
            keyboard = [[InlineKeyboardButton("تعديل خصائص الختمة",
                                              callback_data=CallBackData.Khatmas_Properties + "_" + str(khatma_id))], [
                            InlineKeyboardButton("إدارة الأجزاء ⚙️",
                                                 callback_data=CallBackData.Khatmas_Parts_Manage + "_" + str(
                                                     khatma_id))],
                        [
                            InlineKeyboardButton("إلغاء الختمة ❌",
                                                 callback_data=CallBackData.Khatmas_Mark_As_Canceled + "_" + str(
                                                     khatma_id)),
                            InlineKeyboardButton("إنهاء قراءة الختمة ✅",
                                                 callback_data=CallBackData.Khatmas_Mark_As_Done + "_" + str(
                                                     khatma_id)),
                        ],
                        [InlineKeyboardButton(text="اضغط للمشاركة مع مجموعة", url=share_link)]
                , [InlineKeyboardButton("رجوع", callback_data=CallBackData.Current_Contribution_Khatmas)]]

        else:
            keyboard = [[InlineKeyboardButton("رجوع", callback_data=CallBackData.Current_Contribution_Khatmas)]]
        return keyboard

    @staticmethod
    def get_mark_khatma_as_canceled_by_admin_confirmation(khatma_id):
        keyboard = [
            [InlineKeyboardButton("تأكيد إلغاء الختمة ❌",
                                  callback_data=CallBackData.Khatmas_Mark_As_Canceled_Confirmed + "_" + str(
                                      khatma_id))],
            [InlineKeyboardButton("رجوع", callback_data=CallBackData.Khatmas_Options + "_" + str(khatma_id))]
        ]
        return keyboard

    @staticmethod
    def get_mark_khatma_as_done_by_admin_confirmation(khatma_id):
        keyboard = [
            [InlineKeyboardButton("تأكيد إنهاء قراءة الختمة ✅",
                                  callback_data=CallBackData.Khatmas_Mark_As_Done_Confirmed + "_" + str(
                                      khatma_id))],
            [InlineKeyboardButton("رجوع", callback_data=CallBackData.Khatmas_Options + "_" + str(khatma_id))]
        ]
        return keyboard

    @staticmethod
    def get_manage_khatma_properties_keyboard(khatma_id, is_opened):
        if is_opened:
            keyboard = [
                [
                    InlineKeyboardButton("تعديل النية",
                                         callback_data=CallBackData.Khatmas_Change_Intention + "_" + str(
                                             khatma_id)),
                    InlineKeyboardButton("تعديل الاسم",
                                         callback_data=CallBackData.Khatmas_Change_Opener_Name + "_" + str(
                                             khatma_id)),
                ]
                ,
                [
                    InlineKeyboardButton("تعديل مدة الحجز",
                                         callback_data=CallBackData.Khatmas_Change_Duration + "_" + str(
                                             khatma_id)),
                ],
                [InlineKeyboardButton("تحديث 🔄", callback_data=CallBackData.Khatmas_Properties + "_" + str(khatma_id))],
                [InlineKeyboardButton("رجوع", callback_data=CallBackData.Khatmas_Options + "_" + str(khatma_id))]

            ]
        else:
            keyboard = [
                [InlineKeyboardButton("رجوع", callback_data=CallBackData.Khatmas_Options + "_" + str(khatma_id))]]
        return keyboard

    @staticmethod
    async def get_my_khatmas_list_keyboard(khatma_list: List[Khatma], sort_asc=True):
        keyboard = []
        for khatma in khatma_list:
            khatma_no = khatma.id
            intention = get_elided_text_version(text=khatma.description, limit=30)
            time_since_start_in_second = (datetime.utcnow() - khatma.time).total_seconds()
            number_of_finished_parts = await db.count_number_of_finished_parts_of_khatma(khatma_id=khatma.id)
            text = "الرقم: "
            text += str(khatma_no)
            text += " | "
            # text += "النية: "
            text += str(intention)
            text += " | "
            text += "منذ: "
            text += format_timespan_in_arabic(total_time=time_since_start_in_second, max_units=1)
            text += " | "
            # text += "الأجزاء المنتهية: "
            text += f"{number_of_finished_parts}/30"
            temp_keyboard = [
                InlineKeyboardButton(text, callback_data=CallBackData.Khatmas_Options +
                                                         "_" + str(khatma.id))
            ]
            keyboard.append(temp_keyboard)
        if len(keyboard) == 0:
            keyboard.append([InlineKeyboardButton("لا يوجد ختمات", callback_data=CallBackData.Nothing + "_" +
                                                                                 CallBackData.Current_Contribution_Khatmas)])
        if sort_asc:
            keyboard.append([
                InlineKeyboardButton("الأقدم أولاً", callback_data=CallBackData.Current_Contribution_Khatmas + "_0"),
                InlineKeyboardButton("تحديث 🔄", callback_data=CallBackData.Current_Contribution_Khatmas)
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("الأحدث أولاً", callback_data=CallBackData.Current_Contribution_Khatmas + "_1"),
                InlineKeyboardButton("تحديث 🔄", callback_data=CallBackData.Current_Contribution_Khatmas)
            ])
        keyboard.append(
            [InlineKeyboardButton("عودة", callback_data=CallBackData.Main_Menu_Current_Contribution)])
        return keyboard

    @staticmethod
    async def get_khatma_public_list_keyboard(khatma_list: List[Khatma], number_of_all_khatmas, is_asc=True, page_id=0,
                                              page_size=7):
        keyboard = []
        for khatma in khatma_list:
            name_of_opener = khatma.name_of_opener
            intention = get_elided_text_version(text=khatma.description, limit=30)
            time_since_start_in_second = (datetime.utcnow() - khatma.time).total_seconds()
            number_of_finished_parts = await db.count_number_of_finished_parts_of_khatma(khatma_id=khatma.id)
            text = ""
            # text = "الاسم: "
            text += str(name_of_opener)
            text += " | "
            # text += "النية: "
            text += str(intention)
            text += " | "
            # text += "منذ: "
            text += format_timespan_in_arabic(total_time=time_since_start_in_second, max_units=1)
            text += " | "
            # text += "الأجزاء المنتهية: "
            text += f"{number_of_finished_parts}/30"
            temp_keyboard = [
                InlineKeyboardButton(text, callback_data=CallBackData.Contribute_Khatma_Public +
                                                         "_" + str(khatma.id) +
                                                         "_" + str(page_id) +
                                                         "_" + str(page_size) +
                                                         "_" + str(int(is_asc)))
            ]
            keyboard.append(temp_keyboard)
        previous_page_id = max(0, page_id - 1)
        pages_count = (number_of_all_khatmas + page_size - 1) // page_size
        next_page_id = min(pages_count - 1, page_id + 1)
        keyboard.append(
            [InlineKeyboardButton(" << ", callback_data=CallBackData.Contribute_Khatma_Public_Page_Option +
                                                        "_" + "0" +
                                                        "_" + str(page_size) +
                                                        "_" + str(int(is_asc))),
             InlineKeyboardButton(" < ", callback_data=CallBackData.Contribute_Khatma_Public_Page_Option +
                                                       "_" + str(previous_page_id) +
                                                       "_" + str(page_size) +
                                                       "_" + str(int(is_asc))),
             InlineKeyboardButton(str(page_id + 1), callback_data=CallBackData.Nothing),
             InlineKeyboardButton(" > ", callback_data=CallBackData.Contribute_Khatma_Public_Page_Option +
                                                       "_" + str(next_page_id) +
                                                       "_" + str(page_size) +
                                                       "_" + str(int(is_asc))),
             InlineKeyboardButton(" >> ", callback_data=CallBackData.Contribute_Khatma_Public_Page_Option +
                                                        "_" + str(pages_count - 1) +
                                                        "_" + str(page_size) +
                                                        "_" + str(int(is_asc))),
             ])
        if not is_asc:
            keyboard.append([
                InlineKeyboardButton("الأحدث أولاً",
                                     callback_data=CallBackData.Contribute_Khatma_Public_Page_Option +
                                                   "_" + str(page_id) + "_" + str(page_size) + "_" + "1"),
                InlineKeyboardButton("عودة", callback_data=CallBackData.Main_Menu_Contribute_Khatma)
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("الأقدم أولاً",
                                     callback_data=CallBackData.Contribute_Khatma_Public_Page_Option +
                                                   "_" + str(page_id) + "_" + str(page_size) + "_" + "0"),
                InlineKeyboardButton("عودة", callback_data=CallBackData.Main_Menu_Contribute_Khatma)
            ])
        return keyboard

    @staticmethod
    def get_about_bot_keyboard():
        return [
            [InlineKeyboardButton("ورد يومي من القرآن الكريم", url="https://t.me/QuranDailyPage")],
            [InlineKeyboardButton("عودة", callback_data=CallBackData.Main_Menu)]
        ]

    @staticmethod
    def get_back_to_main_menu():
        return [
            [InlineKeyboardButton("عودة", callback_data=CallBackData.Main_Menu)]
        ]

    @staticmethod
    def get_khatma_part_details_keyboard(user_id, part_id):
        return [
            [InlineKeyboardButton("إلغاء الحجز ❌", callback_data=CallBackData.Mark_Part_As_Cancel +
                                                                 "_" + str(part_id) + "_" + str(user_id)),
             InlineKeyboardButton("تمت القراءة ✅", callback_data=CallBackData.Mark_Part_As_Done +
                                                                 "_" + str(part_id) + "_" + str(user_id))]
            ,
            [InlineKeyboardButton("عودة", callback_data=CallBackData.Current_Contribution_Parts)]
        ]

    @staticmethod
    def get_khatma_parts_keyboard(khatma_id, khatma_parts: List[Khatma_Parts], have_refresh_button=True,
                                  have_return_button=False,
                                  return_button_page_id=0,
                                  return_button_page_size=7, return_button_is_asc=False, is_group=False):
        # CallBackData = "KP_#khatma_id_#part_no
        keyboard = []
        for khatma_part_id in range(0, len(khatma_parts) // 3):
            temp_keyboard = [InlineKeyboardButton(part_no_dict[khatma_parts[khatma_part_id + 20].part_no] + " " +
                                                  part_status_color[khatma_parts[khatma_part_id + 20].part_state],
                                                  callback_data=CallBackData.Khatma_Part_ID + "_" + str(
                                                      khatma_id) + "_" + str(
                                                      khatma_parts[khatma_part_id + 20].part_no)),
                             InlineKeyboardButton(part_no_dict[khatma_parts[khatma_part_id + 10].part_no] + " " +
                                                  part_status_color[khatma_parts[khatma_part_id + 10].part_state],
                                                  callback_data=CallBackData.Khatma_Part_ID + "_" + str(
                                                      khatma_id) + "_" + str(
                                                      khatma_parts[khatma_part_id + 10].part_no)),
                             InlineKeyboardButton(part_no_dict[khatma_parts[khatma_part_id].part_no] + " " +
                                                  part_status_color[khatma_parts[khatma_part_id].part_state],
                                                  callback_data=CallBackData.Khatma_Part_ID + "_" + str(
                                                      khatma_id) + "_" + str(khatma_parts[khatma_part_id].part_no))]
            keyboard.append(temp_keyboard)
        if have_return_button:
            if have_refresh_button:
                keyboard.append(
                    [InlineKeyboardButton("تحديث 🔄", callback_data=CallBackData.Khatma_Refresh + "_" + str(khatma_id)
                                                                   + "_" + str(return_button_page_id) +
                                                                   "_" + str(return_button_page_size) +
                                                                   "_" + str(int(return_button_is_asc)))])
            keyboard.append(
                [InlineKeyboardButton("عودة", callback_data=CallBackData.Contribute_Khatma_Public_Page_Option +
                                                            "_" + str(return_button_page_id) +
                                                            "_" + str(return_button_page_size) +
                                                            "_" + str(int(return_button_is_asc)))]
            )
        elif have_refresh_button:
            keyboard.append(
                [InlineKeyboardButton("تحديث 🔄", callback_data=CallBackData.Khatma_Refresh + "_" + str(khatma_id))])
        if is_group:
            keyboard.append(
                [InlineKeyboardButton("تصفح القرآن الكريم 📖", url="https://telegram.me/QuranCompletionBot?start")])
        return keyboard

    @staticmethod
    def get_khatma_parts_from_my_parts_options_keyboard(khatma_id, khatma_parts: List[Khatma_Parts]):
        # CallBackData = "KP_#khatma_id_#part_no
        keyboard = []
        for khatma_part_id in range(0, len(khatma_parts) // 3):
            temp_keyboard = [InlineKeyboardButton(part_no_dict[khatma_parts[khatma_part_id + 20].part_no] + " " +
                                                  part_status_color[khatma_parts[khatma_part_id + 20].part_state],
                                                  callback_data=CallBackData.Khatma_Part_ID + "_" + str(
                                                      khatma_id) + "_" + str(
                                                      khatma_parts[khatma_part_id + 20].part_no)),
                             InlineKeyboardButton(part_no_dict[khatma_parts[khatma_part_id + 10].part_no] + " " +
                                                  part_status_color[khatma_parts[khatma_part_id + 10].part_state],
                                                  callback_data=CallBackData.Khatma_Part_ID + "_" + str(
                                                      khatma_id) + "_" + str(
                                                      khatma_parts[khatma_part_id + 10].part_no)),
                             InlineKeyboardButton(part_no_dict[khatma_parts[khatma_part_id].part_no] + " " +
                                                  part_status_color[khatma_parts[khatma_part_id].part_state],
                                                  callback_data=CallBackData.Khatma_Part_ID + "_" + str(
                                                      khatma_id) + "_" + str(khatma_parts[khatma_part_id].part_no))]
            keyboard.append(temp_keyboard)
        keyboard.append(
            [InlineKeyboardButton("تحديث 🔄",
                                  callback_data=CallBackData.Current_Contribution_Parts_View_Khatma + "_" + str(
                                      khatma_id) + "R")])
        keyboard.append(
            [InlineKeyboardButton("عودة", callback_data=CallBackData.Current_Contribution_Parts)])
        return keyboard

    @staticmethod
    def get_khatma_parts_options_keyboard(khatma_id, khatma_parts: List[Khatma_Parts], is_opened):
        keyboard = []
        if is_opened:
            for khatma_part_id in range(0, len(khatma_parts) // 3):
                temp_keyboard = [InlineKeyboardButton(part_no_dict[khatma_parts[khatma_part_id + 20].part_no] + " " +
                                                      part_status_options_color[
                                                          khatma_parts[khatma_part_id + 20].part_state],
                                                      callback_data=CallBackData.Khatma_Part_Options_ID + "_" + str(
                                                          khatma_id) + "_" + str(
                                                          khatma_parts[khatma_part_id + 20].part_no)),
                                 InlineKeyboardButton(part_no_dict[khatma_parts[khatma_part_id + 10].part_no] + " " +
                                                      part_status_options_color[
                                                          khatma_parts[khatma_part_id + 10].part_state],
                                                      callback_data=CallBackData.Khatma_Part_Options_ID + "_" + str(
                                                          khatma_id) + "_" + str(
                                                          khatma_parts[khatma_part_id + 10].part_no)),
                                 InlineKeyboardButton(part_no_dict[khatma_parts[khatma_part_id].part_no] + " " +
                                                      part_status_options_color[
                                                          khatma_parts[khatma_part_id].part_state],
                                                      callback_data=CallBackData.Khatma_Part_Options_ID + "_" + str(
                                                          khatma_id) + "_" + str(khatma_parts[khatma_part_id].part_no))]
                keyboard.append(temp_keyboard)

            keyboard.append(
                [InlineKeyboardButton("تحديث 🔄", callback_data=CallBackData.Khatmas_Parts_Manage + "_" + str(
                    khatma_id))]
            )
        keyboard.append(
            [InlineKeyboardButton("رجوع", callback_data=CallBackData.Khatmas_Options + "_" + str(khatma_id))]
        )
        return keyboard

    @staticmethod
    def get_khatma_part_options_opened_keyboard(khatma_id, part_no):
        keyboard = [[InlineKeyboardButton("حجز هذا الجزء 📘",
                                          callback_data=CallBackData.Mark_Part_As_Occupied_By_Admin + "_" + str(
                                              khatma_id) + "_" + str(part_no))],
                    [InlineKeyboardButton("رجوع", callback_data=CallBackData.Khatmas_Parts_Manage + "_" + str(
                        khatma_id))]]
        return keyboard

    @staticmethod
    def get_khatma_part_options_done_keyboard(khatma_id, part_no):
        keyboard = [[InlineKeyboardButton("إلغاء قراءة الجزء ❌",
                                          callback_data=CallBackData.Mark_Part_As_Cancel_Read_By_Admin + "_" + str(
                                              khatma_id) + "_" + str(part_no))],
                    [InlineKeyboardButton("رجوع", callback_data=CallBackData.Khatmas_Parts_Manage + "_" + str(
                        khatma_id))]]
        return keyboard

    @staticmethod
    def get_khatma_part_options_occupied_keyboard(khatma_id, part_no):
        keyboard = [[InlineKeyboardButton("إلغاء الحجز ❌",
                                          callback_data=CallBackData.Mark_Part_As_Cancel_Occupy_By_Admin + "_" + str(
                                              khatma_id) + "_" + str(part_no))
                        , InlineKeyboardButton("تمت القراءة ✅",
                                               callback_data=CallBackData.Mark_Part_As_Done_By_Admin + "_" + str(
                                                   khatma_id) + "_" + str(part_no))],
                    [InlineKeyboardButton("رجوع", callback_data=CallBackData.Khatmas_Parts_Manage + "_" + str(
                        khatma_id))]]
        return keyboard
