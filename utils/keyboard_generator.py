from telebot import types
from config.constants import MAIN_MENU, CHAT_MENU, GENDERS, COIN_PACKAGES


class KeyboardGenerator:
    """
    کلاس سازنده کیبوردهای اینلاین
    """

    @staticmethod
    def get_main_menu():
        """
        ایجاد کیبورد اصلی
        """
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = [types.KeyboardButton(text) for text in MAIN_MENU]
        markup.add(*buttons)
        return markup

    @staticmethod
    def get_chat_menu():
        """
        ایجاد کیبورد چت
        """
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        buttons = [types.KeyboardButton(text) for text in CHAT_MENU]
        markup.add(*buttons)
        return markup

    @staticmethod
    def get_profile_menu():
        """
        ایجاد کیبورد پروفایل
        """
        markup = types.InlineKeyboardMarkup(row_width=2)

        # دکمه‌های ویرایش پروفایل
        edit_name = types.InlineKeyboardButton("✏️ ویرایش نام", callback_data="edit_name")
        edit_age = types.InlineKeyboardButton("✏️ ویرایش سن", callback_data="edit_age")
        edit_gender = types.InlineKeyboardButton("✏️ ویرایش جنسیت", callback_data="edit_gender")
        edit_bio = types.InlineKeyboardButton("✏️ ویرایش بیوگرافی", callback_data="edit_bio")
        edit_city = types.InlineKeyboardButton("✏️ ویرایش شهر", callback_data="edit_city")
        edit_pic = types.InlineKeyboardButton("🖼 آپلود عکس", callback_data="edit_pic")
        back = types.InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")

        markup.add(edit_name, edit_age)
        markup.add(edit_gender, edit_city)
        markup.add(edit_bio)
        markup.add(edit_pic)
        markup.add(back)

        return markup

    @staticmethod
    def get_gender_selection():
        """
        ایجاد کیبورد انتخاب جنسیت
        """
        markup = types.InlineKeyboardMarkup(row_width=1)

        buttons = [
            types.InlineKeyboardButton(text, callback_data=f"gender_{i}")
            for i, text in enumerate(GENDERS)
        ]

        markup.add(*buttons)
        markup.add(types.InlineKeyboardButton("🔙 انصراف", callback_data="cancel_edit"))

        return markup

    @staticmethod
    def get_search_menu():
        """
        ایجاد کیبورد جستجو
        """
        markup = types.InlineKeyboardMarkup(row_width=2)

        random_man = types.InlineKeyboardButton("🔍 پیدا کردن یک پسر", callback_data="search_random_male")
        random_woman = types.InlineKeyboardButton("🔍 پیدا کردن یک دختر", callback_data="search_random_female")
        random_any = types.InlineKeyboardButton("🔄 پیدا کردن هر کسی", callback_data="search_random_any")
        advanced_search = types.InlineKeyboardButton("🔍 جستجوی پیشرفته", callback_data="search_advanced")
        back = types.InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")

        markup.add(random_man, random_woman)
        markup.add(random_any)
        markup.add(advanced_search)
        markup.add(back)

        return markup

    @staticmethod
    def get_advanced_search_menu():
        """
        ایجاد کیبورد جستجوی پیشرفته
        """
        markup = types.InlineKeyboardMarkup(row_width=2)

        gender_male = types.InlineKeyboardButton("👨 فقط پسرها", callback_data="adv_gender_male")
        gender_female = types.InlineKeyboardButton("👩 فقط دخترها", callback_data="adv_gender_female")
        gender_any = types.InlineKeyboardButton("👥 همه", callback_data="adv_gender_any")

        age_18_25 = types.InlineKeyboardButton("🔢 سن: 18-25", callback_data="adv_age_18_25")
        age_26_35 = types.InlineKeyboardButton("🔢 سن: 26-35", callback_data="adv_age_26_35")
        age_36_plus = types.InlineKeyboardButton("🔢 سن: +36", callback_data="adv_age_36_plus")

        city_select = types.InlineKeyboardButton("🏙 انتخاب شهر", callback_data="adv_city_select")
        clear_filters = types.InlineKeyboardButton("🗑 پاک کردن فیلترها", callback_data="adv_clear_filters")

        search_btn = types.InlineKeyboardButton("🔍 جستجو", callback_data="adv_search_start")
        back = types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_search")

        markup.add(gender_male, gender_female, gender_any)
        markup.add(age_18_25, age_26_35, age_36_plus)
        markup.add(city_select)
        markup.add(clear_filters)
        markup.add(search_btn)
        markup.add(back)

        return markup

    @staticmethod
    def get_coin_packages():
        """
        ایجاد کیبورد بسته‌های سکه
        """
        markup = types.InlineKeyboardMarkup(row_width=1)

        for package in COIN_PACKAGES:
            btn = types.InlineKeyboardButton(
                f"{package['name']} - {package['amount']} سکه ({package['price']} تومان)",
                callback_data=f"buy_coin_{package['amount']}"
            )
            markup.add(btn)

        free_coins = types.InlineKeyboardButton("🎁 دریافت سکه رایگان", callback_data="free_coins")
        back = types.InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_main")

        markup.add(free_coins)
        markup.add(back)

        return markup

    @staticmethod
    def get_user_profile_actions(user_id):
        """
        ایجاد کیبورد اکشن‌های پروفایل کاربر
        """
        markup = types.InlineKeyboardMarkup(row_width=2)

        chat_request = types.InlineKeyboardButton("💬 درخواست چت", callback_data=f"chat_request_{user_id}")
        like_profile = types.InlineKeyboardButton("❤️ لایک پروفایل", callback_data=f"like_profile_{user_id}")
        follow_user = types.InlineKeyboardButton("👁 دنبال کردن", callback_data=f"follow_user_{user_id}")
        block_user = types.InlineKeyboardButton("⛔ بلاک کردن", callback_data=f"block_user_{user_id}")
        report_user = types.InlineKeyboardButton("🚩 گزارش تخلف", callback_data=f"report_user_{user_id}")
        back = types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_search")

        markup.add(chat_request)
        markup.add(like_profile, follow_user)
        markup.add(block_user, report_user)
        markup.add(back)

        return markup

    @staticmethod
    def get_report_reasons():
        """
        ایجاد کیبورد دلایل گزارش تخلف
        """
        markup = types.InlineKeyboardMarkup(row_width=1)

        reasons = [
            ("محتوای نامناسب", "report_inappropriate"),
            ("آزار و اذیت", "report_harassment"),
            ("اسپم", "report_spam"),
            ("کلاهبرداری", "report_scam"),
            ("سایر موارد", "report_other")
        ]

        for text, callback in reasons:
            markup.add(types.InlineKeyboardButton(text, callback_data=callback))

        markup.add(types.InlineKeyboardButton("🔙 انصراف", callback_data="cancel_report"))

        return markup

    @staticmethod
    def get_chat_request_confirmation():
        """
        ایجاد کیبورد تأیید درخواست چت
        """
        markup = types.InlineKeyboardMarkup(row_width=2)

        accept = types.InlineKeyboardButton("✅ قبول درخواست", callback_data="accept_chat_request")
        reject = types.InlineKeyboardButton("❌ رد درخواست", callback_data="reject_chat_request")

        markup.add(accept, reject)

        return markup