from handlers.start_handler import StartHandler
from handlers.profile_handler import ProfileHandler
from handlers.chat_handler import ChatHandler
from handlers.search_handler import SearchHandler
from handlers.coin_handler import CoinHandler
from handlers.social_handler import SocialHandler
from admin.admin_base import AdminHandler


def register_all_handlers(bot, db_manager):
    """
    ثبت تمام هندلرها
    """
    handlers = [
        StartHandler(bot, db_manager),
        ProfileHandler(bot, db_manager),
        ChatHandler(bot, db_manager),
        SearchHandler(bot, db_manager),
        CoinHandler(bot, db_manager),
        SocialHandler(bot, db_manager),
        AdminHandler(bot, db_manager)
    ]

    for handler in handlers:
        handler.register_handlers()