import re
import logging
from datetime import datetime

logger = logging.getLogger('chatogram.utils.validators')


def validate_name(name):
    """
    اعتبارسنجی نام کاربری

    معیارها:
    - باید بین 3 تا 20 کاراکتر باشد
    - فقط حروف فارسی، انگلیسی، اعداد و برخی علائم مجاز است
    - نباید شامل کلمات نامناسب باشد

    Args:
        name (str): نام کاربری برای اعتبارسنجی

    Returns:
        bool: True اگر معتبر باشد، False در غیر این صورت
    """
    if not name or not isinstance(name, str):
        logger.debug(f"Invalid name: {name} - Not a string or None")
        return False

    if len(name) < 3 or len(name) > 20:
        logger.debug(f"Invalid name: {name} - Length not between 3-20")
        return False

    # بررسی کاراکترهای مجاز (حروف فارسی و انگلیسی، اعداد و برخی علائم)
    if not re.match(r'^[\u0600-\u06FFa-zA-Z0-9\s_.-]+$', name):
        logger.debug(f"Invalid name: {name} - Contains invalid characters")
        return False

    # بررسی کلمات غیرمجاز
    forbidden_words = ['admin', 'support', 'پشتیبانی', 'مدیر', 'ادمین']
    for word in forbidden_words:
        if word.lower() in name.lower():
            logger.debug(f"Invalid name: {name} - Contains forbidden word: {word}")
            return False

    return True


def validate_age(age):
    """
    اعتبارسنجی سن

    معیارها:
    - باید بین 18 تا 99 سال باشد

    Args:
        age (int|str): سن برای اعتبارسنجی

    Returns:
        bool: True اگر معتبر باشد، False در غیر این صورت
    """
    try:
        age = int(age)
        valid = 18 <= age <= 99
        if not valid:
            logger.debug(f"Invalid age: {age} - Not between 18-99")
        return valid
    except (ValueError, TypeError):
        logger.debug(f"Invalid age: {age} - Not a valid integer")
        return False


def validate_bio(bio):
    """
    اعتبارسنجی بیوگرافی

    معیارها:
    - نباید بیش از 500 کاراکتر باشد
    - نباید شامل لینک باشد
    - نباید شامل کلمات نامناسب باشد

    Args:
        bio (str): بیوگرافی برای اعتبارسنجی

    Returns:
        bool: True اگر معتبر باشد، False در غیر این صورت
    """
    if not bio or not isinstance(bio, str):
        logger.debug(f"Invalid bio: Not a string or None")
        return False

    if len(bio) > 500:
        logger.debug(f"Invalid bio: Too long (over 500 characters)")
        return False

    # بررسی عدم وجود لینک‌ها
    if re.search(r'(https?://|www\.)', bio, re.IGNORECASE):
        logger.debug(f"Invalid bio: Contains links")
        return False

    # بررسی کلمات غیرمجاز
    forbidden_patterns = [
        r'تلگرام[: ]',
        r'اینستاگرام[: ]',
        r'شماره[: ]',
        r'موبایل[: ]',
        r'@[\w\d]+'  # الگوی یوزرنیم تلگرام/اینستاگرام
    ]

    for pattern in forbidden_patterns:
        if re.search(pattern, bio, re.IGNORECASE):
            logger.debug(f"Invalid bio: Contains forbidden pattern: {pattern}")
            return False

    return True


def validate_city(city):
    """
    اعتبارسنجی نام شهر

    معیارها:
    - باید بین 2 تا 30 کاراکتر باشد
    - فقط حروف فارسی، انگلیسی و فاصله مجاز است

    Args:
        city (str): نام شهر برای اعتبارسنجی

    Returns:
        bool: True اگر معتبر باشد، False در غیر این صورت
    """
    if not city or not isinstance(city, str):
        logger.debug(f"Invalid city: Not a string or None")
        return False

    if len(city) < 2 or len(city) > 30:
        logger.debug(f"Invalid city: {city} - Length not between 2-30")
        return False

    # بررسی کاراکترهای مجاز (حروف فارسی و انگلیسی و فاصله)
    if not re.match(r'^[\u0600-\u06FFa-zA-Z\s]+$', city):
        logger.debug(f"Invalid city: {city} - Contains invalid characters")
        return False

    return True


def validate_payment_info(payment_info):
    """
    اعتبارسنجی اطلاعات پرداخت

    معیارها:
    - باید در فرمت JSON معتبر باشد
    - باید شامل فیلدهای amount و transaction_id باشد

    Args:
        payment_info (str): اطلاعات پرداخت در قالب JSON

    Returns:
        bool: True اگر معتبر باشد، False در غیر این صورت
    """
    import json

    try:
        # تبدیل رشته به دیکشنری JSON
        info = json.loads(payment_info)

        # بررسی وجود فیلدهای ضروری
        if 'amount' not in info or 'transaction_id' not in info:
            logger.debug(f"Invalid payment info: Missing required fields")
            return False

        # بررسی نوع داده‌های فیلدها
        if not isinstance(info['amount'], (int, float)) or info['amount'] <= 0:
            logger.debug(f"Invalid payment info: Invalid amount")
            return False

        if not isinstance(info['transaction_id'], str) or len(info['transaction_id']) < 5:
            logger.debug(f"Invalid payment info: Invalid transaction_id")
            return False

        return True
    except (json.JSONDecodeError, TypeError):
        logger.debug(f"Invalid payment info: Not a valid JSON string")
        return False


def validate_date_format(date_str, format='%Y-%m-%d'):
    """
    اعتبارسنجی فرمت تاریخ

    Args:
        date_str (str): رشته تاریخ
        format (str): فرمت مورد انتظار

    Returns:
        bool: True اگر معتبر باشد، False در غیر این صورت
    """
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        logger.debug(f"Invalid date format: {date_str} - Expected format: {format}")
        return False


def validate_message_content(content, max_length=2000):
    """
    اعتبارسنجی محتوای پیام

    معیارها:
    - نباید بیش از حداکثر تعیین شده کاراکتر باشد
    - نباید خالی باشد

    Args:
        content (str): محتوای پیام
        max_length (int): حداکثر طول مجاز

    Returns:
        bool: True اگر معتبر باشد، False در غیر این صورت
    """
    if not content or not isinstance(content, str):
        logger.debug(f"Invalid message content: Not a string or None")
        return False

    if len(content) > max_length:
        logger.debug(f"Invalid message content: Too long (over {max_length} characters)")
        return False

    return True