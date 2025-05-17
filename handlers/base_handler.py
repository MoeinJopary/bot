import logging
from telebot import TeleBot
from models.user import User


class BaseHandler:
    """
    کلاس پایه برای همه هندلرها
    """

    def __init__(self, bot: TeleBot, db_manager):
        """
        مقداردهی اولیه هندلر پایه
        """
        self.bot = bot
        self.db_manager = db_manager
        self.logger = logging.getLogger(f'chatogram.handlers.{self.__class__.__name__}')

    def register_handlers(self):
        """
        ثبت هندلرهای پیام - باید در کلاس‌های فرزند پیاده‌سازی شود
        """
        raise NotImplementedError("Subclasses must implement register_handlers")

    def get_user(self, telegram_id):
        """
        دریافت یا ایجاد شیء کاربر
        """
        return User(self.db_manager, telegram_id)

    def update_user_status(self, message, is_online=True):
        """
        به‌روزرسانی وضعیت آنلاین بودن کاربر
        """
        user = self.get_user(message.from_user.id)
        user.update_status(is_online)
