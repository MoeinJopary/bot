import logging
import json
from telebot import types
from datetime import datetime
from admin.admin_base import AdminHandler
from config.settings import ADMIN_IDS


class SettingsAdmin(AdminHandler):
    """
    کلاس مدیریت تنظیمات در پنل ادمین
    """

    def __init__(self, bot, db_manager):
        """
        مقداردهی اولیه کلاس مدیریت تنظیمات

        Args:
            bot (telebot.TeleBot): نمونه ربات تلگرام
            db_manager: مدیریت‌کننده پایگاه داده
        """
        super().__init__(bot, db_manager)
        self.logger = logging.getLogger('chatogram.admin.SettingsAdmin')

        # ذخیره‌سازی داده‌های موقت برای ویرایش تنظیمات
        self.edit_settings_cache = {}

    def register_handlers(self):
        """
        ثبت هندلرهای مدیریت تنظیمات
        """

        # منوی تنظیمات
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_settings")
        def handle_admin_settings(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # ثبت لاگ
                self._log_admin_action(call.from_user.id, 'settings_menu', 'ورود به بخش تنظیمات')

                # نمایش منوی تنظیمات
                self.show_settings_menu(call.message.chat.id, call.message.message_id)
            except Exception as e:
                self.logger.error(f"Error in admin settings handler: {str(e)}")

        # تنظیمات چت
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_settings_chat")
        def handle_admin_settings_chat(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش تنظیمات چت
                self.show_category_settings(call.message.chat.id, call.message.message_id, 'chat')
            except Exception as e:
                self.logger.error(f"Error in admin settings chat handler: {str(e)}")

        # تنظیمات جستجو
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_settings_search")
        def handle_admin_settings_search(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش تنظیمات جستجو
                self.show_category_settings(call.message.chat.id, call.message.message_id, 'search')
            except Exception as e:
                self.logger.error(f"Error in admin settings search handler: {str(e)}")

        # تنظیمات پروفایل
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_settings_profile")
        def handle_admin_settings_profile(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش تنظیمات پروفایل
                self.show_category_settings(call.message.chat.id, call.message.message_id, 'profile')
            except Exception as e:
                self.logger.error(f"Error in admin settings profile handler: {str(e)}")

        # تنظیمات سکه
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_settings_coins")
        def handle_admin_settings_coins(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش تنظیمات سکه
                self.show_category_settings(call.message.chat.id, call.message.message_id, 'economy')
            except Exception as e:
                self.logger.error(f"Error in admin settings coins handler: {str(e)}")

        # تنظیمات سیستم
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_settings_system")
        def handle_admin_settings_system(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش تنظیمات سیستم
                self.show_category_settings(call.message.chat.id, call.message.message_id, 'system')
            except Exception as e:
                self.logger.error(f"Error in admin settings system handler: {str(e)}")

        # تنظیمات عمومی
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_settings_general")
        def handle_admin_settings_general(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش تنظیمات عمومی
                self.show_category_settings(call.message.chat.id, call.message.message_id, 'general')
            except Exception as e:
                self.logger.error(f"Error in admin settings general handler: {str(e)}")

        # ویرایش تنظیم
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("admin_edit_setting_"))
        def handle_admin_edit_setting(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # استخراج کلید تنظیم
                setting_key = call.data.replace("admin_edit_setting_", "")

                # نمایش فرم ویرایش تنظیم
                self.show_edit_setting_form(call.message.chat.id, call.message.message_id, setting_key)
            except Exception as e:
                self.logger.error(f"Error in admin edit setting handler: {str(e)}")

        # بازگشت به منوی تنظیمات
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_back_to_settings")
        def handle_admin_back_to_settings(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش منوی تنظیمات
                self.show_settings_menu(call.message.chat.id, call.message.message_id)
            except Exception as e:
                self.logger.error(f"Error in admin back to settings handler: {str(e)}")

        # بازگشت به دسته تنظیمات
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("admin_back_to_category_"))
        def handle_admin_back_to_category(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # استخراج دسته
                category = call.data.replace("admin_back_to_category_", "")

                # نمایش تنظیمات دسته
                self.show_category_settings(call.message.chat.id, call.message.message_id, category)
            except Exception as e:
                self.logger.error(f"Error in admin back to category handler: {str(e)}")

        # فعال/غیرفعال کردن حالت تعمیر و نگهداری
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_toggle_maintenance")
        def handle_admin_toggle_maintenance(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # تغییر وضعیت حالت تعمیر و نگهداری
                self.toggle_maintenance_mode(call.from_user.id)

                # نمایش تنظیمات سیستم
                self.show_category_settings(call.message.chat.id, call.message.message_id, 'system')
            except Exception as e:
                self.logger.error(f"Error in admin toggle maintenance handler: {str(e)}")

        # ویرایش پیام خوش‌آمدگویی
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_edit_welcome_message")
        def handle_admin_edit_welcome_message(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # درخواست پیام جدید
                msg = self.bot.edit_message_text(
                    "📝 لطفاً پیام خوش‌آمدگویی جدید را وارد کنید:",
                    call.message.chat.id,
                    call.message.message_id
                )

                self.bot.register_next_step_handler(msg, self.process_welcome_message)
            except Exception as e:
                self.logger.error(f"Error in admin edit welcome message handler: {str(e)}")

        # فعال/غیرفعال کردن تأیید خودکار عکس پروفایل
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_toggle_auto_approve_pics")
        def handle_admin_toggle_auto_approve_pics(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # تغییر وضعیت تأیید خودکار عکس پروفایل
                self.toggle_setting(call.from_user.id, 'auto_approve_profile_pics')

                # نمایش تنظیمات پروفایل
                self.show_category_settings(call.message.chat.id, call.message.message_id, 'profile')
            except Exception as e:
                self.logger.error(f"Error in admin toggle auto approve pics handler: {str(e)}")

        # فعال/غیرفعال کردن فیلتر موقعیت مکانی
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_toggle_location_filter")
        def handle_admin_toggle_location_filter(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # تغییر وضعیت فیلتر موقعیت مکانی
                self.toggle_setting(call.from_user.id, 'enable_location_filter')

                # نمایش تنظیمات جستجو
                self.show_category_settings(call.message.chat.id, call.message.message_id, 'search')
            except Exception as e:
                self.logger.error(f"Error in admin toggle location filter handler: {str(e)}")

        # ریست تنظیمات به حالت پیش‌فرض
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_reset_settings")
        def handle_admin_reset_settings(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # تأیید ریست تنظیمات
                markup = types.InlineKeyboardMarkup(row_width=2)

                btn_confirm = types.InlineKeyboardButton("✅ تأیید", callback_data="admin_confirm_reset_settings")
                btn_cancel = types.InlineKeyboardButton("❌ انصراف", callback_data="admin_back_to_settings")

                markup.add(btn_confirm, btn_cancel)

                self.bot.edit_message_text(
                    "⚠️ *هشدار: ریست تنظیمات*\n\nآیا از ریست تمامی تنظیمات به حالت پیش‌فرض اطمینان دارید؟\nاین عمل قابل بازگشت نیست!",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            except Exception as e:
                self.logger.error(f"Error in admin reset settings handler: {str(e)}")

        # تأیید ریست تنظیمات
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_confirm_reset_settings")
        def handle_admin_confirm_reset_settings(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # ریست تنظیمات
                success = self.reset_settings(call.from_user.id)

                if success:
                    # نمایش پیام موفقیت
                    self.bot.edit_message_text(
                        "✅ تمامی تنظیمات با موفقیت به حالت پیش‌فرض بازگشتند.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت به منوی تنظیمات",
                                                       callback_data="admin_back_to_settings")
                        )
                    )
                else:
                    # نمایش پیام خطا
                    self.bot.edit_message_text(
                        "❌ خطا در ریست تنظیمات. لطفاً مجدداً تلاش کنید.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت به منوی تنظیمات",
                                                       callback_data="admin_back_to_settings")
                        )
                    )
            except Exception as e:
                self.logger.error(f"Error in admin confirm reset settings handler: {str(e)}")

    def show_settings_menu(self, chat_id, message_id=None):
        """
        نمایش منوی تنظیمات

        Args:
            chat_id (int): شناسه چت
            message_id (int, optional): شناسه پیام برای ویرایش
        """
        try:
            # دریافت وضعیت تعمیر و نگهداری
            maintenance_mode = self.get_setting_value('maintenance_mode', 'false')
            maintenance_status = "فعال ✅" if maintenance_mode == 'true' else "غیرفعال ❌"

            # ایجاد متن منو
            menu_text = "⚙️ *تنظیمات ربات*\n\n"
            menu_text += f"🛠 حالت تعمیر و نگهداری: {maintenance_status}\n\n"
            menu_text += "لطفاً دسته مورد نظر خود را انتخاب کنید:"

            # ایجاد کیبورد اینلاین
            markup = types.InlineKeyboardMarkup(row_width=2)

            btn_chat = types.InlineKeyboardButton("💬 تنظیمات چت", callback_data="admin_settings_chat")
            btn_search = types.InlineKeyboardButton("🔍 تنظیمات جستجو", callback_data="admin_settings_search")
            btn_profile = types.InlineKeyboardButton("👤 تنظیمات پروفایل", callback_data="admin_settings_profile")
            btn_coins = types.InlineKeyboardButton("💰 تنظیمات سکه", callback_data="admin_settings_coins")
            btn_system = types.InlineKeyboardButton("⚙️ تنظیمات سیستم", callback_data="admin_settings_system")
            btn_general = types.InlineKeyboardButton("📝 تنظیمات عمومی", callback_data="admin_settings_general")
            btn_reset = types.InlineKeyboardButton("🔄 ریست تنظیمات", callback_data="admin_reset_settings")
            btn_back = types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back_main")

            markup.add(btn_chat, btn_search)
            markup.add(btn_profile, btn_coins)
            markup.add(btn_system, btn_general)
            markup.add(btn_reset)
            markup.add(btn_back)

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
        except Exception as e:
            self.logger.error(f"Error in show settings menu: {str(e)}")

            # نمایش پیام خطا
            error_text = "❌ خطا در نمایش منوی تنظیمات. لطفاً مجدداً تلاش کنید."

            if message_id:
                self.bot.edit_message_text(
                    error_text,
                    chat_id,
                    message_id,
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back_main")
                    )
                )
            else:
                self.bot.send_message(
                    chat_id,
                    error_text,
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back_main")
                    )
                )

    def show_category_settings(self, chat_id, message_id, category):
        """
        نمایش تنظیمات یک دسته

        Args:
            chat_id (int): شناسه چت
            message_id (int): شناسه پیام برای ویرایش
            category (str): دسته تنظیمات
        """
        try:
            # دریافت تنظیمات دسته
            settings = self.get_category_settings(category)

            # عنوان دسته
            category_titles = {
                'chat': "💬 تنظیمات چت",
                'search': "🔍 تنظیمات جستجو",
                'profile': "👤 تنظیمات پروفایل",
                'economy': "💰 تنظیمات سکه",
                'system': "⚙️ تنظیمات سیستم",
                'general': "📝 تنظیمات عمومی"
            }

            # ایجاد متن تنظیمات
            settings_text = f"*{category_titles.get(category, 'تنظیمات')}*\n\n"

            if not settings:
                settings_text += "هیچ تنظیمی در این دسته وجود ندارد."
            else:
                for setting in settings:
                    value = setting.get('value', '')
                    value_text = self._format_setting_value(setting.get('key', ''), value)
                    settings_text += f"🔹 *{setting.get('description', '')}*\n"
                    settings_text += f"   کلید: `{setting.get('key', '')}`\n"
                    settings_text += f"   مقدار: `{value_text}`\n\n"

            # ایجاد کیبورد اینلاین
            markup = types.InlineKeyboardMarkup(row_width=1)

            # دکمه‌های ویرایش تنظیمات
            if settings:
                for setting in settings:
                    setting_key = setting.get('key', '')
                    btn_text = f"✏️ ویرایش {setting.get('description', '')}"

                    # دکمه‌های ویژه برای برخی تنظیمات
                    if setting_key == 'maintenance_mode':
                        btn_text = "🛠 تغییر وضعیت تعمیر و نگهداری"
                        markup.add(types.InlineKeyboardButton(btn_text, callback_data="admin_toggle_maintenance"))
                    elif setting_key == 'welcome_message':
                        btn_text = "✏️ ویرایش پیام خوش‌آمدگویی"
                        markup.add(types.InlineKeyboardButton(btn_text, callback_data="admin_edit_welcome_message"))
                    elif setting_key == 'auto_approve_profile_pics':
                        btn_text = "✅ تغییر وضعیت تأیید خودکار عکس پروفایل"
                        markup.add(types.InlineKeyboardButton(btn_text, callback_data="admin_toggle_auto_approve_pics"))
                    elif setting_key == 'enable_location_filter':
                        btn_text = "📍 تغییر وضعیت فیلتر موقعیت مکانی"
                        markup.add(types.InlineKeyboardButton(btn_text, callback_data="admin_toggle_location_filter"))
                    else:
                        markup.add(
                            types.InlineKeyboardButton(btn_text, callback_data=f"admin_edit_setting_{setting_key}"))

            # دکمه بازگشت
            markup.add(types.InlineKeyboardButton("🔙 بازگشت به منوی تنظیمات", callback_data="admin_back_to_settings"))

            # ارسال یا ویرایش پیام
            self.bot.edit_message_text(
                settings_text,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception as e:
            self.logger.error(f"Error in show category settings: {str(e)}")

            # نمایش پیام خطا
            self.bot.edit_message_text(
                "❌ خطا در نمایش تنظیمات. لطفاً مجدداً تلاش کنید.",
                chat_id,
                message_id,
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back_to_settings")
                )
            )

    def show_edit_setting_form(self, chat_id, message_id, setting_key):
        """
        نمایش فرم ویرایش تنظیم

        Args:
            chat_id (int): شناسه چت
            message_id (int): شناسه پیام برای ویرایش
            setting_key (str): کلید تنظیم
        """
        try:
            # دریافت اطلاعات تنظیم
            setting = self.get_setting(setting_key)

            if not setting:
                # تنظیم یافت نشد
                self.bot.edit_message_text(
                    "❌ تنظیم مورد نظر یافت نشد.",
                    chat_id,
                    message_id,
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back_to_settings")
                    )
                )
                return

            # ذخیره موقت کلید تنظیم
            self.edit_settings_cache[chat_id] = {
                'key': setting_key,
                'category': setting.get('category', '')
            }

            # ایجاد متن فرم
            form_text = f"✏️ *ویرایش تنظیم*\n\n"
            form_text += f"🔹 *{setting.get('description', '')}*\n"
            form_text += f"🔑 کلید: `{setting_key}`\n"
            form_text += f"📊 مقدار فعلی: `{setting.get('value', '')}`\n\n"
            form_text += "لطفاً مقدار جدید را وارد کنید:"

            # ارسال فرم
            msg = self.bot.edit_message_text(
                form_text,
                chat_id,
                message_id,
                parse_mode='Markdown'
            )

            self.bot.register_next_step_handler(msg, self.process_edit_setting)
        except Exception as e:
            self.logger.error(f"Error in show edit setting form: {str(e)}")

            # نمایش پیام خطا
            self.bot.edit_message_text(
                "❌ خطا در نمایش فرم ویرایش تنظیم. لطفاً مجدداً تلاش کنید.",
                chat_id,
                message_id,
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back_to_settings")
                )
            )

    def process_edit_setting(self, message):
        """
        پردازش ویرایش تنظیم

        Args:
            message (types.Message): پیام کاربر
        """
        try:
            # بررسی دسترسی ادمین
            if not self.check_admin_access(message.from_user.id):
                return

            # دریافت اطلاعات تنظیم
            if message.from_user.id not in self.edit_settings_cache:
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطا در ویرایش تنظیم. لطفاً مجدداً تلاش کنید.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back_to_settings")
                    )
                )
                return

            setting_info = self.edit_settings_cache[message.from_user.id]
            setting_key = setting_info['key']
            category = setting_info['category']

            # دریافت مقدار جدید
            new_value = message.text.strip()

            if not new_value:
                self.bot.send_message(
                    message.chat.id,
                    "❌ مقدار نمی‌تواند خالی باشد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data=f"admin_back_to_category_{category}")
                    )
                )
                return

            # به‌روزرسانی تنظیم
            success = self.update_setting(message.from_user.id, setting_key, new_value)

            if success:
                # نمایش پیام موفقیت
                self.bot.send_message(
                    message.chat.id,
                    f"✅ تنظیم `{setting_key}` با موفقیت به‌روزرسانی شد.",
                    parse_mode='Markdown',
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت به دسته",
                                                   callback_data=f"admin_back_to_category_{category}"),
                        types.InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="admin_back_to_settings")
                    )
                )

                # حذف اطلاعات موقت
                del self.edit_settings_cache[message.from_user.id]
            else:
                # نمایش پیام خطا
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطا در به‌روزرسانی تنظیم. لطفاً مجدداً تلاش کنید.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data=f"admin_back_to_category_{category}")
                    )
                )
        except Exception as e:
            self.logger.error(f"Error in process edit setting: {str(e)}")
            self.bot.send_message(
                message.chat.id,
                "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back_to_settings")
                )
            )

    def process_welcome_message(self, message):
        """
        پردازش ویرایش پیام خوش‌آمدگویی

        Args:
            message (types.Message): پیام کاربر
        """
        try:
            # بررسی دسترسی ادمین
            if not self.check_admin_access(message.from_user.id):
                return

            # دریافت پیام جدید
            new_message = message.text.strip()

            if not new_message:
                self.bot.send_message(
                    message.chat.id,
                    "❌ پیام خوش‌آمدگویی نمی‌تواند خالی باشد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back_to_category_general")
                    )
                )
                return

            # به‌روزرسانی پیام خوش‌آمدگویی
            success = self.update_setting(message.from_user.id, 'welcome_message', new_message)

            if success:
                # نمایش پیام موفقیت
                self.bot.send_message(
                    message.chat.id,
                    "✅ پیام خوش‌آمدگویی با موفقیت به‌روزرسانی شد.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت به تنظیمات عمومی",
                                                   callback_data="admin_back_to_category_general"),
                        types.InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="admin_back_to_settings")
                    )
                )
            else:
                # نمایش پیام خطا
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطا در به‌روزرسانی پیام خوش‌آمدگویی. لطفاً مجدداً تلاش کنید.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back_to_category_general")
                    )
                )
        except Exception as e:
            self.logger.error(f"Error in process welcome message: {str(e)}")
            self.bot.send_message(
                message.chat.id,
                "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back_to_settings")
                )
            )

    def toggle_maintenance_mode(self, admin_id):
        """
        تغییر وضعیت حالت تعمیر و نگهداری

        Args:
            admin_id (int): شناسه ادمین

        Returns:
            bool: True اگر عملیات موفق باشد، False در غیر این صورت
        """
        try:
            # بررسی دسترسی ادمین
            if not self.check_admin_access(admin_id):
                return False

            # دریافت وضعیت فعلی
            current_value = self.get_setting_value('maintenance_mode', 'false')

            # تغییر وضعیت
            new_value = 'false' if current_value == 'true' else 'true'

            # به‌روزرسانی تنظیم
            return self.update_setting(admin_id, 'maintenance_mode', new_value)
        except Exception as e:
            self.logger.error(f"Error in toggle maintenance mode: {str(e)}")
            return False

    def toggle_setting(self, admin_id, setting_key):
        """
        تغییر وضعیت یک تنظیم (true/false)

        Args:
            admin_id (int): شناسه ادمین
            setting_key (str): کلید تنظیم

        Returns:
            bool: True اگر عملیات موفق باشد، False در غیر این صورت
        """
        try:
            # بررسی دسترسی ادمین
            if not self.check_admin_access(admin_id):
                return False

            # دریافت وضعیت فعلی
            current_value = self.get_setting_value(setting_key, 'false')

            # تغییر وضعیت
            new_value = 'false' if current_value == 'true' else 'true'

            # به‌روزرسانی تنظیم
            return self.update_setting(admin_id, setting_key, new_value)
        except Exception as e:
            self.logger.error(f"Error in toggle setting: {str(e)}")
            return False

    def get_setting(self, key):
        """
        دریافت اطلاعات یک تنظیم

        Args:
            key (str): کلید تنظیم

        Returns:
            dict: اطلاعات تنظیم
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM settings WHERE key = ?",
                (key,)
            )

            result = cursor.fetchone()

            if result:
                return dict(result)
            return None
        except Exception as e:
            self.logger.error(f"Error in get setting: {str(e)}")
            return None

    def get_setting_value(self, key, default=None):
        """
        دریافت مقدار یک تنظیم

        Args:
            key (str): کلید تنظیم
            default: مقدار پیش‌فرض در صورت عدم وجود تنظیم

        Returns:
            str: مقدار تنظیم
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT value FROM settings WHERE key = ?",
                (key,)
            )

            result = cursor.fetchone()

            if result:
                return result['value']
            return default
        except Exception as e:
            self.logger.error(f"Error in get setting value: {str(e)}")
            return default

    def get_category_settings(self, category):
        """
        دریافت تنظیمات یک دسته

        Args:
            category (str): دسته تنظیمات

        Returns:
            list: لیست تنظیمات
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM settings WHERE category = ? ORDER BY key",
                (category,)
            )

            results = cursor.fetchall()

            if results:
                return [dict(row) for row in results]
            return []
        except Exception as e:
            self.logger.error(f"Error in get category settings: {str(e)}")
            return []

    def update_setting(self, admin_id, key, value):
        """
        به‌روزرسانی یک تنظیم

        Args:
            admin_id (int): شناسه ادمین
            key (str): کلید تنظیم
            value (str): مقدار جدید

        Returns:
            bool: True اگر عملیات موفق باشد، False در غیر این صورت
        """
        try:
            # بررسی دسترسی ادمین
            if not self.check_admin_access(admin_id):
                return False

            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE settings 
                SET value = ?, updated_at = ?, updated_by = ?
                WHERE key = ?
                """,
                (
                    value,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    admin_id,
                    key
                )
            )

            conn.commit()

            # ثبت لاگ
            self._log_admin_action(
                admin_id,
                'update_setting',
                f"به‌روزرسانی تنظیم {key} به مقدار {value}"
            )

            return True
        except Exception as e:
            self.logger.error(f"Error in update setting: {str(e)}")
            return False

    def reset_settings(self, admin_id):
        """
        ریست تنظیمات به حالت پیش‌فرض

        Args:
            admin_id (int): شناسه ادمین

        Returns:
            bool: True اگر عملیات موفق باشد، False در غیر این صورت
        """
        try:
            # بررسی دسترسی ادمین
            if not self.check_admin_access(admin_id):
                return False

            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            # تنظیمات پیش‌فرض
            default_settings = [
                ('min_age', '18', 'حداقل سن مجاز برای استفاده از ربات', 'profile'),
                ('enable_location_filter', 'true', 'فعال بودن فیلتر موقعیت مکانی', 'search'),
                ('max_daily_chat_requests', '10', 'حداکثر تعداد درخواست چت روزانه', 'chat'),
                ('auto_approve_profile_pics', 'false', 'تأیید خودکار عکس پروفایل', 'profile'),
                ('welcome_message', 'به ربات چتوگرام خوش آمدید!', 'پیام خوش‌آمدگویی به کاربران جدید', 'general'),
                ('maintenance_mode', 'false', 'حالت تعمیر و نگهداری ربات', 'system'),
                ('initial_coins', '20', 'تعداد سکه‌های اولیه برای کاربران جدید', 'economy'),
                ('chat_request_coins', '5', 'هزینه ارسال درخواست چت', 'economy'),
                ('advanced_search_coins', '10', 'هزینه استفاده از جستجوی پیشرفته', 'economy'),
                ('invite_reward_coins', '10', 'پاداش دعوت دوستان', 'economy')
            ]

            # حذف تمام تنظیمات موجود
            cursor.execute("DELETE FROM settings")

            # درج تنظیمات پیش‌فرض
            for key, value, description, category in default_settings:
                cursor.execute(
                    """
                    INSERT INTO settings (key, value, description, category, updated_at, updated_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        key,
                        value,
                        description,
                        category,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        admin_id
                    )
                )

            conn.commit()

            # ثبت لاگ
            self._log_admin_action(
                admin_id,
                'reset_settings',
                "ریست تمامی تنظیمات به حالت پیش‌فرض"
            )

            return True
        except Exception as e:
            self.logger.error(f"Error in reset settings: {str(e)}")
            return False

    def _format_setting_value(self, key, value):
        """
        فرمت‌بندی مقدار تنظیم برای نمایش بهتر

        Args:
            key (str): کلید تنظیم
            value (str): مقدار تنظیم

        Returns:
            str: مقدار فرمت‌بندی شده
        """
        # تبدیل مقادیر بولین به فارسی
        if value.lower() in ['true', 'false']:
            return "فعال ✅" if value.lower() == 'true' else "غیرفعال ❌"

        # کوتاه کردن پیام‌های طولانی
        if key == 'welcome_message' and len(value) > 30:
            return value[:30] + "..."

        return value