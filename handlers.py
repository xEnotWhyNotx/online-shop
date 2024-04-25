from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputFile
import kb
import text
import csv
from db import BotDB
import aiofiles
router = Router()
user_id = int()
bot_db = BotDB('online-shop.db')



@router.message(Command("start"))
async def start_handler(msg: Message):
    global user_id
    user_id = Message.from_user.id
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.start_menu)
    await Message.answer(f"Твой телеграм id: {user_id}")
    

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

@router.callback_query(F.data == "authorize")
async def check_password(query: types.callbackQuery):
    bot_db.create_user()