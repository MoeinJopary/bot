import json
import logging
from datetime import datetime


class Transaction:
    """
    کلاس مدل تراکنش
    """

    def __init__(self, db_manager, transaction_id=None, transaction_data=None):
        """
        مقداردهی اولیه مدل تراکنش

        Args:
            db_manager: مدیریت‌کننده پایگاه داده
            transaction_id (int, optional): شناسه تراکنش برای بازیابی از دیتابیس
            transaction_data (dict, optional): داده‌های تراکنش
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger('chatogram.models.transaction')

        if transaction_data:
            self.data = transaction_data
        elif transaction_id:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
            result = cursor.fetchone()

            if result:
                self.data = dict(result)
            else:
                self.data = None
        else:
            self.data = None

    @classmethod
    def create(cls, db_manager, user_id, amount, transaction_type, description, payment_info=None):
        """
        ایجاد تراکنش جدید

        Args:
            db_manager: مدیریت‌کننده پایگاه داده
            user_id (int): شناسه کاربر
            amount (int): مقدار سکه‌ها (مثبت برای افزایش، منفی برای کاهش)
            transaction_type (str): نوع تراکنش
            description (str): توضیحات تراکنش
            payment_info (str, optional): اطلاعات پرداخت (JSON)

        Returns:
            Transaction: نمونه از کلاس تراکنش
        """
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO transactions 
                (user_id, amount, transaction_type, description, payment_info, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    amount,
                    transaction_type,
                    description,
                    payment_info,
                    'pending' if payment_info else 'completed',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            )
            conn.commit()

            transaction_id = cursor.lastrowid
            return cls(db_manager, transaction_id)
        except Exception as e:
            conn.rollback()
            logger = logging.getLogger('chatogram.models.transaction')
            logger.error(f"Error creating transaction: {str(e)}")
            return None

    def update_status(self, status):
        """
        به‌روزرسانی وضعیت تراکنش

        Args:
            status (str): وضعیت جدید (completed, failed, refunded)

        Returns:
            bool: True اگر به‌روزرسانی موفق باشد، False در غیر این صورت
        """
        if not self.data:
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE transactions 
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    status,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    self.data['id']
                )
            )
            conn.commit()

            self.data['status'] = status
            self.data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # اگر تراکنش کامل شده، سکه‌های کاربر را به‌روزرسانی کنیم
            if status == 'completed' and self.data['status'] != 'completed':
                # به‌روزرسانی سکه‌های کاربر فقط برای تراکنش‌های خرید (مثبت)
                if self.data['transaction_type'] in ['purchase', 'admin_add', 'invite_reward'] and self.data[
                    'amount'] > 0:
                    self._update_user_coins()

            return True
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error updating transaction status: {str(e)}")
            return False

    def update_payment_info(self, payment_info):
        """
        به‌روزرسانی اطلاعات پرداخت

        Args:
            payment_info (str): اطلاعات پرداخت جدید (JSON)

        Returns:
            bool: True اگر به‌روزرسانی موفق باشد، False در غیر این صورت
        """
        if not self.data:
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE transactions 
                SET payment_info = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    payment_info,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    self.data['id']
                )
            )
            conn.commit()

            self.data['payment_info'] = payment_info
            self.data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            return True
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error updating payment info: {str(e)}")
            return False

    def _update_user_coins(self):
        """
        به‌روزرسانی سکه‌های کاربر بر اساس مقدار تراکنش

        Returns:
            bool: True اگر به‌روزرسانی موفق باشد، False در غیر این صورت
        """
        if not self.data:
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            # دریافت تعداد فعلی سکه‌های کاربر
            cursor.execute("SELECT coins FROM users WHERE id = ?", (self.data['user_id'],))
            result = cursor.fetchone()

            if not result:
                self.logger.error(f"User not found for transaction: {self.data['id']}")
                return False

            current_coins = result['coins']
            new_coins = current_coins + self.data['amount']

            # اطمینان از عدم منفی شدن سکه‌ها
            if new_coins < 0:
                new_coins = 0

            # به‌روزرسانی سکه‌های کاربر
            cursor.execute(
                "UPDATE users SET coins = ? WHERE id = ?",
                (new_coins, self.data['user_id'])
            )
            conn.commit()

            return True
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error updating user coins: {str(e)}")
            return False

    def get_payment_info_dict(self):
        """
        دریافت اطلاعات پرداخت به صورت دیکشنری

        Returns:
            dict: اطلاعات پرداخت
        """
        if not self.data or not self.data.get('payment_info'):
            return {}

        try:
            return json.loads(self.data['payment_info'])
        except json.JSONDecodeError:
            self.logger.error(f"Error parsing payment info JSON: {self.data['payment_info']}")
            return {}

    def get_formatted_amount(self):
        """
        دریافت مقدار سکه به فرمت مناسب

        Returns:
            str: مقدار سکه با فرمت مناسب
        """
        if not self.data:
            return "0"

        amount = self.data['amount']

        if amount > 0:
            return f"+{amount}"
        else:
            return str(amount)

    def get_formatted_date(self):
        """
        دریافت تاریخ تراکنش با فرمت مناسب

        Returns:
            str: تاریخ فرمت‌شده
        """
        if not self.data:
            return ""

        created_at = self.data.get('created_at', '')

        try:
            dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%Y/%m/%d %H:%M')
        except ValueError:
            return created_at

    def get_status_text(self):
        """
        دریافت متن وضعیت تراکنش

        Returns:
            str: متن وضعیت
        """
        if not self.data:
            return ""

        status_map = {
            'pending': 'در انتظار',
            'completed': 'تکمیل شده',
            'failed': 'ناموفق',
            'refunded': 'برگشت داده شده'
        }

        return status_map.get(self.data.get('status', ''), 'نامشخص')

    def get_type_text(self):
        """
        دریافت متن نوع تراکنش

        Returns:
            str: متن نوع تراکنش
        """
        if not self.data:
            return ""

        type_map = {
            'purchase': 'خرید سکه',
            'chat_request': 'درخواست چت',
            'advanced_search': 'جستجوی پیشرفته',
            'admin_add': 'افزایش توسط ادمین',
            'admin_deduct': 'کاهش توسط ادمین',
            'invite_reward': 'پاداش دعوت دوستان'
        }

        return type_map.get(self.data.get('transaction_type', ''), 'نامشخص')