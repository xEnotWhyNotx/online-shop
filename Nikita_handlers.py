from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputFile
import kb
import text
import csv
from Nikita_db import BotDB
import aiofiles
from States import user_states
from aiogram.fsm.context import FSMContext
rt = Router()
bot_db = BotDB('online-shop_V2_1.db')





@rt.message(Command("start"))
async def start_handler(msg: Message, state:FSMContext):
    user_id = msg.from_user.id
    name= msg.from_user.full_name
    bot_db = BotDB('online-shop_V2_1.db')
    if bot_db.is_user_in_db(user_id):

        user_role = bot_db.get_role(user_id)
        
        if user_role == ('Seller',):
            await msg.answer(text = f"Вы авторизованы как продавец. С возвращением, {name}", reply_markup= kb.seller_role_menu)
        
        elif user_role == ('Customer',):
            await msg.answer(text = f"Вы авторизованы как покупатель. С возвращением, {name}", reply_markup=kb.customer_role_menu)

        
        elif user_role == ('Administrator',):
            await msg.answer(text = f"Вы авторизованы как администратор. С возвращением, {name}", reply_markup=kb.admin_role_menu)
    
    else:
        bot_db.create_new_user(user_id)
        await msg.answer(text = f"Кажется, вы у нас впервые. Пожалуйста, выберите роль.", reply_markup= kb.select_role_menu)
        await state.set_state(user_states.waiting_for_users_role)


@rt.message(user_states.waiting_for_users_role)
async def add_role(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "Продавец":
        bot_db.insert_seller(user_id)
        await message.answer(text=f"Вы были успешно добавлены как продавец. Для продолжения введите команду /start")
        await state.clear()
    elif message.text == "Покупатель":
        bot_db.insert_customer(user_id)
        await message.answer(text=f"Вы были успешно добавлены как покупатель. Для продолжения введите команду /start")
        await state.clear()

@rt.callback_query(F.data == "get_all_orders")
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
        await query.answer()

@rt.callback_query(F.data == "get_users")
async def get_users(query: types.CallbackQuery):
    ##
    data = bot_db.users_list()

    csv_file = 'users_list.csv'

    try:
        async with aiofiles.open(csv_file, mode='rb') as file:
            input_file = types.FSInputFile('users_list.csv')
            await query.message.answer_document(input_file)
            await query.answer()
    except Exception as e:
        print(f"Произошла ошибка при отправке файла: {e}")
        await query.message.answer(text="Произошла ошибка при отправке файла")
        await query.answer()


    
@rt.callback_query(F.data == "create_item")
async def create_item(query:types.CallbackQuery, state:FSMContext):
    #Инициализация создания новой карточки товара#
    new_id = bot_db.create_new_item()
    await query.message.answer(text="Пожалуйста, укажите название для нового товара")
    #await state.set("new_item_id", new_id)  # Сохраняем id созданного товара в состоянии
    await state.set_state(user_states.waiting_for_name)  # Переводим стейт в ожидание названия
    

@rt.message(user_states.waiting_for_name)
async def add_name(message: Message, state: FSMContext):
    item_name = message.text
    bot_db.insert_name(item_name)
    await message.answer(text=f"Отлично! Теперь укажите описание к товару.")
    await state.set_state(user_states.waiting_for_description)

@rt.message(user_states.waiting_for_description)
async def add_description(message: Message, state: FSMContext):
    bot_db.insert_description(message.text)
    await message.answer(text=f"Теперь укажите цену товара.")
    await state.set_state(user_states.waiting_for_price)

@rt.message(user_states.waiting_for_price)
async def add_price(message: Message, state: FSMContext):
    bot_db.insert_price(message.text)
    await message.answer(text="Теперь укажите количество товара в наличии.")
    await state.set_state(user_states.waiting_for_amount)

@rt.message(user_states.waiting_for_amount)
async def add_amount(message: Message, state: FSMContext):
    bot_db.insert_amount(message.text)
    await message.answer(text="Новый товар успешно создан!")
    await state.clear()

@rt.callback_query(F.data == "plug")
async def plug(query:CallbackQuery):
    await query.answer(text = "Данный функционал еще не реализован, однако мы уже работаем над ним")


@rt.callback_query(F.data == "switch_user_role_to_seller")
async def switch_user_role_to_seller(query:CallbackQuery):
    user_id = query.from_user.id
    bot_db.switch_user_role_to_seller(user_id)
    await query.answer(text = f"Вы успешно сменили роль на продавца. Чтобы открыть новое меню, введите команду /start")

@rt.callback_query(F.data == "switch_user_role_to_customer")
async def switch_user_role_to_customer(query:CallbackQuery):
    user_id = query.from_user.id
    bot_db.switch_user_role_to_customer(user_id)
    await query.answer(text = f"Вы успешно сменили роль на покупателя. Чтобы открыть новое меню, введите команду /start")

@rt.callback_query(F.data == "get_this_seller_orders")
async def get_orders(query: types.CallbackQuery):
    user_id = query.from_user.id
    bot_db.get_seller_orders(user_id)
    csv_file = f"order_list_for_this_seller_{user_id}.csv"

    try:
        async with aiofiles.open(csv_file, mode='rb') as file:
            input_file = types.FSInputFile(f"order_list_for_this_seller_{user_id}.csv")
            await query.message.answer_document(input_file)
            await query.answer()
    except Exception as e:
        print(f"Произошла ошибка при отправке файла: {e}")
        await query.message.answer(text="Произошла ошибка при отправке файла")
        await query.answer()