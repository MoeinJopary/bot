"""
تنظیمات اصلی ربات
"""
import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# توکن ربات تلگرام
BOT_TOKEN = os.getenv('BOT_TOKEN')

# تنظیمات دیتابیس
DB_NAME = os.getenv('DB_NAME', 'chatogram.db')

# تنظیمات لاگ
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# تنظیمات رمزنگاری
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'your-secure-key-here')

# تنظیمات ادمین
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',')))

# تنظیمات سکه
INITIAL_COINS = 20  # سکه‌های اولیه هنگام ثبت‌نام
CHAT_REQUEST_COINS = 5  # هزینه ارسال درخواست چت
ADVANCED_SEARCH_COINS = 10  # هزینه استفاده از فیلترهای پیشرفته