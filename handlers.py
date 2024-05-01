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
from aiogram.fsm.state import State, StatesGroup
router = Router()
bot_db = BotDB('online-shop_V2_1.db')



@router.message(Command("start"))
async def start_handler(msg: Message, state:FSMContext):
    user_id = msg.from_user.id
    name= msg.from_user.full_name
    bot_db = BotDB('online-shop_V2_1.db')
    if bot_db.is_user_in_db(user_id):
        await msg.answer(text = f"Вижу вас в базе. С возвращением, {name}")
        await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.start_menu)
    else:
        bot_db.create_new_user(user_id)
        await msg.answer(text = f"Кажется, вы у нас впервые. Пожалуйста, выберите роль.", reply_markup= kb.select_role_menu)
        await state.set_state(user_states.waiting_for_users_role)


@router.message(user_states.waiting_for_users_role)
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

#@router.message(user_states.waiting_for_users_role and Message.text == "Покупатель")



@router.message(F.text == "get_guide")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
async def menu(msg: Message):
    await msg.answer(text.menu, reply_markup=kb.menu)


@router.callback_query(F.data == "login")
async def login(query: types.CallbackQuery):
    # Здесь можно реализовать код, который будет выполняться при получении callback_data 'login'
    await query.answer()
    await query.message.answer(text="")



@router.callback_query(F.data == "get_users")
async def get_users(query: types.CallbackQuery):
    ##
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


