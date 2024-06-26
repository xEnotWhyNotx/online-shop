from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from aiogram import types


select_role_button = [[
    InlineKeyboardButton(text="Покупатель", callback_data="user_is_customer"),
    InlineKeyboardButton(text="Продавец", callback_data= "user_is_seller")
                    ]]
                    
select_role_menu = InlineKeyboardMarkup(inline_keyboard = select_role_button)

admin_role_button = [
     [InlineKeyboardButton(text="Получить список всех пользователей", callback_data="get_users")],
     [InlineKeyboardButton(text="Получить список всех заказов", callback_data="get_all_orders")],
     [InlineKeyboardButton(text="Поиск по названию", callback_data="search_by_name")],
     [InlineKeyboardButton(text="Создать промокод", callback_data="create_promocode")],
     [InlineKeyboardButton(text="Сменить роль на продавца", callback_data="request_role_change_to_seller")],
     [InlineKeyboardButton(text="Получить гайд", url="https://t.me/GigaShopGuide")]
     ]

admin_role_menu = InlineKeyboardMarkup(inline_keyboard=admin_role_button)

seller_role_button = [
     [InlineKeyboardButton(text="Добавить карточку товара", callback_data="create_item")],
     [InlineKeyboardButton(text="Отобразить заказы моего магазина", callback_data="get_this_seller_orders")],
     [InlineKeyboardButton(text="Создать промокод", callback_data="create_promocode")],
     [InlineKeyboardButton(text="Изменить название магазина", callback_data="plug")],
     [InlineKeyboardButton(text="Сменить роль на покупателя", callback_data="switch_user_role_to_customer")],
     [InlineKeyboardButton(text="Получить гайд", url="https://t.me/GigaShopGuide")]
               ]

seller_role_menu = InlineKeyboardMarkup(inline_keyboard=seller_role_button)

customer_role_button = [
     [InlineKeyboardButton(text="Поиск по названию", callback_data="search_by_name")],
     [InlineKeyboardButton(text="Все товары", callback_data = "show_all_items")],
     [InlineKeyboardButton(text="Найти товар через конфигуратор", callback_data = "plug")],
     [InlineKeyboardButton(text="Ввести промокод", callback_data="enter_promocode")],
     [InlineKeyboardButton(text="Сменить роль на продавца", callback_data="request_role_change_to_seller")],
     #[InlineKeyboardButton(text="Сменить роль на продавца", callback_data="switch_user_role_to_seller")],
     [InlineKeyboardButton(text="Отобразить мои заказы", callback_data= "get_this_customer_orders")],
     [InlineKeyboardButton(text="Получить гайд", url="https://t.me/GigaShopGuide")]
               ]

customer_role_menu = InlineKeyboardMarkup(inline_keyboard=customer_role_button)

select_discount_button = [
    [InlineKeyboardButton(text=f"5%", callback_data=f"discount_5")],
    [InlineKeyboardButton(text=f"10%", callback_data=f"discount_10")],
    [InlineKeyboardButton(text=f"15%", callback_data=f"discount_15")],
    [InlineKeyboardButton(text=f"20%", callback_data=f"discount_20")],
    [InlineKeyboardButton(text=f"25%", callback_data=f"discount_25")],
    [InlineKeyboardButton(text="Назад", callback_data="go_back")]
]
back_button = [
    [InlineKeyboardButton(text="Назад", callback_data="go_back_customer")]
]

seller_dicount_menu = InlineKeyboardMarkup(inline_keyboard=select_discount_button)

back_button_menu = InlineKeyboardMarkup(inline_keyboard=back_button)

back_button1 = InlineKeyboardButton(text="Назад", callback_data="go_back_latest")
back_to_menu = InlineKeyboardMarkup(inline_keyboard=[[back_button1]])
