from telebot import types
from handlers.base_handler import BaseHandler
from utils.keyboard_generator import KeyboardGenerator
from config.constants import MESSAGES


class StartHandler(BaseHandler):
    """
    کلاس مدیریت دستور شروع و منوی اصلی
    """

    def register_handlers(self):
        """
        ثبت هندلرهای پیام
        """

        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            try:
                self.update_user_status(message)

                # بررسی کد دعوت
                args = message.text.split()
                if len(args) > 1:
                    try:
                        invite_code = int(args[1])
                        user = self.get_user(message.from_user.id)

                        # ثبت استفاده از کد دعوت
                        inviter_id = self.db_manager.register_invite(invite_code, user.data['id'])

                        if inviter_id:
                            # افزودن سکه به دعوت‌کننده
                            inviter = User(self.db_manager,
                                           user_data=self.db_manager.get_user_by_telegram_id(inviter_id))
                            inviter.add_coins(10, "invite_reward", "پاداش دعوت دوست")

                            # ارسال پیام به دعوت‌کننده
                            self.bot.send_message(
                                inviter_id,
                                "🎁 یک دوست با لینک دعوت شما عضو شد! 10 سکه به حساب شما اضافه شد."
                            )
                    except ValueError:
                        pass

                # ارسال پیام خوش‌آمدگویی
                self.bot.send_message(
                    message.chat.id,
                    MESSAGES['start'],
                    parse_mode='Markdown',
                    reply_markup=KeyboardGenerator.get_main_menu()
                )
            except Exception as e:
                self.logger.error(f"Error in start handler: {str(e)}")

        @self.bot.message_handler(func=lambda message: message.text == "📄 راهنما")
        def handle_help(message):
            try:
                self.update_user_status(message)

                self.bot.send_message(
                    message.chat.id,
                    MESSAGES['help'],
                    parse_mode='Markdown'
                )
            except Exception as e:
                self.logger.error(f"Error in help handler: {str(e)}")

        @self.bot.message_handler(func=lambda message: message.text == "🎁 دعوت دوستان")
        def handle_invite(message):
            try:
                self.update_user_status(message)

                user = self.get_user(message.from_user.id)
                invite_code = user.get_invite_code()

                invite_message = MESSAGES['invite'].format(invite_code)

                self.bot.send_message(
                    message.chat.id,
                    invite_message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                self.logger.error(f"Error in invite handler: {str(e)}")

        # هندلر بازگشت به منوی اصلی
        @self.bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
        def handle_back_to_main(call):
            try:
                self.bot.answer_callback_query(call.id)

                self.bot.edit_message_text(
                    MESSAGES['start'],
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=None
                )
            except Exception as e:
                self.logger.error(f"Error in back to main handler: {str(e)}")
