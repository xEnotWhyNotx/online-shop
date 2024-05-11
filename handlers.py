from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputFile
import kb
import text
import csv
from db import BotDB
import aiofiles
from States import user_states
from aiogram.fsm.context import FSMContext
import re
import asyncio
from Exceptions import WrongItemException

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
        elif user_role == (None,):
            await msg.answer(text = f"Пожалуйста, выберите роль.", reply_markup= kb.select_role_menu)
              

    else:
        bot_db.create_new_user(user_id)
        await msg.answer(text = f"Кажется, вы у нас впервые. Пожалуйста, выберите роль.", reply_markup= kb.select_role_menu)
          
        


@rt.callback_query(F.data.in_(["user_is_seller","user_is_customer"]))
async def add_role(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    bot_db = BotDB('online-shop_V2_1.db')
    if bot_db.get_role(user_id) != (None,):
        await query.answer(text = "Вы уже выбрали роль. Сменить роль можно через главное меню")
    elif F.data == "user_is_seller":
        bot_db.insert_seller(user_id)
        await query.answer(text=f"Вы были успешно добавлены как продавец. Для продолжения введите команду /start")
    elif F.data == "user_is_customer":
        bot_db.insert_customer(user_id)
        await query.answer(text=f"Вы были успешно добавлены как покупатель. Для продолжения введите команду /start")

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
    await query.message.answer(text="Пожалуйста, укажите название для нового товара.")
    await state.set_state(user_states.waiting_for_name)  # Переводим стейт в ожидание названия

@rt.callback_query(F.data == "search_by_name")
async def prompt_search(query: types.CallbackQuery, state: FSMContext):  # Make sure FSMContext is passed here
    await query.message.answer("Введите название товара, который вы хотите найти:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(user_states.waiting_for_product_search)  # Correctly set state 

@rt.message(user_states.waiting_for_name)
async def add_name(message: Message, state: FSMContext):
    #Очищаем полученную строку от спец.символов, двойные пробелы заменяем на одинарные
    pattern = r"([А-Яа-яA-Za-z]+(?:\s[А-Яа-яA-Za-z0-9]+)*)"
    match = re.search(pattern,message.text)
    if match:
        cleaned_string = re.sub(r'[^a-zA-ZА-Яа-я0-9 ]+', '', message.text).strip()
        cleaned_string = re.sub(r'\s+', ' ', cleaned_string)
        if len(cleaned_string)>=4: #Проверка на длину уже очищенной строки
            bot_db.insert_name(cleaned_string)
            await message.answer(text=f"Отлично! Теперь укажите описание к товару.")
            await state.set_state(user_states.waiting_for_description)
        else:
            await message.answer(text = "Кажется, длина названия меньше 4 символов. Минимальная длина 4 символа")
    else:
        await message.answer(text = "Похоже название товара не соответствует требованиям. Введите, пожалуйста корректное название.")

@rt.message(user_states.waiting_for_description)
async def add_description(message: Message, state: FSMContext):
    bot_db.insert_description(message.text)
    await message.answer(text=f"Теперь укажите цену товара.")
    await state.set_state(user_states.waiting_for_price)

# @rt.message(user_states.waiting_for_product_search)
# async def search_product(message: Message, state: FSMContext):
#     product_name = message.text
#     product = bot_db.get_product_by_name(product_name)
#     if product:
#         # Assuming 'product' is a tuple with (id, name, description, price, amount, picture)
#         response = f"Наименование: {product[1]}\nОписание: {product[2]}\nЦена: {product[3]} руб.\nКоличество: {product[4]}"
#         if product[5]:
#             await message.answer_photo(photo=product[5], caption=response)
#         else:
#             await message.answer(response)
#     else:
#         await message.answer("Товар не найден.")
#     await state.clear()

@rt.message(user_states.waiting_for_product_search)
async def search_product(message: Message, state: FSMContext):
    product_name = message.text
    products = bot_db.get_product_by_name(product_name)
    print(products)
    for product in products:
        if product:
            response = f"Наименование: {product[1]}\nОписание: {product[2]}\nЦена: {product[3]} руб.\nКоличество: {product[4]}"
            if product[5]:
                await message.answer_photo(photo=product[5], caption=response)
            else:
                await message.answer(response)
        else:
            await message.answer("Товар не найден.")
    await state.clear()

@rt.message(user_states.waiting_for_price)
async def add_price(message: Message, state: FSMContext):
    pattern = r"^\d+$"

    if re.match(pattern, message.text):
        bot_db.insert_price(message.text)
        await message.answer(text="Теперь укажите количество товара в наличии.")
        await state.set_state(user_states.waiting_for_amount)
    else:
        await message.answer(text = "Введенное вами значение не является целым числом. Укажите целое число.")

@rt.message(user_states.waiting_for_amount)
async def add_amount(message: Message, state: FSMContext):
    pattern = r"^\d+$"
    if re.match(pattern, message.text):

        bot_db.insert_amount(message.text)
        await message.answer(text="Теперь отправьте фото товара")
        await state.set_state(user_states.waiting_for_picture)
    else:
        await message.answer(text = "Введенное вами значение не является целым числом. Укажите целое число.")


@rt.message(user_states.waiting_for_picture)
async def add_picture(message:Message, state: FSMContext):
    try:
        picture = message.photo[-1].file_id
        bot_db.insert_picture(picture)
        await message.answer(text= "Новый товар был успешно создан", reply_markup= kb.seller_role_menu)
        await state.clear()
    except:
        await message.answer(text = "Это не фотография. Отправьте фотографию.")
    


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
async def get_seller_orders(query: types.CallbackQuery):
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

@rt.callback_query(F.data == "get_this_customer_orders")
async def get_customer_orders(query: types.CallbackQuery):
    user_id = query.from_user.id
    bot_db.get_customer_orders(user_id)
    csv_file = f"order_list_for_this_customer_{user_id}.csv"
    
    try:
        async with aiofiles.open(csv_file, mode='rb') as file:
            input_file = types.FSInputFile(f"order_list_for_this_customer_{user_id}.csv")
            await query.message.answer_document(input_file)
            await query.answer()
    except Exception as e:
        print(f"Произошла ошибка при отправке файла: {e}")
        await query.message.answer(text="Произошла ошибка при отправке файла")
        await query.answer()

@rt.callback_query(F.data == "show_all_items")
async def show_all_items(query: types.CallbackQuery, state:FSMContext):
    items = bot_db.show_all_item()
#    print(items)
    
    for item in items:
        id = item[0]
        Name = item[1]
        Description = item[2]
        Price = item[3]
        Amount = item[4]
        picture = item[5]
        if picture == None:

            Card = str(
                f'Id товара: {id}\n'
                f'Наименование: {Name}\n'
                f'Описание: {Description}\n'
                f'Цена в рублях: {Price}\n'
                f'В наличии: {Amount}\n'
            )
            await query.message.answer(Card)
            await query.answer()
        else:
            Card = str(
                f"{'<b>'}Id товара:{'</b>'} {'<code>'}{id}{'</code>'}\n"
                f"{'<b>'}Наименование:{'</b>'} {Name}\n"
                f"{'<b>'}Описание:{'</b>'} {Description}\n"
                f"{'<b>'}Цена в рублях:{'</b>'} {Price}\n"
                f"{'<b>'}В наличии:{'</b>'} {Amount}\n"
            )
            await query.message.answer_photo(photo=picture, caption = Card, parse_mode="HTML")
            await query.answer()
    await query.message.answer("Пожалуйста, введите артикул товара, который вы хотите добавить в корзину.")
    await state.set_state(user_states.waiting_for_item_pick)
    
@rt.message(user_states.waiting_for_item_pick)
async def add_item_to_cart(message: Message, state: FSMContext):
    user_id = message.from_user.id
    item = message.text
    try:
        bot_db.add_item_to_cart(user_id,item)
        await message.answer(text = "Товар был успешно добавлен в корзину")
        await state.clear()
    except (WrongItemException):
        await message.answer(text = "Похоже, вы указали id несуществующего товара. Либо указанный товар уже есть в вашей корзине.")




@router.message(F.text == "Меню")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
async def menu(msg: Message):
    await msg.answer(text.menu, reply_markup=kb.menu)