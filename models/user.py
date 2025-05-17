import time
import logging
from telebot import types
from utils.validators import validate_name, validate_age, validate_bio


class User:
    """
    کلاس مدل کاربر
    """

    def __init__(self, db_manager, telegram_id=None, user_data=None):
        """
        مقداردهی اولیه مدل کاربر
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger('chatogram.models.user')

        if user_data:
            self.data = user_data
        elif telegram_id:
            self.data = self.db_manager.get_user_by_telegram_id(telegram_id)
            if not self.data:
                user_id = self.db_manager.add_user(telegram_id)
                self.data = self.db_manager.get_user_by_telegram_id(telegram_id)
        else:
            self.data = None

    def update_status(self, is_online):
        """
        به‌روزرسانی وضعیت آنلاین بودن کاربر
        """
        if self.data:
            self.db_manager.update_user(
                self.data['id'],
                is_online=is_online,
                last_active=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            self.data['is_online'] = is_online
            self.data['last_active'] = time.strftime('%Y-%m-%d %H:%M:%S')

    def update_profile(self, field, value):
        """
        به‌روزرسانی پروفایل کاربر
        """
        if not self.data:
            return False

        # اعتبارسنجی داده‌ها
        if field == 'display_name':
            if not validate_name(value):
                return False
        elif field == 'age':
            if not validate_age(value):
                return False
        elif field == 'bio':
            if not validate_bio(value):
                return False

        # به‌روزرسانی در دیتابیس
        success = self.db_manager.update_user(self.data['id'], **{field: value})

        if success:
            self.data[field] = value

        return success

    def get_coins(self):
        """
        دریافت تعداد سکه‌های کاربر
        """
        if self.data:
            return self.data.get('coins', 0)
        return 0

    def add_coins(self, amount, transaction_type, description):
        """
        افزودن سکه به حساب کاربر
        """
        if not self.data:
            return False

        success = self.db_manager.add_coins(
            self.data['id'],
            amount,
            transaction_type,
            description
        )

        if success:
            self.data['coins'] = self.get_coins() + amount

        return success

    def use_coins(self, amount, transaction_type, description):
        """
        استفاده از سکه‌های کاربر
        """
        if not self.data or self.get_coins() < amount:
            return False

        success = self.db_manager.use_coins(
            self.data['id'],
            amount,
            transaction_type,
            description
        )

        if success:
            self.data['coins'] = self.get_coins() - amount

        return success

    def get_active_chat(self):
        """
        دریافت چت فعال کاربر
        """
        if not self.data:
            return None

        return self.db_manager.get_active_chat(self.data['id'])

    def is_following(self, user_id):
        """
        بررسی دنبال کردن کاربر
        """
        if not self.data:
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM followers WHERE follower_id = ? AND followed_id = ?",
            (self.data['id'], user_id)
        )

        return cursor.fetchone() is not None

    def has_liked(self, user_id):
        """
        بررسی لایک کردن کاربر
        """
        if not self.data:
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM likes WHERE user_id = ? AND liked_user_id = ?",
            (self.data['id'], user_id)
        )

        return cursor.fetchone() is not None

    def has_blocked(self, user_id):
        """
        بررسی بلاک کردن کاربر
        """
        if not self.data:
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM blocks WHERE blocker_id = ? AND blocked_id = ?",
            (self.data['id'], user_id)
        )

        return cursor.fetchone() is not None

    def get_invite_code(self):
        """
        دریافت یا ایجاد کد دعوت
        """
        if not self.data:
            return None

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        # بررسی وجود کد دعوت
        cursor.execute(
            "SELECT id FROM invites WHERE inviter_id = ? AND invited_id = 0 LIMIT 1",
            (self.data['id'],)
        )

        result = cursor.fetchone()

        if result:
            return result['id']
        else:
            # ایجاد کد دعوت جدید
            return self.db_manager.create_invite(self.data['id'])

    def get_profile_text(self):
        """
        دریافت متن پروفایل کاربر
        """
        if not self.data:
            return "پروفایل یافت نشد."

        gender_text = {
            "male": "مرد 👨",
            "female": "زن 👩",
            "other": "سایر 🤖"
        }.get(self.data.get('gender', ''), "تعیین نشده")

        profile = f"👤 *پروفایل*\n\n"
        profile += f"🔹 *نام*: {self.data.get('display_name', 'کاربر ناشناس')}\n"

        if self.data.get('age'):
            profile += f"🔹 *سن*: {self.data.get('age')} سال\n"
        else:
            profile += f"🔹 *سن*: تعیین نشده\n"

        profile += f"🔹 *جنسیت*: {gender_text}\n"

        if self.data.get('city'):
            profile += f"🔹 *شهر*: {self.data.get('city')}\n"

        profile += f"\n📝 *بیوگرافی*:\n{self.data.get('bio', 'هنوز اطلاعاتی وارد نشده!')}"

        return profile
