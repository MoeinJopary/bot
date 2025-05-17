import logging
from telebot import types
from config.settings import ADMIN_IDS
from handlers.base_handler import BaseHandler
from models.user import User


class UserAdminHandler(BaseHandler):
    """
    کلاس مدیریت کاربران در پنل ادمین
    """

    def __init__(self, bot, db_manager):
        """
        مقداردهی اولیه هندلر ادمین کاربران
        """
        super().__init__(bot, db_manager)
        self.logger = logging.getLogger('chatogram.admin.user_admin')
        self.search_cache = {}  # کش برای نگهداری نتایج جستجو

    def register_handlers(self):
        """
        ثبت هندلرهای مدیریت کاربران
        """

        # جستجوی کاربر
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_user_search")
        def handle_user_search(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if call.from_user.id not in ADMIN_IDS:
                    return

                markup = types.InlineKeyboardMarkup(row_width=1)

                btn_id = types.InlineKeyboardButton("🔍 جستجو با شناسه تلگرام", callback_data="admin_user_search_id")
                btn_username = types.InlineKeyboardButton("🔍 جستجو با یوزرنیم",
                                                          callback_data="admin_user_search_username")
                btn_name = types.InlineKeyboardButton("🔍 جستجو با نام", callback_data="admin_user_search_name")
                btn_back = types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")

                markup.add(btn_id, btn_username, btn_name, btn_back)

                self.bot.edit_message_text(
                    "👤 *جستجوی کاربر*\n\nلطفاً روش جستجو را انتخاب کنید:",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            except Exception as e:
                self.logger.error(f"Error in user search handler: {str(e)}")

        # جستجو با شناسه تلگرام
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_user_search_id")
        def handle_user_search_id(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if call.from_user.id not in ADMIN_IDS:
                    return

                msg = self.bot.edit_message_text(
                    "👤 *جستجوی کاربر با شناسه تلگرام*\n\nلطفاً شناسه تلگرام کاربر مورد نظر را وارد کنید:",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown'
                )

                self.bot.register_next_step_handler(msg, process_user_search_id)
            except Exception as e:
                self.logger.error(f"Error in user search id handler: {str(e)}")

        def process_user_search_id(message):
            try:
                # بررسی دسترسی ادمین
                if message.from_user.id not in ADMIN_IDS:
                    return

                try:
                    user_id = int(message.text.strip())
                except ValueError:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ شناسه تلگرام باید یک عدد صحیح باشد. لطفاً مجدداً تلاش کنید.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                        )
                    )
                    return

                # جستجوی کاربر
                user_data = self.db_manager.get_user_by_telegram_id(user_id)

                if not user_data:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ کاربری با این شناسه یافت نشد.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                        )
                    )
                    return

                # نمایش اطلاعات کاربر
                self.show_user_info(message.chat.id, user_data['id'])
            except Exception as e:
                self.logger.error(f"Error in process user search id: {str(e)}")
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                    )
                )

        # جستجو با یوزرنیم
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_user_search_username")
        def handle_user_search_username(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if call.from_user.id not in ADMIN_IDS:
                    return

                msg = self.bot.edit_message_text(
                    "👤 *جستجوی کاربر با یوزرنیم*\n\nلطفاً یوزرنیم کاربر مورد نظر را وارد کنید (بدون @):",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown'
                )

                self.bot.register_next_step_handler(msg, process_user_search_username)
            except Exception as e:
                self.logger.error(f"Error in user search username handler: {str(e)}")

        def process_user_search_username(message):
            try:
                # بررسی دسترسی ادمین
                if message.from_user.id not in ADMIN_IDS:
                    return

                username = message.text.strip().replace('@', '')

                if not username:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ یوزرنیم نمی‌تواند خالی باشد. لطفاً مجدداً تلاش کنید.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                        )
                    )
                    return

                # جستجوی کاربر
                user_data = self.db_manager.get_user_by_username(username)

                if not user_data:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ کاربری با این یوزرنیم یافت نشد.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                        )
                    )
                    return

                # نمایش اطلاعات کاربر
                self.show_user_info(message.chat.id, user_data['id'])
            except Exception as e:
                self.logger.error(f"Error in process user search username: {str(e)}")
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                    )
                )

        # جستجو با نام
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_user_search_name")
        def handle_user_search_name(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if call.from_user.id not in ADMIN_IDS:
                    return

                msg = self.bot.edit_message_text(
                    "👤 *جستجوی کاربر با نام*\n\nلطفاً نام کاربر مورد نظر را وارد کنید:",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown'
                )

                self.bot.register_next_step_handler(msg, process_user_search_name)
            except Exception as e:
                self.logger.error(f"Error in user search name handler: {str(e)}")

        def process_user_search_name(message):
            try:
                # بررسی دسترسی ادمین
                if message.from_user.id not in ADMIN_IDS:
                    return

                name = message.text.strip()

                if not name or len(name) < 3:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ نام باید حداقل 3 کاراکتر باشد. لطفاً مجدداً تلاش کنید.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                        )
                    )
                    return

                # جستجوی کاربران با نام مشابه
                users = self.db_manager.search_users_by_name(name)

                if not users:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ کاربری با این نام یافت نشد.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                        )
                    )
                    return

                # ذخیره نتایج در کش
                self.search_cache[message.from_user.id] = users

                # نمایش نتایج
                self.show_search_results(message.chat.id, users, 0)
            except Exception as e:
                self.logger.error(f"Error in process user search name: {str(e)}")
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                    )
                )

        # مشاهده کاربر بعدی در نتایج جستجو
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("admin_user_next_"))
        def handle_user_next(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if call.from_user.id not in ADMIN_IDS:
                    return

                # دریافت ایندکس کاربر بعدی
                index = int(call.data.split("_")[3])

                # دریافت نتایج جستجو از کش
                users = self.search_cache.get(call.from_user.id)

                if not users or index >= len(users):
                    self.bot.edit_message_text(
                        "❌ اطلاعات جستجو یافت نشد یا به انتهای لیست رسیده‌اید.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                        )
                    )
                    return

                # نمایش نتایج
                self.show_search_results(call.message.chat.id, users, index, call.message.message_id)
            except Exception as e:
                self.logger.error(f"Error in user next handler: {str(e)}")

        # مسدودسازی کاربر
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_user_ban")
        def handle_user_ban(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if call.from_user.id not in ADMIN_IDS:
                    return

                msg = self.bot.edit_message_text(
                    "⛔ *مسدودسازی کاربر*\n\nلطفاً شناسه تلگرام کاربر مورد نظر را وارد کنید:",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown'
                )

                self.bot.register_next_step_handler(msg, process_user_ban_id)
            except Exception as e:
                self.logger.error(f"Error in user ban handler: {str(e)}")

        def process_user_ban_id(message):
            try:
                # بررسی دسترسی ادمین
                if message.from_user.id not in ADMIN_IDS:
                    return

                try:
                    user_id = int(message.text.strip())
                except ValueError:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ شناسه تلگرام باید یک عدد صحیح باشد. لطفاً مجدداً تلاش کنید.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")
                        )
                    )
                    return

                # جستجوی کاربر
                user_data = self.db_manager.get_user_by_telegram_id(user_id)

                if not user_data:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ کاربری با این شناسه یافت نشد.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")
                        )
                    )
                    return

                # بررسی وضعیت فعلی کاربر
                if user_data.get('is_banned'):
                    # کاربر قبلاً بن شده، پرسیدن برای آنبن
                    self.bot.send_message(
                        message.chat.id,
                        f"⚠️ کاربر «{user_data.get('display_name', 'کاربر ناشناس')}» قبلاً مسدود شده است. آیا می‌خواهید او را از حالت مسدود خارج کنید؟",
                        reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                            types.InlineKeyboardButton("✅ بله", callback_data=f"admin_user_unban_{user_data['id']}"),
                            types.InlineKeyboardButton("❌ خیر", callback_data="admin_users")
                        )
                    )
                else:
                    # درخواست دلیل بن
                    self.bot.send_message(
                        message.chat.id,
                        f"👤 کاربر: {user_data.get('display_name', 'کاربر ناشناس')}\n\nلطفاً دلیل مسدودسازی را وارد کنید:",
                        reply_markup=types.ForceReply(selective=True)
                    )

                    # ذخیره موقت شناسه کاربر
                    if not hasattr(self, 'admin_ban_users'):
                        self.admin_ban_users = {}

                    self.admin_ban_users[message.from_user.id] = user_data['id']

                    self.bot.register_next_step_handler(message, process_user_ban_reason)
            except Exception as e:
                self.logger.error(f"Error in process user ban id: {str(e)}")
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")
                    )
                )

        def process_user_ban_reason(message):
            try:
                # بررسی دسترسی ادمین
                if message.from_user.id not in ADMIN_IDS:
                    return

                # دریافت شناسه کاربر
                if not hasattr(self, 'admin_ban_users') or message.from_user.id not in self.admin_ban_users:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")
                        )
                    )
                    return

                user_id = self.admin_ban_users[message.from_user.id]
                reason = message.text.strip()

                if not reason:
                    reason = "بدون ذکر دلیل"

                # به‌روزرسانی وضعیت کاربر
                success = self.db_manager.update_user(user_id, is_banned=1)

                if success:
                    # ثبت لاگ ادمین
                    user_data = self.db_manager.get_user_by_id(user_id)
                    self.db_manager.add_admin_log(
                        message.from_user.id,
                        "ban_user",
                        f"مسدودسازی کاربر {user_data.get('display_name', 'کاربر ناشناس')} (ID: {user_data.get('telegram_id')}) به دلیل: {reason}"
                    )

                    # پایان دادن به تمام چت‌های فعال کاربر
                    self.db_manager.end_all_active_chats(user_id)

                    # ارسال پیام به کاربر
                    try:
                        self.bot.send_message(
                            user_data['telegram_id'],
                            f"⛔ *حساب شما مسدود شد*\n\nبه دلیل نقض قوانین، حساب کاربری شما در چتوگرام مسدود شده است.\n\nدلیل: {reason}\n\nبرای بررسی مجدد، لطفاً با پشتیبانی تماس بگیرید.",
                            parse_mode='Markdown'
                        )
                    except Exception:
                        pass

                    self.bot.send_message(
                        message.chat.id,
                        f"✅ کاربر «{user_data.get('display_name', 'کاربر ناشناس')}» با موفقیت مسدود شد.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")
                        )
                    )
                else:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ خطا در مسدودسازی کاربر. لطفاً مجدداً تلاش کنید.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")
                        )
                    )

                # حذف اطلاعات موقت
                del self.admin_ban_users[message.from_user.id]
            except Exception as e:
                self.logger.error(f"Error in process user ban reason: {str(e)}")
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")
                    )
                )

        # آنبن کردن کاربر
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("admin_user_unban_"))
        def handle_user_unban(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if call.from_user.id not in ADMIN_IDS:
                    return

                user_id = int(call.data.split("_")[3])

                # به‌روزرسانی وضعیت کاربر
                success = self.db_manager.update_user(user_id, is_banned=0)

                if success:
                    # ثبت لاگ ادمین
                    user_data = self.db_manager.get_user_by_id(user_id)
                    self.db_manager.add_admin_log(
                        call.from_user.id,
                        "unban_user",
                        f"رفع مسدودیت کاربر {user_data.get('display_name', 'کاربر ناشناس')} (ID: {user_data.get('telegram_id')})"
                    )

                    # ارسال پیام به کاربر
                    try:
                        self.bot.send_message(
                            user_data['telegram_id'],
                            "✅ *حساب شما از حالت مسدود خارج شد*\n\nمحدودیت حساب کاربری شما در چتوگرام برداشته شده است و اکنون می‌توانید از تمام امکانات ربات استفاده کنید.",
                            parse_mode='Markdown'
                        )
                    except Exception:
                        pass

                    self.bot.edit_message_text(
                        f"✅ کاربر «{user_data.get('display_name', 'کاربر ناشناس')}» با موفقیت از حالت مسدود خارج شد.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")
                        )
                    )
                else:
                    self.bot.edit_message_text(
                        "❌ خطا در رفع مسدودیت کاربر. لطفاً مجدداً تلاش کنید.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")
                        )
                    )
            except Exception as e:
                self.logger.error(f"Error in user unban handler: {str(e)}")

        # تأیید عکس پروفایل
        @self.bot.callback_query_handler(func=lambda call: call.data == "admin_user_verify")
        def handle_user_verify(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if call.from_user.id not in ADMIN_IDS:
                    return

                # دریافت عکس‌های پروفایل در انتظار تأیید
                pending_profiles = self.db_manager.get_pending_profile_pics(10)

                if not pending_profiles:
                    self.bot.edit_message_text(
                        "✅ در حال حاضر هیچ عکس پروفایلی در انتظار تأیید نیست.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")
                        )
                    )
                    return

                # ذخیره موقت لیست عکس‌ها
                if not hasattr(self, 'pending_profiles'):
                    self.pending_profiles = {}

                self.pending_profiles[call.from_user.id] = pending_profiles

                # نمایش اولین عکس
                self.show_pending_profile(call.message.chat.id, pending_profiles[0], call.message.message_id)
            except Exception as e:
                self.logger.error(f"Error in user verify handler: {str(e)}")

        # مشاهده اقدامات کاربر
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("admin_user_actions_"))
        def handle_user_actions(call):
            try:
                self.bot.answer_callback_query(call.id)

                # بررسی دسترسی ادمین
                if call.from_user.id not in ADMIN_IDS:
                    return

                user_id = int(call.data.split("_")[3])

                # دریافت اطلاعات کاربر
                user_data = self.db_manager.get_user_by_id(user_id)

                if not user_data:
                    self.bot.edit_message_text(
                        "❌ کاربر یافت نشد.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                        )
                    )
                    return

                # نمایش منوی اقدامات
                markup = types.InlineKeyboardMarkup(row_width=1)

                if user_data.get('is_banned'):
                    btn_ban = types.InlineKeyboardButton("✅ رفع مسدودیت", callback_data=f"admin_user_unban_{user_id}")
                else:
                    btn_ban = types.InlineKeyboardButton("⛔ مسدودسازی",
                                                         callback_data=f"admin_user_ban_direct_{user_id}")

                btn_add_coins = types.InlineKeyboardButton("💰 افزودن سکه",
                                                           callback_data=f"admin_user_add_coins_{user_id}")
                btn_chats = types.InlineKeyboardButton("💬 چت‌های فعال", callback_data=f"admin_user_chats_{user_id}")
                btn_reports = types.InlineKeyboardButton("🚩 گزارش‌های تخلف",
                                                         callback_data=f"admin_user_reports_{user_id}")
                btn_transactions = types.InlineKeyboardButton("💳 تراکنش‌ها",
                                                              callback_data=f"admin_user_transactions_{user_id}")
                btn_back = types.InlineKeyboardButton("🔙 بازگشت", callback_data=f"admin_user_info_{user_id}")

                markup.add(btn_ban, btn_add_coins, btn_chats, btn_reports, btn_transactions, btn_back)

                self.bot.edit_message_text(
                    f"👤 *اقدامات کاربر*\n\nکاربر: {user_data.get('display_name', 'کاربر ناشناس')}\nشناسه تلگرام: {user_data.get('telegram_id')}\n\nلطفاً اقدام مورد نظر خود را انتخاب کنید:",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            except Exception as e:
                self.logger.error(f"Error in user actions handler: {str(e)}")

    def show_user_info(self, chat_id, user_id, message_id=None):
        """
        نمایش اطلاعات کاربر

        Args:
            chat_id: شناسه چت
            user_id: شناسه کاربر
            message_id: شناسه پیام (در صورتی که می‌خواهیم پیام را ویرایش کنیم)
        """
        try:
            # دریافت اطلاعات کاربر
            user_data = self.db_manager.get_user_by_id(user_id)

            if not user_data:
                if message_id:
                    self.bot.edit_message_text(
                        "❌ کاربر یافت نشد.",
                        chat_id,
                        message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                        )
                    )
                else:
                    self.bot.send_message(
                        chat_id,
                        "❌ کاربر یافت نشد.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                        )
                    )
                return

            # آماده‌سازی اطلاعات کاربر
            user_model = User(self.db_manager, user_data=user_data)

            gender_text = {
                "male": "مرد 👨",
                "female": "زن 👩",
                "other": "سایر 🤖"
            }.get(user_data.get('gender', ''), "تعیین نشده")

            ban_status = "✅ فعال" if not user_data.get('is_banned') else "⛔ مسدود"
            online_status = "🟢 آنلاین" if user_data.get('is_online') else "⚪ آفلاین"

            # آماده‌سازی متن اطلاعات کاربر
            info_text = f"👤 *اطلاعات کاربر*\n\n"
            info_text += f"🔹 *نام*: {user_data.get('display_name', 'کاربر ناشناس')}\n"
            info_text += f"🔹 *یوزرنیم*: {'@' + user_data.get('username') if user_data.get('username') else 'ندارد'}\n"
            info_text += f"🔹 *شناسه تلگرام*: {user_data.get('telegram_id')}\n"
            info_text += f"🔹 *شناسه داخلی*: {user_data.get('id')}\n"

            if user_data.get('age'):
                info_text += f"🔹 *سن*: {user_data.get('age')} سال\n"
            else:
                info_text += f"🔹 *سن*: تعیین نشده\n"

            info_text += f"🔹 *جنسیت*: {gender_text}\n"

            if user_data.get('city'):
                info_text += f"🔹 *شهر*: {user_data.get('city')}\n"

            info_text += f"🔹 *سکه‌ها*: {user_data.get('coins', 0)}\n"
            info_text += f"🔹 *وضعیت*: {ban_status}\n"
            info_text += f"🔹 *آنلاین*: {online_status}\n"
            info_text += f"🔹 *تاریخ ثبت‌نام*: {user_data.get('created_at')}\n"
            info_text += f"🔹 *آخرین فعالیت*: {user_data.get('last_active')}\n"

            info_text += f"\n📝 *بیوگرافی*:\n{user_data.get('bio', 'هنوز اطلاعاتی وارد نشده!')}"

            # آماده‌سازی دکمه‌ها
            markup = types.InlineKeyboardMarkup(row_width=1)

            btn_actions = types.InlineKeyboardButton("⚙️ اقدامات", callback_data=f"admin_user_actions_{user_id}")
            btn_back = types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")

            markup.add(btn_actions, btn_back)

            # ارسال پیام
            if user_data.get('profile_pic'):
                try:
                    if message_id:
                        # حذف پیام قبلی
                        self.bot.delete_message(chat_id, message_id)

                    # ارسال پیام جدید با عکس
                    self.bot.send_photo(
                        chat_id,
                        user_data['profile_pic'],
                        caption=info_text,
                        parse_mode='Markdown',
                        reply_markup=markup
                    )
                except Exception:
                    # در صورت خطا، ارسال بدون عکس
                    if message_id:
                        self.bot.edit_message_text(
                            info_text,
                            chat_id,
                            message_id,
                            parse_mode='Markdown',
                            reply_markup=markup
                        )
                    else:
                        self.bot.send_message(
                            chat_id,
                            info_text,
                            parse_mode='Markdown',
                            reply_markup=markup
                        )
            else:
                if message_id:
                    self.bot.edit_message_text(
                        info_text,
                        chat_id,
                        message_id,
                        parse_mode='Markdown',
                        reply_markup=markup
                    )
                else:
                    self.bot.send_message(
                        chat_id,
                        info_text,
                        parse_mode='Markdown',
                        reply_markup=markup
                    )
        except Exception as e:
            self.logger.error(f"Error in show user info: {str(e)}")

            if message_id:
                self.bot.edit_message_text(
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    chat_id,
                    message_id,
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                    )
                )
            else:
                self.bot.send_message(
                    chat_id,
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                    )
                )

    def show_search_results(self, chat_id, users, index, message_id=None):
        """
        نمایش نتایج جستجو

        Args:
            chat_id: شناسه چت
            users: لیست کاربران
            index: ایندکس کاربر فعلی
            message_id: شناسه پیام (در صورتی که می‌خواهیم پیام را ویرایش کنیم)
        """
        try:
            if not users or index >= len(users):
                if message_id:
                    self.bot.edit_message_text(
                        "❌ کاربری یافت نشد یا به انتهای لیست رسیده‌اید.",
                        chat_id,
                        message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                        )
                    )
                else:
                    self.bot.send_message(
                        chat_id,
                        "❌ کاربری یافت نشد یا به انتهای لیست رسیده‌اید.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                        )
                    )
                return

            # دریافت کاربر فعلی
            user = users[index]

            # ساخت متن نتیجه
            result_text = f"👤 *نتیجه {index + 1} از {len(users)}*\n\n"
            result_text += f"🔹 *نام*: {user.get('display_name', 'کاربر ناشناس')}\n"
            result_text += f"🔹 *یوزرنیم*: {'@' + user.get('username') if user.get('username') else 'ندارد'}\n"
            result_text += f"🔹 *شناسه تلگرام*: {user.get('telegram_id')}\n"

            if user.get('gender'):
                gender_text = {
                    "male": "مرد 👨",
                    "female": "زن 👩",
                    "other": "سایر 🤖"
                }.get(user.get('gender', ''), "نامشخص")
                result_text += f"🔹 *جنسیت*: {gender_text}\n"

            # ساخت دکمه‌ها
            markup = types.InlineKeyboardMarkup(row_width=2)

            btn_view = types.InlineKeyboardButton("👁 مشاهده کامل", callback_data=f"admin_user_info_{user['id']}")

            if index < len(users) - 1:
                btn_next = types.InlineKeyboardButton("➡️ بعدی", callback_data=f"admin_user_next_{index + 1}")
                markup.add(btn_view, btn_next)
            else:
                markup.add(btn_view)

            markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search"))

            # ارسال پیام
            if message_id:
                self.bot.edit_message_text(
                    result_text,
                    chat_id,
                    message_id,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            else:
                self.bot.send_message(
                    chat_id,
                    result_text,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
        except Exception as e:
            self.logger.error(f"Error in show search results: {str(e)}")

            if message_id:
                self.bot.edit_message_text(
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    chat_id,
                    message_id,
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                    )
                )
            else:
                self.bot.send_message(
                    chat_id,
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_user_search")
                    )
                )

    def show_pending_profile(self, chat_id, profile, message_id=None):
        """
        نمایش عکس پروفایل در انتظار تأیید

        Args:
            chat_id: شناسه چت
            profile: اطلاعات پروفایل
            message_id: شناسه پیام (در صورتی که می‌خواهیم پیام را ویرایش کنیم)
        """
        try:
            # ساخت متن توضیحات
            info_text = f"🖼 *عکس پروفایل در انتظار تأیید*\n\n"
            info_text += f"👤 کاربر: {profile.get('display_name', 'کاربر ناشناس')}\n"
            info_text += f"🆔 شناسه تلگرام: {profile.get('telegram_id')}\n"
            info_text += f"📅 تاریخ درخواست: {profile.get('last_active')}\n\n"
            info_text += "آیا این عکس پروفایل را تأیید می‌کنید؟"

            # ساخت دکمه‌ها
            markup = types.InlineKeyboardMarkup(row_width=2)

            btn_approve = types.InlineKeyboardButton("✅ تأیید", callback_data=f"approve_pic_{profile['telegram_id']}")
            btn_reject = types.InlineKeyboardButton("❌ رد", callback_data=f"reject_pic_{profile['telegram_id']}")

            # اضافه کردن دکمه‌های صفحه‌بندی در صورت نیاز
            btn_back = types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")

            markup.add(btn_approve, btn_reject)
            markup.add(btn_back)

            # ارسال عکس
            if message_id:
                # حذف پیام قبلی
                self.bot.delete_message(chat_id, message_id)

            self.bot.send_photo(
                chat_id,
                profile['profile_pic'],
                caption=info_text,
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception as e:
            self.logger.error(f"Error in show pending profile: {str(e)}")

            if message_id:
                self.bot.edit_message_text(
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    chat_id,
                    message_id,
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")
                    )
                )
            else:
                self.bot.send_message(
                    chat_id,
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")
                    )
                )
