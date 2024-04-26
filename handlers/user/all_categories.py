from typing import Union

from aiogram import types, Router, F
from aiogram.enums import ParseMode
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.common.common import add_pagination_buttons
from services.buy import BuyService
from services.buyItem import BuyItemService
from services.category import CategoryService
from services.item import ItemService
from services.subcategory import SubcategoryService
from services.user import UserService
from utils.custom_filters import IsUserExistFilter
from utils.notification_manager import NotificationManager


# Класс AllCategoriesCallback определяет структуру данных для обратного вызова "Все категории".
# Он наследуется от CallbackData и имеет префикс "all_categories".
# Атрибуты класса:
# - level: уровень доступа
# - category_id: ID категории
# - subcategory_id: ID подкатегории
# - price: цена товара
# - quantity: количество товара
# - total_price: общая стоимость
# - confirmation: флаг подтверждения
# - page: страница
class AllCategoriesCallback(CallbackData, prefix="all_categories"):
    level: int
    category_id: int
    subcategory_id: int
    price: float
    quantity: int
    total_price: float
    confirmation: bool
    page: int


# Функция create_callback_all_categories создает экземпляр AllCategoriesCallback и упаковывает его в строку.
# Параметры:
# - level: уровень доступа
# - category_id: ID категории (необязательный)
# - subcategory_id: ID подкатегории (необязательный)
# - price: цена товара (необязательный)
# - total_price: общая стоимость (необязательный)
# - quantity: количество товара (необязательный)
# - confirmation: флаг подтверждения (необязательный)
# - page: страница (необязательный)
def create_callback_all_categories(level: int,
                                   category_id: int = -1,
                                   subcategory_id: int = -1,
                                   price: float = 0.0,
                                   total_price: float = 0.0,
                                   quantity: int = 0,
                                   confirmation: bool = False,
                                   page: int = 0):
    return AllCategoriesCallback(level=level, category_id=category_id, subcategory_id=subcategory_id, price=price,
                                 total_price=total_price,
                                 quantity=quantity, confirmation=confirmation, page=page).pack()


# Создание маршрутизатора для "Все категории"
all_categories_router = Router()


# Обработчик текстового сообщения "🔍 All categories"
@all_categories_router.message(F.text == "🔍 All categories", IsUserExistFilter())
async def all_categories_text_message(message: types.message):
    await all_categories(message)


# Функция create_category_buttons создает кнопки для категорий
async def create_category_buttons(page: int):
    # Получаем непроданные категории
    categories = await CategoryService.get_unsold(page)
    if categories:
        # Создаем строитель кнопок для категорий
        categories_builder = InlineKeyboardBuilder()
        # Добавляем кнопки для каждой категории
        for category in categories:
            category_button_callback = create_callback_all_categories(level=1, category_id=category.id)
            category_button = types.InlineKeyboardButton(text=category.name, callback_data=category_button_callback)
            categories_builder.add(category_button)
        # Выравниваем кнопки в два столбца
        categories_builder.adjust(2)
        return categories_builder


# Функция create_subcategory_buttons создает кнопки для подкатегорий
async def create_subcategory_buttons(category_id: int, page: int = 0):
    # Устанавливаем текущий уровень
    current_level = 1
    # Получаем непроданные подкатегории для указанной категории
    items = await ItemService.get_unsold_subcategories_by_category(category_id, page)
    # Создаем строитель кнопок для подкатегорий
    subcategories_builder = InlineKeyboardBuilder()
    # Добавляем кнопки для каждой подкатегории
    for item in items:
        # Получаем цену и доступное количество для подкатегории
        subcategory_price = await ItemService.get_price_by_subcategory(item.subcategory_id)
        available_quantity = await ItemService.get_available_quantity(item.subcategory_id)
        # Создаем обратный вызов для подкатегории
        subcategory_inline_button = create_callback_all_categories(level=current_level + 1,
                                                                   category_id=category_id,
                                                                   subcategory_id=item.subcategory_id,
                                                                   price=subcategory_price)
        # Добавляем кнопку для подкатегории
        subcategories_builder.add(
            types.InlineKeyboardButton(
                text=f"{item.subcategory.name}| Price: ${subcategory_price} | Quantity: {available_quantity} pcs",
                callback_data=subcategory_inline_button))
    # Выравниваем кнопки в один столбец
    subcategories_builder.adjust(1)
    return subcategories_builder


