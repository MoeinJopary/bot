import logging
from utils.crypto import encrypt, decrypt


class Chat:
    """
    کلاس مدل چت
    """

    def __init__(self, db_manager, chat_id=None, chat_data=None):
        """
        مقداردهی اولیه مدل چت
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger('chatogram.models.chat')

        if chat_data:
            self.data = chat_data
        elif chat_id:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM chats WHERE id = ?", (chat_id,))
            result = cursor.fetchone()

            if result:
                self.data = dict(result)
            else:
                self.data = None
        else:
            self.data = None

    @classmethod
    def create(cls, db_manager, user1_id, user2_id):
        """
        ایجاد چت جدید
        """
        chat_id = db_manager.start_chat(user1_id, user2_id)
        return cls(db_manager, chat_id)

    def end(self):
        """
        پایان دادن به چت
        """
        if not self.data or not self.data.get('is_active', False):
            return False

        success = self.db_manager.end_chat(self.data['id'])

        if success:
            self.data['is_active'] = False

        return success

    def add_message(self, sender_id, message_type, content):
        """
        افزودن پیام به چت
        """
        if not self.data or not self.data.get('is_active', False):
            return False

        return self.db_manager.add_message(
            self.data['id'],
            sender_id,
            message_type,
            content
        )

    def get_messages(self, limit=50):
        """
        دریافت پیام‌های چت
        """
        if not self.data:
            return []

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM messages 
            WHERE chat_id = ? 
            ORDER BY sent_at DESC 
            LIMIT ?
            """,
            (self.data['id'], limit)
        )

        messages = [dict(row) for row in cursor.fetchall()]

        # رمزگشایی محتوای پیام‌ها
        for message in messages:
            if message.get('content'):
                try:
                    message['content'] = decrypt(message['content'])
                except Exception as e:
                    self.logger.error(f"Error decrypting message: {str(e)}")
                    message['content'] = "[خطا در رمزگشایی پیام]"

        # مرتب‌سازی پیام‌ها به ترتیب زمان ارسال
        messages.sort(key=lambda m: m.get('sent_at', ''))

        return messages

    def get_partner_id(self, user_id):
        """
        دریافت شناسه کاربر مقابل در چت
        """
        if not self.data:
            return None

        if self.data['user1_id'] == user_id:
            return self.data['user2_id']
        elif self.data['user2_id'] == user_id:
            return self.data['user1_id']
        else:
            return None

    def is_participant(self, user_id):
        """
        بررسی اینکه آیا کاربر در چت شرکت دارد
        """
        if not self.data:
            return False

        return self.data['user1_id'] == user_id or self.data['user2_id'] == user_id
