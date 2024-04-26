import asyncio
import inspect
import logging
from typing import Union

from aiogram import types, Router, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from bot import bot
from handlers.common.common import add_pagination_buttons
from services.buy import BuyService
from services.category import CategoryService
from services.item import ItemService
from services.subcategory import SubcategoryService
from services.user import UserService
from utils.custom_filters import AdminIdFilter
from utils.new_items_manager import NewItemsManager
from utils.notification_manager import NotificationManager
from utils.other_sql import OtherSQLQuery


# Класс AdminCallback определяет структуру данных для обратного вызова администратора.
# Он наследуется от CallbackData и имеет префикс "admin".
# Атрибуты класса:
# - level: уровень доступа администратора
# - action: действие, которое должно быть выполнено
# - args_to_action: аргументы для действия
# - page: страница, на которой находится администратор
class AdminCallback(CallbackData, prefix="admin"):
    level: int
    action: str
    args_to_action: Union[str, int]
    page: int


# Создание маршрутизатора для администраторских команд
admin_router = Router()


# Функция create_admin_callback создает экземпляр AdminCallback и упаковывает его в строку.
# Параметры:
# - level: уровень доступа администратора
# - action: действие, которое должно быть выполнено (необязательный)
# - args_to_action: аргументы для действия (необязательный)
# - page: страница, на которой находится администратор (необязательный)
def create_admin_callback(level: int, action: str = "", args_to_action: str = "", page: int = 0):
    return AdminCallback(level=level, action=action, args_to_action=args_to_action, page=page).pack()


# Класс AdminConstants содержит константы, используемые в администраторском меню.
class AdminConstants:
    # Создание кнопок подтверждения и отмены
    confirmation_builder = InlineKeyboardBuilder()
    confirmation_button = types.InlineKeyboardButton(text="Confirm",
                                                     callback_data=create_admin_callback(level=2, action="confirm"))
    decline_button = types.InlineKeyboardButton(text="Decline",
                                                callback_data=create_admin_callback(level=3, action="decline"))
    confirmation_builder.add(decline_button, confirmation_button)

    # Кнопка "Назад в главное меню администратора"
    back_to_main_button = types.InlineKeyboardButton(text="Back to admin menu",
                                                     callback_data=create_admin_callback(level=0))

    # Статический метод, который создает кнопку "Назад" с соответствующим обратным вызовом
    @staticmethod
    async def get_back_button(unpacked_callback: AdminCallback) -> types.InlineKeyboardButton:
        new_callback = unpacked_callback.model_copy(update={"level": unpacked_callback.level - 1})
        return types.InlineKeyboardButton(text="Back", callback_data=new_callback.pack())


# Обработчик команды "/admin" для администраторов
@admin_router.message(Command("admin"), AdminIdFilter())
async def admin_command_handler(message: types.message):
    await admin(message)


# Функция, отображающая меню администратора
async def admin(message: Union[Message, CallbackQuery]):
    admin_menu_builder = InlineKeyboardBuilder()

    # Добавление кнопок в меню администратора
    admin_menu_builder.button(text="Send to everyone",
                              callback_data=create_admin_callback(level=1,
                                                                  action="send_to_everyone"))
    admin_menu_builder.button(text="Add items",
                              callback_data=create_admin_callback(level=4,
                                                                  action="add_items"))
    admin_menu_builder.button(text="Send restocking message",
                              callback_data=create_admin_callback(
                                  level=5,
                                  action="send_to_everyone"))
    admin_menu_builder.button(text="Get database file",
                              callback_data=create_admin_callback(
                                  level=6,
                                  action="get_db_file"
                              ))
    admin_menu_builder.button(text="Delete category",
                              callback_data=create_admin_callback(
                                  level=7
                              ))
    admin_menu_builder.button(text="Delete subcategory",
                              callback_data=create_admin_callback(
                                  level=8
                              ))
    admin_menu_builder.button(text="Make refund",
                              callback_data=create_admin_callback(
                                  level=11
                              ))
    admin_menu_builder.button(text="Statistics",
                              callback_data=create_admin_callback(level=14))
    admin_menu_builder.adjust(2)

    # Отправка меню администратора
    if isinstance(message, Message):
        await message.answer("<b>Admin Menu:</b>", parse_mode=ParseMode.HTML,
                             reply_markup=admin_menu_builder.as_markup())
    elif isinstance(message, CallbackQuery):
        callback = message
        await callback.message.edit_text("<b>Admin Menu:</b>", parse_mode=ParseMode.HTML,
                                         reply_markup=admin_menu_builder.as_markup())


