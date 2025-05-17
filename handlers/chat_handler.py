import json
from telebot import types
from handlers.base_handler import BaseHandler
from utils.keyboard_generator import KeyboardGenerator
from config.constants import MESSAGES
from models.chat import Chat
from models.user import User


class ChatHandler(BaseHandler):
    """
    کلاس مدیریت چت ناشناس
    """

    def register_handlers(self):
        """
        ثبت هندلرهای پیام
        """

        # شروع چت ناشناس
        @self.bot.message_handler(func=lambda message: message.text == "🔗 به یک ناشناس وصلم کن!")
        def handle_random_chat(message):
            try:
                self.update_user_status(message)

                user = self.get_user(message.from_user.id)

                # بررسی اینکه آیا کاربر چت فعال دارد
                active_chat = user.get_active_chat()
                if active_chat:
                    self.bot.send_message(
                        message.chat.id,
                        "⚠️ شما یک چت فعال دارید. ابتدا باید آن را پایان دهید.",
                        reply_markup=KeyboardGenerator.get_chat_menu()
                    )
                    return

                # ارسال پیام در حال جستجو
                self.bot.send_message(
                    message.chat.id,
                    MESSAGES['random_chat_start']
                )

                # جستجوی کاربر تصادفی
                partner = self.db_manager.find_random_partner(user.data['id'])

                if partner:
                    # ایجاد چت جدید
                    chat = Chat.create(self.db_manager, user.data['id'], partner['id'])

                    # ارسال پیام به هر دو کاربر
                    self.bot.send_message(
                        message.chat.id,
                        MESSAGES['random_chat_connected'],
                        reply_markup=KeyboardGenerator.get_chat_menu()
                    )

                    self.bot.send_message(
                        partner['telegram_id'],
                        MESSAGES['random_chat_connected'],
                        reply_markup=KeyboardGenerator.get_chat_menu()
                    )
                else:
                    self.bot.send_message(
                        message.chat.id,
                        "😕 متأسفانه در حال حاضر کاربری برای چت پیدا نشد. لطفاً بعداً دوباره تلاش کنید.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
            except Exception as e:
                self.logger.error(f"Error in random chat handler: {str(e)}")

        # جستجوی کاربر خاص (مرد)
        @self.bot.callback_query_handler(func=lambda call: call.data == "search_random_male")
        def handle_search_random_male(call):
            try:
                self.bot.answer_callback_query(call.id)

                user = self.get_user(call.from_user.id)

                # بررسی اینکه آیا کاربر چت فعال دارد
                active_chat = user.get_active_chat()
                if active_chat:
                    self.bot.send_message(
                        call.message.chat.id,
                        "⚠️ شما یک چت فعال دارید. ابتدا باید آن را پایان دهید.",
                        reply_markup=KeyboardGenerator.get_chat_menu()
                    )
                    return

                # ارسال پیام در حال جستجو
                self.bot.edit_message_text(
                    "🔄 در حال جستجو برای یک پسر...\nلطفاً صبر کنید.",
                    call.message.chat.id,
                    call.message.message_id
                )

                # جستجوی کاربر تصادفی مرد
                partner = self.db_manager.find_random_partner(user.data['id'], gender="male")

                if partner:
                    # ایجاد چت جدید
                    chat = Chat.create(self.db_manager, user.data['id'], partner['id'])

                    # ارسال پیام به هر دو کاربر
                    self.bot.send_message(
                        call.message.chat.id,
                        MESSAGES['random_chat_connected'],
                        reply_markup=KeyboardGenerator.get_chat_menu()
                    )

                    self.bot.send_message(
                        partner['telegram_id'],
                        MESSAGES['random_chat_connected'],
                        reply_markup=KeyboardGenerator.get_chat_menu()
                    )
                else:
                    self.bot.edit_message_text(
                        "😕 متأسفانه در حال حاضر پسری برای چت پیدا نشد. لطفاً بعداً دوباره تلاش کنید.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=KeyboardGenerator.get_search_menu()
                    )
            except Exception as e:
                self.logger.error(f"Error in search random male handler: {str(e)}")

        # جستجوی کاربر خاص (زن)
        @self.bot.callback_query_handler(func=lambda call: call.data == "search_random_female")
        def handle_search_random_female(call):
            try:
                self.bot.answer_callback_query(call.id)

                user = self.get_user(call.from_user.id)

                # بررسی اینکه آیا کاربر چت فعال دارد
                active_chat = user.get_active_chat()
                if active_chat:
                    self.bot.send_message(
                        call.message.chat.id,
                        "⚠️ شما یک چت فعال دارید. ابتدا باید آن را پایان دهید.",
                        reply_markup=KeyboardGenerator.get_chat_menu()
                    )
                    return

                # ارسال پیام در حال جستجو
                self.bot.edit_message_text(
                    "🔄 در حال جستجو برای یک دختر...\nلطفاً صبر کنید.",
                    call.message.chat.id,
                    call.message.message_id
                )

                # جستجوی کاربر تصادفی زن
                partner = self.db_manager.find_random_partner(user.data['id'], gender="female")

                if partner:
                    # ایجاد چت جدید
                    chat = Chat.create(self.db_manager, user.data['id'], partner['id'])

                    # ارسال پیام به هر دو کاربر
                    self.bot.send_message(
                        call.message.chat.id,
                        MESSAGES['random_chat_connected'],
                        reply_markup=KeyboardGenerator.get_chat_menu()
                    )

                    self.bot.send_message(
                        partner['telegram_id'],
                        MESSAGES['random_chat_connected'],
                        reply_markup=KeyboardGenerator.get_chat_menu()
                    )
                else:
                    self.bot.edit_message_text(
                        "😕 متأسفانه در حال حاضر دختری برای چت پیدا نشد. لطفاً بعداً دوباره تلاش کنید.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=KeyboardGenerator.get_search_menu()
                    )
            except Exception as e:
                self.logger.error(f"Error in search random female handler: {str(e)}")

        # جستجوی کاربر تصادفی (هر جنسیتی)
        @self.bot.callback_query_handler(func=lambda call: call.data == "search_random_any")
        def handle_search_random_any(call):
            try:
                self.bot.answer_callback_query(call.id)

                user = self.get_user(call.from_user.id)

                # بررسی اینکه آیا کاربر چت فعال دارد
                active_chat = user.get_active_chat()
                if active_chat:
                    self.bot.send_message(
                        call.message.chat.id,
                        "⚠️ شما یک چت فعال دارید. ابتدا باید آن را پایان دهید.",
                        reply_markup=KeyboardGenerator.get_chat_menu()
                    )
                    return

                # ارسال پیام در حال جستجو
                self.bot.edit_message_text(
                    "🔄 در حال جستجو برای یک کاربر...\nلطفاً صبر کنید.",
                    call.message.chat.id,
                    call.message.message_id
                )

                # جستجوی کاربر تصادفی با هر جنسیتی
                partner = self.db_manager.find_random_partner(user.data['id'])

                if partner:
                    # ایجاد چت جدید
                    chat = Chat.create(self.db_manager, user.data['id'], partner['id'])

                    # ارسال پیام به هر دو کاربر
                    self.bot.send_message(
                        call.message.chat.id,
                        MESSAGES['random_chat_connected'],
                        reply_markup=KeyboardGenerator.get_chat_menu()
                    )

                    self.bot.send_message(
                        partner['telegram_id'],
                        MESSAGES['random_chat_connected'],
                        reply_markup=KeyboardGenerator.get_chat_menu()
                    )
                else:
                    self.bot.edit_message_text(
                        "😕 متأسفانه در حال حاضر کاربری برای چت پیدا نشد. لطفاً بعداً دوباره تلاش کنید.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=KeyboardGenerator.get_search_menu()
                    )
            except Exception as e:
                self.logger.error(f"Error in search random any handler: {str(e)}")

        # پایان دادن به چت
        @self.bot.message_handler(func=lambda message: message.text == "⛔ پایان چت")
        def handle_end_chat(message):
            try:
                self.update_user_status(message)

                user = self.get_user(message.from_user.id)
                active_chat = user.get_active_chat()

                if not active_chat:
                    self.bot.send_message(
                        message.chat.id,
                        "⚠️ شما هیچ چت فعالی ندارید.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
                    return

                # دریافت کاربر مقابل
                partner_id = active_chat['user1_id'] if active_chat['user2_id'] == user.data['id'] else active_chat[
                    'user2_id']
                partner = User(self.db_manager, user_data=self.db_manager.get_user_by_telegram_id(partner_id))

                # پایان دادن به چت
                chat = Chat(self.db_manager, chat_id=active_chat['id'])
                chat.end()

                # ارسال پیام به هر دو کاربر
                self.bot.send_message(
                    message.chat.id,
                    MESSAGES['chat_ended'],
                    reply_markup=KeyboardGenerator.get_main_menu()
                )

                if partner and partner.data:
                    self.bot.send_message(
                        partner.data['telegram_id'],
                        MESSAGES['chat_ended'],
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
            except Exception as e:
                self.logger.error(f"Error in end chat handler: {str(e)}")

        # مشاهده پروفایل طرف مقابل در چت
        @self.bot.message_handler(func=lambda message: message.text == "👤 مشاهده پروفایل مقابل")
        def handle_view_partner_profile(message):
            try:
                self.update_user_status(message)

                user = self.get_user(message.from_user.id)
                active_chat = user.get_active_chat()

                if not active_chat:
                    self.bot.send_message(
                        message.chat.id,
                        "⚠️ شما هیچ چت فعالی ندارید.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
                    return

                # دریافت کاربر مقابل
                partner_id = active_chat['user1_id'] if active_chat['user2_id'] == user.data['id'] else active_chat[
                    'user2_id']
                partner = User(self.db_manager, user_data=self.db_manager.get_user_by_telegram_id(partner_id))

                if partner and partner.data:
                    # نمایش پروفایل طرف مقابل
                    profile_text = partner.get_profile_text()

                    self.bot.send_message(
                        message.chat.id,
                        profile_text,
                        parse_mode='Markdown'
                    )
                else:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ خطا در دریافت اطلاعات کاربر مقابل.",
                        reply_markup=KeyboardGenerator.get_chat_menu()
                    )
            except Exception as e:
                self.logger.error(f"Error in view partner profile handler: {str(e)}")

        # فعال‌سازی چت خصوصی
        @self.bot.message_handler(func=lambda message: message.text == "🔓 فعال‌سازی چت خصوصی")
        def handle_private_chat_request(message):
            try:
                self.update_user_status(message)

                user = self.get_user(message.from_user.id)
                active_chat = user.get_active_chat()

                if not active_chat:
                    self.bot.send_message(
                        message.chat.id,
                        "⚠️ شما هیچ چت فعالی ندارید.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
                    return

                # دریافت کاربر مقابل
                partner_id = active_chat['user1_id'] if active_chat['user2_id'] == user.data['id'] else active_chat[
                    'user2_id']
                partner = User(self.db_manager, user_data=self.db_manager.get_user_by_telegram_id(partner_id))

                if partner and partner.data:
                    # ارسال درخواست به طرف مقابل
                    self.bot.send_message(
                        partner.data['telegram_id'],
                        f"🔓 کاربر مقابل می‌خواهد چت را از حالت ناشناس خارج کند. آیا موافق هستید؟",
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("✅ بله", callback_data="accept_private_chat"),
                            types.InlineKeyboardButton("❌ خیر", callback_data="reject_private_chat")
                        )
                    )

                    self.bot.send_message(
                        message.chat.id,
                        "🔄 درخواست شما برای فعال‌سازی چت خصوصی ارسال شد. منتظر پاسخ کاربر مقابل باشید."
                    )
                else:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ خطا در دریافت اطلاعات کاربر مقابل.",
                        reply_markup=KeyboardGenerator.get_chat_menu()
                    )
            except Exception as e:
                self.logger.error(f"Error in private chat request handler: {str(e)}")

        # پذیرش درخواست چت خصوصی
        @self.bot.callback_query_handler(func=lambda call: call.data == "accept_private_chat")
        def handle_accept_private_chat(call):
            try:
                self.bot.answer_callback_query(call.id)

                user = self.get_user(call.from_user.id)
                active_chat = user.get_active_chat()

                if not active_chat:
                    self.bot.edit_message_text(
                        "⚠️ چت قبلاً پایان یافته است.",
                        call.message.chat.id,
                        call.message.message_id
                    )
                    return

                # دریافت کاربر مقابل
                partner_id = active_chat['user1_id'] if active_chat['user2_id'] == user.data['id'] else active_chat[
                    'user2_id']
                partner = User(self.db_manager, user_data=self.db_manager.get_user_by_telegram_id(partner_id))

                if partner and partner.data:
                    # ارسال پیام به هر دو کاربر
                    self.bot.edit_message_text(
                        "✅ شما درخواست چت خصوصی را پذیرفتید.",
                        call.message.chat.id,
                        call.message.message_id
                    )

                    # ارسال اطلاعات تماس به هر دو طرف
                    user_contact = f"اطلاعات تماس طرف مقابل:\nنام: {partner.data.get('display_name', 'کاربر ناشناس')}\n"
                    if partner.data.get('username'):
                        user_contact += f"یوزرنیم: @{partner.data.get('username')}\n"

                    partner_contact = f"اطلاعات تماس طرف مقابل:\nنام: {user.data.get('display_name', 'کاربر ناشناس')}\n"
                    if user.data.get('username'):
                        partner_contact += f"یوزرنیم: @{user.data.get('username')}\n"

                    self.bot.send_message(
                        call.message.chat.id,
                        user_contact
                    )

                    self.bot.send_message(
                        partner.data['telegram_id'],
                        f"✅ کاربر مقابل درخواست چت خصوصی را پذیرفت.\n\n{partner_contact}"
                    )
                else:
                    self.bot.edit_message_text(
                        "❌ خطا در دریافت اطلاعات کاربر مقابل.",
                        call.message.chat.id,
                        call.message.message_id
                    )
            except Exception as e:
                self.logger.error(f"Error in accept private chat handler: {str(e)}")

        # رد درخواست چت خصوصی
        @self.bot.callback_query_handler(func=lambda call: call.data == "reject_private_chat")
        def handle_reject_private_chat(call):
            try:
                self.bot.answer_callback_query(call.id)

                user = self.get_user(call.from_user.id)
                active_chat = user.get_active_chat()

                if not active_chat:
                    self.bot.edit_message_text(
                        "⚠️ چت قبلاً پایان یافته است.",
                        call.message.chat.id,
                        call.message.message_id
                    )
                    return

                # دریافت کاربر مقابل
                partner_id = active_chat['user1_id'] if active_chat['user2_id'] == user.data['id'] else active_chat[
                    'user2_id']
                partner = User(self.db_manager, user_data=self.db_manager.get_user_by_telegram_id(partner_id))

                if partner and partner.data:
                    # ارسال پیام به هر دو کاربر
                    self.bot.edit_message_text(
                        "❌ شما درخواست چت خصوصی را رد کردید.",
                        call.message.chat.id,
                        call.message.message_id
                    )

                    self.bot.send_message(
                        partner.data['telegram_id'],
                        "❌ کاربر مقابل درخواست چت خصوصی را رد کرد."
                    )
                else:
                    self.bot.edit_message_text(
                        "❌ خطا در دریافت اطلاعات کاربر مقابل.",
                        call.message.chat.id,
                        call.message.message_id
                    )
            except Exception as e:
                self.logger.error(f"Error in reject private chat handler: {str(e)}")

        # پردازش پیام‌های چت
        @self.bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'voice', 'sticker'],
                                  chat_types=['private'])
        def handle_chat_messages(message):
            try:
                # به‌روزرسانی وضعیت آنلاین
                self.update_user_status(message)

                # اگر پیام از منوی اصلی نباشد
                if message.text and message.text in [
                    "🔗 به یک ناشناس وصلم کن!",
                    "🔍 جستجوی کاربران",
                    "👤 پروفایل من",
                    "💰 افزایش سکه",
                    "📄 راهنما",
                    "🎁 دعوت دوستان",
                    "⛔ پایان چت",
                    "🔓 فعال‌سازی چت خصوصی",
                    "👤 مشاهده پروفایل مقابل"
                ]:
                    return

                user = self.get_user(message.from_user.id)
                active_chat = user.get_active_chat()

                if not active_chat:
                    return  # کاربر چت فعالی ندارد

                # دریافت کاربر مقابل
                partner_id = active_chat['user1_id'] if active_chat['user2_id'] == user.data['id'] else active_chat[
                    'user2_id']
                partner = User(self.db_manager, user_data=self.db_manager.get_user_by_telegram_id(partner_id))

                if not partner or not partner.data:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ خطا در دریافت اطلاعات کاربر مقابل. چت پایان یافت.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
                    chat = Chat(self.db_manager, chat_id=active_chat['id'])
                    chat.end()
                    return

                # پردازش و ارسال پیام بر اساس نوع آن
                chat = Chat(self.db_manager, chat_id=active_chat['id'])

                if message.text:
                    # ذخیره پیام متنی
                    chat.add_message(user.data['id'], 'text', message.text)

                    # ارسال پیام به کاربر مقابل
                    self.bot.send_message(
                        partner.data['telegram_id'],
                        message.text
                    )
                elif message.photo:
                    # دریافت عکس با بالاترین کیفیت
                    file_id = message.photo[-1].file_id
                    caption = message.caption or ""

                    # ذخیره اطلاعات عکس
                    content = {'file_id': file_id, 'caption': caption}
                    chat.add_message(user.data['id'], 'photo', json.dumps(content))

                    # ارسال عکس به کاربر مقابل
                    self.bot.send_photo(
                        partner.data['telegram_id'],
                        file_id,
                        caption=caption
                    )
                elif message.voice:
                    # دریافت صدا
                    file_id = message.voice.file_id

                    # ذخیره اطلاعات صدا
                    content = {'file_id': file_id}
                    chat.add_message(user.data['id'], 'voice', json.dumps(content))

                    # ارسال صدا به کاربر مقابل
                    self.bot.send_voice(
                        partner.data['telegram_id'],
                        file_id
                    )
                elif message.sticker:
                    # دریافت استیکر
                    file_id = message.sticker.file_id

                    # ذخیره اطلاعات استیکر
                    content = {'file_id': file_id}
                    chat.add_message(user.data['id'], 'sticker', json.dumps(content))

                    # ارسال استیکر به کاربر مقابل
                    self.bot.send_sticker(
                        partner.data['telegram_id'],
                        file_id
                    )
            except Exception as e:
                self.logger.error(f"Error in chat messages handler: {str(e)}")

