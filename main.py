import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router


async def main():
    bot = Bot(token="BOT_TOKEN")
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

# BIM-BIM BAM-BAM
# import logging
# import asyncio
# from aiogram import Bot, Dispatcher
# from handlers import questions, different_types
# from aiogram.fsm.state import StatesGroup, State
#
#
# logging.basicConfig(level=logging.INFO)
#
#
# class TelegramStates(StatesGroup):
#     main_menu = State()
#     search_menu = State()
#     personal_account = State()
#     favorites = State()
#     my_orders = State()
#     bonuses = State()
#     settings = State()
#     configurator = State()
#     model_selection = State()
#     color_selection = State()
#     memory_selection = State()
#     condition_selection = State()
#
#
# # Запуск бота
# async def main():
#     bot = Bot(token="")
#     dp = Dispatcher()
#
#     dp.include_routers(questions.router, different_types.router)
#
#     # Альтернативный вариант регистрации роутеров по одному на строку
#     # dp.include_router(questions.router)
#     # dp.include_router(different_types.router)
#
#     # Запускаем бота и пропускаем все накопленные входящие
#     # Да, этот метод можно вызвать даже если у вас поллинг
#     await bot.delete_webhook(drop_pending_updates=True)
#     await dp.start_polling(bot)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())


########################################################################################################################
# # Команды для начала работы с ботом
# @dp.message(F.text, Command('start'))
# async def cmd_start(message: types.Message):
#     await message.answer("Привет! Это главное меню.", reply_markup=get_main_menu())
#
#
# # Обработка кнопок главного меню
# @dp.message(lambda message: message.text == "Поиск", state="*")
# async def process_search_button(message: types.Message, state: FSMContext):
#     await message.answer("Вы в разделе поиска.", reply_markup=get_search_menu())
#     await state.set_state(SearchMenuStates.search_menu)
#
#
# @dp.message(lambda message: message.text == "Личный кабинет", state="*")
# async def process_profile_button(message: types.Message, state: FSMContext):
#     await message.answer("Вы в личном кабинете.", reply_markup=get_main_menu())
#
#
# @dp.message(lambda message: message.text == "Помощь", state="*")
# async def process_help_button(message: types.Message, state: FSMContext):
#     await message.answer("Вы в разделе помощи.", reply_markup=get_main_menu())
#
#
# @dp.message(lambda message: message.text == "О нас", state="*")
# async def process_about_button(message: types.Message, state: FSMContext):
#     await message.answer("Информация о нас.", reply_markup=get_main_menu())
#
#
# # Машина состояний для меню поиска
# class SearchMenuStates(StatesGroup):
#     search_menu = State()
#
#
# # Обработка кнопок меню поиска
# @dp.message(lambda message: message.text == "Поиск по названию", state=SearchMenuStates.search_menu)
# async def process_search_by_name_button(message: types.Message, state: FSMContext):
#     await message.answer("Вы выбрали поиск по названию.", reply_markup=get_search_menu())
#     # Ваш код обработки
#
#
# @dp.message(lambda message: message.text == "Конфигуратор", state=SearchMenuStates.search_menu)
# async def process_configurator_button(message: types.Message, state: FSMContext):
#     await message.answer("Вы выбрали конфигуратор.", reply_markup=get_search_menu())
#     # Ваш код обработки
#
#
# @dp.message(lambda message: message.text == "Назад", state=SearchMenuStates.search_menu)
# async def process_back_button(message: types.Message, state: FSMContext):
#     await message.answer("Вы вернулись в главное меню.", reply_markup=get_main_menu())
#     await state.set_state(None)
#
#
# # Функции для получения разметки клавиатуры
# def get_main_menu():
#     buttons = [
#         KeyboardButton("Поиск"),
#         KeyboardButton("Личный кабинет"),
#         KeyboardButton("Помощь"),
#         KeyboardButton("О нас")
#     ]
#     return ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)
#
#
# def get_search_menu():
#     buttons = [
#         KeyboardButton("Поиск по названию"),
#         KeyboardButton("Конфигуратор"),
#         KeyboardButton("Назад")
#     ]
#     return ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)
#
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     dp.start_polling(dp, loop=loop, skip_updates=True)