# Определение состояний для администраторских действий
class AdminStates(StatesGroup):
    message_to_send = State()
    new_items_file = State()


# Обработчик действия "Отправить всем"
async def send_to_everyone(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("<b>Send a message to the newsletter</b>:", parse_mode=ParseMode.HTML)
    await state.set_state(AdminStates.message_to_send)


# Обработчик сообщения с текстом для рассылки
@admin_router.message(AdminIdFilter(), StateFilter(AdminStates.message_to_send))
async def get_message_to_sending(message: types.message, state: FSMContext):
    await message.copy_to(message.chat.id, reply_markup=AdminConstants.confirmation_builder.as_markup())
    await state.clear()

# Функция confirm_and_send обрабатывает подтверждение отправки сообщения всем пользователям
async def confirm_and_send(callback: CallbackQuery):
    # Отвечаем пользователю, что отправка началась
    await callback.answer(text="Sending started")

    # Проверяем, было ли действие "confirm"
    confirmed = AdminCallback.unpack(callback.data).action == "confirm"

    # Проверяем, есть ли подпись у сообщения и содержит ли сообщение текст об обновлении
    is_caption = callback.message.caption
    is_restocking = callback.message.text and callback.message.text.__contains__("📅 Update")

    if confirmed:
        # Счетчик успешно отправленных сообщений
        counter = 0
        # Получаем общее количество пользователей
        users_count = await UserService.get_all_users_count()
        # Получаем список ID пользователей для рассылки
        telegram_ids = await UserService.get_users_tg_ids_for_sending()

        # Отправляем сообщение каждому пользователю
        for telegram_id in telegram_ids:
            try:
                # Копируем сообщение и отправляем пользователю
                await callback.message.copy_to(telegram_id, reply_markup=None)
                counter += 1
                # Делаем паузу, чтобы не перегружать Telegram
                await asyncio.sleep(1.5)
            except TelegramForbiddenError as e:
                # Обрабатываем ошибки, связанные с блокировкой бота пользователем
                logging.error(f"TelegramForbiddenError: {e.message}")
                if "user is deactivated" in e.message.lower():
                    await UserService.update_receive_messages(telegram_id, False)
                elif "bot was blocked by the user" in e.message.lower():
                    await UserService.update_receive_messages(telegram_id, False)
            except Exception as e:
                # Обрабатываем другие исключения
                logging.error(e)

        # Формируем текст сообщения об итогах рассылки
        message_text = (f"<b>Message sent to {counter} out of {len(telegram_ids)} active users.\n"
                        f"Total users:{users_count}</b>")

        # Отправляем или редактируем сообщение с итогами рассылки
        if is_caption:
            await callback.message.delete()
            await callback.message.answer(text=message_text, parse_mode=ParseMode.HTML)
        elif callback.message.text:
            await callback.message.edit_text(
                text=message_text,
                parse_mode=ParseMode.HTML)

    # Если сообщение содержит информацию об обновлении, помечаем товары как не новые
    if is_restocking:
        await ItemService.set_items_not_new()


# Функция decline_action обрабатывает отмену действия
async def decline_action(callback: CallbackQuery):
    # Удаляем сообщение с подтверждением и отправляем сообщение об отмене
    await callback.message.delete()
    await callback.message.answer(text="<b>Declined!</b>", parse_mode=ParseMode.HTML)


# Функция add_items обрабатывает добавление новых товаров
async def add_items(callback: CallbackQuery, state: FSMContext):
    # Получаем распакованный обратный вызов
    unpacked_callback = AdminCallback.unpack(callback.data)

    # Если уровень доступа 4 и действие "add_items"
    if unpacked_callback.level == 4 and unpacked_callback.action == "add_items":
        # Отправляем сообщение с инструкциями по добавлению товаров
        await callback.message.edit_text(text="<b>Send .json file with new items or type \"cancel\" for cancel.</b>",
                                         parse_mode=ParseMode.HTML)
        # Устанавливаем состояние для ожидания файла с новыми товарами
        await state.set_state(AdminStates.new_items_file)


# Обработчик сообщения с файлом новых товаров или командой "cancel"
@admin_router.message(AdminIdFilter(), F.document | F.text, StateFilter(AdminStates.new_items_file))
async def receive_new_items_file(message: types.message, state: FSMContext):
    # Если получен файл
    if message.document:
        # Очищаем состояние
        await state.clear()
        # Задаем имя файла
        file_name = "new_items.json"
        # Получаем ID файла
        file_id = message.document.file_id
        # Загружаем файл
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, file_name)
        # Добавляем новые товары
        adding_result = await NewItemsManager.add(file_name)
        # Обрабатываем результат добавления
        if isinstance(adding_result, BaseException):
            await message.answer(text=f"<b>Exception:</b>\n<code>{adding_result}</code>", parse_mode=ParseMode.HTML)
        elif type(adding_result) is int:
            await message.answer(text=f"<b>Successfully added {adding_result} items!</b>", parse_mode=ParseMode.HTML)
    # Если получена команда "cancel"
    elif message.text and message.text.lower() == "cancel":
        # Очищаем состояние и отправляем сообщение об отмене
        await state.clear()
        await message.answer("<b>Adding items successfully cancelled!</b>", parse_mode=ParseMode.HTML)
    # Если получено что-то другое, отправляем инструкции
    else:
        await message.answer(text="<b>Send .json file with new items or type \"cancel\" for cancel.</b>",
                             parse_mode=ParseMode.HTML)


