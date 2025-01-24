import asyncio, logging, sys
from aiogram import Bot, Dispatcher
# from app.handlers import router
# from app.tests import router as tester_router
from app.keyboards import set_commands
from decouple import config
from app.middlewares.cleanup import CleanupMiddleware
from app.handlers.products import router as product_router
from app.handlers.main_handlers import router
from app.handlers.stocks import router as stock_router

TOKEN = config('TELEGRAM_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.message.middleware(CleanupMiddleware())

dp.include_router(router)
dp.include_router(product_router)
dp.include_router(stock_router)

async def main():
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot stopped')