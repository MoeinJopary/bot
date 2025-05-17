import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name, level=logging.INFO):
    """
    راه‌اندازی سیستم لاگ
    """
    # ایجاد پوشه logs اگر وجود ندارد
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # تنظیم فرمت لاگ
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # ایجاد هندلر فایل
    file_handler = RotatingFileHandler(
        f'logs/{name}.log',
        maxBytes=10 * 1024 * 1024,  # 10 مگابایت
        backupCount=5
    )
    file_handler.setFormatter(formatter)

    # ایجاد هندلر کنسول
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # ایجاد لاگر
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # اضافه کردن هندلرها
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
