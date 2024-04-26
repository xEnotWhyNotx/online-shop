# Импорт необходимых библиотек и модулей
from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import dp, main  # Диспетчер и основной модуль бота
from config import SUPPORT_LINK  # Импорт ссылки на поддержку
import logging

# Импорт роутеров для различных функциональностей
from handlers.admin.admin import admin_router
from handlers.user.all_categories import all_categories_router
from handlers.user.my_profile import my_profile_router
from handlers.user.Nikita_handlers import nikita_router
from services.user import UserService  # Сервис для работы с пользователями
from utils.custom_filters import IsUserExistFilter  # Фильтр проверки существования пользователя
import kb  # Модуль с клавиатурами
import Nikita_text  # Модуль с текстами

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Определение команд start и help
@dp.message(Command(commands=["start", "help"]))
async def start(message: types.message):
    # Создание кнопок для клавиатуры
    all_categories_button = types.KeyboardButton(text='🔍 All categories')
    my_profile_button = types.KeyboardButton(text='🎓 My profile')
    faq_button = types.KeyboardButton(text='🤝 FAQ')
    help_button = types.KeyboardButton(text='🚀 Help')
    # Группировка кнопок в клавиатуру
    keyboard = [[all_categories_button, my_profile_button], [faq_button, help_button]]
    start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=keyboard)

    # Получение информации о пользователе
    user_telegram_id = message.chat.id
    user_telegram_username = message.from_user.username
    # Проверка существования пользователя и создание/обновление данных
    is_exist = await UserService.is_exist(user_telegram_id)
    if is_exist is False:
        await UserService.create(user_telegram_id, user_telegram_username)
    else:
        await UserService.update_receive_messages(user_telegram_id, True)
        await UserService.update_username(user_telegram_id, user_telegram_username)
    # Ответ пользователю с приветствием и клавиатурой
    await message.answer(Nikita_text.greet.format(name=message.from_user.full_name), reply_markup=kb.start_menu)

# Определение команды FAQ
@dp.message(F.text == '🤝 FAQ', IsUserExistFilter())
async def faq(message: types.message):
    # Отправка правил магазина
    faq_string = """<b>В нашем магазине незнание правил не освобождает вас от ответственности. Покупая хотя бы один продукт в магазине, вы автоматически соглашаетесь со всеми правилами магазина!\n
Правила магазина</b>\n

❗️1. В случае неадекватного/оскорбительного поведения продавец имеет право отказать в обслуживании!  
❗️2. Замена предоставляется только если продукт недействителен.
❗️3. Замена предоставляется только при наличии видеодоказательства.
❗️4. Гарантийный период 30 минут.
❗️5. Администрация не несет ответственности за любые незаконные действия, совершенные покупателем с товарами, приобретенными в магазине.
❗️6. Эти правила и условия могут изменяться в любое время.
❗️7. Деньги не могут быть сняты с вашего баланса."""
    await message.answer(faq_string, parse_mode='html')


# Обработчик сообщения для команды "Help"
@dp.message(F.text == '🚀 Help', IsUserExistFilter())
async def support(message: types.message):
    # Создание объекта для построения инлайн-клавиатуры
    admin_keyboard_builder = InlineKeyboardBuilder()
    # Добавление кнопки с ссылкой на администратора
    admin_keyboard_builder.button(text='Admin', url=SUPPORT_LINK)
    # Отправка сообщения с кнопкой для перехода к администратору
    await message.answer(f'<b>Support</b>', parse_mode='html', reply_markup=admin_keyboard_builder.as_markup())

# Создание главного роутера
main_router = Router()
# Включение в главный роутер других роутеров для разных функциональностей
main_router.include_router(admin_router)  # Роутер для административных функций
main_router.include_router(my_profile_router)  # Роутер для профиля пользователя
main_router.include_router(all_categories_router)  # Роутер для просмотра всех категорий
main_router.include_router(nikita_router)  # Роутер для специфических обработчиков
# Добавление главного роутера в диспетчер
dp.include_router(main_router)

# Запуск бота, если скрипт выполняется как основная программа
if __name__ == '__main__':
    main()
