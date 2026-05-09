import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ChatMemberHandler
from config import BOT_TOKEN
from handlers.subscription import start, check_command, check_callback, greet_new_member
from handlers.admin import restrict_unsubscribed

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("checkall", restrict_unsubscribed))
    application.add_handler(CallbackQueryHandler(check_callback, pattern="^check_sub$"))
    application.add_handler(ChatMemberHandler(greet_new_member, ChatMemberHandler.CHAT_MEMBER))
    
    logging.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()