from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from aiogram import types
# menu = [
#     [InlineKeyboardButton(text="📝 Генерировать текст", callback_data="generate_text"),
#      InlineKeyboardButton(text="🖼 Генерировать изображение", callback_data="generate_image")],
#     [InlineKeyboardButton(text="💳 Купить токены", callback_data="buy_tokens"),
#      InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
#     [InlineKeyboardButton(text="💎 Партнёрская программа", callback_data="ref"),
#      InlineKeyboardButton(text="🎁 Бесплатные токены", callback_data="free_tokens")],
#     [InlineKeyboardButton(text="🔎 Помощь", callback_data="help")]
# ]



select_role_button = [[
    KeyboardButton(text="Покупатель"),
    KeyboardButton(text="Продавец")
                    ]]
                    

select_role_menu = ReplyKeyboardMarkup(keyboard = select_role_button, resize_keyboard = True)

start_menu1 = [[InlineKeyboardButton(text="Зайти в аккаунт", callback_data="login")],
     [InlineKeyboardButton(text="Получить гайд", url="https://t.me/GigaShopGuide")]]



start_menu1 = [[InlineKeyboardButton(text="Зайти в аккаунт", callback_data="login")],
     [InlineKeyboardButton(text="Получить гайд", url="https://t.me/GigaShopGuide")]]

#admin_menu = [InlineKeyboardButton(text="Получить список пользователей", callback_data="get_users")]

start_menu = InlineKeyboardMarkup(inline_keyboard=start_menu1)
#admin_menu = InlineKeyboardMarkup(inline_keyboard= admin_menu)

exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])
