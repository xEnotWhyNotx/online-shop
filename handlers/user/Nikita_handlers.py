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
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputFile

import csv
from Nikita_db import BotDB
import aiofiles
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from States import user_states


router = Router()
id = 0
bot_db = BotDB('online-shop.db')

nikita_router = Router()

@nikita_router.callback_query(F.data == "get_users")
async def get_users(query: types.CallbackQuery):
    #Формируем файл со списком пользователей#
    bot_db = BotDB('online-shop.db')
    data = bot_db.users_list()

    csv_file = 'users_list.csv'

    try:
        async with aiofiles.open(csv_file, mode='rb') as file:
            input_file = types.FSInputFile('users_list.csv')
            await query.message.answer_document(input_file)
    except Exception as e:
        print(f"Произошла ошибка при отправке файла: {e}")
        await query.message.answer(text="Произошла ошибка при отправке файла")

@nikita_router.callback_query(F.data == "get_orders")
async def get_orders(query: types.CallbackQuery):
    bot_db.check_orders()
    csv_file = 'current_orders.csv'

    try:
        async with aiofiles.open(csv_file, mode='rb') as file:
            input_file = types.FSInputFile('current_orders.csv')
            await query.message.answer_document(input_file)
    except Exception as e:
        print(f"Произошла ошибка при отправке файла: {e}")
        await query.message.answer(text="Произошла ошибка при отправке файла")

@nikita_router.callback_query(F.data == "create_item")
async def create_item(query:types.CallbackQuery, state:FSMContext):
    #Инициализация создания новой карточки товара#
    new_id = bot_db.create_new_item()
    await query.message.answer(text="Пожалуйста, укажите название для нового товара")
    #await state.set("new_item_id", new_id)  # Сохраняем id созданного товара в состоянии
    await state.set_state(user_states.waiting_for_name)  # Переводим стейт в ожидание названия
    

@nikita_router.message(user_states.waiting_for_name)
async def add_name(message: Message, state: FSMContext):
    item_name = message.text
    bot_db.insert_name(item_name)
    await message.answer(text=f"Отлично! Теперь укажите описание к товару.")
    await state.set_state(user_states.waiting_for_description)

@nikita_router.message(user_states.waiting_for_description)
async def add_description(message: Message, state: FSMContext):
    bot_db.insert_description(message.text)
    await message.answer(text=f"Теперь укажите цену товара.")
    await state.set_state(user_states.waiting_for_price)

@nikita_router.message(user_states.waiting_for_price)
async def add_price(message: Message, state: FSMContext):
    bot_db.insert_price(message.text)
    await message.answer(text="Теперь укажите количество товара в наличии.")
    await state.set_state(user_states.waiting_for_amount)

@nikita_router.message(user_states.waiting_for_amount)
async def add_amount(message: Message, state: FSMContext):
    bot_db.insert_amount(message.text)
    await message.answer(text="Новый товар успешно создан!")
    await state.clear()