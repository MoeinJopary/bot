import sqlite3
import logging
from config.settings import DB_NAME


def create_tables():
    """
    ایجاد جداول پایگاه داده
    """
    logger = logging.getLogger('chatogram.database.migrations')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
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
            profile_pic_status TEXT DEFAULT 'pending',
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
            payment_info TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            details TEXT,
            status TEXT DEFAULT 'pending',
            admin_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
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
            registered_at TIMESTAMP,
            FOREIGN KEY (inviter_id) REFERENCES users (id),
            FOREIGN KEY (invited_id) REFERENCES users (id)
        )
        ''')

        # جدول درخواست‌های چت
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_requests (
            id INTEGER PRIMARY KEY,
            requester_id INTEGER,
            requested_id INTEGER,
            message TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (requester_id) REFERENCES users (id),
            FOREIGN KEY (requested_id) REFERENCES users (id)
        )
        ''')

        # جدول تنظیمات
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            description TEXT,
            category TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by INTEGER
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

        # جدول بسته‌های سکه
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS coin_packages (
            id INTEGER PRIMARY KEY,
            name TEXT,
            amount INTEGER,
            price INTEGER,
            discount_percent INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        logger.info("Database tables created successfully")

        # درج تنظیمات پیش‌فرض
        default_settings = [
            ('min_age', '18', 'حداقل سن مجاز برای استفاده از ربات', 'profile'),
            ('enable_location_filter', 'true', 'فعال بودن فیلتر موقعیت مکانی', 'search'),
            ('max_daily_chat_requests', '10', 'حداکثر تعداد درخواست چت روزانه', 'chat'),
            ('auto_approve_profile_pics', 'false', 'تأیید خودکار عکس پروفایل', 'profile'),
            ('welcome_message', 'به ربات چتوگرام خوش آمدید!', 'پیام خوش‌آمدگویی به کاربران جدید', 'general'),
            ('maintenance_mode', 'false', 'حالت تعمیر و نگهداری ربات', 'system'),
            ('initial_coins', '20', 'تعداد سکه‌های اولیه برای کاربران جدید', 'economy'),
            ('chat_request_coins', '5', 'هزینه ارسال درخواست چت', 'economy'),
            ('advanced_search_coins', '10', 'هزینه استفاده از جستجوی پیشرفته', 'economy'),
            ('invite_reward_coins', '10', 'پاداش دعوت دوستان', 'economy')
        ]

        for key, value, description, category in default_settings:
            cursor.execute(
                """
                INSERT OR IGNORE INTO settings (key, value, description, category) 
                VALUES (?, ?, ?, ?)
                """,
                (key, value, description, category)
            )

        # درج بسته‌های سکه پیش‌فرض
        default_packages = [
            ('بسته برنزی', 100, 5000, 0),
            ('بسته نقره‌ای', 300, 12000, 10),
            ('بسته طلایی', 500, 18000, 15),
            ('بسته الماسی', 1000, 30000, 20)
        ]

        for name, amount, price, discount in default_packages:
            cursor.execute(
                """
                INSERT OR IGNORE INTO coin_packages (name, amount, price, discount_percent) 
                VALUES (?, ?, ?, ?)
                """,
                (name, amount, price, discount)
            )

        conn.commit()
        logger.info("Default settings and packages inserted successfully")

    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
    finally:
        conn.close()


def apply_migrations():
    """
    اعمال به‌روزرسانی‌های پایگاه داده
    """
    logger = logging.getLogger('chatogram.database.migrations')

    try:
        # ابتدا جداول اصلی را ایجاد می‌کنیم
        create_tables()

        # اینجا می‌توانیم به‌روزرسانی‌های آتی را اضافه کنیم
        # مثال: add_new_column_to_users()

        logger.info("All migrations applied successfully")
    except Exception as e:
        logger.error(f"Error applying migrations: {str(e)}")


# این تابع می‌تواند در نسخه‌های آینده برای اضافه کردن ستون جدید به جدول کاربران استفاده شود
def add_new_column_to_users():
    """
    اضافه کردن ستون جدید به جدول کاربران
    """
    logger = logging.getLogger('chatogram.database.migrations')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        # بررسی وجود ستون
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        # اضافه کردن ستون جدید اگر وجود ندارد
        if 'new_column' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN new_column TEXT")
            conn.commit()
            logger.info("Added new_column to users table")
    except Exception as e:
        logger.error(f"Error adding new column: {str(e)}")
    finally:
        conn.close()