from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove


start_menu = [[InlineKeyboardButton(text="Зайти в аккаунт", callback_data="login")],
[InlineKeyboardButton(text="Получить список пользователей", callback_data="get_users")],
[InlineKeyboardButton(text="Получить гайд", url="https://t.me/GigaShopGuide")],
[InlineKeyboardButton(text="Все заказы", callback_data="get_orders")],
[InlineKeyboardButton(text="Создать карточку товара", callback_data="create_item")]]

start_menu = InlineKeyboardMarkup(inline_keyboard=start_menu)



