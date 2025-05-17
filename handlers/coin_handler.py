from telebot import types
from handlers.base_handler import BaseHandler
from utils.keyboard_generator import KeyboardGenerator
from config.constants import MESSAGES, COIN_PACKAGES


class CoinHandler(BaseHandler):
    """
    کلاس مدیریت سکه‌ها
    """

    def register_handlers(self):
        """
        ثبت هندلرهای پیام
        """

        # منوی افزایش سکه
        @self.bot.message_handler(func=lambda message: message.text == "💰 افزایش سکه")
        def handle_coins(message):
            try:
                self.update_user_status(message)

                user = self.get_user(message.from_user.id)
                coins = user.get_coins()

                self.bot.send_message(
                    message.chat.id,
                    MESSAGES['coin_info'].format(coins),
                    parse_mode='Markdown',
                    reply_markup=KeyboardGenerator.get_coin_packages()
                )
            except Exception as e:
                self.logger.error(f"Error in coins handler: {str(e)}")

        # خرید سکه
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("buy_coin_"))
        def handle_buy_coin(call):
            try:
                self.bot.answer_callback_query(call.id)

                amount = int(call.data.split("_")[2])
                package = next((p for p in COIN_PACKAGES if p['amount'] == amount), None)

                if not package:
                    self.bot.edit_message_text(
                        "❌ بسته انتخاب شده یافت نشد. لطفاً مجدداً تلاش کنید.",
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=KeyboardGenerator.get_coin_packages()
                    )
                    return

                # دریافت اطلاعات پرداخت
                payment_message = f"💰 *خرید {amount} سکه*\n\nمبلغ قابل پرداخت: *{package['price']} تومان*\n\nبرای پرداخت، لطفاً مبلغ را به شماره کارت زیر واریز کنید و سپس تصویر رسید را ارسال نمایید:\n\n`6037-9979-5804-6775`\nبه نام: محمد امینی\n\nیا اینکه می‌توانید از دکمه زیر برای پرداخت اینترنتی استفاده کنید."

                self.bot.edit_message_text(
                    payment_message,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                        types.InlineKeyboardButton("💳 پرداخت آنلاین",
                                                   url=f"https://chatogram.com/payment?user_id={call.from_user.id}&amount={package['price']}&package={amount}"),
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_coins")
                    )
                )
            except Exception as e:
                self.logger.error(f"Error in buy coin handler: {str(e)}")

        # دریافت سکه رایگان
        @self.bot.callback_query_handler(func=lambda call: call.data == "free_coins")
        def handle_free_coins(call):
            try:
                self.bot.answer_callback_query(call.id)

                user = self.get_user(call.from_user.id)
                invite_code = user.get_invite_code()

                self.bot.edit_message_text(
                    f"🎁 *دریافت سکه رایگان*\n\nشما می‌توانید با دعوت دوستان خود به چتوگرام، برای هر دعوت 10 سکه رایگان دریافت کنید!\n\nلینک دعوت شخصی شما:\nhttps://t.me/ChatogramBot?start={invite_code}\n\nهمچنین با پیوستن به کانال ما، می‌توانید از آخرین اخبار و کدهای تخفیف مطلع شوید:",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                        types.InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/ChatogramChannel"),
                        types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_coins")
                    )
                )
            except Exception as e:
                self.logger.error(f"Error in free coins handler: {str(e)}")

        # بازگشت به منوی سکه‌ها
        @self.bot.callback_query_handler(func=lambda call: call.data == "back_to_coins")
        def handle_back_to_coins(call):
            try:
                self.bot.answer_callback_query(call.id)

                user = self.get_user(call.from_user.id)
                coins = user.get_coins()

                self.bot.edit_message_text(
                    MESSAGES['coin_info'].format(coins),
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=KeyboardGenerator.get_coin_packages()
                )
            except Exception as e:
                self.logger.error(f"Error in back to coins handler: {str(e)}")

