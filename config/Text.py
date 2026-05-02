from datetime import datetime
from html import escape
from typing import List, Optional

from telegram.helpers import mention_html

from domain.PartData import PartData
from domain.TelegramUser import TelegramUser
from bot.Global_Functions import format_timespan_in_arabic, escape_markdown_v2, get_text_copyable, \
    get_local_date_from_utc_time, QURAN_BOOK_ID

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


class Text:
    @staticmethod
    def create_finish_khatma_pray(with_escape: bool = False) -> str:
        text = ""
        if with_escape:
            text += escape_markdown_v2("💚 اللهم ارحمنى بالقرآن وأجعله لى إماماً ونوراً وهدًى ورحمة.")
            text += "\n\n"
            text += escape_markdown_v2(
                "💙 اللهم ذكرنى منه مانسيت وعلمنى منه ماجهلت وارزقني تلاوته آناء الليل وأطراف النهار واجعله لي حجة يارب العالمين.")
            text += "\n\n"
            text += escape_markdown_v2(
                "🤍 اللهم أصلح لى دينى الذي هو عصمة أمري، وأصلح لي دنياي التي فيها معاشي، وأصلح لي آخرتي التي فيها معادي، وأجعل الحياة زيادة لي في كل خير وأجعل الموت راحة لي من كل شر.")
            text += "\n\n"
            text += escape_markdown_v2("❤️ اللهم أجعل خير عمري آخره وخير عملي خواتمه وخير أيامي يوم ألقاك فيه.")
            text += "\n\n"
            text += escape_markdown_v2("💚 اللهم إني أسألك عيشة هنية وميتة سوية ومردا غير مخز ولا فاضح.")
            text += "\n\n"
            text += escape_markdown_v2(
                "💙 اللهم إنى أسألك خير المسألة وخير الدعاء وخير النجاح وخير العلم وخير العمل وخير الثواب وخير الحياة وخير الممات وثبتنى وثقل موازيني وحقق إيماني وارفع درجتي وتقبل صلاتي واغفر خطيئاتي وأسألك العلا من الجنة.")
            text += "\n\n"
            text += escape_markdown_v2(
                "💛 اللهم أقسم لنا من خشيتك ما تحول به بيننا وبين معصيتك ومن طاعتك ما تبلغنا بها جنتك ومن اليقين ما تهون به علينا مصائب الدنيا ومتعنا بأسماعنا وأبصارنا وقوتنا ما أحييتنا واجعله الوارث منا واجعل ثأرنا على من ظلمنا وانصرنا على من عادانا ولا تجعل مصيبتنا في ديننا ولا تجعل الدنيا أكبر همنا ولا مبلغ علمنا ولا تسلط علينا من لا يرحمنا.")
        else:
            text += "💚 اللهم ارحمنى بالقرآن وأجعله لى إماماً ونوراً وهدًى ورحمة."
            text += "\n\n"
            text += "💙 اللهم ذكرنى منه مانسيت وعلمنى منه ماجهلت وارزقني تلاوته آناء الليل وأطراف النهار واجعله لي حجة يارب العالمين."
            text += "\n\n"
            text += "🤍 اللهم أصلح لى دينى الذي هو عصمة أمري، وأصلح لي دنياي التي فيها معاشي، وأصلح لي آخرتي التي فيها معادي، وأجعل الحياة زيادة لي في كل خير وأجعل الموت راحة لي من كل شر."
            text += "\n\n"
            text += "❤️ اللهم أجعل خير عمري آخره وخير عملي خواتمه وخير أيامي يوم ألقاك فيه."
            text += "\n\n"
            text += "💚 اللهم إني أسألك عيشة هنية وميتة سوية ومردا غير مخز ولا فاضح."
            text += "\n\n"
            text += "💙 اللهم إنى أسألك خير المسألة وخير الدعاء وخير النجاح وخير العلم وخير العمل وخير الثواب وخير الحياة وخير الممات وثبتنى وثقل موازيني وحقق إيماني وارفع درجتي وتقبل صلاتي واغفر خطيئاتي وأسألك العلا من الجنة."
            text += "\n\n"
            text += "💛 اللهم أقسم لنا من خشيتك ما تحول به بيننا وبين معصيتك ومن طاعتك ما تبلغنا بها جنتك ومن اليقين ما تهون به علينا مصائب الدنيا ومتعنا بأسماعنا وأبصارنا وقوتنا ما أحييتنا واجعله الوارث منا واجعل ثأرنا على من ظلمنا وانصرنا على من عادانا ولا تجعل مصيبتنا في ديننا ولا تجعل الدنيا أكبر همنا ولا مبلغ علمنا ولا تسلط علينا من لا يرحمنا."
        return text

    @staticmethod
    def create_new_khatma_info_nothing() -> str:
        text = ""
        text += "*__"
        text += escape_markdown_v2("ختمة جديدة:")
        text += "__*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة: 👤")
        text += ""
        text += "\n"
        text += escape_markdown_v2("النية: 🤲🏻")
        text += ""
        text += "\n"
        text += escape_markdown_v2("المدة المتاحة لإنهاء جزء ما: ⌛️")
        text += ""
        return text

    @staticmethod
    def create_new_khatma_info_with_name(name: str) -> str:
        text = ""
        text += "*__"
        text += escape_markdown_v2("ختمة جديدة:")
        text += "__*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة: ")
        text += escape_markdown_v2(name)
        text += escape_markdown_v2(" 👤")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("النية: 🤲🏻")
        text += ""
        text += "\n"
        text += escape_markdown_v2("المدة المتاحة لإنهاء جزء ما: ⌛️")
        text += ""
        return text

    @staticmethod
    def create_new_khatma_info_with_name_and_intention(name: str, intention: str) -> str:
        text = ""
        text += "*__"
        text += escape_markdown_v2("ختمة جديدة:")
        text += "__*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة: ")
        text += escape_markdown_v2(str(name))
        text += escape_markdown_v2(" 👤")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("النية: ")
        text += escape_markdown_v2(str(intention))
        text += escape_markdown_v2(" 🤲🏻")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("المدة المتاحة لإنهاء جزء ما: ⌛️")
        text += ""
        return text

    @staticmethod
    def create_new_khatma_info_with_name_and_intention_and_duration(name: str, intention: str, duration_in_days: int) -> str:
        text = ""
        text += "*__"
        text += escape_markdown_v2("ختمة جديدة:")
        text += "__*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة: ")
        text += escape_markdown_v2(str(name))
        text += escape_markdown_v2(" 👤")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("النية: ")
        text += escape_markdown_v2(str(intention))
        text += escape_markdown_v2(" 🤲🏻")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("المدة المتاحة لإنهاء جزء ما: ")
        text += escape_markdown_v2(str(duration_in_days))
        if 3 <= duration_in_days <= 10:
            text += escape_markdown_v2(" أيام")
        else:
            text += escape_markdown_v2(" يوم")
        text += " "
        text += escape_markdown_v2("⌛️")
        text += escape_markdown_v2(".")
        return text

    @staticmethod
    def create_new_khatma_info_with_all(name: str, intention: str, duration_in_days: int) -> str:
        text = ""
        text += "*__"
        text += escape_markdown_v2("ختمة جديدة:")
        text += "__*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة: ")
        text += escape_markdown_v2(str(name))
        text += escape_markdown_v2(" 👤")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("النية: ")
        text += escape_markdown_v2(str(intention))
        text += escape_markdown_v2(" 🤲🏻")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("المدة المتاحة لإنهاء جزء ما: ")
        text += str(duration_in_days)
        if 3 <= duration_in_days <= 10:
            text += escape_markdown_v2(" أيام")
        else:
            text += escape_markdown_v2(" يوم")
        text += " "
        text += escape_markdown_v2("⌛️")
        text += escape_markdown_v2(".")
        text += "\n"
        return text

    @staticmethod
    def create_khatma_info_in_options(khatma_id: int, name: str, intention: str, duration_in_days: int, start_date: Optional[datetime] = None) -> str:
        text = escape_markdown_v2("")
        text += " \n"
        text += escape_markdown_v2("رقم الختمة: ")
        text += "*"
        text += get_text_copyable(str(khatma_id))
        text += "*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة: ")
        text += escape_markdown_v2(str(name))
        text += escape_markdown_v2(" 👤")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("النية: ")
        text += escape_markdown_v2(str(intention))
        text += escape_markdown_v2(" 🤲🏻")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("المدة المتاحة لإنهاء جزء ما: ")
        text += str(duration_in_days)
        if 3 <= duration_in_days <= 10:
            text += escape_markdown_v2(" أيام")
        else:
            text += escape_markdown_v2(" يوم")
        text += " "
        text += escape_markdown_v2("⌛️")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("حالة الختمة: ")
        text += escape_markdown_v2("مستمرة.")
        text += "\n"
        text += escape_markdown_v2("بدأت بتاريخ: ")
        text += escape_markdown_v2(get_local_date_from_utc_time(start_date))
        text += "\n"
        text += escape_markdown_v2("يمكنك التعديل على الختمة باستعمال الأزرار التالية: ")
        return text

    @staticmethod
    def create_khatma_info_in_properties_options(khatma_id: int, name: str, intention: str, duration_in_days: int, start_date: Optional[datetime] = None) -> str:
        text = escape_markdown_v2("")
        text += " \n"
        text += escape_markdown_v2("رقم الختمة: ")
        text += "*"
        text += get_text_copyable(str(khatma_id))
        text += "*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة: ")
        text += escape_markdown_v2(str(name))
        text += escape_markdown_v2(" 👤")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("النية: ")
        text += escape_markdown_v2(str(intention))
        text += escape_markdown_v2(" 🤲🏻")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("المدة المتاحة لإنهاء جزء ما: ")
        text += str(duration_in_days)
        if 3 <= duration_in_days <= 10:
            text += escape_markdown_v2(" أيام")
        else:
            text += escape_markdown_v2(" يوم")
        text += " "
        text += escape_markdown_v2("⌛️")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("حالة الختمة: ")
        text += escape_markdown_v2("مستمرة.")
        text += "\n"
        text += escape_markdown_v2("بدأت بتاريخ: ")
        text += escape_markdown_v2(get_local_date_from_utc_time(start_date))
        text += "\n"
        text += escape_markdown_v2("يمكنك التعديل على الخصائص التالية: ")
        return text

    @staticmethod
    def create_khatma_info_in_cancel_khatma_confirmation(khatma_id: int, name: str, intention: str, duration_in_days: int,
                                                         start_date: Optional[datetime] = None) -> str:
        text = escape_markdown_v2("")
        text += " \n"
        text += escape_markdown_v2("رقم الختمة: ")
        text += "*"
        text += get_text_copyable(str(khatma_id))
        text += "*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة: ")
        text += escape_markdown_v2(str(name))
        text += escape_markdown_v2(" 👤")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("النية: ")
        text += escape_markdown_v2(str(intention))
        text += escape_markdown_v2(" 🤲🏻")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("المدة المتاحة لإنهاء جزء ما: ")
        text += str(duration_in_days)
        if 3 <= duration_in_days <= 10:
            text += escape_markdown_v2(" أيام")
        else:
            text += escape_markdown_v2(" يوم")
        text += " "
        text += escape_markdown_v2("⌛️")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("حالة الختمة: ")
        text += escape_markdown_v2("مستمرة.")
        text += "\n"
        text += escape_markdown_v2("بدأت بتاريخ: ")
        text += escape_markdown_v2(get_local_date_from_utc_time(start_date))
        text += "\n"
        text += "*"
        text += escape_markdown_v2("هل أنت متأكد من إلغاء هذه الختمة؟")
        text += "*"
        return text

    @staticmethod
    def create_khatma_info_in_read_khatma_confirmation(khatma_id: int, name: str, intention: str, duration_in_days: int,
                                                       start_date: Optional[datetime] = None) -> str:
        text = escape_markdown_v2("")
        text += " \n"
        text += escape_markdown_v2("رقم الختمة: ")
        text += "*"
        text += get_text_copyable(str(khatma_id))
        text += "*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة: ")
        text += escape_markdown_v2(str(name))
        text += escape_markdown_v2(" 👤")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("النية: ")
        text += escape_markdown_v2(str(intention))
        text += escape_markdown_v2(" 🤲🏻")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("المدة المتاحة لإنهاء جزء ما: ")
        text += str(duration_in_days)
        if 3 <= duration_in_days <= 10:
            text += escape_markdown_v2(" أيام")
        else:
            text += escape_markdown_v2(" يوم")
        text += " "
        text += escape_markdown_v2("⌛️")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("حالة الختمة: ")
        text += escape_markdown_v2("مستمرة.")
        text += "\n"
        text += escape_markdown_v2("بدأت بتاريخ: ")
        text += escape_markdown_v2(get_local_date_from_utc_time(start_date))
        text += "\n"
        text += "*"
        text += escape_markdown_v2("هل تؤكّد قراءة هذه الختمة كاملةً؟")
        text += "*"
        return text

    @staticmethod
    def create_khatma_info_parts_options(khatma_id: int, name: str, intention: str, duration_in_days: int, start_date: Optional[datetime] = None) -> str:
        text = escape_markdown_v2("")
        text += " \n"
        text += escape_markdown_v2("رقم الختمة: ")
        text += "*"
        text += get_text_copyable(str(khatma_id))
        text += "*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة: ")
        text += escape_markdown_v2(str(name))
        text += escape_markdown_v2(" 👤")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("النية: ")
        text += escape_markdown_v2(str(intention))
        text += escape_markdown_v2(" 🤲🏻")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("المدة المتاحة لإنهاء جزء ما: ")
        text += str(duration_in_days)
        if 3 <= duration_in_days <= 10:
            text += escape_markdown_v2(" أيام")
        else:
            text += escape_markdown_v2(" يوم")
        text += " "
        text += escape_markdown_v2("⌛️")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("حالة الختمة: ")
        text += escape_markdown_v2("مستمرة.")
        text += "\n"
        text += escape_markdown_v2("بدأت بتاريخ: ")
        text += escape_markdown_v2(get_local_date_from_utc_time(start_date))
        text += "\n"
        text += escape_markdown_v2("حالة الأجزاء:")
        text += "\n"
        text += escape_markdown_v2("📕 :غير محجوز بعد.")
        text += "\n"
        text += escape_markdown_v2("📖 :محجوز.")
        text += "\n"
        text += escape_markdown_v2("✅ :تمت قراءته.")
        text += "\n"
        text += escape_markdown_v2("يمكنك الضغط على الجزء الذي تود التعديل عليه من ضمن الأجزاء التالية:")
        return text

    @staticmethod
    def create_khatma_info(khatma_id: int, name: str, intention: str, duration_in_days: int,
                           start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                           is_finished: bool = False,
                           is_canceled: bool = False) -> str:
        text = escape_markdown_v2("")
        text += " \n"
        text += escape_markdown_v2("رقم الختمة: ")
        text += "*"
        text += get_text_copyable(str(khatma_id))
        text += "*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة: ")
        text += escape_markdown_v2(str(name))
        text += escape_markdown_v2(" 👤")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("النية: ")
        text += escape_markdown_v2(str(intention))
        text += escape_markdown_v2(" 🤲🏻")
        text += escape_markdown_v2(".")
        text += "\n"
        if not is_finished and not is_canceled:
            text += escape_markdown_v2("المدة المتاحة لإنهاء جزء ما: ")
            text += str(duration_in_days)
            if 3 <= duration_in_days <= 10:
                text += escape_markdown_v2(" أيام")
            else:
                text += escape_markdown_v2(" يوم")
            text += " "
            text += escape_markdown_v2("⌛️")
            text += escape_markdown_v2(".")
            text += "\n"
            text += escape_markdown_v2("حالة الختمة: ")
            text += escape_markdown_v2("مستمرة.")
            text += "\n"
            text += escape_markdown_v2("بدأت بتاريخ: ")
            text += escape_markdown_v2(get_local_date_from_utc_time(start_date))
            text += "\n"
            text += escape_markdown_v2("حالة الأجزاء:")
            text += "\n"
            text += escape_markdown_v2("⚪️ :هذا الجزء متاح و لم يحجز بعد.")
            text += "\n"
            text += escape_markdown_v2("🔵 :هذا الجزء محجوز حاليا.")
            text += "\n"
            text += escape_markdown_v2("🟢 :تمت قراءة هذا الجزء.")
            text += "\n"
            text += "*"
            text += escape_markdown_v2("📘 لحجز جزء معين يمكنك ببساطة النقر عليه.")
            text += "*"
            text += "\n"
            text += escape_markdown_v2("💠 عند انتهائك من قراءة الجزء الذي حجزته تستطيع ببساطة النقر عليه مجدداً لكي "
                                       "يرى الآخرون مدى التقدم في هذه الختمة.")
            text += "\n"
        elif is_finished:
            text += escape_markdown_v2("حالة الختمة: ")
            text += escape_markdown_v2("منتهية ✅.")
            text += "\n"
            text += escape_markdown_v2("بدأت بتاريخ: ")
            text += escape_markdown_v2(get_local_date_from_utc_time(start_date))
            text += "\n"
            text += escape_markdown_v2("انتهت بتاريخ: ")
            text += escape_markdown_v2(get_local_date_from_utc_time(end_date))
            text += "\n"
            text += escape_markdown_v2("استغرقت: ")
            total_time_in_seconds = (end_date - start_date).total_seconds()
            text += escape_markdown_v2(format_timespan_in_arabic(total_time=total_time_in_seconds, max_units=2))
            text += escape_markdown_v2(".")
            text += "\n"
            text += escape_markdown_v2("بعض من الأدعية المأثورة: ")
            text += "\n"
            text += Text.create_finish_khatma_pray(with_escape=True)
            text += "\n"
        elif is_canceled:
            text += escape_markdown_v2("حالة الختمة: ")
            text += escape_markdown_v2("ملغية ❌.")
            text += "\n"
            text += escape_markdown_v2("بدأت بتاريخ: ")
            text += escape_markdown_v2(get_local_date_from_utc_time(start_date))
            text += "\n"
            text += escape_markdown_v2("أُلغيت بتاريخ: ")
            text += escape_markdown_v2(get_local_date_from_utc_time(end_date))
        # text += escape_markdown_v2("　")
        return text

    @staticmethod
    def create_khatma_info_on_creation(khatma_id: int, name: str, intention: str, duration_in_days: int, start_date: Optional[datetime] = None) -> str:
        group_link = f"https://telegram.me/QuranCompletionBot?startgroup=khatma_id_{khatma_id}"
        text = escape_markdown_v2("")
        text += " \n"
        text += escape_markdown_v2("رقم الختمة: ")
        text += "*"
        text += get_text_copyable(str(khatma_id))
        text += "*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة: ")
        text += escape_markdown_v2(str(name))
        text += escape_markdown_v2(" 👤")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("النية: ")
        text += escape_markdown_v2(str(intention))
        text += escape_markdown_v2(" 🤲🏻")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("المدة المتاحة لإنهاء جزء ما: ")
        text += str(duration_in_days)
        if 3 <= duration_in_days <= 10:
            text += escape_markdown_v2(" أيام")
        else:
            text += escape_markdown_v2(" يوم")
        text += " "
        text += escape_markdown_v2("⌛️")
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("حالة الختمة: ")
        text += escape_markdown_v2("مستمرة.")
        text += "\n"
        text += escape_markdown_v2("بدأت بتاريخ: ")
        text += escape_markdown_v2(get_local_date_from_utc_time(start_date))
        text += "\n"
        text += escape_markdown_v2("حالة الأجزاء:")
        text += "\n"
        text += escape_markdown_v2("⚪️ :هذا الجزء متاح و لم يحجز بعد.")
        text += "\n"
        text += escape_markdown_v2("🔵 :هذا الجزء محجوز حاليا.")
        text += "\n"
        text += escape_markdown_v2("🟢 :تمت قراءة هذا الجزء.")
        text += "\n"
        text += "*"
        text += escape_markdown_v2("📘 لحجز جزء معين يمكنك ببساطة النقر عليه.")
        text += "*"
        text += "\n"
        text += escape_markdown_v2("💠 عند انتهائك من قراءة الجزء الذي حجزته تستطيع ببساطة النقر عليه مجدداً لكي "
                                   "يرى الآخرون مدى التقدم في هذه الختمة.")
        text += escape_markdown_v2("　")
        text += "\n"
        text += escape_markdown_v2("لمشاركة الختمة في مجموعة يرجى الضغط على الزر التالي: ")
        text += f"[*اضغط هنا*]({group_link})"
        return text

    @staticmethod
    def create_khatma_part_booked_data(name: str, time_since_start_in_second: float) -> str:
        text = "هذه الختمة محجوز من قبل: "
        text += str(name)
        text += "\n"
        text += "منذ: "
        text += format_timespan_in_arabic(total_time=time_since_start_in_second, max_units=2)
        return text

    @staticmethod
    def create_khatma_part_details_text(khatma_id: int, name: str, intention: str, part_no: int,
                                        booked_since_total_time: float, deadline_total_time: float) -> str:
        text = ""
        text += "\n"
        text += "رقم الختمة: "
        text += str(khatma_id)
        text += "\n"
        text += "منشئ الختمة: "
        text += str(name)
        text += "\n"
        text += "النية: "
        text += str(intention)
        text += "\n"
        text += "الجزء: "
        text += part_no_dict_in_details[part_no]
        text += "\n"
        text += "لقد حجزته منذ: "
        text += str(format_timespan_in_arabic(total_time=booked_since_total_time, max_units=2))
        text += "\n"
        text += "المدة المتبقية: "
        text += str(format_timespan_in_arabic(total_time=deadline_total_time, max_units=2))
        text += " ⏳."
        text += "\n"
        text += "🔷 في حال انتهاء الوقت ولم تقم بإنهاء القراءة سيُلغى الحجز تلقائياً."
        text += "\n"
        return text

    @staticmethod
    def create_khatma_part_options_text_opened(khatma_id: int, name: str, intention: str, part_no: int) -> str:
        text = ""
        text += "رقم الختمة: "
        text += str(khatma_id)
        text += "\n"
        text += "منشئ الختمة: "
        text += str(name)
        text += "\n"
        text += "النية: "
        text += str(intention)
        text += "\n"
        text += "الجزء: "
        text += "<b>"
        text += part_no_dict_in_details[part_no]
        text += "</b>"
        text += "\n"
        text += "<b>"
        text += "📕 هذا الجزء غير محجوز حالياً"
        text += "</b>"
        return text

    @staticmethod
    def create_khatma_part_options_text_occupied(khatma_id: int, name: str, intention: str, part_no: int,
                                                 booked_user_id: int, booked_user_fullname: str,
                                                 booked_since_total_time: float, deadline_total_time: float) -> str:
        text = ""
        text += "رقم الختمة: "
        text += str(khatma_id)
        text += "\n"
        text += "منشئ الختمة: "
        text += str(name)
        text += "\n"
        text += "النية: "
        text += str(intention)
        text += "\n"
        text += "الجزء: "
        text += "<b>"
        text += part_no_dict_in_details[part_no]
        text += "</b>"
        text += "\n"
        text += "محجوز بإسم: "
        text += mention_html(user_id=booked_user_id, name=booked_user_fullname)
        text += "\n"
        text += "حجزه منذ: "
        text += str(format_timespan_in_arabic(total_time=booked_since_total_time, max_units=2))
        text += "\n"
        text += "بقي له من الوقت: "
        text += str(format_timespan_in_arabic(total_time=deadline_total_time, max_units=2))
        text += " ⏳."
        return text

    @staticmethod
    def create_khatma_part_options_text_done(khatma_id: int, name: str, intention: str, part_no: int,
                                             booked_user_id: int, booked_user_fullname: str,
                                             ended_since_total_time: float) -> str:
        text = ""
        text += "رقم الختمة: "
        text += str(khatma_id)
        text += "\n"
        text += "منشئ الختمة: "
        text += str(name)
        text += "\n"
        text += "النية: "
        text += str(intention)
        text += "\n"
        text += "الجزء: "
        text += "<b>"
        text += part_no_dict_in_details[part_no]
        text += "</b>"
        text += "\n"
        text += "<b>"
        text += "تمت قرائته ✅"
        text += "</b>"
        text += "\n"
        text += "من قبل: "
        text += mention_html(user_id=booked_user_id, name=booked_user_fullname)
        text += "\n"
        text += "وذلك منذ: "
        text += str(format_timespan_in_arabic(total_time=ended_since_total_time, max_units=2))
        text += "\n"
        return text

    @staticmethod
    def create_reached_limit_of_booked_parts() -> str:
        text = "عذراً لا يمكن حجز أكثر من "
        text += "4"
        text += " أجزاء في نفس الوقت."
        return text

    @staticmethod
    def create_reached_limit_of_opened_khatmas() -> str:
        text = "عذراً لا يمكن إنشاء أكثر من "
        text += "5"
        text += " ختمات في نفس الوقت."
        return text

    @staticmethod
    def create_public_khatma_explain_text() -> str:
        text = "قم باختيار إحدى الختمات التالية للمشاركة بها\:"
        text += "\n"
        text += "*"
        text += "يتم عرض الختمات على الشكل\:  \[الاسم \| النية \| تاريخ الإنشاء \| الأجزاء المنتهية\]"
        text += "*"
        return text

    @staticmethod
    def create_current_contribution_parts_explain_text() -> str:
        text = "قم باختيار إحدى الأجزاء التالية\:"
        text += "\n"
        text += "يتم عرض الختمات على الشكل\:"
        text += "*"
        text += "  \[الاسم \| النية \| الأجزاء المنتهية\]"
        text += "*"
        text += "\n"
        text += escape_markdown_v2("يليها الأجزاء المحجوزة من قبلك 😄.")
        return text

    @staticmethod
    def create_my_khatmas_explain_text() -> str:
        text = "قم باختيار إحدى الختمات التالية لإدارتها\:"
        text += "\n"
        text += "*"
        text += "يتم عرض الختمات على الشكل\:  \[الرقم \|النية \| تاريخ الإنشاء \| الأجزاء المنتهية\]"
        text += "*"
        return text

    @staticmethod
    def create_finished_khatma_text_for_user(done_parts: List[PartData], is_message_to_admin: bool = False) -> str:
        text = ""
        text += " \n"
        text += escape_markdown_v2("رقم الختمة: ")
        text += "*"
        text += get_text_copyable(str(done_parts[0].khatma_id))
        text += "*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة 👤: ")
        text += escape_markdown_v2(str(done_parts[0].khatma_opener_name))
        text += "\n"
        text += escape_markdown_v2("النية 🤲🏻: ")
        text += escape_markdown_v2(str(done_parts[0].khatma_intention))
        text += "\n"
        text += "*"
        text += escape_markdown_v2("✅تم إنهاء الختمة✅")
        text += "*"
        if not is_message_to_admin:
            text += "\n"
            text += escape_markdown_v2("جزاك الله خيراً في (إنهائك/مشاركتك في قراءة) الأجزاء التالية:")
            text += "\n"
            for done_part_id in range(len(done_parts)):
                text += "*"
                text += escape_markdown_v2(str(done_part_id + 1))
                text += escape_markdown_v2("-")
                text += " "
                text += escape_markdown_v2(part_no_dict_in_details[done_parts[done_part_id].part_no])
                text += "*"
                if done_part_id + 1 < len(done_parts):
                    text += "\n"
        text += "\n"
        text += escape_markdown_v2("بعض من الأدعية المأثورة: ")
        text += "\n"
        text += Text.create_finish_khatma_pray(with_escape=True)
        text += "\n"
        text += escape_markdown_v2("　")
        return text

    @staticmethod
    def create_canceled_khatma_text_for_user(done_parts: List[PartData], is_message_to_admin: bool = False) -> str:
        text = escape_markdown_v2("")
        text += " \n"
        text += escape_markdown_v2("رقم الختمة: ")
        text += "*"
        text += get_text_copyable(str(done_parts[0].khatma_id))
        text += "*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة 👤: ")
        text += escape_markdown_v2(str(done_parts[0].khatma_opener_name))
        text += "\n"
        text += escape_markdown_v2("النية 🤲🏻: ")
        text += escape_markdown_v2(str(done_parts[0].khatma_intention))
        text += "\n"
        if not is_message_to_admin:
            text += "*"
            text += escape_markdown_v2("لقد تم إلغاء الختمة من قبل صاحبها ❌")
            text += "*"
            text += "\n"
            text += escape_markdown_v2("جزاك الله خيراً في (إنهائك/مشاركتك في قراءة) الأجزاء التالية:")
            text += "\n"
            for done_part_id in range(len(done_parts)):
                text += "*"
                text += escape_markdown_v2(str(done_part_id + 1))
                text += escape_markdown_v2("-")
                text += " "
                text += "الجزء "
                text += escape_markdown_v2(part_no_dict_in_details[done_parts[done_part_id].part_no])
                text += "*"
                if done_part_id + 1 < len(done_parts):
                    text += "\n"
        else:
            text += "*"
            text += escape_markdown_v2("لقد تم إلغاء الختمة من قبلك ❌")
            text += "*"
        text += "\n"
        text += escape_markdown_v2("جزاكم الله خيراً جميعاً")
        text += "\n"
        text += escape_markdown_v2("💚 اللهم ارحمنا بالقرآن وأجعله لنا إماماً ونوراً وهدًى ورحمة 💚")
        text += "\n"
        text += escape_markdown_v2("　")
        return text

    @staticmethod
    def create_canceled_khatma_text_for_user_due_to_expired(done_parts: List[PartData]) -> str:
        text = escape_markdown_v2("")
        text += " \n"
        text += escape_markdown_v2("رقم الختمة: ")
        text += "*"
        text += get_text_copyable(str(done_parts[0].khatma_id))
        text += "*"
        text += "\n"
        text += escape_markdown_v2("منشئ الختمة 👤: ")
        text += escape_markdown_v2(str(done_parts[0].khatma_opener_name))
        text += "\n"
        text += escape_markdown_v2("النية 🤲🏻: ")
        text += escape_markdown_v2(str(done_parts[0].khatma_intention))
        text += "\n"
        text += "*"
        text += escape_markdown_v2("لقد تم إلغاء الختمة بسبب التقاعس عن القراءة لمدة طويلة (210 يوماً) ❌")
        text += "*"
        text += "\n"
        text += escape_markdown_v2("جزاك الله خيراً في (إنهائك/مشاركتك في قراءة) الأجزاء التالية:")
        text += "\n"
        for done_part_id in range(len(done_parts)):
            text += "*"
            text += escape_markdown_v2(str(done_part_id + 1))
            text += escape_markdown_v2("-")
            text += " "
            text += "الجزء "
            text += escape_markdown_v2(part_no_dict_in_details[done_parts[done_part_id].part_no])
            text += "*"
            if done_part_id + 1 < len(done_parts):
                text += "\n"
        text += "\n"
        text += escape_markdown_v2("جزاكم الله خيراً جميعاً")
        text += "\n"
        text += escape_markdown_v2("💚 اللهم ارحمنا بالقرآن وأجعله لنا إماماً ونوراً وهدًى ورحمة 💚")
        text += "\n"
        text += escape_markdown_v2("　")
        return text

    @staticmethod
    def create_expired_khatma_part_text(khatma_id: int, part_no: int, khatma_opener_name: str, khatma_intention: str, khatma_part_duration: int) -> str:
        text = "*__"
        text += "للأسف تم إلغاء حجز الجزء "
        text += escape_markdown_v2(part_no_dict_in_details[part_no])
        text += escape_markdown_v2(" 😔")
        text += "__*"
        text += "\n"
        text += "من الختمة رقم "
        text += escape_markdown_v2("(")
        text += str(khatma_id)
        text += escape_markdown_v2(")")
        text += " والتي هي بإسم: "
        text += escape_markdown_v2(khatma_opener_name)
        text += "\nبنيّة: "
        text += escape_markdown_v2(khatma_intention)
        text += "\n"
        text += escape_markdown_v2("وذلك بسبب انتهاء المدة (")
        text += str(khatma_part_duration)
        text += escape_markdown_v2(")")
        if 3 <= khatma_part_duration <= 10:
            text += escape_markdown_v2(" أيام.")
        else:
            text += escape_markdown_v2(" يوم.")
        return text

    @staticmethod
    def create_notification_khatma_part_text(khatma_id: int, part_no: int, khatma_opener_name: str, khatma_intention: str, remain_time: float) -> str:
        text = "*__"
        text += "تذكير "
        text += escape_markdown_v2("⏰:")
        text += "__*"
        text += "\n"
        text += "بقي لك من الوقت: "
        text += str(format_timespan_in_arabic(total_time=remain_time, max_units=2))
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("لكي تنهي قراءة الجزء ")
        text += escape_markdown_v2(part_no_dict_in_details[part_no])
        text += escape_markdown_v2(".")
        text += "\n"
        text += escape_markdown_v2("من الختمة ذات الرقم ")
        text += "*"
        text += get_text_copyable(str(khatma_id))
        text += "*"
        text += "\n"
        text += escape_markdown_v2("والتي هي بإسم: ")
        text += escape_markdown_v2(khatma_opener_name)
        text += "\nبنيّة: "
        text += escape_markdown_v2(khatma_intention)
        text += "\n"
        text += escape_markdown_v2("وجزاكم الله عنا كل خير.")
        return text

    @staticmethod
    def create_cancel_khatma_part_by_admin_text(khatma_id: int, khatma_opener_name: str, part_no: int) -> str:
        text = ""
        text += "لقد تم إلغاء حجزك للجزء "
        text += part_no_dict_in_details[part_no]
        text += "\n"
        text += "من الختمة التي رقمها: "
        text += str(khatma_id)
        text += "\n"
        text += "من قبل صاحبها: "
        text += str(khatma_opener_name)
        return text

    @staticmethod
    def create_done_khatma_part_by_admin_text(khatma_id: int, khatma_opener_name: str, part_no: int) -> str:
        text = ""
        text += "لقد تم تسجيل قراءتك للجزء "
        text += part_no_dict_in_details[part_no]
        text += " "
        text += "✅"
        text += "\n"
        text += "من الختمة التي رقمها: "
        text += str(khatma_id)
        text += "\n"
        text += "من قبل صاحبها: "
        text += str(khatma_opener_name)
        text += "\n"
        text += "جزاكم الله خيراً"
        return text

    @staticmethod
    def create_cancel_read_khatma_part_by_admin_text(khatma_id: int, khatma_opener_name: str, part_no: int) -> str:
        text = ""
        text += "لقد تم إلغاء تسجيل قراءتك للجزء "
        text += part_no_dict_in_details[part_no]
        text += "\n"
        text += "من الختمة التي رقمها: "
        text += str(khatma_id)
        text += "\n"
        text += "من قبل صاحبها: "
        text += str(khatma_opener_name)
        return text

    @staticmethod
    def get_quran_page_description_by_chapter(book_id: int, chapter_no: int, total_pages: int, current_page: int) -> str:
        book_id = int(book_id)
        text = ""
        text += f"الصفحة الـ({current_page})"
        text += " من أصل "
        text += str(total_pages)
        text += " صفحة"
        text += "\nمن الجزء "
        text += part_no_dict_in_details[chapter_no][:part_no_dict_in_details[chapter_no].rindex(" ")]
        text += "\n"
        if book_id == QURAN_BOOK_ID.Hafs.value:
            text += "📖 المصحف برواية حفص عن عاصم."
        elif book_id == QURAN_BOOK_ID.Hafs_with_tajwid.value:
            text += "📖 مصحف التجويد برواية حفص عن عاصم."
        return text

    @staticmethod
    def get_quran_chapter_file_description(book_id: int, chapter_no: int) -> str:
        book_id = int(book_id)
        text = ""
        text += "الجزء "
        text += part_no_dict_in_details[chapter_no][:part_no_dict_in_details[chapter_no].rindex(" ")]
        text += " من "
        if book_id == QURAN_BOOK_ID.Hafs.value:
            text += "المصحف برواية حفص عن عاصم."
        elif book_id == QURAN_BOOK_ID.Hafs_with_tajwid.value:
            text += "مصحف التجويد برواية حفص عن عاصم."
        return text

    @staticmethod
    def get_quran_book_file_description(book_id: int) -> str:
        book_id = int(book_id)
        text = ""
        if book_id == QURAN_BOOK_ID.Hafs.value:
            text += "المصحف  برواية حفص عن عاصم."
        elif book_id == QURAN_BOOK_ID.Hafs_with_tajwid.value:
            text += "مصحف التجوید برواية حفص عن عاصم."
        return text

    @staticmethod
    def get_quran_page_description_by_page_no(book_id: int, page_no: int) -> str:
        book_id = int(book_id)
        text = ""
        text += f"الصفحة الـ({page_no})"
        text += " من "
        text += "(604)"
        text += " صفحة"
        text += " من القرآن الكريم\n"
        if book_id == QURAN_BOOK_ID.Hafs.value:
            text += "📖 المصحف  برواية حفص عن عاصم."
        elif book_id == QURAN_BOOK_ID.Hafs_with_tajwid.value:
            text += "📖 مصحف التجويد برواية حفص عن عاصم."
        return text

    @staticmethod
    def get_quran_description_by_book_id(book_id: int) -> str:
        text = "تصفح القرآن الكريم بالمصحف التالي:\n"
        if book_id == QURAN_BOOK_ID.Hafs.value:
            text += "📖 المصحف برواية حفص عن عاصم."
        elif book_id == QURAN_BOOK_ID.Hafs_with_tajwid.value:
            text += "📖 مصحف التجويد برواية حفص عن عاصم."
        return text

    @staticmethod
    def get_welcome_by_user_message(telegram_user: TelegramUser) -> str:
        text = "مرحباً بك "
        mention_string = f'<a href="tg://user?id={telegram_user.id}">{escape(telegram_user.fullname)}</a>'
        text += mention_string
        text += escape(" ☺️")
        text += "\n"
        text += "في بوت ختمات القرآن الكريم"
        text += escape(" 📖")
        text += "."
        return text

    Welcome = "مرحباً بك في بوت ختمات القرآن"
    Please_Enter_Opener_Name = "أدخل اسمك من فضلك."
    Please_Enter_New_Opener_Name = "أدخل الاسم الجديد من فضلك."
    Please_Enter_Intention = "ماهي نية هذه الختمة؟ "
    Please_Enter_New_Intention = "ماهي نية هذه الختمة؟ "
    Please_Enter_Duration_In_Days = "ماهي المدة المتاحة لإنهاء جزء ما ؟ (بالأيام)"
    Please_Enter_New_Duration_In_Days = "ماهي المدة المتاحة لإنهاء جزء ما ؟ (بالأيام)"
    Please_Enter_Khatma_Type = "هل الختمة عامة أم خاصة؟"
    Please_Enter_New_Khatma_Type = "هل تود أن تصبح الختمة عامة أم خاصة؟"
    Please_Confirm_Information = "الرجاء التأكد من المعلومات قبل تأكيد فتح الختمة"
    Please_Enter_Correct_Number = "الرجاء إدخال قيمة عددية صحيحة"
    Please_Enter_Not_Big_Duration_Number = "الرجاء إدخال قيمة عددية صحيحة (أقل من 60 يوماً)"
    Operation_Canceled = "تم إلغاء الأمر."
    New_Khatma_Started = "تم إنشاء الختمة بنجاح"
    Update_Khatma_Info_Done = "تم تعديل المعلومات بنجاح"
    Khatma_Part_Occupied = "عذراً لقد تم حجز هذا الجزء مسبقاً"
    Khatma_Part_Done = "عذراً لقد تمت قراءة هذا الجزء مسبقاً"
    Khatma_Not_Found = "عذراً هذه الختمة غير موجودة."
    Khatma_Is_Ended = "هذه الختمة منتهية."
    Khatma_Is_Canceled = "هذه الختمة ملغية."
    Khatma_Part_Occupied_Done = "تم حجز هذا الجزء بنجاح\nوالله ولي التوفيق"
    Khatma_Part_Done_By_Admin = "تم تسجيل هذا الجزء كمقروء\nوجزاكم الله خيراً"
    Khatma_Parts_Refresh_Done = "تم تحديث المعلومات بنجاح."
    Quran_Browse_Text = "📖 تصفح القرآن الكريم\nاختر المصحف الذي يناسبك:"

    Quran_Browse_By_Chapter_Text = "تصفح القرآن الكريم برواية حفص عن عاصم\nاختر الجزء الذي تود قراءته:"
    Quran_Browse_By_Surah_Text = "تصفح القرآن الكريم برواية حفص عن عاصم\nاختر السورة التي تود قراءتها:"
    Quran_Browse_By_Page_Text = "أدخل رقم الصفحة من فضلك (1-604):"
    Contribute_Khatma_Explain_Text = "ما هو نوع الختمة التي تود المشاركة فيها؟\nالختمة العامة: تكون متاحة للجميع.\nالختمة الخاصة: تكون متاحة للأشخاص الذين يملكون رقم الختمة فقط."
    Current_Contribute_Explain_Text = "🔰 إدارة ختماتي: لتنظيم و تعديل المعلومات الخاصة بالختمات التي قمت بإنشائها\n" \
                                      "🔰 إدارة أجزائي: لمشاهدة الأجزاء التي قمت بحجزها و تعديل حالتها."
    Contribute_Private_Khatma_Explain_Text = "فضلاً قم بإدخال رقم الختمة التي تود المساهمة بها"
    Contribute_Public_Khatma_Empty_Explain_Text = "عذراً لا يوجد ختمات عامة حالياً\nقم بالمبادرة و أنشأ ختمة جديدة 😄"
    Mark_Khatma_Part_As_Done_Text = "جزاكم الله خيراً\nتم تسجيل قرائتك لهذا الجزء\nاللهم ارحمنا بالقرآن واجعله " \
                                    "لنا إمامًا ونورًا وهدىً ورحمة. "

    Mark_Khatma_Part_As_Cancel_Text = "تم إلغاء الحجز بنجاح."
    Mark_Khatma_Part_As_Cancel_Read_Text = "تم إلغاء تسجيل قراءة الجزء بنجاح."
    Unknown_Error_Text = "عذراً حدث خطأ ما\nيرجى المحاولة لاحقاً"
    Khatma_Part_Not_Found = "عذراً حدث خطأ ما\nقدتكون الختمة منتهية."
    Mark_Part_As_Done_Time_Limit = "عذراً لا يمكن تعيين الجزء كمقروء قبل مرور 20 دقيقة من حجزه."
    Wrong_Input_Browse_Quran = "عذراً يجب إدخال رقم يمثل رقم الصفحة ضمن المصحف (1-604)."
    Wrong_Range_Browse_Quran = "عذراً يجب إدخال رقم ضمن المجال (1-604)."
    Blocked_User = "عذراً أنت محظور من استعمال البوت\nيرجى التواصل مع الأدمن لمعرفة المشكلة\n@yaser01"
    About_Bot = """🖌 يمكنك هذا البوت من إنشاء ختمة للقرآن الكريم و مشاركتها مع الآخرين وتنسيق مهمة توزيع الأجزاء على القراء.
إضافة لإمكانية تصفح وتحميل المصحف من داخل البوت.
💭 لاقتراحاتكم واستفساراتكم يمكنكم التواصل معي ‎⁦.⁦⁦@yaser01
🤲 هذا البوت بمثابة صدقة جارية على روح أمي و أبي و جميع أموات المسلمين.
  لا تنسونا من دعاؤكم و جزاكم الله عنا كل خير."""
