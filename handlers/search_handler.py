from telebot import types
from handlers.base_handler import BaseHandler
from models.chat import Chat
from utils.keyboard_generator import KeyboardGenerator
from config.constants import MESSAGES
from models.user import User
from config.settings import ADVANCED_SEARCH_COINS

class SearchHandler(BaseHandler):
    """
    کلاس مدیریت جستجوی کاربران
    """
    def __init__(self, bot, db_manager):
        """
        مقداردهی اولیه هندلر جستجو
        """
        super().__init__(bot, db_manager)
        # ذخیره‌سازی فیلترهای جستجوی کاربران
        self.search_filters = {}
    
    def register_handlers(self):
        """
        ثبت هندلرهای پیام
        """
        # منوی جستجو
        @self.bot.message_handler(func=lambda message: message.text == "🔍 جستجوی کاربران")
        def handle_search(message):
            try:
                self.update_user_status(message)
                
                self.bot.send_message(
                    message.chat.id,
                    MESSAGES['search_options'],
                    parse_mode='Markdown',
                    reply_markup=KeyboardGenerator.get_search_menu()
                )
            except Exception as e:
                self.logger.error(f"Error in search handler: {str(e)}")
        
        # بازگشت به منوی جستجو
        @self.bot.callback_query_handler(func=lambda call: call.data == "back_to_search")
        def handle_back_to_search(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                self.bot.edit_message_text(
                    MESSAGES['search_options'],
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=KeyboardGenerator.get_search_menu()
                )
            except Exception as e:
                self.logger.error(f"Error in back to search handler: {str(e)}")
        
        # جستجوی پیشرفته
        @self.bot.callback_query_handler(func=lambda call: call.data == "search_advanced")
        def handle_advanced_search(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                user = self.get_user(call.from_user.id)
                
                # بررسی سکه‌های کافی
                if user.get_coins() < ADVANCED_SEARCH_COINS:
                    self.bot.edit_message_text(
                        f"⚠️ برای استفاده از جستجوی پیشرفته به {ADVANCED_SEARCH_COINS} سکه نیاز دارید. موجودی فعلی شما: {user.get_coins()} سکه",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("💰 افزایش سکه", callback_data="buy_coins"),
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_search")
                        )
                    )
                    return
                
                # حذف فیلترهای قبلی
                if call.from_user.id in self.search_filters:
                    del self.search_filters[call.from_user.id]
                
                # نمایش منوی جستجوی پیشرفته
                self.bot.edit_message_text(
                    "🔍 *جستجوی پیشرفته*\n\nلطفاً فیلترهای مورد نظر خود را انتخاب کنید:",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=KeyboardGenerator.get_advanced_search_menu()
                )
            except Exception as e:
                self.logger.error(f"Error in advanced search handler: {str(e)}")
        
        # انتخاب جنسیت در جستجوی پیشرفته
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("adv_gender_"))
        def handle_adv_gender_selection(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                gender = call.data.split("_")[2]
                gender_map = {
                    "male": "male",
                    "female": "female",
                    "any": None
                }
                
                # ذخیره انتخاب کاربر
                if call.from_user.id not in self.search_filters:
                    self.search_filters[call.from_user.id] = {}
                
                self.search_filters[call.from_user.id]['gender'] = gender_map.get(gender)
                
                # به‌روزرسانی پیام
                gender_text = "👨 فقط پسرها" if gender == "male" else "👩 فقط دخترها" if gender == "female" else "👥 همه"
                self.bot.edit_message_text(
                    f"🔍 *جستجوی پیشرفته*\n\nفیلترهای انتخاب شده:\nجنسیت: {gender_text}\n\nلطفاً سایر فیلترها را نیز انتخاب کنید:",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=KeyboardGenerator.get_advanced_search_menu()
                )
            except Exception as e:
                self.logger.error(f"Error in advanced gender selection handler: {str(e)}")
        
        # انتخاب محدوده سنی در جستجوی پیشرفته
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("adv_age_"))
        def handle_adv_age_selection(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                age_range = call.data.split("_")[2]
                age_map = {
                    "18_25": {"min_age": 18, "max_age": 25},
                    "26_35": {"min_age": 26, "max_age": 35},
                    "36_plus": {"min_age": 36, "max_age": 99}
                }
                
                # ذخیره انتخاب کاربر
                if call.from_user.id not in self.search_filters:
                    self.search_filters[call.from_user.id] = {}
                
                self.search_filters[call.from_user.id].update(age_map.get(age_range, {}))
                
                # به‌روزرسانی پیام
                age_text = "18-25 سال" if age_range == "18_25" else "26-35 سال" if age_range == "26_35" else "36+ سال"
                
                # نمایش فیلترهای انتخاب شده
                filters_text = "🔍 *جستجوی پیشرفته*\n\nفیلترهای انتخاب شده:\n"
                
                if 'gender' in self.search_filters[call.from_user.id]:
                    gender = self.search_filters[call.from_user.id]['gender']
                    gender_text = "👨 مرد" if gender == "male" else "👩 زن" if gender == "female" else "👥 همه"
                    filters_text += f"جنسیت: {gender_text}\n"
                
                filters_text += f"سن: {age_text}\n"
                
                if 'city' in self.search_filters[call.from_user.id]:
                    filters_text += f"شهر: {self.search_filters[call.from_user.id]['city']}\n"
                
                filters_text += "\nلطفاً سایر فیلترها را نیز انتخاب کنید:"
                
                self.bot.edit_message_text(
                    filters_text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=KeyboardGenerator.get_advanced_search_menu()
                )
            except Exception as e:
                self.logger.error(f"Error in advanced age selection handler: {str(e)}")
        
        # انتخاب شهر در جستجوی پیشرفته
        @self.bot.callback_query_handler(func=lambda call: call.data == "adv_city_select")
        def handle_adv_city_selection(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                msg = self.bot.edit_message_text(
                    "🏙 لطفاً نام شهر مورد نظر خود را وارد کنید:",
                    call.message.chat.id,
                    call.message.message_id
                )
                
                self.bot.register_next_step_handler(msg, process_city_selection)
            except Exception as e:
                self.logger.error(f"Error in advanced city selection handler: {str(e)}")
        
        def process_city_selection(message):
            try:
                city = message.text.strip()
                
                if len(city) < 2 or len(city) > 50:
                    self.bot.send_message(
                        message.chat.id,
                        "⚠️ نام شهر باید بین 2 تا 50 کاراکتر باشد. لطفاً مجدداً تلاش کنید."
                    )
                    return
                
                # ذخیره انتخاب کاربر
                if message.from_user.id not in self.search_filters:
                    self.search_filters[message.from_user.id] = {}
                
                self.search_filters[message.from_user.id]['city'] = city
                
                # نمایش فیلترهای انتخاب شده
                filters_text = "🔍 *جستجوی پیشرفته*\n\nفیلترهای انتخاب شده:\n"
                
                if 'gender' in self.search_filters[message.from_user.id]:
                    gender = self.search_filters[message.from_user.id]['gender']
                    gender_text = "👨 مرد" if gender == "male" else "👩 زن" if gender == "female" else "👥 همه"
                    filters_text += f"جنسیت: {gender_text}\n"
                
                if 'min_age' in self.search_filters[message.from_user.id] and 'max_age' in self.search_filters[message.from_user.id]:
                    min_age = self.search_filters[message.from_user.id]['min_age']
                    max_age = self.search_filters[message.from_user.id]['max_age']
                    age_text = f"{min_age}-{max_age} سال" if max_age < 99 else f"{min_age}+ سال"
                    filters_text += f"سن: {age_text}\n"
                
                filters_text += f"شهر: {city}\n"
                
                filters_text += "\nلطفاً روی دکمه «جستجو» کلیک کنید یا فیلترهای دیگری را انتخاب نمایید:"
                
                self.bot.send_message(
                    message.chat.id,
                    filters_text,
                    parse_mode='Markdown',
                    reply_markup=KeyboardGenerator.get_advanced_search_menu()
                )
            except Exception as e:
                self.logger.error(f"Error in process city selection: {str(e)}")
        
        # پاک کردن فیلترها
        @self.bot.callback_query_handler(func=lambda call: call.data == "adv_clear_filters")
        def handle_adv_clear_filters(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                # حذف فیلترهای کاربر
                if call.from_user.id in self.search_filters:
                    del self.search_filters[call.from_user.id]
                
                self.bot.edit_message_text(
                    "🔍 *جستجوی پیشرفته*\n\nتمام فیلترها پاک شدند. لطفاً فیلترهای جدید را انتخاب کنید:",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=KeyboardGenerator.get_advanced_search_menu()
                )
            except Exception as e:
                self.logger.error(f"Error in advanced clear filters handler: {str(e)}")
        
        # شروع جستجو
        @self.bot.callback_query_handler(func=lambda call: call.data == "adv_search_start")
        def handle_adv_search_start(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                user = self.get_user(call.from_user.id)
                
                # کسر سکه از کاربر
                if not user.use_coins(ADVANCED_SEARCH_COINS, "advanced_search", "استفاده از جستجوی پیشرفته"):
                    self.bot.edit_message_text(
                        f"⚠️ سکه‌های شما کافی نیست. برای استفاده از جستجوی پیشرفته به {ADVANCED_SEARCH_COINS} سکه نیاز دارید.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("💰 افزایش سکه", callback_data="buy_coins"),
                            types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_search")
                        )
                    )
                    return
                
                # دریافت فیلترهای جستجو
                search_params = self.search_filters.get(call.from_user.id, {})
                
                # جستجوی کاربران
                users = self.db_manager.search_users(search_params, user.data['id'])
                
                if not users:
                    self.bot.edit_message_text(
                        "😕 متأسفانه کاربری با این مشخصات پیدا نشد. لطفاً فیلترهای دیگری را امتحان کنید.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("🔙 بازگشت به جستجو", callback_data="back_to_search")
                        )
                    )
                    return
                
                # نمایش نتایج جستجو
                self.bot.edit_message_text(
                    f"✅ {len(users)} کاربر پیدا شد. در حال نمایش نتایج...",
                    call.message.chat.id,
                    call.message.message_id
                )
                
                # نمایش اولین کاربر
                self.show_search_result(call.message.chat.id, users, 0)
            except Exception as e:
                self.logger.error(f"Error in advanced search start handler: {str(e)}")
        
        def show_search_result(self ,chat_id, users, index):
            """
            نمایش نتیجه جستجو
            """
            if not users or index >= len(users):
                self.bot.send_message(
                    chat_id,
                    "پایان نتایج جستجو.",
                    reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("🔙 بازگشت به جستجو", callback_data="back_to_search")
                    )
                )
                return
            
            user = users[index]
            user_model = User(self.db_manager, user_data=user)
            profile_text = user_model.get_profile_text()
            
            # کیبورد نمایش کاربر
            markup = types.InlineKeyboardMarkup(row_width=2)
            
            # دکمه‌های مشاهده پروفایل کاربر
            actions_btn = types.InlineKeyboardButton("💬 اقدامات", callback_data=f"user_actions_{user['id']}")
            next_btn = types.InlineKeyboardButton("➡️ بعدی", callback_data=f"next_user_{index + 1}")
            back_search_btn = types.InlineKeyboardButton("🔙 بازگشت به جستجو", callback_data="back_to_search")
            
            if index < len(users) - 1:
                markup.add(actions_btn, next_btn)
            else:
                markup.add(actions_btn)
            
            markup.add(back_search_btn)
            
            # ارسال پروفایل کاربر
            if user.get('profile_pic'):
                try:
                    self.bot.send_photo(
                        chat_id,
                        user['profile_pic'],
                        caption=profile_text,
                        parse_mode='Markdown',
                        reply_markup=markup
                    )
                except Exception:
                    self.bot.send_message(
                        chat_id,
                        profile_text,
                        parse_mode='Markdown',
                        reply_markup=markup
                    )
            else:
                self.bot.send_message(
                    chat_id,
                    profile_text,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
        
        # نمایش کاربر بعدی
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("next_user_"))
        def handle_next_user(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                index = int(call.data.split("_")[2])
                
                # دریافت فیلترهای جستجو
                search_params = self.search_filters.get(call.from_user.id, {})
                
                # جستجوی کاربران
                user = self.get_user(call.from_user.id)
                users = self.db_manager.search_users(search_params, user.data['id'])
                
                # نمایش کاربر بعدی
                self.show_search_result(call.message.chat.id, users, index)
            except Exception as e:
                self.logger.error(f"Error in next user handler: {str(e)}")
        
        # نمایش اقدامات روی کاربر
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("user_actions_"))
        def handle_user_actions(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                user_id = int(call.data.split("_")[2])
                
                # دریافت اطلاعات کاربر
                user_data = self.db_manager.get_user_by_id(user_id)
                
                if not user_data:
                    self.bot.edit_message_reply_markup(
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("❌ کاربر یافت نشد", callback_data="back_to_search")
                        )
                    )
                    return
                
                # نمایش اقدامات
                self.bot.edit_message_reply_markup(
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=KeyboardGenerator.get_user_profile_actions(user_id)
                )
            except Exception as e:
                self.logger.error(f"Error in user actions handler: {str(e)}")
        
        # درخواست چت به کاربر
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("chat_request_"))
        def handle_chat_request(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                target_user_id = int(call.data.split("_")[2])
                user = self.get_user(call.from_user.id)
                
                # بررسی سکه‌های کافی
                if user.get_coins() < 5:  # هزینه ارسال درخواست چت
                    self.bot.edit_message_reply_markup(
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("⚠️ سکه ناکافی", callback_data="back_to_search"),
                            types.InlineKeyboardButton("💰 افزایش سکه", callback_data="buy_coins")
                        )
                    )
                    return
                
                # دریافت اطلاعات کاربر هدف
                target_user_data = self.db_manager.get_user_by_id(target_user_id)
                
                if not target_user_data:
                    self.bot.edit_message_reply_markup(
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("❌ کاربر یافت نشد", callback_data="back_to_search")
                        )
                    )
                    return
                
                # ذخیره درخواست چت
                request_id = self.db_manager.add_chat_request(user.data['id'], target_user_id)
                
                if not request_id:
                    self.bot.edit_message_reply_markup(
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("❌ خطا در ارسال درخواست", callback_data="back_to_search")
                        )
                    )
                    return
                
                # کسر سکه از کاربر
                user.use_coins(5, "chat_request", f"ارسال درخواست چت به کاربر {target_user_data['display_name']}")
                
                # درخواست پیام همراه با درخواست چت
                msg = self.bot.send_message(
                    call.message.chat.id,
                    "✅ لطفاً یک پیام کوتاه به همراه درخواست چت خود ارسال کنید:\n(این پیام به کاربر مورد نظر نمایش داده خواهد شد)",
                    reply_markup=types.ForceReply(selective=True)
                )
                
                self.bot.register_next_step_handler(msg, lambda m: process_chat_request_message(m, target_user_id, request_id))
            except Exception as e:
                self.logger.error(f"Error in chat request handler: {str(e)}")
        
        def process_chat_request_message(message, target_user_id, request_id):
            try:
                # بررسی طول پیام
                if len(message.text) > 200:
                    self.bot.send_message(
                        message.chat.id,
                        "⚠️ پیام شما نمی‌تواند بیش از 200 کاراکتر باشد. لطفاً مجدداً تلاش کنید:",
                        reply_markup=types.ForceReply(selective=True)
                    )
                    self.bot.register_next_step_handler(message, lambda m: process_chat_request_message(m, target_user_id, request_id))
                    return
                
                user = self.get_user(message.from_user.id)
                target_user_data = self.db_manager.get_user_by_id(target_user_id)
                
                # ذخیره پیام درخواست
                self.db_manager.update_chat_request(request_id, message.text)
                
                # ارسال درخواست به کاربر هدف
                self.bot.send_message(
                    target_user_data['telegram_id'],
                    f"💬 *درخواست چت جدید*\n\nکاربر «{user.data.get('display_name', 'کاربر ناشناس')}» می‌خواهد با شما چت کند.\n\nپیام کاربر:\n\"{message.text}\"",
                    parse_mode='Markdown',
                    reply_markup=KeyboardGenerator.get_chat_request_confirmation(request_id)
                )
                
                self.bot.send_message(
                    message.chat.id,
                    "✅ درخواست چت شما با موفقیت ارسال شد. در صورت پذیرش توسط کاربر، به شما اطلاع داده خواهد شد.",
                    reply_markup=KeyboardGenerator.get_main_menu()
                )
            except Exception as e:
                self.logger.error(f"Error in process chat request message: {str(e)}")
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطا در ارسال درخواست چت. لطفاً مجدداً تلاش کنید.",
                    reply_markup=KeyboardGenerator.get_main_menu()
                )
        
        # پذیرش درخواست چت
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("accept_chat_request_"))
        def handle_accept_chat_request(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                request_id = int(call.data.split("_")[3])
                
                # دریافت اطلاعات درخواست
                request_data = self.db_manager.get_chat_request(request_id)
                
                if not request_data or request_data['status'] != 'pending':
                    self.bot.edit_message_text(
                        "⚠️ این درخواست دیگر معتبر نیست.",
                        call.message.chat.id,
                        call.message.message_id
                    )
                    return
                
                # دریافت اطلاعات کاربران
                user = self.get_user(call.from_user.id)
                requester = User(self.db_manager, user_data=self.db_manager.get_user_by_id(request_data['requester_id']))
                
                # ایجاد چت جدید
                chat = Chat.create(self.db_manager, requester.data['id'], user.data['id'])
                
                if not chat.data:
                    self.bot.edit_message_text(
                        "❌ خطا در ایجاد چت. لطفاً مجدداً تلاش کنید.",
                        call.message.chat.id,
                        call.message.message_id
                    )
                    return
                
                # به‌روزرسانی وضعیت درخواست
                self.db_manager.update_chat_request_status(request_id, 'accepted')
                
                # ارسال پیام به هر دو کاربر
                self.bot.edit_message_text(
                    "✅ شما درخواست چت را پذیرفتید. اکنون می‌توانید با کاربر مورد نظر گفتگو کنید.",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=None
                )
                
                self.bot.send_message(
                    call.message.chat.id,
                    MESSAGES['random_chat_connected'],
                    reply_markup=KeyboardGenerator.get_chat_menu()
                )
                
                self.bot.send_message(
                    requester.data['telegram_id'],
                    f"✅ کاربر «{user.data.get('display_name', 'کاربر ناشناس')}» درخواست چت شما را پذیرفت. اکنون می‌توانید با ایشان گفتگو کنید.",
                    reply_markup=KeyboardGenerator.get_chat_menu()
                )
            except Exception as e:
                self.logger.error(f"Error in accept chat request handler: {str(e)}")
        
        # رد درخواست چت
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("reject_chat_request_"))
        def handle_reject_chat_request(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                request_id = int(call.data.split("_")[3])
                
                # دریافت اطلاعات درخواست
                request_data = self.db_manager.get_chat_request(request_id)
                
                if not request_data or request_data['status'] != 'pending':
                    self.bot.edit_message_text(
                        "⚠️ این درخواست دیگر معتبر نیست.",
                        call.message.chat.id,
                        call.message.message_id
                    )
                    return
                
                # دریافت اطلاعات کاربران
                user = self.get_user(call.from_user.id)
                requester = User(self.db_manager, user_data=self.db_manager.get_user_by_id(request_data['requester_id']))
                
                # به‌روزرسانی وضعیت درخواست
                self.db_manager.update_chat_request_status(request_id, 'rejected')
                
                # ارسال پیام به هر دو کاربر
                self.bot.edit_message_text(
                    "❌ شما درخواست چت را رد کردید.",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=None
                )
                
                self.bot.send_message(
                    requester.data['telegram_id'],
                    f"❌ کاربر «{user.data.get('display_name', 'کاربر ناشناس')}» درخواست چت شما را رد کرد."
                )
            except Exception as e:
                self.logger.error(f"Error in reject chat request handler: {str(e)}")
        
        # لایک کردن پروفایل
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("like_profile_"))
        def handle_like_profile(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                target_user_id = int(call.data.split("_")[2])
                user = self.get_user(call.from_user.id)
                
                # بررسی وجود کاربر
                target_user_data = self.db_manager.get_user_by_id(target_user_id)
                
                if not target_user_data:
                    self.bot.edit_message_reply_markup(
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("❌ کاربر یافت نشد", callback_data="back_to_search")
                        )
                    )
                    return
                
                # لایک یا آنلایک کردن پروفایل
                is_liked = self.db_manager.toggle_like(user.data['id'], target_user_id)
                
                # ارسال نوتیفیکیشن به کاربر هدف در صورت لایک شدن
                if is_liked:
                    self.bot.send_message(
                        target_user_data['telegram_id'],
                        f"❤️ کاربر «{user.data.get('display_name', 'کاربر ناشناس')}» پروفایل شما را لایک کرد."
                    )
                
                # به‌روزرسانی دکمه
                action_text = "❤️ لایک شده" if is_liked else "❤️ لایک پروفایل"
                self.bot.edit_message_reply_markup(
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=self.update_keyboard_button(
                        call.message.reply_markup, 
                        f"like_profile_{target_user_id}", 
                        action_text
                    )
                )
            except Exception as e:
                self.logger.error(f"Error in like profile handler: {str(e)}")
        
        # دنبال کردن کاربر
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("follow_user_"))
        def handle_follow_user(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                target_user_id = int(call.data.split("_")[2])
                user = self.get_user(call.from_user.id)
                
                # بررسی وجود کاربر
                target_user_data = self.db_manager.get_user_by_id(target_user_id)
                
                if not target_user_data:
                    self.bot.edit_message_reply_markup(
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("❌ کاربر یافت نشد", callback_data="back_to_search")
                        )
                    )
                    return
                
                # دنبال یا آنفالو کردن کاربر
                is_following = self.db_manager.toggle_follow(user.data['id'], target_user_id)
                
                # ارسال نوتیفیکیشن به کاربر هدف در صورت دنبال شدن
                if is_following:
                    self.bot.send_message(
                        target_user_data['telegram_id'],
                        f"👁 کاربر «{user.data.get('display_name', 'کاربر ناشناس')}» شما را دنبال کرد."
                    )
                
                # به‌روزرسانی دکمه
                action_text = "👁 دنبال شده" if is_following else "👁 دنبال کردن"
                self.bot.edit_message_reply_markup(
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=self.update_keyboard_button(
                        call.message.reply_markup, 
                        f"follow_user_{target_user_id}", 
                        action_text
                    )
                )
            except Exception as e:
                self.logger.error(f"Error in follow user handler: {str(e)}")
        
        # بلاک کردن کاربر
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("block_user_"))
        def handle_block_user(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                target_user_id = int(call.data.split("_")[2])
                user = self.get_user(call.from_user.id)
                
                # بررسی وجود کاربر
                target_user_data = self.db_manager.get_user_by_id(target_user_id)
                
                if not target_user_data:
                    self.bot.edit_message_reply_markup(
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("❌ کاربر یافت نشد", callback_data="back_to_search")
                        )
                    )
                    return
                
                # بلاک یا آنبلاک کردن کاربر
                is_blocked = self.db_manager.toggle_block(user.data['id'], target_user_id)
                
                # به‌روزرسانی دکمه
                action_text = "⛔ بلاک شده" if is_blocked else "⛔ بلاک کردن"
                self.bot.edit_message_reply_markup(
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=self.update_keyboard_button(
                        call.message.reply_markup, 
                        f"block_user_{target_user_id}", 
                        action_text
                    )
                )
                
                # ارسال پیام به کاربر
                if is_blocked:
                    self.bot.send_message(
                        call.message.chat.id,
                        f"✅ کاربر «{target_user_data.get('display_name', 'کاربر ناشناس')}» بلاک شد."
                    )
                else:
                    self.bot.send_message(
                        call.message.chat.id,
                        f"✅ کاربر «{target_user_data.get('display_name', 'کاربر ناشناس')}» از لیست بلاک خارج شد."
                    )
            except Exception as e:
                self.logger.error(f"Error in block user handler: {str(e)}")
        
        # گزارش تخلف کاربر
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("report_user_"))
        def handle_report_user(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                target_user_id = int(call.data.split("_")[2])
                
                # بررسی وجود کاربر
                target_user_data = self.db_manager.get_user_by_id(target_user_id)
                
                if not target_user_data:
                    self.bot.edit_message_reply_markup(
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("❌ کاربر یافت نشد", callback_data="back_to_search")
                        )
                    )
                    return
                
                # ذخیره موقت شناسه کاربر هدف
                if not hasattr(self, 'report_targets'):
                    self.report_targets = {}
                
                self.report_targets[call.from_user.id] = target_user_id
                
                # نمایش دلایل گزارش
                self.bot.edit_message_reply_markup(
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=KeyboardGenerator.get_report_reasons()
                )
            except Exception as e:
                self.logger.error(f"Error in report user handler: {str(e)}")
        
        # انتخاب دلیل گزارش
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("report_") and not call.data.startswith("report_user_"))
        def handle_report_reason(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                reason_code = call.data.split("_")[1]
                
                reason_map = {
                    "inappropriate": "محتوای نامناسب",
                    "harassment": "آزار و اذیت",
                    "spam": "اسپم",
                    "scam": "کلاهبرداری",
                    "other": "سایر موارد"
                }
                
                reason = reason_map.get(reason_code, "سایر موارد")
                
                if reason_code == "other":
                    # درخواست توضیحات بیشتر
                    msg = self.bot.edit_message_text(
                        "لطفاً توضیحات بیشتری درباره دلیل گزارش خود ارائه دهید:",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=None
                    )
                    
                    self.bot.register_next_step_handler(msg, process_report_details)
                    return
                
                # ثبت گزارش
                user = self.get_user(call.from_user.id)
                target_user_id = self.report_targets.get(call.from_user.id)
                
                if not target_user_id:
                    self.bot.edit_message_text(
                        "❌ خطا در ثبت گزارش. لطفاً مجدداً تلاش کنید.",
                        call.message.chat.id,
                        call.message.message_id
                    )
                    return
                
                # ثبت گزارش در دیتابیس
                report_id = self.db_manager.report_user(user.data['id'], target_user_id, reason)
                
                if report_id:
                    # ارسال گزارش به ادمین‌ها
                    for admin_id in self.db_manager.get_admins():
                        try:
                            target_user = User(self.db_manager, user_data=self.db_manager.get_user_by_id(target_user_id))
                            
                            self.bot.send_message(
                                admin_id,
                                f"🚩 *گزارش تخلف جدید*\n\nگزارش‌دهنده: {user.data.get('display_name', 'کاربر ناشناس')} (ID: {user.data['telegram_id']})\n\nکاربر گزارش‌شده: {target_user.data.get('display_name', 'کاربر ناشناس')} (ID: {target_user.data['telegram_id']})\n\nدلیل: {reason}",
                                parse_mode='Markdown',
                                reply_markup=types.InlineKeyboardMarkup().add(
                                    types.InlineKeyboardButton("✅ تأیید و بن کاربر", callback_data=f"admin_ban_{target_user_id}"),
                                    types.InlineKeyboardButton("❌ رد گزارش", callback_data=f"admin_reject_report_{report_id}")
                                )
                            )
                        except Exception:
                            continue
                    
                    # پاک کردن اطلاعات موقت
                    del self.report_targets[call.from_user.id]
                    
                    # اطلاع به کاربر
                    self.bot.edit_message_text(
                        "✅ گزارش شما با موفقیت ثبت شد و توسط تیم پشتیبانی بررسی خواهد شد.",
                        call.message.chat.id,
                        call.message.message_id
                    )
                else:
                    self.bot.edit_message_text(
                        "❌ خطا در ثبت گزارش. لطفاً مجدداً تلاش کنید.",
                        call.message.chat.id,
                        call.message.message_id
                    )
            except Exception as e:
                self.logger.error(f"Error in report reason handler: {str(e)}")
        
        def process_report_details(message):
            try:
                reason = f"سایر موارد: {message.text}"
                
                # ثبت گزارش
                user = self.get_user(message.from_user.id)
                target_user_id = self.report_targets.get(message.from_user.id)
                
                if not target_user_id:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ خطا در ثبت گزارش. لطفاً مجدداً تلاش کنید.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
                    return
                
                # ثبت گزارش در دیتابیس
                report_id = self.db_manager.report_user(user.data['id'], target_user_id, reason)
                
                if report_id:
                    # ارسال گزارش به ادمین‌ها
                    for admin_id in self.db_manager.get_admins():
                        try:
                            target_user = User(self.db_manager, user_data=self.db_manager.get_user_by_id(target_user_id))
                            
                            self.bot.send_message(
                                admin_id,
                                f"🚩 *گزارش تخلف جدید*\n\nگزارش‌دهنده: {user.data.get('display_name', 'کاربر ناشناس')} (ID: {user.data['telegram_id']})\n\nکاربر گزارش‌شده: {target_user.data.get('display_name', 'کاربر ناشناس')} (ID: {target_user.data['telegram_id']})\n\nدلیل: {reason}",
                                parse_mode='Markdown',
                                reply_markup=types.InlineKeyboardMarkup().add(
                                    types.InlineKeyboardButton("✅ تأیید و بن کاربر", callback_data=f"admin_ban_{target_user_id}"),
                                    types.InlineKeyboardButton("❌ رد گزارش", callback_data=f"admin_reject_report_{report_id}")
                                )
                            )
                        except Exception:
                            continue
                    
                    # پاک کردن اطلاعات موقت
                    del self.report_targets[message.from_user.id]
                    
                    # اطلاع به کاربر
                    self.bot.send_message(
                        message.chat.id,
                        "✅ گزارش شما با موفقیت ثبت شد و توسط تیم پشتیبانی بررسی خواهد شد.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
                else:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ خطا در ثبت گزارش. لطفاً مجدداً تلاش کنید.",
                        reply_markup=KeyboardGenerator.get_main_menu()
                    )
            except Exception as e:
                self.logger.error(f"Error in process report details: {str(e)}")
                self.bot.send_message(
                    message.chat.id,
                    "❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
                    reply_markup=KeyboardGenerator.get_main_menu()
                )
        
        # انصراف از گزارش
        @self.bot.callback_query_handler(func=lambda call: call.data == "cancel_report")
        def handle_cancel_report(call):
            try:
                self.bot.answer_callback_query(call.id)
                
                # پاک کردن اطلاعات موقت
                if hasattr(self, 'report_targets') and call.from_user.id in self.report_targets:
                    del self.report_targets[call.from_user.id]
                
                # بازگشت به منوی قبلی
                target_user_id = int(call.data.split("_")[2])
                self.bot.edit_message_reply_markup(
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=KeyboardGenerator.get_user_profile_actions(target_user_id)
                )
            except Exception as e:
                self.logger.error(f"Error in cancel report handler: {str(e)}")
    
    def update_keyboard_button(self, markup, callback_data_prefix, new_text):
        """
        به‌روزرسانی متن دکمه در کیبورد
        """
        new_markup = types.InlineKeyboardMarkup(row_width=markup.row_width)
        
        for row in markup.keyboard:
            new_row = []
            for button in row:
                if button.callback_data and button.callback_data.startswith(callback_data_prefix):
                    new_row.append(types.InlineKeyboardButton(new_text, callback_data=button.callback_data))
                else:
                    new_row.append(button)
            new_markup.row(*new_row)
        
        return new_markup
