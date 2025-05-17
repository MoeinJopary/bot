import sqlite3
import json
import logging
from config.settings import DB_NAME
from utils.crypto import encrypt, decrypt


class DBManager:
    """
    کلاس مدیریت پایگاه داده
    """

    def __init__(self):
        """
        مقداردهی اولیه مدیریت پایگاه داده
        """
        self.db_name = DB_NAME
        self.logger = logging.getLogger('chatogram.database')
        self.conn = None

    def get_connection(self):
        """
        برقراری اتصال به پایگاه داده
        """
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def setup(self):
        """
        ایجاد جداول پایگاه داده
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # جدول کاربران
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE,
            username TEXT,
            display_name TEXT DEFAULT 'کاربر ناشناس',
            age INTEGER DEFAULT 0,
            gender TEXT,
            bio TEXT DEFAULT 'هنوز اطلاعاتی وارد نشده!',
            city TEXT,
            profile_pic TEXT,
            coins INTEGER DEFAULT 20,
            is_online BOOLEAN DEFAULT 0,
            is_banned BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # جدول چت‌ها
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY,
            user1_id INTEGER,
            user2_id INTEGER,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user1_id) REFERENCES users (id),
            FOREIGN KEY (user2_id) REFERENCES users (id)
        )
        ''')

        # جدول پیام‌ها
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            sender_id INTEGER,
            message_type TEXT,
            content TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats (id),
            FOREIGN KEY (sender_id) REFERENCES users (id)
        )
        ''')

        # جدول تراکنش‌ها
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            amount INTEGER,
            transaction_type TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        # جدول دنبال‌کنندگان
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS followers (
            id INTEGER PRIMARY KEY,
            follower_id INTEGER,
            followed_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (follower_id) REFERENCES users (id),
            FOREIGN KEY (followed_id) REFERENCES users (id)
        )
        ''')

        # جدول لایک‌ها
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            liked_user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (liked_user_id) REFERENCES users (id)
        )
        ''')

        # جدول بلاک‌ها
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocks (
            id INTEGER PRIMARY KEY,
            blocker_id INTEGER,
            blocked_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (blocker_id) REFERENCES users (id),
            FOREIGN KEY (blocked_id) REFERENCES users (id)
        )
        ''')

        # جدول گزارش‌ها
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY,
            reporter_id INTEGER,
            reported_id INTEGER,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reporter_id) REFERENCES users (id),
            FOREIGN KEY (reported_id) REFERENCES users (id)
        )
        ''')

        # جدول دعوت‌ها
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS invites (
            id INTEGER PRIMARY KEY,
            inviter_id INTEGER,
            invited_id INTEGER,
            is_registered BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (inviter_id) REFERENCES users (id),
            FOREIGN KEY (invited_id) REFERENCES users (id)
        )
        ''')

        # جدول تنظیمات
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # جدول فعالیت ادمین‌ها
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY,
            admin_id INTEGER,
            action TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES users (id)
        )
        ''')

        conn.commit()
        self.logger.info("Database tables created successfully")

    def add_user(self, telegram_id, username=None):
        """
        افزودن کاربر جدید
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (telegram_id, username) VALUES (?, ?)",
                (telegram_id, username)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            self.logger.warning(f"User with telegram_id {telegram_id} already exists")
            cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
            result = cursor.fetchone()
            return result['id'] if result else None

    def get_user_by_telegram_id(self, telegram_id):
        """
        دریافت اطلاعات کاربر با شناسه تلگرام
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()

        if result:
            return dict(result)
        return None

    def update_user(self, user_id, **kwargs):
        """
        به‌روزرسانی اطلاعات کاربر
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # ساخت کوئری به‌روزرسانی بر اساس پارامترهای ورودی
        update_fields = []
        update_values = []

        for key, value in kwargs.items():
            update_fields.append(f"{key} = ?")
            update_values.append(value)

        if not update_fields:
            return False

        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        update_values.append(user_id)

        cursor.execute(query, update_values)
        conn.commit()

        return cursor.rowcount > 0

    def start_chat(self, user1_id, user2_id):
        """
        شروع یک چت جدید
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO chats (user1_id, user2_id) VALUES (?, ?)",
            (user1_id, user2_id)
        )
        conn.commit()

        return cursor.lastrowid

    def end_chat(self, chat_id):
        """
        پایان دادن به یک چت
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE chats SET is_active = 0, ended_at = CURRENT_TIMESTAMP WHERE id = ?",
            (chat_id,)
        )
        conn.commit()

        return cursor.rowcount > 0

    def add_message(self, chat_id, sender_id, message_type, content):
        """
        افزودن پیام به چت
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # رمزگذاری محتوای پیام
        encrypted_content = encrypt(content)

        cursor.execute(
            "INSERT INTO messages (chat_id, sender_id, message_type, content) VALUES (?, ?, ?, ?)",
            (chat_id, sender_id, message_type, encrypted_content)
        )
        conn.commit()

        return cursor.lastrowid

    def get_active_chat(self, user_id):
        """
        دریافت چت فعال کاربر
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM chats 
            WHERE (user1_id = ? OR user2_id = ?) AND is_active = 1
        """, (user_id, user_id))

        result = cursor.fetchone()

        if result:
            return dict(result)
        return None

    def get_chat_partner(self, chat_id, user_id):
        """
        دریافت اطلاعات طرف مقابل در چت
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM chats WHERE id = ?
        """, (chat_id,))

        chat = cursor.fetchone()

        if not chat:
            return None

        partner_id = chat['user1_id'] if chat['user2_id'] == user_id else chat['user2_id']

        cursor.execute("SELECT * FROM users WHERE id = ?", (partner_id,))
        result = cursor.fetchone()

        if result:
            return dict(result)
        return None

    def find_random_partner(self, user_id, gender=None, city=None):
        """
        یافتن یک کاربر تصادفی برای چت
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM users 
            WHERE id != ? 
            AND is_online = 1 
            AND is_banned = 0
            AND id NOT IN (
                SELECT user1_id FROM chats WHERE is_active = 1
                UNION
                SELECT user2_id FROM chats WHERE is_active = 1
            )
            AND id NOT IN (
                SELECT blocked_id FROM blocks WHERE blocker_id = ?
                UNION
                SELECT blocker_id FROM blocks WHERE blocked_id = ?
            )
        """

        params = [user_id, user_id, user_id]

        if gender:
            query += " AND gender = ?"
            params.append(gender)

        if city:
            query += " AND city = ?"
            params.append(city)

        query += " ORDER BY RANDOM() LIMIT 1"

        cursor.execute(query, params)
        result = cursor.fetchone()

        if result:
            return dict(result)
        return None

    def search_users(self, search_params, exclude_user_id):
        """
        جستجوی کاربران بر اساس پارامترها
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM users 
            WHERE id != ? 
            AND is_banned = 0
        """

        params = [exclude_user_id]

        if 'gender' in search_params and search_params['gender']:
            query += " AND gender = ?"
            params.append(search_params['gender'])

        if 'city' in search_params and search_params['city']:
            query += " AND city = ?"
            params.append(search_params['city'])

        if 'min_age' in search_params and search_params['min_age']:
            query += " AND age >= ?"
            params.append(search_params['min_age'])

        if 'max_age' in search_params and search_params['max_age']:
            query += " AND age <= ?"
            params.append(search_params['max_age'])

        query += " LIMIT 20"

        cursor.execute(query, params)
        results = cursor.fetchall()

        return [dict(row) for row in results]

    def add_coins(self, user_id, amount, transaction_type, description):
        """
        افزودن سکه به حساب کاربر
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # آپدیت تعداد سکه‌های کاربر
            cursor.execute(
                "UPDATE users SET coins = coins + ? WHERE id = ?",
                (amount, user_id)
            )

            # ثبت تراکنش
            cursor.execute(
                "INSERT INTO transactions (user_id, amount, transaction_type, description) VALUES (?, ?, ?, ?)",
                (user_id, amount, transaction_type, description)
            )

            conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error adding coins: {str(e)}")
            conn.rollback()
            return False

    def use_coins(self, user_id, amount, transaction_type, description):
        """
        استفاده از سکه‌های کاربر
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # بررسی موجودی کافی
        cursor.execute("SELECT coins FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        if not result or result['coins'] < amount:
            return False

        try:
            # کاهش تعداد سکه‌ها
            cursor.execute(
                "UPDATE users SET coins = coins - ? WHERE id = ?",
                (amount, user_id)
            )

            # ثبت تراکنش
            cursor.execute(
                "INSERT INTO transactions (user_id, amount, transaction_type, description) VALUES (?, ?, ?, ?)",
                (user_id, -amount, transaction_type, description)
            )

            conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error using coins: {str(e)}")
            conn.rollback()
            return False

    def toggle_follow(self, follower_id, followed_id):
        """
        دنبال/عدم دنبال کردن کاربر
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # بررسی وضعیت فعلی
        cursor.execute(
            "SELECT id FROM followers WHERE follower_id = ? AND followed_id = ?",
            (follower_id, followed_id)
        )

        existing = cursor.fetchone()

        if existing:
            # حذف دنبال کننده
            cursor.execute(
                "DELETE FROM followers WHERE id = ?",
                (existing['id'],)
            )
            conn.commit()
            return False  # الان دنبال نمی‌کند
        else:
            # افزودن دنبال کننده
            cursor.execute(
                "INSERT INTO followers (follower_id, followed_id) VALUES (?, ?)",
                (follower_id, followed_id)
            )
            conn.commit()
            return True  # الان دنبال می‌کند

    def toggle_like(self, user_id, liked_user_id):
        """
        لایک/عدم لایک کردن کاربر
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # بررسی وضعیت فعلی
        cursor.execute(
            "SELECT id FROM likes WHERE user_id = ? AND liked_user_id = ?",
            (user_id, liked_user_id)
        )

        existing = cursor.fetchone()

        if existing:
            # حذف لایک
            cursor.execute(
                "DELETE FROM likes WHERE id = ?",
                (existing['id'],)
            )
            conn.commit()
            return False  # الان لایک نکرده
        else:
            # افزودن لایک
            cursor.execute(
                "INSERT INTO likes (user_id, liked_user_id) VALUES (?, ?)",
                (user_id, liked_user_id)
            )
            conn.commit()
            return True  # الان لایک کرده

    def toggle_block(self, blocker_id, blocked_id):
        """
        بلاک/آنبلاک کردن کاربر
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # بررسی وضعیت فعلی
        cursor.execute(
            "SELECT id FROM blocks WHERE blocker_id = ? AND blocked_id = ?",
            (blocker_id, blocked_id)
        )

        existing = cursor.fetchone()

        if existing:
            # حذف بلاک
            cursor.execute(
                "DELETE FROM blocks WHERE id = ?",
                (existing['id'],)
            )
            conn.commit()
            return False  # الان بلاک نکرده
        else:
            # افزودن بلاک
            cursor.execute(
                "INSERT INTO blocks (blocker_id, blocked_id) VALUES (?, ?)",
                (blocker_id, blocked_id)
            )
            conn.commit()
            return True  # الان بلاک کرده

    def report_user(self, reporter_id, reported_id, reason):
        """
        گزارش کاربر متخلف
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO reports (reporter_id, reported_id, reason) VALUES (?, ?, ?)",
            (reporter_id, reported_id, reason)
        )
        conn.commit()

        return cursor.lastrowid

    def create_invite(self, inviter_id):
        """
        ایجاد کد دعوت
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO invites (inviter_id, invited_id) VALUES (?, ?)",
            (inviter_id, 0)  # از 0 به عنوان مقدار موقت استفاده می‌کنیم
        )
        conn.commit()

        # از شناسه رکورد به عنوان کد دعوت استفاده می‌کنیم
        invite_id = cursor.lastrowid

        return invite_id

    def register_invite(self, invite_code, invited_user_id):
        """
        ثبت استفاده از کد دعوت
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE invites SET invited_id = ?, is_registered = 1 WHERE id = ? AND is_registered = 0",
                (invited_user_id, invite_code)
            )
            conn.commit()

            if cursor.rowcount > 0:
                # دریافت شناسه دعوت‌کننده
                cursor.execute("SELECT inviter_id FROM invites WHERE id = ?", (invite_code,))
                result = cursor.fetchone()

                if result:
                    return result['inviter_id']

            return None
        except Exception as e:
            self.logger.error(f"Error registering invite: {str(e)}")
            return None

    def close(self):
        """
        بستن اتصال به پایگاه داده
        """
        if self.conn:
            self.conn.close()
            self.conn = None
