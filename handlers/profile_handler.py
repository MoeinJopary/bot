from telebot import types
from handlers.base_handler import BaseHandler
from utils.keyboard_generator import KeyboardGenerator
from config.constants import MESSAGES, GENDERS


class ProfileHandler(BaseHandler):
    """
    کلاس مدیریت پروفایل کاربر
    """

    def register_handlers(self):
        """
        ثبت هندلرهای پیام
        """

        # نمایش پروفایل
        @self.bot.message_handler(func=lambda message: message.text == "👤 پروفایل من")
        def handle_profile(message):
            try:
                self.update_user_status(message)

                user = self.get_user(message.from_user.id)
                profile_text = user.get_profile_text()

                self.bot.send_message(
                    message.chat.id,
                    profile_text,
                    parse_mode='Markdown',
                    reply_markup=KeyboardGenerator.get_profile_menu()
                )
            except Exception as e:
                self.logger.error(f"Error in profile handler: {str(e)}")

        # ویرایش نام
        @self.bot.callback_query_handler(func=lambda call: call.data == "edit_name")
        def handle_edit_name(call):
            try:
                self.bot.answer_callback_query(call.id)

                msg = self.bot.send_message(
                    call.message.chat.id,
                    "لطفاً نام جدید خود را وارد کنید (حداقل 3 و حداکثر 20 کاراکتر):",
                    reply_markup=types.ForceReply(selective=True)
                )

                self.bot.register_next_step_handler(msg, process_name_step)
            except Exception as e:
                self.logger.error(f"Error in edit name handler: {str(e)}")

        def process_name_step(message):
            try:
                if len(message.text) < 3 or len(message.text) > 20:
                    msg = self.bot.send_message(
                        message.chat.id,
                        "نام باید بین 3 تا 20 کاراکتر باشد. لطفاً مجدداً تلاش کنید:",
                        reply_markup=types.ForceReply(selective=True)
                    )
                    self.bot.register_next_step_handler(msg, process_name_step)
                    return

                user = self.get_user(message.from_user.id)
                success = user.update_profile('display_name', message.text)

                if success:
                    self.bot.send_message(
                        message.chat.id,
                        f"✅ نام شما به «{message.text}» تغییر یافت.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
                else:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ خطا در به‌روزرسانی نام. لطفاً مجدداً تلاش کنید.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
            except Exception as e:
                self.logger.error(f"Error in process name step: {str(e)}")
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=KeyboardGenerator.get_main_menu()
                )

        # ویرایش سن
        @self.bot.callback_query_handler(func=lambda call: call.data == "edit_age")
        def handle_edit_age(call):
            try:
                self.bot.answer_callback_query(call.id)

                msg = self.bot.send_message(
                    call.message.chat.id,
                    "لطفاً سن خود را وارد کنید (بین 18 تا 99 سال):",
                    reply_markup=types.ForceReply(selective=True)
                )

                self.bot.register_next_step_handler(msg, process_age_step)
            except Exception as e:
                self.logger.error(f"Error in edit age handler: {str(e)}")

        def process_age_step(message):
            try:
                try:
                    age = int(message.text)
                except ValueError:
                    msg = self.bot.send_message(
                        message.chat.id,
                        "لطفاً یک عدد صحیح وارد کنید:",
                        reply_markup=types.ForceReply(selective=True)
                    )
                    self.bot.register_next_step_handler(msg, process_age_step)
                    return

                if age < 18 or age > 99:
                    msg = self.bot.send_message(
                        message.chat.id,
                        "سن باید بین 18 تا 99 سال باشد. لطفاً مجدداً تلاش کنید:",
                        reply_markup=types.ForceReply(selective=True)
                    )
                    self.bot.register_next_step_handler(msg, process_age_step)
                    return

                user = self.get_user(message.from_user.id)
                success = user.update_profile('age', age)

                if success:
                    self.bot.send_message(
                        message.chat.id,
                        f"✅ سن شما به {age} سال تغییر یافت.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
                else:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ خطا در به‌روزرسانی سن. لطفاً مجدداً تلاش کنید.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
            except Exception as e:
                self.logger.error(f"Error in process age step: {str(e)}")
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=KeyboardGenerator.get_main_menu()
                )

        # ویرایش جنسیت
        @self.bot.callback_query_handler(func=lambda call: call.data == "edit_gender")
        def handle_edit_gender(call):
            try:
                self.bot.answer_callback_query(call.id)

                self.bot.edit_message_text(
                    "لطفاً جنسیت خود را انتخاب کنید:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=KeyboardGenerator.get_gender_selection()
                )
            except Exception as e:
                self.logger.error(f"Error in edit gender handler: {str(e)}")

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("gender_"))
        def handle_gender_selection(call):
            try:
                self.bot.answer_callback_query(call.id)

                gender_index = int(call.data.split("_")[1])

                gender_map = {
                    0: "male",
                    1: "female",
                    2: "other"
                }

                gender = gender_map.get(gender_index, "other")
                gender_text = GENDERS[gender_index]

                user = self.get_user(call.from_user.id)
                success = user.update_profile('gender', gender)

                if success:
                    self.bot.edit_message_text(
                        f"✅ جنسیت شما به {gender_text} تغییر یافت.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=None
                    )
                else:
                    self.bot.edit_message_text(
                        "❌ خطا در به‌روزرسانی جنسیت. لطفاً مجدداً تلاش کنید.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=None
                    )
            except Exception as e:
                self.logger.error(f"Error in gender selection handler: {str(e)}")

        # ویرایش شهر
        @self.bot.callback_query_handler(func=lambda call: call.data == "edit_city")
        def handle_edit_city(call):
            try:
                self.bot.answer_callback_query(call.id)

                msg = self.bot.send_message(
                    call.message.chat.id,
                    "لطفاً شهر خود را وارد کنید:",
                    reply_markup=types.ForceReply(selective=True)
                )

                self.bot.register_next_step_handler(msg, process_city_step)
            except Exception as e:
                self.logger.error(f"Error in edit city handler: {str(e)}")

        def process_city_step(message):
            try:
                if len(message.text) < 2 or len(message.text) > 50:
                    msg = self.bot.send_message(
                        message.chat.id,
                        "نام شهر باید بین 2 تا 50 کاراکتر باشد. لطفاً مجدداً تلاش کنید:",
                        reply_markup=types.ForceReply(selective=True)
                    )
                    self.bot.register_next_step_handler(msg, process_city_step)
                    return

                user = self.get_user(message.from_user.id)
                success = user.update_profile('city', message.text)

                if success:
                    self.bot.send_message(
                        message.chat.id,
                        f"✅ شهر شما به «{message.text}» تغییر یافت.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
                else:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ خطا در به‌روزرسانی شهر. لطفاً مجدداً تلاش کنید.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
            except Exception as e:
                self.logger.error(f"Error in process city step: {str(e)}")
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=KeyboardGenerator.get_main_menu()
                )

        # ویرایش بیوگرافی
        @self.bot.callback_query_handler(func=lambda call: call.data == "edit_bio")
        def handle_edit_bio(call):
            try:
                self.bot.answer_callback_query(call.id)

                msg = self.bot.send_message(
                    call.message.chat.id,
                    "لطفاً بیوگرافی خود را وارد کنید (حداکثر 500 کاراکتر):",
                    reply_markup=types.ForceReply(selective=True)
                )

                self.bot.register_next_step_handler(msg, process_bio_step)
            except Exception as e:
                self.logger.error(f"Error in edit bio handler: {str(e)}")

        def process_bio_step(message):
            try:
                if len(message.text) > 500:
                    msg = self.bot.send_message(
                        message.chat.id,
                        "بیوگرافی نمی‌تواند بیش از 500 کاراکتر باشد. لطفاً مجدداً تلاش کنید:",
                        reply_markup=types.ForceReply(selective=True)
                    )
                    self.bot.register_next_step_handler(msg, process_bio_step)
                    return

                user = self.get_user(message.from_user.id)
                success = user.update_profile('bio', message.text)

                if success:
                    self.bot.send_message(
                        message.chat.id,
                        "✅ بیوگرافی شما با موفقیت به‌روزرسانی شد.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
                else:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ خطا در به‌روزرسانی بیوگرافی. لطفاً مجدداً تلاش کنید.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
            except Exception as e:
                self.logger.error(f"Error in process bio step: {str(e)}")
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=KeyboardGenerator.get_main_menu()
                )

        # آپلود عکس پروفایل
        @self.bot.callback_query_handler(func=lambda call: call.data == "edit_pic")
        def handle_edit_pic(call):
            try:
                self.bot.answer_callback_query(call.id)

                msg = self.bot.send_message(
                    call.message.chat.id,
                    "لطفاً عکس پروفایل خود را ارسال کنید.\n\n⚠️ توجه: عکس شما پس از تأیید توسط ادمین نمایش داده خواهد شد."
                )

                self.bot.register_next_step_handler(msg, process_profile_pic)
            except Exception as e:
                self.logger.error(f"Error in edit pic handler: {str(e)}")

        def process_profile_pic(message):
            try:
                if not message.photo:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ لطفاً یک تصویر ارسال کنید.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
                    return

                # دریافت آیدی فایل عکس با بالاترین کیفیت
                file_id = message.photo[-1].file_id

                user = self.get_user(message.from_user.id)
                success = user.update_profile('profile_pic', file_id)

                if success:
                    # ارسال پیام به ادمین برای تأیید
                    for admin_id in self.db_manager.get_admins():
                        try:
                            self.bot.send_photo(
                                admin_id,
                                file_id,
                                caption=f"درخواست تأیید عکس پروفایل\nکاربر: {user.data.get('display_name', 'کاربر ناشناس')}\nآیدی: {message.from_user.id}",
                                reply_markup=types.InlineKeyboardMarkup().add(
                                    types.InlineKeyboardButton("✅ تأیید",
                                                               callback_data=f"approve_pic_{message.from_user.id}"),
                                    types.InlineKeyboardButton("❌ رد",
                                                               callback_data=f"reject_pic_{message.from_user.id}")
                                )
                            )
                        except Exception:
                            continue

                    self.bot.send_message(
                        message.chat.id,
                        "✅ عکس پروفایل شما ارسال شد و در انتظار تأیید ادمین است.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
                else:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ خطا در آپلود عکس پروفایل. لطفاً مجدداً تلاش کنید.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
            except Exception as e:
                self.logger.error(f"Error in process profile pic: {str(e)}")
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=KeyboardGenerator.get_main_menu()
                )

        # انصراف از ویرایش
        @self.bot.callback_query_handler(func=lambda call: call.data == "cancel_edit")
        def handle_cancel_edit(call):
            try:
                self.bot.answer_callback_query(call.id)

                user = self.get_user(call.from_user.id)
                profile_text = user.get_profile_text()

                self.bot.edit_message_text(
                    profile_text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=KeyboardGenerator.get_profile_menu()
                )
            except Exception as e:
                self.logger.error(f"Error in cancel edit handler: {str(e)}")

