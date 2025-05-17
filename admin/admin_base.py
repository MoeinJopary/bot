import logging
from telebot import types
from config.settings import ADMIN_IDS


class AdminHandler:
    """
    کلاس پایه پنل ادمین
    """

    def __init__(self, bot, db_manager):
        """
        مقداردهی اولیه هندلر ادمین

        Args:
            bot (telebot.TeleBot): نمونه ربات تلگرام
            db_manager: مدیریت‌کننده پایگاه داده
        """
        self.bot = bot
        self.db_manager = db_manager
        self.logger = logging.getLogger('chatogram.admin.AdminHandler')

        # ذخیره‌سازی داده‌های موقت
        self.temp_data = {}

    def register_handlers(self):
        """
        ثبت هندلرهای ادمین
        """

        @self.bot.message_handler(commands=['admin'])
        def handle_admin(message):
            try:
                # بررسی دسترسی ادمین
                if message.from_user.id not in ADMIN_IDS:
                    self.logger.warning(f"Unauthorized admin access attempt: {message.from_user.id}")
                    self.bot.send_message(
                        message.chat.id,
                        "⛔ شما دسترسی به پنل ادمین ندارید."
                    )
                    return

                # ثبت لاگ ورود ادمین
                self._log_admin_action(message.from_user.id, 'admin_login', 'ورود به پنل ادمین')

                # نمایش منوی اصلی ادمین
                self.show_admin_main_menu(message.chat.id)
            except Exception as e:
                self.logger.error(f"Error in admin handler: {str(e)}")

        # بازگشت به منوی اصلی ادمین
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_back_main")
        def handle_admin_back_main(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if call.from_user.id not in ADMIN_IDS:
                    return

                # نمایش منوی اصلی ادمین
                self.show_admin_main_menu(call.message.chat.id, call.message.message_id)
            except Exception as e:
                self.logger.error(f"Error in admin back main handler: {str(e)}")

    def show_admin_main_menu(self, chat_id, message_id=None):
        """
        نمایش منوی اصلی ادمین

        Args:
            chat_id (int): شناسه چت
            message_id (int, optional): شناسه پیام برای ویرایش
        """
        # دریافت آمار کلی
        user_count = self._get_total_users()
        active_users = self._get_active_users_today()
        pending_reports = self._get_pending_reports_count()
        active_chats = self._get_active_chats_count()

        menu_text = f"🔐 *پنل مدیریت چتوگرام*\n\n"
        menu_text += f"📊 آمار کلی:\n"
        menu_text += f"👥 کاربران: {user_count} (امروز: {active_users})\n"
        menu_text += f"💬 چت‌های فعال: {active_chats}\n"
        menu_text += f"🚩 گزارشات: {pending_reports} در انتظار بررسی\n\n"
        menu_text += "لطفاً گزینه مورد نظر خود را انتخاب کنید:"

        # ایجاد کیبورد اینلاین
        markup = types.InlineKeyboardMarkup(row_width=2)

        btn_users = types.InlineKeyboardButton("👥 مدیریت کاربران", callback_data="admin_users")
        btn_reports = types.InlineKeyboardButton("🚩 گزارشات تخلف", callback_data="admin_reports")
        btn_coins = types.InlineKeyboardButton("💰 مدیریت سکه‌ها", callback_data="admin_coins")
        btn_stats = types.InlineKeyboardButton("📊 آمار و گزارشات", callback_data="admin_stats")
        btn_broadcast = types.InlineKeyboardButton("📢 پیام همگانی", callback_data="admin_broadcast")
        btn_settings = types.InlineKeyboardButton("⚙️ تنظیمات", callback_data="admin_settings")

        markup.add(btn_users, btn_reports)
        markup.add(btn_coins, btn_stats)
        markup.add(btn_broadcast, btn_settings)

        # ارسال یا ویرایش پیام
        if message_id:
            self.bot.edit_message_text(
                menu_text,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        else:
            self.bot.send_message(
                chat_id,
                menu_text,
                parse_mode='Markdown',
                reply_markup=markup
            )

    def _get_total_users(self):
        """
        دریافت تعداد کل کاربران

        Returns:
            int: تعداد کل کاربران
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()

        return result['count'] if result else 0

    def _get_active_users_today(self):
        """
        دریافت تعداد کاربران فعال امروز

        Returns:
            int: تعداد کاربران فعال امروز
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) as count FROM users WHERE DATE(last_active) = DATE('now')"
        )
        result = cursor.fetchone()

        return result['count'] if result else 0

    def _get_pending_reports_count(self):
        """
        دریافت تعداد گزارشات در انتظار بررسی

        Returns:
            int: تعداد گزارشات در انتظار بررسی
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM reports WHERE status = 'pending'")
        result = cursor.fetchone()

        return result['count'] if result else 0

    def _get_active_chats_count(self):
        """
        دریافت تعداد چت‌های فعال

        Returns:
            int: تعداد چت‌های فعال
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM chats WHERE is_active = 1")
        result = cursor.fetchone()

        return result['count'] if result else 0

    def _log_admin_action(self, admin_id, action, details):
        """
        ثبت فعالیت ادمین در لاگ

        Args:
            admin_id (int): شناسه ادمین
            action (str): نوع فعالیت
            details (str): جزئیات فعالیت

        Returns:
            bool: True اگر ثبت موفق باشد، False در غیر این صورت
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO admin_logs (admin_id, action, details) VALUES (?, ?, ?)",
                (admin_id, action, details)
            )
            conn.commit()

            return True
        except Exception as e:
            self.logger.error(f"Error logging admin action: {str(e)}")
            return False

    def check_admin_access(self, user_id):
        """
        بررسی دسترسی ادمین

        Args:
            user_id (int): شناسه کاربر

        Returns:
            bool: True اگر کاربر ادمین باشد، False در غیر این صورت
        """
        return user_id in ADMIN_IDS

    def get_admin_info(self, admin_id):
        """
        دریافت اطلاعات ادمین

        Args:
            admin_id (int): شناسه ادمین

        Returns:
            dict: اطلاعات ادمین
        """
        if admin_id not in ADMIN_IDS:
            return None

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (admin_id,))
        result = cursor.fetchone()

        if result:
            return dict(result)
        return None

    def format_number(self, number):
        """
        فرمت‌بندی عدد برای نمایش بهتر

        Args:
            number (int): عدد

        Returns:
            str: عدد فرمت‌بندی شده
        """
        return '{:,}'.format(number)