# Функция send_restocking_message отправляет сообщение об обновлении товаров
async def send_restocking_message(callback: CallbackQuery):
    # Генерируем сообщение об обновлении
    message = await NewItemsManager.generate_restocking_message()
    # Отправляем сообщение с кнопками подтверждения
    await callback.message.answer(message, parse_mode=ParseMode.HTML,
                                  reply_markup=AdminConstants.confirmation_builder.as_markup())


# Функция delete_category обрабатывает удаление категории
async def delete_category(callback: CallbackQuery):
    # Получаем распакованный обратный вызов
    unpacked_callback = AdminCallback.unpack(callback.data)
    # Создаем кнопки для удаления категорий
    delete_category_builder = await create_delete_entity_buttons(
        CategoryService.get_all_categories(
            unpacked_callback.page),
        "category")
    # Добавляем кнопки пагинации
    delete_category_builder = await add_pagination_buttons(delete_category_builder, callback.data,
                                                           CategoryService.get_maximum_page(), AdminCallback.unpack,
                                                           AdminConstants.back_to_main_button)
    # Отправляем сообщение с кнопками для удаления категорий
    await callback.message.edit_text(text="<b>Categories:</b>", parse_mode=ParseMode.HTML,
                                     reply_markup=delete_category_builder.as_markup())


# Функция create_delete_entity_buttons создает кнопки для удаления сущностей
async def create_delete_entity_buttons(get_all_entities_function,
                                       entity_name):
    # Получаем все сущности
    entities = await get_all_entities_function
    # Создаем строитель кнопок для удаления
    delete_entity_builder = InlineKeyboardBuilder()
    # Добавляем кнопки для каждой сущности
    for entity in entities:
        delete_entity_callback = create_admin_callback(level=9,
                                                       action=f"delete_{entity_name}",
                                                       args_to_action=entity.id)
        delete_entity_button = types.InlineKeyboardButton(text=entity.name, callback_data=delete_entity_callback)
        delete_entity_builder.add(delete_entity_button)
    # Выравниваем кнопки в один столбец
    delete_entity_builder.adjust(1)
    return delete_entity_builder


# Функция delete_subcategory обрабатывает удаление подкатегории
async def delete_subcategory(callback: CallbackQuery):
    # Получаем распакованный обратный вызов
    unpacked_callback = AdminCallback.unpack(callback.data)
    # Создаем кнопки для удаления подкатегорий
    delete_subcategory_builder = await create_delete_entity_buttons(
        SubcategoryService.get_all(unpacked_callback.page),
        "subcategory")
    # Добавляем кнопки пагинации
    delete_subcategory_builder = await add_pagination_buttons(delete_subcategory_builder, callback.data,
                                                              SubcategoryService.get_maximum_page(),
                                                              AdminCallback.unpack,
                                                              AdminConstants.back_to_main_button)
    # Отправляем сообщение с кнопками для удаления подкатегорий
    await callback.message.edit_text(text="<b>Subcategories:</b>", parse_mode=ParseMode.HTML,
                                     reply_markup=delete_subcategory_builder.as_markup())