# Функция all_categories обрабатывает отображение всех категорий
async def all_categories(message: Union[Message, CallbackQuery]):
    # Если сообщение - текстовое
    if isinstance(message, Message):
        # Создаем кнопки для категорий
        category_inline_buttons = await create_category_buttons(0)
        # Создаем обратный вызов для нулевого уровня
        zero_level_callback = create_callback_all_categories(0)
        # Если есть категории
        if category_inline_buttons:
            # Добавляем кнопки пагинации
            category_inline_buttons = await add_pagination_buttons(category_inline_buttons, zero_level_callback,
                                                                   CategoryService.get_maximum_page(),
                                                                   AllCategoriesCallback.unpack, None)
            # Отправляем сообщение с кнопками категорий
            await message.answer('🔍 <b>All categories</b>', parse_mode=ParseMode.HTML,
                                 reply_markup=category_inline_buttons.as_markup())
        # Если нет категорий
        else:
            await message.answer('<b>No categories</b>', parse_mode=ParseMode.HTML)
    # Если сообщение - обратный вызов
    elif isinstance(message, CallbackQuery):
        callback = message
        # Получаем распакованный обратный вызов
        unpacked_callback = AllCategoriesCallback.unpack(callback.data)
        # Создаем кнопки для категорий
        category_inline_buttons = await create_category_buttons(unpacked_callback.page)
        # Если есть категории
        if category_inline_buttons:
            # Добавляем кнопки пагинации
            category_inline_buttons = await add_pagination_buttons(category_inline_buttons, callback.data,
                                                                   CategoryService.get_maximum_page(),
                                                                   AllCategoriesCallback.unpack, None)
            # Редактируем сообщение с кнопками категорий
            await callback.message.edit_text('🔍 <b>All categories</b>', parse_mode=ParseMode.HTML,
                                             reply_markup=category_inline_buttons.as_markup())
        # Если нет категорий
        else:
            await callback.message.edit_text('<b>No categories</b>', parse_mode=ParseMode.HTML)


# Функция show_subcategories_in_category отображает подкатегории в выбранной категории
async def show_subcategories_in_category(callback: CallbackQuery):
    # Получаем распакованный обратный вызов
    unpacked_callback = AllCategoriesCallback.unpack(callback.data)
    # Создаем кнопки для подкатегорий
    subcategory_buttons = await create_subcategory_buttons(unpacked_callback.category_id, page=unpacked_callback.page)
    # Создаем кнопку "Назад ко всем категориям"
    back_button = types.InlineKeyboardButton(text="⤵️ Back to all categories",
                                             callback_data=create_callback_all_categories(
                                                 level=unpacked_callback.level - 1))
    # Добавляем кнопки пагинации
    subcategory_buttons = await add_pagination_buttons(subcategory_buttons, callback.data,
                                                       ItemService.get_maximum_page(unpacked_callback.category_id),
                                                       AllCategoriesCallback.unpack,
                                                       back_button)
    # Отправляем сообщение с кнопками подкатегорий
    await callback.message.edit_text("<b>Subcategories:</b>", reply_markup=subcategory_buttons.as_markup(),
                                     parse_mode=ParseMode.HTML)


