from cryptography.fernet import Fernet
import base64
from config.settings import ENCRYPTION_KEY


# ایجاد کلید رمزنگاری بر اساس کلید امنیتی
def get_encryption_key():
    """
    ایجاد کلید رمزنگاری از کلید امنیتی
    """
    # تبدیل کلید به یک رشته ۳۲ بایتی
    key = ENCRYPTION_KEY
    if len(key) < 32:
        key = key.ljust(32, 'x')
    elif len(key) > 32:
        key = key[:32]

    # تبدیل به فرمت base64 برای استفاده در Fernet
    key_bytes = key.encode('utf-8')
    return base64.urlsafe_b64encode(key_bytes)


# ایجاد نمونه Fernet
fernet = Fernet(get_encryption_key())


def encrypt(data):
    """
    رمزگذاری داده
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    return fernet.encrypt(data).decode('utf-8')


def decrypt(data):
    """
    رمزگشایی داده
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    return fernet.decrypt(data).decode('utf-8')

