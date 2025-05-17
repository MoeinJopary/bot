from telebot import types
from handlers.base_handler import BaseHandler
from models.user import User


class SocialHandler(BaseHandler):
    """
    کلاس مدیریت تعاملات اجتماعی
    """

    def register_handlers(self):
        """
        ثبت هندلرهای پیام
        """

        # مشاهده لیست دنبال‌کنندگان
        @self.bot.message_handler(commands=['followers'])
        def handle_followers(message):
            try:
                self.update_user_status(message)

                user = self.get_user(message.from_user.id)

                # دریافت لیست دنبال‌کنندگان
                followers = self.db_manager.get_followers(user.data['id'])

                if not followers:
                    self.bot.send_message(
                        message.chat.id,
                        "👁 هنوز کسی شما را دنبال نکرده است."
                    )
                    return

                # نمایش لیست دنبال‌کنندگان
                follower_text = "👁 *لیست دنبال‌کنندگان شما*\n\n"

                for i, follower in enumerate(followers, 1):
                    follower_user = User(self.db_manager, user_data=follower)
                    follower_text += f"{i}. {follower_user.data.get('display_name', 'کاربر ناشناس')}\n"

                self.bot.send_message(
                    message.chat.id,
                    follower_text,
                    parse_mode='Markdown'
                )
            except Exception as e:
                self.logger.error(f"Error in followers handler: {str(e)}")

        # مشاهده لیست دنبال‌شده‌ها
        @self.bot.message_handler(commands=['following'])
        def handle_following(message):
            try:
                self.update_user_status(message)

                user = self.get_user(message.from_user.id)

                # دریافت لیست دنبال‌شده‌ها
                following = self.db_manager.get_following(user.data['id'])

                if not following:
                    self.bot.send_message(
                        message.chat.id,
                        "👁 شما هنوز کسی را دنبال نکرده‌اید."
                    )
                    return

                # نمایش لیست دنبال‌شده‌ها
                following_text = "👁 *لیست کاربرانی که دنبال می‌کنید*\n\n"

                for i, followed in enumerate(following, 1):
                    followed_user = User(self.db_manager, user_data=followed)
                    following_text += f"{i}. {followed_user.data.get('display_name', 'کاربر ناشناس')}\n"

                self.bot.send_message(
                    message.chat.id,
                    following_text,
                    parse_mode='Markdown'
                )
            except Exception as e:
                self.logger.error(f"Error in following handler: {str(e)}")

        # مشاهده لیست لایک‌ها
        @self.bot.message_handler(commands=['likes'])
        def handle_likes(message):
            try:
                self.update_user_status(message)

                user = self.get_user(message.from_user.id)

                # دریافت لیست لایک‌ها
                likes = self.db_manager.get_likes(user.data['id'])

                if not likes:
                    self.bot.send_message(
                        message.chat.id,
                        "❤️ هنوز کسی پروفایل شما را لایک نکرده است."
                    )
                    return

                # نمایش لیست لایک‌ها
                likes_text = "❤️ *لیست کاربرانی که پروفایل شما را لایک کرده‌اند*\n\n"

                for i, like in enumerate(likes, 1):
                    like_user = User(self.db_manager, user_data=like)
                    likes_text += f"{i}. {like_user.data.get('display_name', 'کاربر ناشناس')}\n"

                self.bot.send_message(
                    message.chat.id,
                    likes_text,
                    parse_mode='Markdown'
                )
            except Exception as e:
                self.logger.error(f"Error in likes handler: {str(e)}")

        # مشاهده لیست بلاک
        @self.bot.message_handler(commands=['blocks'])
        def handle_blocks(message):
            try:
                self.update_user_status(message)

                user = self.get_user(message.from_user.id)

                # دریافت لیست بلاک‌ها
                blocks = self.db_manager.get_blocks(user.data['id'])

                if not blocks:
                    self.bot.send_message(
                        message.chat.id,
                        "⛔ شما هنوز کسی را بلاک نکرده‌اید."
                    )
                    return

                # نمایش لیست بلاک‌ها
                blocks_text = "⛔ *لیست کاربران بلاک شده*\n\n"

                for i, block in enumerate(blocks, 1):
                    block_user = User(self.db_manager, user_data=block)
                    blocks_text += f"{i}. {block_user.data.get('display_name', 'کاربر ناشناس')} "
                    blocks_text += f"- [آنبلاک](/unblock_{block_user.data['id']})\n"

                blocks_text += "\nبرای آنبلاک کردن یک کاربر، روی لینک «آنبلاک» کلیک کنید."

                self.bot.send_message(
                    message.chat.id,
                    blocks_text,
                    parse_mode='Markdown'
                )
            except Exception as e:
                self.logger.error(f"Error in blocks handler: {str(e)}")

        # آنبلاک کردن کاربر
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("unblock_"))
        def handle_unblock(call):
            try:
                self.bot.answer_callback_query(call.id)

                target_user_id = int(call.data.split("_")[1])
                user = self.get_user(call.from_user.id)

                # آنبلاک کردن کاربر
                self.db_manager.toggle_block(user.data['id'], target_user_id)

                self.bot.edit_message_text(
                    "✅ کاربر با موفقیت از لیست بلاک خارج شد.",
                    call.message.chat.id,
                    call.message.message_id
                )
            except Exception as e:
                self.logger.error(f"Error in unblock handler: {str(e)}")