# Функция select_quantity отображает меню выбора количества товара
async def select_quantity(callback: CallbackQuery):
    # Получаем распакованный обратный вызов
    unpacked_callback = AllCategoriesCallback.unpack(callback.data)
    # Получаем цену, ID подкатегории, ID категории и текущий уровень
    price = unpacked_callback.price
    subcategory_id = unpacked_callback.subcategory_id
    category_id = unpacked_callback.category_id
    current_level = unpacked_callback.level
    # Получаем описание товара
    description = await ItemService.get_description(subcategory_id)
    # Создаем строитель кнопок для выбора количества
    count_builder = InlineKeyboardBuilder()
    # Добавляем кнопки от 1 до 10
    for i in range(1, 11):
        count_button_callback = create_callback_all_categories(level=current_level + 1, category_id=category_id,
                                                               subcategory_id=subcategory_id, price=price,
                                                               quantity=i, total_price=price * i)
        count_button_inline = types.InlineKeyboardButton(text=str(i), callback_data=count_button_callback)
        count_builder.add(count_button_inline)
    # Добавляем кнопку "Назад"
    back_button = types.InlineKeyboardButton(text="Back",
                                             callback_data=create_callback_all_categories(level=current_level - 1,
                                                                                          category_id=category_id))
    count_builder.add(back_button)
    # Выравниваем кнопки в три столбца
    count_builder.adjust(3)
    # Получаем подкатегорию
    subcategory = await SubcategoryService.get_by_primary_key(subcategory_id)
    # Отправляем сообщение с выбором количества
    await callback.message.edit_text(f'<b>You choose:{subcategory.name}\n'
                                     f'Price:${price}\n'
                                     f'Description:{description}\n'
                                     f'Quantity:</b>', reply_markup=count_builder.as_markup(),
                                     parse_mode=ParseMode.HTML)


# Функция buy_confirmation отображает подтверждение покупки
async def buy_confirmation(callback: CallbackQuery):
    # Получаем распакованный обратный вызов
    unpacked_callback = AllCategoriesCallback.unpack(callback.data)
    # Получаем цену, общую стоимость, ID подкатегории, ID категории, текущий уровень и количество
    price = unpacked_callback.price
    total_price = unpacked_callback.total_price
    subcategory_id = unpacked_callback.subcategory_id
    category_id = unpacked_callback.category_id
    current_level = unpacked_callback.level
    quantity = unpacked_callback.quantity
    # Получаем описание товара
    description = await ItemService.get_description(subcategory_id)
    # Создаем строитель кнопок для подтверждения
    confirmation_builder = InlineKeyboardBuilder()
    # Создаем обратные вызовы для подтверждения и отмены
    confirm_button_callback = create_callback_all_categories(level=current_level + 1,
                                                             category_id=category_id,
                                                             subcategory_id=subcategory_id,
                                                             price=price,
                                                             total_price=total_price,
                                                             quantity=quantity,
                                                             confirmation=True)
    decline_button_callback = create_callback_all_categories(level=current_level + 1,
                                                             category_id=category_id,
                                                             subcategory_id=subcategory_id,
                                                             price=price,
                                                             total_price=total_price,
                                                             quantity=quantity,
                                                             confirmation=False)
    # Добавляем кнопки подтверждения, отмены и "Назад"
    confirmation_button = types.InlineKeyboardButton(text="Confirm", callback_data=confirm_button_callback)
    decline_button = types.InlineKeyboardButton(text="Decline", callback_data=decline_button_callback)
    back_button = types.InlineKeyboardButton(text="Back",
                                             callback_data=create_callback_all_categories(level=current_level - 1,
                                                                                          category_id=category_id,
                                                                                          subcategory_id=subcategory_id,
                                                                                          price=price))
    confirmation_builder.add(confirmation_button, decline_button, back_button)
    # Выравниваем кнопки в два столбца
    confirmation_builder.adjust(2)
    # Получаем подкатегорию
    subcategory = await SubcategoryService.get_by_primary_key(subcategory_id)
    # Отправляем сообщение с подтверждением покупки
    await callback.message.edit_text(text=f'<b>You choose:{subcategory.name}\n'
                                          f'Price:${price}\n'
                                          f'Description:{description}\n'
                                          f'Quantity:{quantity}\n'
                                          f'Total price:${total_price}</b>',
                                     reply_markup=confirmation_builder.as_markup(),
                                     parse_mode=ParseMode.HTML)


