import logging

import config
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import TOKEN, WEBHOOK_URL, ADMIN_ID_LIST
from db import create_db_and_tables

# Создание бота и диспетчера
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())


# Функция, выполняемая при запуске бота
async def on_startup(bot: Bot):
    # Создание базы данных и таблиц
    await create_db_and_tables()
    # Установка webhook-а
    await bot.set_webhook(WEBHOOK_URL)
    # Отправка сообщения администраторам о запуске бота
    for admin in ADMIN_ID_LIST:
        try:
            await bot.send_message(admin, 'Bot is working')
        except Exception as e:
            logging.warning(e)


# Функция, выполняемая при остановке бота
async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # Удаление webhook-а
    await bot.delete_webhook()
    # Закрытие хранилища диспетчера
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


# Точка входа в приложение
def main() -> None:
    # Регистрация функции on_startup
    dp.startup.register(on_startup)

    # Создание веб-приложения
    app = web.Application()
    # Создание обработчика запросов к webhook-у
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    # Регистрация обработчика в веб-приложении
    webhook_requests_handler.register(app, path=config.WEBHOOK_PATH)
    # Настройка веб-приложения
    setup_application(app, dp, bot=bot)
    # Запуск веб-приложения
    web.run_app(app, host=config.WEBAPP_HOST, port=config.WEBAPP_PORT)