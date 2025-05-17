import logging
import telebot
from config.settings import BOT_TOKEN, LOG_LEVEL
from database.db_manager import DBManager
from handlers import register_all_handlers
from utils.logger import setup_logger


class ChatogramBot:
    """
    کلاس اصلی ربات چتوگرام
    """

    def __init__(self, token):
        """
        مقداردهی اولیه ربات با توکن تلگرام
        """
        self.bot = telebot.TeleBot(token)
        self.logger = setup_logger('chatogram', LOG_LEVEL)
        self.db_manager = DBManager()
        self.logger.info("Initializing Chatogram Bot...")

    def setup(self):
        """
        راه‌اندازی اولیه ربات و ثبت هندلرها
        """
        self.logger.info("Setting up database...")
        self.db_manager.setup()

        self.logger.info("Registering handlers...")
        register_all_handlers(self.bot, self.db_manager)

        self.logger.info("Bot setup completed")

    def run(self):
        """
        شروع به کار ربات
        """
        self.logger.info("Starting bot polling...")
        self.bot.polling(none_stop=True, interval=0, timeout=20)


if __name__ == "__main__":
    # راه‌اندازی ربات
    chatogram = ChatogramBot(BOT_TOKEN)
    chatogram.setup()
    chatogram.run()