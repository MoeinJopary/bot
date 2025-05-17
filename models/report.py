import logging
from datetime import datetime


class Report:
    """
    کلاس مدل گزارش تخلف
    """

    def __init__(self, db_manager, report_id=None, report_data=None):
        """
        مقداردهی اولیه مدل گزارش

        Args:
            db_manager: مدیریت‌کننده پایگاه داده
            report_id (int, optional): شناسه گزارش برای بازیابی از دیتابیس
            report_data (dict, optional): داده‌های گزارش
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger('chatogram.models.report')

        if report_data:
            self.data = report_data
        elif report_id:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
            result = cursor.fetchone()

            if result:
                self.data = dict(result)
            else:
                self.data = None
        else:
            self.data = None

    @classmethod
    def create(cls, db_manager, reporter_id, reported_id, reason, details=None):
        """
        ایجاد گزارش جدید

        Args:
            db_manager: مدیریت‌کننده پایگاه داده
            reporter_id (int): شناسه کاربر گزارش‌دهنده
            reported_id (int): شناسه کاربر گزارش‌شده
            reason (str): دلیل گزارش
            details (str, optional): جزئیات بیشتر گزارش

        Returns:
            Report: نمونه از کلاس گزارش
        """
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        try:
            # بررسی تکراری نبودن گزارش
            cursor.execute(
                """
                SELECT id FROM reports 
                WHERE reporter_id = ? AND reported_id = ? AND status = 'pending'
                """,
                (reporter_id, reported_id)
            )

            existing = cursor.fetchone()
            if existing:
                # گزارش تکراری - به‌روزرسانی گزارش قبلی
                cursor.execute(
                    """
                    UPDATE reports 
                    SET reason = ?, details = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        reason,
                        details,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        existing['id']
                    )
                )
                conn.commit()
                return cls(db_manager, existing['id'])

            # ایجاد گزارش جدید
            cursor.execute(
                """
                INSERT INTO reports 
                (reporter_id, reported_id, reason, details, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    reporter_id,
                    reported_id,
                    reason,
                    details,
                    'pending',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            )
            conn.commit()

            report_id = cursor.lastrowid

            # لاگ گزارش در admin_logs
            cursor.execute(
                """
                INSERT INTO admin_logs (admin_id, action, details)
                VALUES (?, ?, ?)
                """,
                (
                    0,  # 0 به معنی سیستم
                    'new_report',
                    f'گزارش جدید با شناسه {report_id} ثبت شد'
                )
            )
            conn.commit()

            return cls(db_manager, report_id)
        except Exception as e:
            conn.rollback()
            logger = logging.getLogger('chatogram.models.report')
            logger.error(f"Error creating report: {str(e)}")
            return None

    def update_status(self, status, admin_id=None, admin_notes=None):
        """
        به‌روزرسانی وضعیت گزارش

        Args:
            status (str): وضعیت جدید (pending, approved, rejected)
            admin_id (int, optional): شناسه ادمین
            admin_notes (str, optional): یادداشت‌های ادمین

        Returns:
            bool: True اگر به‌روزرسانی موفق باشد، False در غیر این صورت
        """
        if not self.data:
            return False

        if status not in ['pending', 'approved', 'rejected']:
            self.logger.error(f"Invalid report status: {status}")
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE reports 
                SET status = ?, admin_notes = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    status,
                    admin_notes,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    self.data['id']
                )
            )
            conn.commit()

            # لاگ تغییر وضعیت در admin_logs
            if admin_id:
                cursor.execute(
                    """
                    INSERT INTO admin_logs (admin_id, action, details)
                    VALUES (?, ?, ?)
                    """,
                    (
                        admin_id,
                        f'report_{status}',
                        f'وضعیت گزارش {self.data["id"]} به {status} تغییر یافت'
                    )
                )
                conn.commit()

            self.data['status'] = status
            self.data['admin_notes'] = admin_notes
            self.data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # اگر گزارش تأیید شده، کاربر گزارش‌شده را بن کنیم
            if status == 'approved':
                self._ban_reported_user(admin_id)

            return True
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error updating report status: {str(e)}")
            return False

    def _ban_reported_user(self, admin_id=None):
        """
        مسدود کردن کاربر گزارش‌شده

        Args:
            admin_id (int, optional): شناسه ادمین

        Returns:
            bool: True اگر عملیات موفق باشد، False در غیر این صورت
        """
        if not self.data:
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            # مسدود کردن کاربر
            cursor.execute(
                "UPDATE users SET is_banned = 1 WHERE id = ?",
                (self.data['reported_id'],)
            )

            # پایان دادن به تمام چت‌های فعال کاربر
            cursor.execute(
                """
                UPDATE chats 
                SET is_active = 0, ended_at = ?
                WHERE (user1_id = ? OR user2_id = ?) AND is_active = 1
                """,
                (
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    self.data['reported_id'],
                    self.data['reported_id']
                )
            )
            conn.commit()

            # لاگ مسدودسازی در admin_logs
            if admin_id:
                cursor.execute(
                    """
                    INSERT INTO admin_logs (admin_id, action, details)
                    VALUES (?, ?, ?)
                    """,
                    (
                        admin_id,
                        'ban_user',
                        f'کاربر {self.data["reported_id"]} به دلیل تأیید گزارش {self.data["id"]} مسدود شد'
                    )
                )
                conn.commit()

            return True
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error banning reported user: {str(e)}")
            return False

    def get_reporter_info(self):
        """
        دریافت اطلاعات کاربر گزارش‌دهنده

        Returns:
            dict: اطلاعات کاربر
        """
        if not self.data:
            return {}

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, telegram_id, display_name, username FROM users WHERE id = ?",
            (self.data['reporter_id'],)
        )
        result = cursor.fetchone()

        if result:
            return dict(result)
        return {}

    def get_reported_info(self):
        """
        دریافت اطلاعات کاربر گزارش‌شده

        Returns:
            dict: اطلاعات کاربر
        """
        if not self.data:
            return {}

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, telegram_id, display_name, username, is_banned FROM users WHERE id = ?",
            (self.data['reported_id'],)
        )
        result = cursor.fetchone()

        if result:
            return dict(result)
        return {}

    def get_formatted_date(self):
        """
        دریافت تاریخ گزارش با فرمت مناسب

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
        دریافت متن وضعیت گزارش

        Returns:
            str: متن وضعیت
        """
        if not self.data:
            return ""

        status_map = {
            'pending': 'در انتظار بررسی',
            'approved': 'تأیید شده',
            'rejected': 'رد شده'
        }

        return status_map.get(self.data.get('status', ''), 'نامشخص')

    def get_reason_text(self):
        """
        دریافت متن دلیل گزارش

        Returns:
            str: متن دلیل
        """
        if not self.data:
            return ""

        reason = self.data.get('reason', '')

        # اگر دلیل گزارش یکی از موارد پیش‌فرض باشد، متن مناسب را برگردانیم
        reason_map = {
            'inappropriate': 'محتوای نامناسب',
            'harassment': 'آزار و اذیت',
            'spam': 'اسپم',
            'scam': 'کلاهبرداری',
            'other': 'سایر موارد'
        }

        for key, value in reason_map.items():
            if key in reason:
                return value

        return reason