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

def search_by_name_menu():
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="Поиск по названию", callback_data="search_by_name")
    markup.add(button)
    return markup



select_role_button = [[
    InlineKeyboardButton(text="Покупатель", callback_data="user_is_customer"),
    InlineKeyboardButton(text="Продавец", callback_data= "user_is_seller")
                    ]]
                    
select_role_menu = InlineKeyboardMarkup(inline_keyboard = select_role_button)

admin_role_button = [
     [InlineKeyboardButton(text="Получить список всех пользователей", callback_data="get_users")],
     [InlineKeyboardButton(text="Получить список всех заказов", callback_data="get_all_orders")],
     [InlineKeyboardButton(text="Поиск по названию", callback_data="search_by_name")],
     [InlineKeyboardButton(text="Получить гайд", url="https://t.me/GigaShopGuide")]
     ]

admin_role_menu = InlineKeyboardMarkup(inline_keyboard=admin_role_button)

seller_role_button = [
     [InlineKeyboardButton(text="Добавить карточку товара", callback_data="create_item")],
     [InlineKeyboardButton(text="Отобразить заказы моего магазина", callback_data="get_this_seller_orders")],
     [InlineKeyboardButton(text="Изменить название магазина", callback_data="plug")],
     [InlineKeyboardButton(text="Сменить роль на покупателя", callback_data="switch_user_role_to_customer")],
     [InlineKeyboardButton(text="Получить гайд", url="https://t.me/GigaShopGuide")]
               ]

seller_role_menu = InlineKeyboardMarkup(inline_keyboard=seller_role_button)

customer_role_button = [
     [InlineKeyboardButton(text="Поиск по названию", callback_data="search_by_name")],
     [InlineKeyboardButton(text= "Все товары", callback_data = "show_all_items")],
     [InlineKeyboardButton(text="Указать интересующий товар вручную", callback_data = "plug")],
     [InlineKeyboardButton(text="Найти товар через конфигуратор", callback_data = "plug")],
     [InlineKeyboardButton(text="Сменить роль на продавца", callback_data="switch_user_role_to_seller")],
     [InlineKeyboardButton(text="Отобразить мои заказы", callback_data= "get_this_customer_orders")],
     [InlineKeyboardButton(text="Получить гайд", url="https://t.me/GigaShopGuide")]
               ]

customer_role_menu = InlineKeyboardMarkup(inline_keyboard=customer_role_button)


#admin_menu = [InlineKeyboardButton(text="Получить список пользователей", callback_data="get_users")]

#admin_menu = InlineKeyboardMarkup(inline_keyboard= admin_menu)

exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])