# Функция delete_confirmation обрабатывает подтверждение удаления сущности
async def delete_confirmation(callback: CallbackQuery):
    # Получаем распакованный обратный вызов
    unpacked_callback = AdminCallback.unpack(callback.data)
    # Получаем текущий уровень, действие и аргументы
    current_level = unpacked_callback.level
    action = unpacked_callback.action
    args_to_action = unpacked_callback.args_to_action
    # Создаем кнопки подтверждения и отмены
    delete_markup = InlineKeyboardBuilder()
    confirm_callback = create_admin_callback(level=current_level + 1,
                                             action=f"confirmed_{action}",
                                             args_to_action=args_to_action)
    confirm_button = types.InlineKeyboardButton(text="Confirm", callback_data=confirm_callback)
    decline_callback = create_admin_callback(level=current_level - 6)
    decline_button = types.InlineKeyboardButton(text="Decline", callback_data=decline_callback)
    delete_markup.add(confirm_button, decline_button)
    # Определяем, что именно нужно удалить (категорию или подкатегорию)
    entity_to_delete = action.split('_')[-1]
    if entity_to_delete == "category":
        # Получаем категорию для удаления
        category_id = args_to_action
        category = await CategoryService.get_by_primary_key(category_id)
        # Отправляем сообщение с запросом на подтверждение удаления категории
        await callback.message.edit_text(text=f"<b>Do you really want to delete the category {category.name}?</b>",
                                         parse_mode=ParseMode.HTML,
                                         reply_markup=delete_markup.as_markup())
    elif entity_to_delete == "subcategory":
        # Получаем подкатегорию для удаления
        subcategory_id = args_to_action
        subcategory = await SubcategoryService.get_by_primary_key(subcategory_id)
        # Отправляем сообщение с запросом на подтверждение удаления подкатегории
        await callback.message.edit_text(
            text=f"<b>Do you really want to delete the subcategory {subcategory.name}?</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=delete_markup.as_markup())


# Функция confirm_and_delete обрабатывает подтверждение удаления категории или подкатегории
async def confirm_and_delete(callback: CallbackQuery):
    # Получаем распакованный обратный вызов
    unpacked_callback = AdminCallback.unpack(callback.data)
    # Получаем аргументы для действия и тип сущности, которую нужно удалить
    args_to_action = unpacked_callback.args_to_action
    entity_to_delete = unpacked_callback.action.split('_')[-1]
    # Создаем кнопку "Назад в главное меню"
    back_to_main_builder = InlineKeyboardBuilder()
    back_to_main_builder.add(AdminConstants.back_to_main_button)

    # Если нужно удалить категорию
    if entity_to_delete == "category":
        # TODO: Реализовать каскадное удаление подкатегорий и товаров, связанных с категорией
        category = await CategoryService.get_by_primary_key(args_to_action)
        message_text = f"<b>Successfully deleted {category.name} {entity_to_delete}!</b>"
        # Удаляем непроданные товары, связанные с категорией
        await ItemService.delete_unsold_with_category_id(args_to_action)
        # Отправляем сообщение об успешном удалении категории
        await callback.message.edit_text(text=message_text,
                                         parse_mode=ParseMode.HTML, reply_markup=back_to_main_builder.as_markup())
    # Если нужно удалить подкатегорию
    elif entity_to_delete == "subcategory":
        subcategory = await SubcategoryService.get_by_primary_key(args_to_action)
        message_text = f"<b>Successfully deleted {subcategory.name} {entity_to_delete}!</b>"
        # Удаляем товары, связанные с подкатегорией
        await ItemService.delete_with_subcategory_id(args_to_action)
        # Удаляем подкатегорию, если она не используется
        await SubcategoryService.delete_if_not_used(args_to_action)
        # Отправляем сообщение об успешном удалении подкатегории
        await callback.message.edit_text(text=message_text,
                                         parse_mode=ParseMode.HTML, reply_markup=back_to_main_builder.as_markup())


# Функция make_refund_markup создает кнопки для возврата средств
async def make_refund_markup(page):
    # Создаем строитель кнопок для возврата средств
    refund_builder = InlineKeyboardBuilder()
    # Получаем ID покупок, которые еще не были возвращены
    not_refunded_buy_ids = await BuyService.get_not_refunded_buy_ids(page)
    # Получаем данные о покупках, которые нужно возвратить
    refund_data = await OtherSQLQuery.get_refund_data(not_refunded_buy_ids)
    # Добавляем кнопки для каждой покупки
    for buy in refund_data:
        if buy.telegram_username:
            # Если у пользователя есть username, используем его
            refund_buy_button = types.InlineKeyboardButton(
                text=f"@{buy.telegram_username}|${buy.total_price}|{buy.subcategory}",
                callback_data=create_admin_callback(level=12,
                                                    action="make_refund",
                                                    args_to_action=buy.buy_id))
        else:
            # Если у пользователя нет username, используем его ID
            refund_buy_button = types.InlineKeyboardButton(
                text=f"ID:{buy.telegram_id}|${buy.total_price}|{buy.subcategory}",
                callback_data=create_admin_callback(level=12,
                                                    action="make_refund",
                                                    args_to_action=buy.buy_id))
        refund_builder.add(refund_buy_button)
    # Выравниваем кнопки в один столбец
    refund_builder.adjust(1)
    return refund_builder


# Функция send_refund_menu отображает меню возврата средств
async def send_refund_menu(callback: CallbackQuery):
    # Получаем распакованный обратный вызов
    unpacked_callback = AdminCallback.unpack(callback.data)
    # Создаем кнопки для возврата средств
    refund_builder = await make_refund_markup(unpacked_callback.page)
    # Добавляем кнопки пагинации
    refund_builder = await add_pagination_buttons(refund_builder, callback.data, BuyService.get_max_refund_pages(),
                                                  AdminCallback.unpack, AdminConstants.back_to_main_button)
    # Отправляем меню возврата средств
    await callback.message.edit_text(text="<b>Refund menu:</b>", reply_markup=refund_builder.as_markup(),
                                     parse_mode=ParseMode.HTML)


# Функция refund_confirmation отображает запрос на подтверждение возврата средств
async def refund_confirmation(callback: CallbackQuery):
    # Получаем распакованный обратный вызов
    unpacked_callback = AdminCallback.unpack(callback.data)
    # Получаем текущий уровень и ID покупки для возврата
    current_level = unpacked_callback.level
    buy_id = int(unpacked_callback.args_to_action)
    # Создаем кнопку "Назад"
    back_button = await AdminConstants.get_back_button(unpacked_callback)
    # Создаем кнопку "Подтвердить"
    confirm_button = types.InlineKeyboardButton(text="Confirm",
                                                callback_data=create_admin_callback(level=current_level + 1,
                                                                                    action="confirm_refund",
                                                                                    args_to_action=str(buy_id)))

    # Создаем строитель кнопок подтверждения
    confirmation_builder = InlineKeyboardBuilder()
    confirmation_builder.add(confirm_button, AdminConstants.decline_button, back_button)
    # Получаем данные о покупке для возврата
    refund_data = await OtherSQLQuery.get_refund_data_single(buy_id)
    # Отправляем запрос на подтверждение возврата средств
    if refund_data.telegram_username:
        await callback.message.edit_text(
            text=f"<b>Do you really want to refund user @{refund_data.telegram_username} "
                 f"for purchasing {refund_data.quantity} {refund_data.subcategory} "
                 f"in the amount of ${refund_data.total_price}</b>", parse_mode=ParseMode.HTML,
            reply_markup=confirmation_builder.as_markup())
    else:
        await callback.message.edit_text(
            text=f"<b>Do you really want to refund user with ID:{refund_data.telegram_id} "
                 f"for purchasing {refund_data.quantity} {refund_data.subcategory} "
                 f"in the amount of ${refund_data.total_price}</b>", parse_mode=ParseMode.HTML,
            reply_markup=confirmation_builder.as_markup())


# Функция pick_statistics_entity отображает меню выбора типа статистики
async def pick_statistics_entity(callback: CallbackQuery):
    # Получаем распакованный обратный вызов
    unpacked_callback = AdminCallback.unpack(callback.data)
    # Создаем обратные вызовы для статистики пользователей и покупок
    users_statistics_callback = create_admin_callback(unpacked_callback.level + 1, "users")
    buys_statistics_callback = create_admin_callback(unpacked_callback.level + 1, "buys")
    # Создаем строитель кнопок
    buttons_builder = InlineKeyboardBuilder()
    # Добавляем кнопки для выбора типа статистики
    buttons_builder.add(types.InlineKeyboardButton(text="📊Users statistics", callback_data=users_statistics_callback))
    buttons_builder.add(types.InlineKeyboardButton(text="📊Buys statistics", callback_data=buys_statistics_callback))
    # Добавляем кнопку "Назад в главное меню"
    buttons_builder.row(AdminConstants.back_to_main_button)
    # Отправляем сообщение с кнопками выбора типа статистики
    await callback.message.edit_text(text="<b>📊 Pick statistics entity</b>", reply_markup=buttons_builder.as_markup(),
                                     parse_mode=ParseMode.HTML)


# Функция pick_statistics_timedelta отображает меню выбора временного интервала для статистики
async def pick_statistics_timedelta(callback: CallbackQuery):
    # Получаем распакованный обратный вызов
    unpacked_callback = AdminCallback.unpack(callback.data)
    # Создаем обратные вызовы для выбора временного интервала в 1, 7 и 30 дней
    one_day_cb = unpacked_callback.model_copy(
        update={"args_to_action": '1', 'level': unpacked_callback.level + 1}).pack()
    seven_days_cb = unpacked_callback.model_copy(
        update={"args_to_action": '7', 'level': unpacked_callback.level + 1}).pack()
    one_month_cb = unpacked_callback.model_copy(
        update={"args_to_action": '30', 'level': unpacked_callback.level + 1}).pack()
    # Создаем строитель кнопок
    timedelta_buttons_builder = InlineKeyboardBuilder()
    # Добавляем кнопки для выбора временного интервала
    timedelta_buttons_builder.add(types.InlineKeyboardButton(text="1 Day", callback_data=one_day_cb))
    timedelta_buttons_builder.add(types.InlineKeyboardButton(text="7 Days", callback_data=seven_days_cb))
    timedelta_buttons_builder.add(types.InlineKeyboardButton(text="30 Days", callback_data=one_month_cb))
    # Добавляем кнопку "Назад"
    timedelta_buttons_builder.row(await AdminConstants.get_back_button(unpacked_callback))
    # Отправляем сообщение с кнопками выбора временного интервала
    await callback.message.edit_text(text="<b>🗓 Pick timedelta to statistics</b>",
                                     reply_markup=timedelta_buttons_builder.as_markup(), parse_mode=ParseMode.HTML)


# Функция get_statistics отображает статистику
async def get_statistics(callback: CallbackQuery):
    # Получаем распакованный обратный вызов
    unpacked_callback = AdminCallback.unpack(callback.data)
    # Создаем строитель кнопок
    statistics_keyboard_builder = InlineKeyboardBuilder()

    # Если выбрана статистика пользователей
    if unpacked_callback.action == "users":
        # Получаем новых пользователей за указанный период времени
        users, users_count = await UserService.get_new_users_by_timedelta(unpacked_callback.args_to_action,
                                                                          unpacked_callback.page)
        # Добавляем кнопки с username пользователей
        for user in users:
            if user.telegram_username:
                user_button = types.InlineKeyboardButton(text=user.telegram_username,
                                                         url=f"t.me/{user.telegram_username}")
                statistics_keyboard_builder.add(user_button)
        # Выравниваем кнопки в один столбец
        statistics_keyboard_builder.adjust(1)
        # Добавляем кнопки пагинации
        statistics_keyboard_builder = await add_pagination_buttons(statistics_keyboard_builder, callback.data,
                                                                   UserService.get_max_page_for_users_by_timedelta(
                                                                       unpacked_callback.args_to_action),
                                                                   AdminCallback.unpack, None)
        # Добавляем кнопки "Назад" и "Назад в главное меню"
        statistics_keyboard_builder.row(
            *[AdminConstants.back_to_main_button, await AdminConstants.get_back_button(unpacked_callback)])
        # Отправляем сообщение со статистикой пользователей
        await callback.message.edit_text(
            text=f"<b>{users_count} new users in the last {unpacked_callback.args_to_action} days:</b>",
            reply_markup=statistics_keyboard_builder.as_markup(), parse_mode=ParseMode.HTML)

    # Если выбрана статистика покупок
    elif unpacked_callback.action == "buys":
        # Получаем кнопку "Назад"
        back_button = await AdminConstants.get_back_button(unpacked_callback)
        # Добавляем кнопки "Назад" и "Назад в главное меню"
        buttons = [back_button,
                   AdminConstants.back_to_main_button]
        statistics_keyboard_builder.add(*buttons)
        # Получаем новые покупки за указанный период времени
        buys = await BuyService.get_new_buys_by_timedelta(unpacked_callback.args_to_action)
        # Рассчитываем общую прибыль, количество проданных товаров и общее количество покупок
        total_profit = 0
        items_sold = 0
        for buy in buys:
            total_profit += buy.total_price
            items_sold += buy.quantity
        # Отправляем сообщение со статистикой покупок
        await callback.message.edit_text(
            text=f"<b>📊 Sales statistics for the last {unpacked_callback.args_to_action} days.\n"
                 f"💰 Total profit: ${total_profit}\n"
                 f"🛍️ Items sold: {items_sold}\n"
                 f"💼 Total buys: {len(buys)}</b>", reply_markup=statistics_keyboard_builder.as_markup(),
            parse_mode=ParseMode.HTML)


# Функция make_refund обрабатывает подтверждение возврата средств
async def make_refund(callback: CallbackQuery):
    # Получаем распакованный обратный вызов
    unpacked_callback = AdminCallback.unpack(callback.data)
    # Получаем ID покупки для возврата
    buy_id = int(unpacked_callback.args_to_action)
    # Проверяем, было ли действие "confirm_refund"
    is_confirmed = unpacked_callback.action == "confirm_refund"

    # Если действие подтверждено
    if is_confirmed:
        # Получаем данные о покупке для возврата
        refund_data = await OtherSQLQuery.get_refund_data_single(buy_id)
        # Выполняем возврат средств
        await BuyService.refund(buy_id, refund_data)
        # Отправляем уведомление пользователю о возврате средств
        await NotificationManager.send_refund_message(refund_data)
        # Отправляем сообщение об успешном возврате средств
        if refund_data.telegram_username:
            await callback.message.edit_text(text=f"<b>Successfully refunded ${refund_data.total_price} "
                                                  f"to user {refund_data.telegram_username} "
                                                  f"for purchasing {refund_data.quantity} "
                                                  f"{refund_data.subcategory}</b>", parse_mode=ParseMode.HTML)
        else:
            await callback.message.edit_text(text=f"<b>Successfully refunded ${refund_data.total_price} "
                                                  f"to user with ID{refund_data.telegram_id} "
                                                  f"for purchasing {refund_data.quantity} "
                                                  f"{refund_data.subcategory}</b>", parse_mode=ParseMode.HTML)


# Функция send_db_file отправляет администратору файл базы данных
async def send_db_file(callback: CallbackQuery):
    # Открываем файл базы данных и отправляем его администратору
    with open(f"./data/{config.DB_NAME}", "rb") as f:
        await callback.message.bot.send_document(callback.from_user.id,
                                                 types.BufferedInputFile(file=f.read(), filename="database.db"))
    # Отвечаем на обратный вызов
    await callback.answer()


# Обработчик обратных вызовов администратора
@admin_router.callback_query(AdminIdFilter(), AdminCallback.filter())
async def admin_menu_navigation(callback: CallbackQuery, state: FSMContext, callback_data: AdminCallback):
    # Получаем текущий уровень доступа из обратного вызова
    current_level = callback_data.level

    # Словарь, сопоставляющий уровни доступа с соответствующими функциями
    levels = {
        0: admin,
        1: send_to_everyone,
        2: confirm_and_send,
        3: decline_action,
        4: add_items,
        6: send_db_file,
        5: send_restocking_message,
        7: delete_category,
        8: delete_subcategory,
        9: delete_confirmation,
        10: confirm_and_delete,
        11: send_refund_menu,
        12: refund_confirmation,
        13: make_refund,
        14: pick_statistics_entity,
        15: pick_statistics_timedelta,
        16: get_statistics
    }

    # Получаем функцию, соответствующую текущему уровню доступа
    current_level_function = levels[current_level]
    # Проверяем, требуется ли контекст состояния для вызова функции
    if inspect.getfullargspec(current_level_function).annotations.get("state") == FSMContext:
        # Вызываем функцию с контекстом состояния
        await current_level_function(callback, state)
    else:
        # Вызываем функцию без контекста состояния
        await current_level_function(callback)
