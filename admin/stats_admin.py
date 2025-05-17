"""
ماژول مدیریت آمار و گزارشات در پنل ادمین
"""

import logging
from telebot import types
from datetime import datetime, timedelta
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from admin.admin_base import AdminHandler
from config.settings import ADMIN_IDS


class StatsAdmin(AdminHandler):
    """
    کلاس مدیریت آمار و گزارشات در پنل ادمین
    """

    def __init__(self, bot, db_manager):
        """
        مقداردهی اولیه کلاس مدیریت آمار

        Args:
            bot (telebot.TeleBot): نمونه ربات تلگرام
            db_manager: مدیریت‌کننده پایگاه داده
        """
        super().__init__(bot, db_manager)
        self.logger = logging.getLogger('chatogram.admin.StatsAdmin')

        # ذخیره‌سازی داده‌های موقت
        self.stats_cache = {}

    def register_handlers(self):
        """
        ثبت هندلرهای مدیریت آمار
        """

        # منوی آمار و گزارشات
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
        def handle_admin_stats(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # ثبت لاگ
                self._log_admin_action(call.from_user.id, 'stats_menu', 'ورود به بخش آمار و گزارشات')

                # نمایش منوی آمار
                self.show_stats_menu(call.message.chat.id, call.message.message_id)
            except Exception as e:
                self.logger.error(f"Error in admin stats handler: {str(e)}")

        # نمودار کاربران
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_stats_users")
        def handle_admin_stats_users(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش آمار کاربران
                self.show_users_stats(call.message.chat.id, call.message.message_id)
            except Exception as e:
                self.logger.error(f"Error in admin stats users handler: {str(e)}")

        # نمودار چت‌ها
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_stats_chats")
        def handle_admin_stats_chats(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش آمار چت‌ها
                self.show_chats_stats(call.message.chat.id, call.message.message_id)
            except Exception as e:
                self.logger.error(f"Error in admin stats chats handler: {str(e)}")

        # نمودار سکه‌ها
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_stats_coins")
        def handle_admin_stats_coins(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش آمار سکه‌ها
                self.show_coins_stats(call.message.chat.id, call.message.message_id)
            except Exception as e:
                self.logger.error(f"Error in admin stats coins handler: {str(e)}")

        # آمار جامع
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_stats_overview")
        def handle_admin_stats_overview(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش آمار جامع
                self.show_overview_stats(call.message.chat.id, call.message.message_id)
            except Exception as e:
                self.logger.error(f"Error in admin stats overview handler: {str(e)}")

        # گزارش روزانه
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_stats_daily")
        def handle_admin_stats_daily(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش گزارش روزانه
                self.show_daily_report(call.message.chat.id, call.message.message_id)
            except Exception as e:
                self.logger.error(f"Error in admin stats daily handler: {str(e)}")

        # گزارش هفتگی
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_stats_weekly")
        def handle_admin_stats_weekly(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش گزارش هفتگی
                self.show_weekly_report(call.message.chat.id, call.message.message_id)
            except Exception as e:
                self.logger.error(f"Error in admin stats weekly handler: {str(e)}")

        # گزارش ماهانه
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_stats_monthly")
        def handle_admin_stats_monthly(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش گزارش ماهانه
                self.show_monthly_report(call.message.chat.id, call.message.message_id)
            except Exception as e:
                self.logger.error(f"Error in admin stats monthly handler: {str(e)}")

        # خروجی اکسل
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_stats_export")
        def handle_admin_stats_export(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # نمایش منوی خروجی اکسل
                self.show_export_menu(call.message.chat.id, call.message.message_id)
            except Exception as e:
                self.logger.error(f"Error in admin stats export handler: {str(e)}")

        # خروجی اکسل کاربران
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_export_users")
        def handle_admin_export_users(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # ارسال خروجی اکسل کاربران
                self.export_users_excel(call.message.chat.id)
            except Exception as e:
                self.logger.error(f"Error in admin export users handler: {str(e)}")

        # خروجی اکسل تراکنش‌ها
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_export_transactions")
        def handle_admin_export_transactions(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # ارسال خروجی اکسل تراکنش‌ها
                self.export_transactions_excel(call.message.chat.id)
            except Exception as e:
                self.logger.error(f"Error in admin export transactions handler: {str(e)}")

        # خروجی اکسل چت‌ها
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_export_chats")
        def handle_admin_export_chats(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if not self.check_admin_access(call.from_user.id):
                    return

                # ارسال خروجی اکسل چت‌ها
                self.export_chats_excel(call.message.chat.id)
            except Exception as e:
                self.logger.error(f"Error in admin export chats handler: {str(e)}")

    def show_stats_menu(self, chat_id, message_id=None):
        """
        نمایش منوی آمار و گزارشات

        Args:
            chat_id (int): شناسه چت
            message_id (int, optional): شناسه پیام برای ویرایش
        """
        try:
            # دریافت آمار کلی
            total_users = self._get_total_users()
            active_users = self._get_active_users_today()
            total_chats = self._get_total_chats()
            active_chats = self._get_active_chats_count()
            total_transactions = self._get_total_transactions()
            total_coins = self._get_total_coins()

            # ایجاد متن منو
            menu_text = "📊 *آمار و گزارشات*\n\n"
            menu_text += f"👥 *کاربران*: {self.format_number(total_users)} (فعال امروز: {self.format_number(active_users)})\n"
            menu_text += f"💬 *چت‌ها*: {self.format_number(total_chats)} (فعال: {self.format_number(active_chats)})\n"
            menu_text += f"💰 *تراکنش‌ها*: {self.format_number(total_transactions)}\n"
            menu_text += f"🪙 *سکه‌های موجود*: {self.format_number(total_coins)}\n\n"
            menu_text += "لطفاً گزینه مورد نظر خود را انتخاب کنید:"

            # ایجاد کیبورد اینلاین
            markup = types.InlineKeyboardMarkup(row_width=2)

            btn_users = types.InlineKeyboardButton("📈 نمودار کاربران", callback_data="admin_stats_users")
            btn_chats = types.InlineKeyboardButton("📈 نمودار چت‌ها", callback_data="admin_stats_chats")
            btn_coins = types.InlineKeyboardButton("📈 نمودار سکه‌ها", callback_data="admin_stats_coins")
            btn_overview = types.InlineKeyboardButton("📊 آمار جامع", callback_data="admin_stats_overview")
            btn_daily = types.InlineKeyboardButton("📆 گزارش روزانه", callback_data="admin_stats_daily")
            btn_weekly = types.InlineKeyboardButton("📆 گزارش هفتگی", callback_data="admin_stats_weekly")
            btn_monthly = types.InlineKeyboardButton("📆 گزارش ماهانه", callback_data="admin_stats_monthly")
            btn_export = types.InlineKeyboardButton("📤 خروجی اکسل", callback_data="admin_stats_export")
            btn_back = types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back_main")

            markup.add(btn_users, btn_chats)
            markup.add(btn_coins, btn_overview)
            markup.add(btn_daily, btn_weekly)
            markup.add(btn_monthly, btn_export)
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
            self.logger.error(f"Error in show stats menu: {str(e)}")

            # نمایش پیام خطا
            error_text = "❌ خطا در نمایش منوی آمار. لطفاً مجدداً تلاش کنید."

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

    def show_users_stats(self, chat_id, message_id):
        """
        نمایش آمار کاربران

        Args:
            chat_id (int): شناسه چت
            message_id (int): شناسه پیام برای ویرایش
        """
        try:
            # ارسال پیام در حال پردازش
            self.bot.edit_message_text(
                "🔄 در حال تهیه نمودار کاربران...",
                chat_id,
                message_id
            )

            # دریافت آمار کاربران
            users_data = self._get_users_stats()

            if not users_data:
                self.bot.edit_message_text(
                    "❌ داده‌ای برای تهیه نمودار وجود ندارد.",
                    chat_id,
                    message_id,
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")
                    )
                )
                return

            # تهیه نمودار
            buffer = self._create_users_chart(users_data)

            # دریافت آمار اضافی
            total_users = self._get_total_users()
            active_users = self._get_active_users_today()
            new_users_week = self._get_new_users_count(days=7)
            new_users_month = self._get_new_users_count(days=30)

            # ارسال نمودار و اطلاعات
            caption = f"📊 *آمار کاربران*\n\n"
            caption += f"👥 کل کاربران: {self.format_number(total_users)}\n"
            caption += f"🟢 کاربران فعال امروز: {self.format_number(active_users)}\n"
            caption += f"📆 کاربران جدید هفته اخیر: {self.format_number(new_users_week)}\n"
            caption += f"📅 کاربران جدید ماه اخیر: {self.format_number(new_users_month)}\n"

            # ایجاد کیبورد اینلاین
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats"))

            # ارسال عکس نمودار
            self.bot.delete_message(chat_id, message_id)
            self.bot.send_photo(
                chat_id,
                buffer,
                caption=caption,
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception as e:
            self.logger.error(f"Error in show users stats: {str(e)}")

            # نمایش پیام خطا
            self.bot.edit_message_text(
                "❌ خطا در تهیه نمودار کاربران. لطفاً مجدداً تلاش کنید.",
                chat_id,
                message_id,
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")
                )
            )

    def show_chats_stats(self, chat_id, message_id):
        """
        نمایش آمار چت‌ها

        Args:
            chat_id (int): شناسه چت
            message_id (int): شناسه پیام برای ویرایش
        """
        try:
            # ارسال پیام در حال پردازش
            self.bot.edit_message_text(
                "🔄 در حال تهیه نمودار چت‌ها...",
                chat_id,
                message_id
            )

            # دریافت آمار چت‌ها
            chats_data = self._get_chats_stats()

            if not chats_data:
                self.bot.edit_message_text(
                    "❌ داده‌ای برای تهیه نمودار وجود ندارد.",
                    chat_id,
                    message_id,
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")
                    )
                )
                return

            # تهیه نمودار
            buffer = self._create_chats_chart(chats_data)

            # دریافت آمار اضافی
            total_chats = self._get_total_chats()
            active_chats = self._get_active_chats_count()
            avg_chat_duration = self._get_average_chat_duration()
            total_messages = self._get_total_messages()

            # ارسال نمودار و اطلاعات
            caption = f"📊 *آمار چت‌ها*\n\n"
            caption += f"💬 کل چت‌ها: {self.format_number(total_chats)}\n"
            caption += f"🟢 چت‌های فعال: {self.format_number(active_chats)}\n"
            caption += f"⏱ میانگین مدت چت: {avg_chat_duration} دقیقه\n"
            caption += f"📝 کل پیام‌ها: {self.format_number(total_messages)}\n"

            # ایجاد کیبورد اینلاین
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats"))

            # ارسال عکس نمودار
            self.bot.delete_message(chat_id, message_id)
            self.bot.send_photo(
                chat_id,
                buffer,
                caption=caption,
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception as e:
            self.logger.error(f"Error in show chats stats: {str(e)}")

            # نمایش پیام خطا
            self.bot.edit_message_text(
                "❌ خطا در تهیه نمودار چت‌ها. لطفاً مجدداً تلاش کنید.",
                chat_id,
                message_id,
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")
                )
            )

    def show_coins_stats(self, chat_id, message_id):
        """
        نمایش آمار سکه‌ها

        Args:
            chat_id (int): شناسه چت
            message_id (int): شناسه پیام برای ویرایش
        """
        try:
            # ارسال پیام در حال پردازش
            self.bot.edit_message_text(
                "🔄 در حال تهیه نمودار سکه‌ها...",
                chat_id,
                message_id
            )

            # دریافت آمار سکه‌ها
            coins_data = self._get_coins_stats()

            if not coins_data:
                self.bot.edit_message_text(
                    "❌ داده‌ای برای تهیه نمودار وجود ندارد.",
                    chat_id,
                    message_id,
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")
                    )
                )
                return

            # تهیه نمودار
            buffer = self._create_coins_chart(coins_data)

            # دریافت آمار اضافی
            total_coins = self._get_total_coins()
            total_transactions = self._get_total_transactions()
            coins_purchased = self._get_coins_purchased()
            coins_spent = self._get_coins_spent()

            # ارسال نمودار و اطلاعات
            caption = f"📊 *آمار سکه‌ها*\n\n"
            caption += f"🪙 کل سکه‌های موجود: {self.format_number(total_coins)}\n"
            caption += f"💰 کل تراکنش‌ها: {self.format_number(total_transactions)}\n"
            caption += f"💲 سکه‌های خریداری شده: {self.format_number(coins_purchased)}\n"
            caption += f"💸 سکه‌های مصرف شده: {self.format_number(coins_spent)}\n"

            # ایجاد کیبورد اینلاین
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats"))

            # ارسال عکس نمودار
            self.bot.delete_message(chat_id, message_id)
            self.bot.send_photo(
                chat_id,
                buffer,
                caption=caption,
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception as e:
            self.logger.error(f"Error in show coins stats: {str(e)}")

            # نمایش پیام خطا
            self.bot.edit_message_text(
                "❌ خطا در تهیه نمودار سکه‌ها. لطفاً مجدداً تلاش کنید.",
                chat_id,
                message_id,
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")
                )
            )

    def show_overview_stats(self, chat_id, message_id):
        """
        نمایش آمار جامع

        Args:
            chat_id (int): شناسه چت
            message_id (int): شناسه پیام برای ویرایش
        """
        try:
            # ارسال پیام در حال پردازش
            self.bot.edit_message_text(
                "🔄 در حال تهیه گزارش آمار جامع...",
                chat_id,
                message_id
            )

            # دریافت آمار کلی
            users_total = self._get_total_users()
            users_active = self._get_active_users_today()
            users_new_week = self._get_new_users_count(days=7)
            users_new_month = self._get_new_users_count(days=30)

            chats_total = self._get_total_chats()
            chats_active = self._get_active_chats_count()
            chats_today = self._get_chats_count_today()
            avg_chat_duration = self._get_average_chat_duration()

            messages_total = self._get_total_messages()
            messages_today = self._get_messages_count_today()

            coins_total = self._get_total_coins()
            coins_purchased = self._get_coins_purchased()
            coins_spent = self._get_coins_spent()

            # ایجاد گزارش
            report_text = f"📊 *آمار جامع ربات*\n\n"

            report_text += "👥 *آمار کاربران*\n"
            report_text += f"▫️ کل کاربران: {self.format_number(users_total)}\n"
            report_text += f"▫️ کاربران فعال امروز: {self.format_number(users_active)}\n"
            report_text += f"▫️ کاربران جدید هفته اخیر: {self.format_number(users_new_week)}\n"
            report_text += f"▫️ کاربران جدید ماه اخیر: {self.format_number(users_new_month)}\n\n"

            report_text += "💬 *آمار چت‌ها*\n"
            report_text += f"▫️ کل چت‌ها: {self.format_number(chats_total)}\n"
            report_text += f"▫️ چت‌های فعال: {self.format_number(chats_active)}\n"
            report_text += f"▫️ چت‌های امروز: {self.format_number(chats_today)}\n"
            report_text += f"▫️ میانگین مدت چت: {avg_chat_duration} دقیقه\n\n"

            report_text += "📝 *آمار پیام‌ها*\n"
            report_text += f"▫️ کل پیام‌ها: {self.format_number(messages_total)}\n"
            report_text += f"▫️ پیام‌های امروز: {self.format_number(messages_today)}\n\n"

            report_text += "💰 *آمار سکه‌ها*\n"
            report_text += f"▫️ کل سکه‌های موجود: {self.format_number(coins_total)}\n"
            report_text += f"▫️ سکه‌های خریداری شده: {self.format_number(coins_purchased)}\n"
            report_text += f"▫️ سکه‌های مصرف شده: {self.format_number(coins_spent)}\n"

            # ایجاد کیبورد اینلاین
            markup = types.InlineKeyboardMarkup(row_width=1)

            btn_users = types.InlineKeyboardButton("📈 نمودار کاربران", callback_data="admin_stats_users")
            btn_chats = types.InlineKeyboardButton("📈 نمودار چت‌ها", callback_data="admin_stats_chats")
            btn_coins = types.InlineKeyboardButton("📈 نمودار سکه‌ها", callback_data="admin_stats_coins")
            btn_back = types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")

            markup.add(btn_users, btn_chats, btn_coins, btn_back)

            # ارسال گزارش
            self.bot.edit_message_text(
                report_text,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception as e:
            self.logger.error(f"Error in show overview stats: {str(e)}")

            # نمایش پیام خطا
            self.bot.edit_message_text(
                "❌ خطا در تهیه گزارش آمار جامع. لطفاً مجدداً تلاش کنید.",
                chat_id,
                message_id,
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")
                )
            )

    def show_daily_report(self, chat_id, message_id):
        """
        نمایش گزارش روزانه

        Args:
            chat_id (int): شناسه چت
            message_id (int): شناسه پیام برای ویرایش
        """
        try:
            # ارسال پیام در حال پردازش
            self.bot.edit_message_text(
                "🔄 در حال تهیه گزارش روزانه...",
                chat_id,
                message_id
            )

            # دریافت آمار روزانه
            today = datetime.now().strftime('%Y-%m-%d')
            users_new = self._get_new_users_count(days=1)
            users_active = self._get_active_users_today()

            chats_new = self._get_chats_count_today()
            chats_active = self._get_active_chats_count()

            messages_count = self._get_messages_count_today()

            coins_purchased = self._get_daily_coins_purchased()
            coins_spent = self._get_daily_coins_spent()

            # ایجاد گزارش
            report_text = f"📊 *گزارش روزانه ({today})*\n\n"

            report_text += "👥 *کاربران*\n"
            report_text += f"▫️ کاربران جدید: {self.format_number(users_new)}\n"
            report_text += f"▫️ کاربران فعال: {self.format_number(users_active)}\n\n"

            report_text += "💬 *چت‌ها*\n"
            report_text += f"▫️ چت‌های جدید: {self.format_number(chats_new)}\n"
            report_text += f"▫️ چت‌های فعال: {self.format_number(chats_active)}\n\n"

            report_text += "📝 *پیام‌ها*\n"
            report_text += f"▫️ تعداد پیام‌ها: {self.format_number(messages_count)}\n\n"

            report_text += "💰 *سکه‌ها*\n"
            report_text += f"▫️ سکه‌های خریداری شده: {self.format_number(coins_purchased)}\n"
            report_text += f"▫️ سکه‌های مصرف شده: {self.format_number(coins_spent)}\n"

            # ایجاد کیبورد اینلاین
            markup = types.InlineKeyboardMarkup(row_width=2)

            btn_weekly = types.InlineKeyboardButton("📆 گزارش هفتگی", callback_data="admin_stats_weekly")
            btn_monthly = types.InlineKeyboardButton("📆 گزارش ماهانه", callback_data="admin_stats_monthly")
            btn_back = types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")

            markup.add(btn_weekly, btn_monthly)
            markup.add(btn_back)

            # ارسال گزارش
            self.bot.edit_message_text(
                report_text,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception as e:
            self.logger.error(f"Error in show daily report: {str(e)}")

            # نمایش پیام خطا
            self.bot.edit_message_text(
                "❌ خطا در تهیه گزارش روزانه. لطفاً مجدداً تلاش کنید.",
                chat_id,
                message_id,
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")
                )
            )

    def show_weekly_report(self, chat_id, message_id):
        """
        نمایش گزارش هفتگی

        Args:
            chat_id (int): شناسه چت
            message_id (int): شناسه پیام برای ویرایش
        """
        try:
            # ارسال پیام در حال پردازش
            self.bot.edit_message_text(
                "🔄 در حال تهیه گزارش هفتگی...",
                chat_id,
                message_id
            )

            # دریافت آمار هفتگی
            today = datetime.now()
            week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
            week_end = today.strftime('%Y-%m-%d')

            users_new = self._get_new_users_count(days=7)
            users_active_week = self._get_active_users_week()

            chats_new = self._get_chats_count_week()

            messages_count = self._get_messages_count_week()

            coins_purchased = self._get_weekly_coins_purchased()
            coins_spent = self._get_weekly_coins_spent()

            # ایجاد گزارش
            report_text = f"📊 *گزارش هفتگی ({week_start} تا {week_end})*\n\n"

            report_text += "👥 *کاربران*\n"
            report_text += f"▫️ کاربران جدید: {self.format_number(users_new)}\n"
            report_text += f"▫️ کاربران فعال: {self.format_number(users_active_week)}\n\n"

            report_text += "💬 *چت‌ها*\n"
            report_text += f"▫️ چت‌های جدید: {self.format_number(chats_new)}\n\n"

            report_text += "📝 *پیام‌ها*\n"
            report_text += f"▫️ تعداد پیام‌ها: {self.format_number(messages_count)}\n\n"

            report_text += "💰 *سکه‌ها*\n"
            report_text += f"▫️ سکه‌های خریداری شده: {self.format_number(coins_purchased)}\n"
            report_text += f"▫️ سکه‌های مصرف شده: {self.format_number(coins_spent)}\n"

            # ایجاد کیبورد اینلاین
            markup = types.InlineKeyboardMarkup(row_width=2)

            btn_daily = types.InlineKeyboardButton("📆 گزارش روزانه", callback_data="admin_stats_daily")
            btn_monthly = types.InlineKeyboardButton("📆 گزارش ماهانه", callback_data="admin_stats_monthly")
            btn_back = types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")

            markup.add(btn_daily, btn_monthly)
            markup.add(btn_back)

            # ارسال گزارش
            self.bot.edit_message_text(
                report_text,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception as e:
            self.logger.error(f"Error in show weekly report: {str(e)}")

            # نمایش پیام خطا
            self.bot.edit_message_text(
                "❌ خطا در تهیه گزارش هفتگی. لطفاً مجدداً تلاش کنید.",
                chat_id,
                message_id,
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")
                )
            )

    def show_monthly_report(self, chat_id, message_id):
        """
        نمایش گزارش ماهانه

        Args:
            chat_id (int): شناسه چت
            message_id (int): شناسه پیام برای ویرایش
        """
        try:
            # ارسال پیام در حال پردازش
            self.bot.edit_message_text(
                "🔄 در حال تهیه گزارش ماهانه...",
                chat_id,
                message_id
            )

            # دریافت آمار ماهانه
            today = datetime.now()
            month_start = today.replace(day=1).strftime('%Y-%m-%d')
            month_end = today.strftime('%Y-%m-%d')

            users_new = self._get_new_users_count(days=30)
            users_active_month = self._get_active_users_month()

            chats_new = self._get_chats_count_month()

            messages_count = self._get_messages_count_month()

            coins_purchased = self._get_monthly_coins_purchased()
            coins_spent = self._get_monthly_coins_spent()

            # ایجاد گزارش
            report_text = f"📊 *گزارش ماهانه ({month_start} تا {month_end})*\n\n"

            report_text += "👥 *کاربران*\n"
            report_text += f"▫️ کاربران جدید: {self.format_number(users_new)}\n"
            report_text += f"▫️ کاربران فعال: {self.format_number(users_active_month)}\n\n"

            report_text += "💬 *چت‌ها*\n"
            report_text += f"▫️ چت‌های جدید: {self.format_number(chats_new)}\n\n"

            report_text += "📝 *پیام‌ها*\n"
            report_text += f"▫️ تعداد پیام‌ها: {self.format_number(messages_count)}\n\n"

            report_text += "💰 *سکه‌ها*\n"
            report_text += f"▫️ سکه‌های خریداری شده: {self.format_number(coins_purchased)}\n"
            report_text += f"▫️ سکه‌های مصرف شده: {self.format_number(coins_spent)}\n"

            # ایجاد کیبورد اینلاین
            markup = types.InlineKeyboardMarkup(row_width=2)

            btn_daily = types.InlineKeyboardButton("📆 گزارش روزانه", callback_data="admin_stats_daily")
            btn_weekly = types.InlineKeyboardButton("📆 گزارش هفتگی", callback_data="admin_stats_weekly")
            btn_back = types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")

            markup.add(btn_daily, btn_weekly)
            markup.add(btn_back)

            # ارسال گزارش
            self.bot.edit_message_text(
                report_text,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception as e:
            self.logger.error(f"Error in show monthly report: {str(e)}")

            # نمایش پیام خطا
            self.bot.edit_message_text(
                "❌ خطا در تهیه گزارش ماهانه. لطفاً مجدداً تلاش کنید.",
                chat_id,
                message_id,
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")
                )
            )

    def show_export_menu(self, chat_id, message_id):
        """
        نمایش منوی خروجی اکسل

        Args:
            chat_id (int): شناسه چت
            message_id (int): شناسه پیام برای ویرایش
        """
        try:
            # ایجاد متن منو
            menu_text = "📤 *خروجی اکسل*\n\nلطفاً نوع خروجی مورد نظر خود را انتخاب کنید:"

            # ایجاد کیبورد اینلاین
            markup = types.InlineKeyboardMarkup(row_width=1)

            btn_users = types.InlineKeyboardButton("👥 خروجی کاربران", callback_data="admin_export_users")
            btn_transactions = types.InlineKeyboardButton("💰 خروجی تراکنش‌ها",
                                                          callback_data="admin_export_transactions")
            btn_chats = types.InlineKeyboardButton("💬 خروجی چت‌ها", callback_data="admin_export_chats")
            btn_back = types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")

            markup.add(btn_users, btn_transactions, btn_chats, btn_back)

            # ارسال منو
            self.bot.edit_message_text(
                menu_text,
                chat_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception as e:
            self.logger.error(f"Error in show export menu: {str(e)}")

            # نمایش پیام خطا
            self.bot.edit_message_text(
                "❌ خطا در نمایش منوی خروجی اکسل. لطفاً مجدداً تلاش کنید.",
                chat_id,
                message_id,
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")
                )
            )

    def export_users_excel(self, chat_id):
        """
        ارسال خروجی اکسل کاربران

        Args:
            chat_id (int): شناسه چت
        """
        try:
            # ارسال پیام در حال پردازش
            msg = self.bot.send_message(
                chat_id,
                "🔄 در حال تهیه خروجی اکسل کاربران..."
            )

            # دریافت لیست کاربران
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, telegram_id, username, display_name, age, gender, city, 
                       coins, is_online, is_banned, created_at, last_active
                FROM users
                ORDER BY id
            """)

            users = cursor.fetchall()

            if not users:
                self.bot.edit_message_text(
                    "❌ داده‌ای برای خروجی وجود ندارد.",
                    chat_id,
                    msg.message_id,
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats_export")
                    )
                )
                return

            # تبدیل به دیتافریم
            df = pd.DataFrame([dict(user) for user in users])

            # تبدیل وضعیت آنلاین و مسدودیت به متن
            df['is_online'] = df['is_online'].apply(lambda x: 'بله' if x else 'خیر')
            df['is_banned'] = df['is_banned'].apply(lambda x: 'بله' if x else 'خیر')

            # تبدیل جنسیت به متن فارسی
            gender_map = {
                'male': 'مرد',
                'female': 'زن',
                'other': 'سایر'
            }
            df['gender'] = df['gender'].map(lambda x: gender_map.get(x, 'نامشخص') if x else 'نامشخص')

            # تغییر نام ستون‌ها
            df.columns = [
                'شناسه', 'آیدی تلگرام', 'یوزرنیم', 'نام نمایشی', 'سن', 'جنسیت', 'شهر',
                'سکه', 'آنلاین', 'مسدود', 'تاریخ ثبت‌نام', 'آخرین فعالیت'
            ]

            # ایجاد فایل اکسل
            now = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f"chatogram_users_{now}.xlsx"

            excel_file = io.BytesIO()
            df.to_excel(excel_file, index=False, engine='openpyxl')
            excel_file.seek(0)

            # ارسال فایل اکسل
            self.bot.edit_message_text(
                "✅ خروجی اکسل کاربران با موفقیت تهیه شد. در حال ارسال فایل...",
                chat_id,
                msg.message_id
            )

            self.bot.send_document(
                chat_id,
                (file_name, excel_file),
                caption="📊 خروجی اکسل کاربران",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats_export")
                )
            )
        except Exception as e:
            self.logger.error(f"Error in export users excel: {str(e)}")

            # نمایش پیام خطا
            self.bot.send_message(
                chat_id,
                "❌ خطا در تهیه خروجی اکسل کاربران. لطفاً مجدداً تلاش کنید.",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats_export")
                )
            )

    def export_transactions_excel(self, chat_id):
        """
        ارسال خروجی اکسل تراکنش‌ها

        Args:
            chat_id (int): شناسه چت
        """
        try:
            # ارسال پیام در حال پردازش
            msg = self.bot.send_message(
                chat_id,
                "🔄 در حال تهیه خروجی اکسل تراکنش‌ها..."
            )

            # دریافت لیست تراکنش‌ها
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT t.id, t.user_id, u.display_name as user_name, t.amount, 
                       t.transaction_type, t.description, t.status, t.created_at
                FROM transactions t
                JOIN users u ON t.user_id = u.id
                ORDER BY t.created_at DESC
            """)

            transactions = cursor.fetchall()

            if not transactions:
                self.bot.edit_message_text(
                    "❌ داده‌ای برای خروجی وجود ندارد.",
                    chat_id,
                    msg.message_id,
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats_export")
                    )
                )
                return

            # تبدیل به دیتافریم
            df = pd.DataFrame([dict(tx) for tx in transactions])

            # تبدیل نوع تراکنش به متن فارسی
            type_map = {
                'purchase': 'خرید سکه',
                'chat_request': 'درخواست چت',
                'advanced_search': 'جستجوی پیشرفته',
                'admin_add': 'افزایش توسط ادمین',
                'admin_deduct': 'کاهش توسط ادمین',
                'invite_reward': 'پاداش دعوت دوستان'
            }
            df['transaction_type'] = df['transaction_type'].map(lambda x: type_map.get(x, x) if x else x)

            # تبدیل وضعیت به متن فارسی
            status_map = {
                'pending': 'در انتظار',
                'completed': 'تکمیل شده',
                'failed': 'ناموفق',
                'refunded': 'برگشت داده شده'
            }
            df['status'] = df['status'].map(lambda x: status_map.get(x, x) if x else x)

            # تغییر نام ستون‌ها
            df.columns = [
                'شناسه', 'شناسه کاربر', 'نام کاربر', 'مقدار', 'نوع تراکنش',
                'توضیحات', 'وضعیت', 'تاریخ'
            ]

            # ایجاد فایل اکسل
            now = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f"chatogram_transactions_{now}.xlsx"

            excel_file = io.BytesIO()
            df.to_excel(excel_file, index=False, engine='openpyxl')
            excel_file.seek(0)

            # ارسال فایل اکسل
            self.bot.edit_message_text(
                "✅ خروجی اکسل تراکنش‌ها با موفقیت تهیه شد. در حال ارسال فایل...",
                chat_id,
                msg.message_id
            )

            self.bot.send_document(
                chat_id,
                (file_name, excel_file),
                caption="📊 خروجی اکسل تراکنش‌ها",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats_export")
                )
            )
        except Exception as e:
            self.logger.error(f"Error in export transactions excel: {str(e)}")

            # نمایش پیام خطا
            self.bot.send_message(
                chat_id,
                "❌ خطا در تهیه خروجی اکسل تراکنش‌ها. لطفاً مجدداً تلاش کنید.",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats_export")
                )
            )

    def export_chats_excel(self, chat_id):
        """
        ارسال خروجی اکسل چت‌ها

        Args:
            chat_id (int): شناسه چت
        """
        try:
            # ارسال پیام در حال پردازش
            msg = self.bot.send_message(
                chat_id,
                "🔄 در حال تهیه خروجی اکسل چت‌ها..."
            )

            # دریافت لیست چت‌ها
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT c.id, c.started_at, c.ended_at, c.is_active,
                       u1.display_name as user1_name, u2.display_name as user2_name,
                       COUNT(m.id) as message_count
                FROM chats c
                JOIN users u1 ON c.user1_id = u1.id
                JOIN users u2 ON c.user2_id = u2.id
                LEFT JOIN messages m ON c.id = m.chat_id
                GROUP BY c.id
                ORDER BY c.started_at DESC
            """)

            chats = cursor.fetchall()

            if not chats:
                self.bot.edit_message_text(
                    "❌ داده‌ای برای خروجی وجود ندارد.",
                    chat_id,
                    msg.message_id,
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats_export")
                    )
                )
                return

            # تبدیل به دیتافریم
            df = pd.DataFrame([dict(chat) for chat in chats])

            # محاسبه مدت چت
            def calculate_duration(row):
                if not row['ended_at'] or row['is_active']:
                    return "فعال"

                try:
                    start = datetime.strptime(row['started_at'], '%Y-%m-%d %H:%M:%S')
                    end = datetime.strptime(row['ended_at'], '%Y-%m-%d %H:%M:%S')
                    duration = end - start
                    minutes = duration.total_seconds() / 60
                    return f"{int(minutes)} دقیقه"
                except:
                    return "نامشخص"

            df['duration'] = df.apply(calculate_duration, axis=1)

            # تبدیل وضعیت فعال به متن
            df['is_active'] = df['is_active'].apply(lambda x: 'بله' if x else 'خیر')

            # تغییر نام ستون‌ها
            df.columns = [
                'شناسه', 'شروع', 'پایان', 'فعال', 'کاربر 1',
                'کاربر 2', 'تعداد پیام', 'مدت'
            ]

            # ایجاد فایل اکسل
            now = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f"chatogram_chats_{now}.xlsx"

            excel_file = io.BytesIO()
            df.to_excel(excel_file, index=False, engine='openpyxl')
            excel_file.seek(0)

            # ارسال فایل اکسل
            self.bot.edit_message_text(
                "✅ خروجی اکسل چت‌ها با موفقیت تهیه شد. در حال ارسال فایل...",
                chat_id,
                msg.message_id
            )

            self.bot.send_document(
                chat_id,
                (file_name, excel_file),
                caption="📊 خروجی اکسل چت‌ها",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats_export")
                )
            )
        except Exception as e:
            self.logger.error(f"Error in export chats excel: {str(e)}")

            # نمایش پیام خطا
            self.bot.send_message(
                chat_id,
                "❌ خطا در تهیه خروجی اکسل چت‌ها. لطفاً مجدداً تلاش کنید.",
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats_export")
                )
            )

    def _create_users_chart(self, data):
        """
        ایجاد نمودار کاربران

        Args:
            data (list): داده‌های کاربران

        Returns:
            io.BytesIO: نمودار در قالب بافر
        """
        # پاکسازی لوکیل فارسی
        plt.clf()
        plt.style.use('ggplot')

        # مشخص کردن اندازه نمودار
        plt.figure(figsize=(10, 6))

        # استخراج داده‌ها
        dates = [item['date'] for item in data]
        users = [item['count'] for item in data]

        # تبدیل تاریخ‌ها
        dates = [datetime.strptime(date, '%Y-%m-%d') for date in dates]

        # رسم نمودار
        plt.plot(dates, users, marker='o', linestyle='-', color='#2196F3', linewidth=2, markersize=6)

        # تنظیم محور X
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))

        # عنوان و برچسب‌ها
        plt.title('نمودار کاربران جدید', fontsize=16)
        plt.xlabel('تاریخ', fontsize=12)
        plt.ylabel('تعداد کاربران', fontsize=12)

        # گرید و افسانه
        plt.grid(True, linestyle='--', alpha=0.7)

        # چرخش برچسب‌های محور X
        plt.xticks(rotation=45)

        # تنظیم حاشیه
        plt.tight_layout()

        # ذخیره نمودار در بافر
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # بستن نمودار
        plt.close()

        return buffer

    def _create_chats_chart(self, data):
        """
        ایجاد نمودار چت‌ها

        Args:
            data (list): داده‌های چت‌ها

        Returns:
            io.BytesIO: نمودار در قالب بافر
        """
        # پاکسازی لوکیل فارسی
        plt.clf()
        plt.style.use('ggplot')

        # مشخص کردن اندازه نمودار
        plt.figure(figsize=(10, 6))

        # استخراج داده‌ها
        dates = [item['date'] for item in data]
        chats = [item['count'] for item in data]

        # تبدیل تاریخ‌ها
        dates = [datetime.strptime(date, '%Y-%m-%d') for date in dates]

        # رسم نمودار
        plt.plot(dates, chats, marker='o', linestyle='-', color='#4CAF50', linewidth=2, markersize=6)

        # تنظیم محور X
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))

        # عنوان و برچسب‌ها
        plt.title('نمودار چت‌های روزانه', fontsize=16)
        plt.xlabel('تاریخ', fontsize=12)
        plt.ylabel('تعداد چت‌ها', fontsize=12)

        # گرید و افسانه
        plt.grid(True, linestyle='--', alpha=0.7)

        # چرخش برچسب‌های محور X
        plt.xticks(rotation=45)

        # تنظیم حاشیه
        plt.tight_layout()

        # ذخیره نمودار در بافر
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # بستن نمودار
        plt.close()

        return buffer

    def _create_coins_chart(self, data):
        """
        ایجاد نمودار سکه‌ها

        Args:
            data (list): داده‌های سکه‌ها

        Returns:
            io.BytesIO: نمودار در قالب بافر
        """
        # پاکسازی لوکیل فارسی
        plt.clf()
        plt.style.use('ggplot')

        # مشخص کردن اندازه نمودار
        plt.figure(figsize=(10, 6))

        # استخراج داده‌ها
        dates = [item['date'] for item in data]
        purchases = [item['purchased'] for item in data]
        spent = [item['spent'] for item in data]

        # تبدیل تاریخ‌ها
        dates = [datetime.strptime(date, '%Y-%m-%d') for date in dates]

        # رسم نمودار
        plt.plot(dates, purchases, marker='o', linestyle='-', color='#2196F3', linewidth=2, markersize=6, label='خرید')
        plt.plot(dates, spent, marker='s', linestyle='-', color='#F44336', linewidth=2, markersize=6, label='مصرف')

        # تنظیم محور X
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))

        # عنوان و برچسب‌ها
        plt.title('نمودار سکه‌های خریداری و مصرف شده', fontsize=16)
        plt.xlabel('تاریخ', fontsize=12)
        plt.ylabel('تعداد سکه', fontsize=12)

        # گرید و افسانه
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='best')

        # چرخش برچسب‌های محور X
        plt.xticks(rotation=45)

        # تنظیم حاشیه
        plt.tight_layout()

        # ذخیره نمودار در بافر
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # بستن نمودار
        plt.close()

        return buffer

    def _get_users_stats(self):
        """
        دریافت آمار کاربران

        Returns:
            list: آمار کاربران
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM users
                WHERE created_at >= date('now', '-30 days')
                GROUP BY DATE(created_at)
                ORDER BY DATE(created_at)
            """)

            results = cursor.fetchall()

            if results:
                return [dict(row) for row in results]
            return []
        except Exception as e:
            self.logger.error(f"Error in get users stats: {str(e)}")
            return []

    def _get_chats_stats(self):
        """
        دریافت آمار چت‌ها

        Returns:
            list: آمار چت‌ها
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DATE(started_at) as date, COUNT(*) as count
                FROM chats
                WHERE started_at >= date('now', '-30 days')
                GROUP BY DATE(started_at)
                ORDER BY DATE(started_at)
            """)

            results = cursor.fetchall()

            if results:
                return [dict(row) for row in results]
            return []
        except Exception as e:
            self.logger.error(f"Error in get chats stats: {str(e)}")
            return []

    def _get_coins_stats(self):
        """
        دریافت آمار سکه‌ها

        Returns:
            list: آمار سکه‌ها
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DATE(created_at) as date,
                       SUM(CASE WHEN amount > 0 AND transaction_type != 'admin_add' AND transaction_type != 'invite_reward' THEN amount ELSE 0 END) as purchased,
                       SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as spent
                FROM transactions
                WHERE created_at >= date('now', '-30 days')
                GROUP BY DATE(created_at)
                ORDER BY DATE(created_at)
            """)

            results = cursor.fetchall()

            if results:
                return [dict(row) for row in results]
            return []
        except Exception as e:
            self.logger.error(f"Error in get coins stats: {str(e)}")
            return []

    def _get_total_chats(self):
        """
        دریافت تعداد کل چت‌ها

        Returns:
            int: تعداد کل چت‌ها
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) as count FROM chats")
            result = cursor.fetchone()

            return result['count'] if result else 0
        except Exception as e:
            self.logger.error(f"Error in get total chats: {str(e)}")
            return 0

    def _get_chats_count_today(self):
        """
        دریافت تعداد چت‌های امروز

        Returns:
            int: تعداد چت‌های امروز
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) as count FROM chats WHERE DATE(started_at) = DATE('now')"
            )
            result = cursor.fetchone()

            return result['count'] if result else 0
        except Exception as e:
            self.logger.error(f"Error in get chats count today: {str(e)}")
            return 0

    def _get_chats_count_week(self):
        """
        دریافت تعداد چت‌های هفته اخیر

        Returns:
            int: تعداد چت‌های هفته اخیر
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) as count FROM chats WHERE started_at >= date('now', '-7 days')"
            )
            result = cursor.fetchone()

            return result['count'] if result else 0
        except Exception as e:
            self.logger.error(f"Error in get chats count week: {str(e)}")
            return 0

    def _get_chats_count_month(self):
        """
        دریافت تعداد چت‌های ماه اخیر

        Returns:
            int: تعداد چت‌های ماه اخیر
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) as count FROM chats WHERE started_at >= date('now', '-30 days')"
            )
            result = cursor.fetchone()

            return result['count'] if result else 0
        except Exception as e:
            self.logger.error(f"Error in get chats count month: {str(e)}")
            return 0

    def _get_average_chat_duration(self):
        """
        دریافت میانگین مدت چت

        Returns:
            float: میانگین مدت چت (دقیقه)
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT AVG((JULIANDAY(ended_at) - JULIANDAY(started_at)) * 24 * 60) as avg_duration
                FROM chats
                WHERE is_active = 0 AND ended_at IS NOT NULL
            """)
            result = cursor.fetchone()

            if result and result['avg_duration']:
                return round(result['avg_duration'], 1)
            return 0
        except Exception as e:
            self.logger.error(f"Error in get average chat duration: {str(e)}")
            return 0

    def _get_total_messages(self):
        """
        دریافت تعداد کل پیام‌ها

        Returns:
            int: تعداد کل پیام‌ها
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) as count FROM messages")
            result = cursor.fetchone()

            return result['count'] if result else 0
        except Exception as e:
            self.logger.error(f"Error in get total messages: {str(e)}")
            return 0

    def _get_messages_count_today(self):
        """
        دریافت تعداد پیام‌های امروز

        Returns:
            int: تعداد پیام‌های امروز
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) as count FROM messages WHERE DATE(sent_at) = DATE('now')"
            )
            result = cursor.fetchone()

            return result['count'] if result else 0
        except Exception as e:
            self.logger.error(f"Error in get messages count today: {str(e)}")
            return 0

    def _get_messages_count_week(self):
        """
        دریافت تعداد پیام‌های هفته اخیر

        Returns:
            int: تعداد پیام‌های هفته اخیر
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) as count FROM messages WHERE sent_at >= date('now', '-7 days')"
            )
            result = cursor.fetchone()

            return result['count'] if result else 0
        except Exception as e:
            self.logger.error(f"Error in get messages count week: {str(e)}")
            return 0

    def _get_messages_count_month(self):
        """
        دریافت تعداد پیام‌های ماه اخیر

        Returns:
            int: تعداد پیام‌های ماه اخیر
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) as count FROM messages WHERE sent_at >= date('now', '-30 days')"
            )
            result = cursor.fetchone()

            return result['count'] if result else 0
        except Exception as e:
            self.logger.error(f"Error in get messages count month: {str(e)}")
            return 0

    def _get_total_transactions(self):
        """
        دریافت تعداد کل تراکنش‌ها

        Returns:
            int: تعداد کل تراکنش‌ها
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) as count FROM transactions")
            result = cursor.fetchone()

            return result['count'] if result else 0
        except Exception as e:
            self.logger.error(f"Error in get total transactions: {str(e)}")
            return 0

    def _get_total_coins(self):
        """
        دریافت تعداد کل سکه‌های موجود

        Returns:
            int: تعداد کل سکه‌های موجود
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT SUM(coins) as total FROM users")
            result = cursor.fetchone()

            return result['total'] if result and result['total'] else 0
        except Exception as e:
            self.logger.error(f"Error in get total coins: {str(e)}")
            return 0

    def _get_coins_purchased(self):
        """
        دریافت تعداد کل سکه‌های خریداری شده

        Returns:
            int: تعداد کل سکه‌های خریداری شده
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT SUM(amount) as total 
                FROM transactions 
                WHERE amount > 0 AND transaction_type = 'purchase'
            """)
            result = cursor.fetchone()

            return result['total'] if result and result['total'] else 0
        except Exception as e:
            self.logger.error(f"Error in get coins purchased: {str(e)}")
            return 0

    def _get_coins_spent(self):
        """
        دریافت تعداد کل سکه‌های مصرف شده

        Returns:
            int: تعداد کل سکه‌های مصرف شده
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT SUM(ABS(amount)) as total 
                FROM transactions 
                WHERE amount < 0
            """)
            result = cursor.fetchone()

            return result['total'] if result and result['total'] else 0
        except Exception as e:
            self.logger.error(f"Error in get coins spent: {str(e)}")
            return 0

    def _get_daily_coins_purchased(self):
        """
        دریافت تعداد سکه‌های خریداری شده امروز

        Returns:
            int: تعداد سکه‌های خریداری شده امروز
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT SUM(amount) as total 
                FROM transactions 
                WHERE amount > 0 AND transaction_type = 'purchase'
                AND DATE(created_at) = DATE('now')
            """)
            result = cursor.fetchone()

            return result['total'] if result and result['total'] else 0
        except Exception as e:
            self.logger.error(f"Error in get daily coins purchased: {str(e)}")
            return 0

    def _get_daily_coins_spent(self):
        """
        دریافت تعداد سکه‌های مصرف شده امروز

        Returns:
            int: تعداد سکه‌های مصرف شده امروز
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT SUM(ABS(amount)) as total 
                FROM transactions 
                WHERE amount < 0
                AND DATE(created_at) = DATE('now')
            """)
            result = cursor.fetchone()

            return result['total'] if result and result['total'] else 0
        except Exception as e:
            self.logger.error(f"Error in get daily coins spent: {str(e)}")
            return 0

    def _get_weekly_coins_purchased(self):
        """
        دریافت تعداد سکه‌های خریداری شده هفته اخیر

        Returns:
            int: تعداد سکه‌های خریداری شده هفته اخیر
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT SUM(amount) as total 
                FROM transactions 
                WHERE amount > 0 AND transaction_type = 'purchase'
                AND created_at >= date('now', '-7 days')
            """)
            result = cursor.fetchone()

            return result['total'] if result and result['total'] else 0
        except Exception as e:
            self.logger.error(f"Error in get weekly coins purchased: {str(e)}")
            return 0

    def _get_weekly_coins_spent(self):
        """
        دریافت تعداد سکه‌های مصرف شده هفته اخیر

        Returns:
            int: تعداد سکه‌های مصرف شده هفته اخیر
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT SUM(ABS(amount)) as total 
                FROM transactions 
                WHERE amount < 0
                AND created_at >= date('now', '-7 days')
            """)
            result = cursor.fetchone()

            return result['total'] if result and result['total'] else 0
        except Exception as e:
            self.logger.error(f"Error in get weekly coins spent: {str(e)}")
            return 0

    def _get_monthly_coins_purchased(self):
        """
        دریافت تعداد سکه‌های خریداری شده ماه اخیر

        Returns:
            int: تعداد سکه‌های خریداری شده ماه اخیر
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT SUM(amount) as total 
                FROM transactions 
                WHERE amount > 0 AND transaction_type = 'purchase'
                AND created_at >= date('now', '-30 days')
            """)
            result = cursor.fetchone()

            return result['total'] if result and result['total'] else 0
        except Exception as e:
            self.logger.error(f"Error in get monthly coins purchased: {str(e)}")
            return 0

    def _get_monthly_coins_spent(self):
        """
        دریافت تعداد سکه‌های مصرف شده ماه اخیر

        Returns:
            int: تعداد سکه‌های مصرف شده ماه اخیر
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT SUM(ABS(amount)) as total 
                FROM transactions 
                WHERE amount < 0
                AND created_at >= date('now', '-30 days')
            """)
            result = cursor.fetchone()

            return result['total'] if result and result['total'] else 0
        except Exception as e:
            self.logger.error(f"Error in get monthly coins spent: {str(e)}")
            return 0

    def _get_active_users_week(self):
        """
        دریافت تعداد کاربران فعال هفته اخیر

        Returns:
            int: تعداد کاربران فعال هفته اخیر
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) as count FROM users WHERE last_active >= date('now', '-7 days')"
            )
            result = cursor.fetchone()

            return result['count'] if result else 0
        except Exception as e:
            self.logger.error(f"Error in get active users week: {str(e)}")
            return 0

    def _get_active_users_month(self):
        """
        دریافت تعداد کاربران فعال ماه اخیر

        Returns:
            int: تعداد کاربران فعال ماه اخیر
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) as count FROM users WHERE last_active >= date('now', '-30 days')"
            )
            result = cursor.fetchone()

            return result['count'] if result else 0
        except Exception as e:
            self.logger.error(f"Error in get active users month: {str(e)}")
            return 0

    def _get_new_users_count(self, days=1):
        """
        دریافت تعداد کاربران جدید

        Args:
            days (int): تعداد روز

        Returns:
            int: تعداد کاربران جدید
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                f"SELECT COUNT(*) as count FROM users WHERE created_at >= date('now', '-{days} days')"
            )
            result = cursor.fetchone()

            return result['count'] if result else 0
        except Exception as e:
            self.logger.error(f"Error in get new users count: {str(e)}")
            return 0
