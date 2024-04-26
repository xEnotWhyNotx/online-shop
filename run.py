from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import dp, main
from config import SUPPORT_LINK
import logging

from handlers.admin.admin import admin_router
from handlers.user.all_categories import all_categories_router
from handlers.user.my_profile import my_profile_router
from handlers.user.Nikita_handlers import nikita_router
from services.user import UserService
from utils.custom_filters import IsUserExistFilter
import kb
import Nikita_text
logging.basicConfig(level=logging.INFO)


@dp.message(Command(commands=["start", "help"]))
async def start(message: types.message):
    all_categories_button = types.KeyboardButton(text='🔍 All categories')
    my_profile_button = types.KeyboardButton(text='🎓 My profile')
    faq_button = types.KeyboardButton(text='🤝 FAQ')
    help_button = types.KeyboardButton(text='🚀 Help')
    keyboard = [[all_categories_button, my_profile_button], [faq_button, help_button]]
    start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=keyboard)
    user_telegram_id = message.chat.id
    user_telegram_username = message.from_user.username
    is_exist = await UserService.is_exist(user_telegram_id)
    if is_exist is False:
        await UserService.create(user_telegram_id, user_telegram_username)
    else:
        await UserService.update_receive_messages(user_telegram_id, True)
        await UserService.update_username(user_telegram_id, user_telegram_username)
    #await message.answer('Hi', reply_markup=start_markup)
    await message.answer(Nikita_text.greet.format(name=message.from_user.full_name), reply_markup=kb.start_menu)


@dp.message(F.text == '🤝 FAQ', IsUserExistFilter())
async def faq(message: types.message):
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


@dp.message(F.text == '🚀 Help', IsUserExistFilter())
async def support(message: types.message):
    admin_keyboard_builder = InlineKeyboardBuilder()

    admin_keyboard_builder.button(text='Admin', url=SUPPORT_LINK)
    await message.answer(f'<b>Support</b>', reply_markup=admin_keyboard_builder.as_markup())


main_router = Router()
main_router.include_router(admin_router)
main_router.include_router(my_profile_router)
main_router.include_router(all_categories_router)
main_router.include_router(nikita_router)
dp.include_router(main_router)

if __name__ == '__main__':
    main()