# Функция buy_processing обрабатывает покупку товара
async def buy_processing(callback: CallbackQuery):
    # Получаем распакованный обратный вызов
    unpacked_callback = AllCategoriesCallback.unpack(callback.data)
    # Получаем флаг подтверждения, общую стоимость, ID подкатегории и количество
    confirmation = unpacked_callback.confirmation
    total_price = unpacked_callback.total_price
    subcategory_id = unpacked_callback.subcategory_id
    quantity = unpacked_callback.quantity
    # Получаем ID пользователя
    telegram_id = callback.from_user.id
    # Проверяем, есть ли товар в наличии
    is_in_stock = await ItemService.get_available_quantity(subcategory_id) >= quantity
    # Проверяем, достаточно ли у пользователя средств
    is_enough_money = await UserService.is_buy_possible(telegram_id, total_price)
    # Создаем кнопку "Назад ко всем категориям"
    back_to_main_builder = InlineKeyboardBuilder()
    back_to_main_callback = create_callback_all_categories(level=0)
    back_to_main_button = types.InlineKeyboardButton(text="🔍 All categories", callback_data=back_to_main_callback)
    back_to_main_builder.add(back_to_main_button)

    # Если подтверждение, товар в наличии и достаточно средств
    if confirmation and is_in_stock and is_enough_money:
        # Обновляем записи о расходах пользователя
        await UserService.update_consume_records(telegram_id, total_price)
        # Получаем проданные товары
        sold_items = await ItemService.get_bought_items(subcategory_id, quantity)
        # Создаем сообщение с информацией о купленных товарах
        message = await create_message_with_bought_items(sold_items)
        # Получаем пользователя
        user = await UserService.get_by_tgid(telegram_id)
        # Создаем новую запись о покупке
        new_buy_id = await BuyService.insert_new(user, quantity, total_price)
        # Добавляем купленные товары к записи о покупке
        await BuyItemService.insert_many(sold_items, new_buy_id)
        # Помечаем купленные товары как проданные
        await ItemService.set_items_sold(sold_items)
        # Отправляем сообщение с информацией о покупке
        await callback.message.edit_text(text=message, parse_mode=ParseMode.HTML)
        # Отправляем уведомление о новой покупке
        await NotificationManager.new_buy(subcategory_id, quantity, total_price, user)
    # Если подтверждение отменено
    elif confirmation is False:
        # Отправляем сообщение об отмене
        await callback.message.edit_text(text='<b>Declined!</b>', parse_mode=ParseMode.HTML,
                                         reply_markup=back_to_main_builder.as_markup())
    # Если недостаточно средств
    elif is_enough_money is False:
        # Отправляем сообщение о недостаточных средствах
        await callback.message.edit_text(text='<b>Insufficient funds!</b>', parse_mode=ParseMode.HTML,
                                         reply_markup=back_to_main_builder.as_markup())
    # Если товара нет в наличии
    elif is_in_stock is False:
        # Отправляем сообщение об отсутствии товара
        await callback.message.edit_text(text='<b>Out of stock!</b>', parse_mode=ParseMode.HTML,
                                         reply_markup=back_to_main_builder.as_markup())


# Функция create_message_with_bought_items создает сообщение с информацией о купленных товарах
async def create_message_with_bought_items(bought_data: list):
    message = "<b>"
    for count, item in enumerate(bought_data, start=1):
        private_data = item.private_data
        message += f"Item#{count}\nData:<code>{private_data}</code>\n"
    message += "</b>"
    return message


# Обработчик обратных вызовов для "Все категории"
@all_categories_router.callback_query(AllCategoriesCallback.filter(), IsUserExistFilter())
async def navigate_categories(call: CallbackQuery, callback_data: AllCategoriesCallback):
    # Получаем текущий уровень из обратного вызова
    current_level = callback_data.level

    # Словарь, сопоставляющий уровни с соответствующими функциями
    levels = {
        0: all_categories,
        1: show_subcategories_in_category,
        2: select_quantity,
        3: buy_confirmation,
        4: buy_processing
    }

    # Получаем функцию, соответствующую текущему уровню
    current_level_function = levels[current_level]

    # Вызываем функцию, соответствующую текущему уровню
    await current_level_function(call)
