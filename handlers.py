from aiogram import F, Router, types, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
import kb
import text
import csv
from db import BotDB
router = Router()

bot = Bot(token="")



@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.start_menu)

@router.message(F.text == "get_guide")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
async def menu(msg: Message):
    await msg.answer(text.menu, reply_markup=kb.menu)


@router.callback_query(F.data == "login")
async def login(query: types.CallbackQuery):
    # Здесь можно реализовать код, который будет выполняться при получении callback_data 'login'
    await query.answer()
    await query.message.answer(text="Введите ваше имя пользователя")

# @router.callback_query(F.data == "get_users")
# async def get_users(query: types.CallbackQuery):
#     data = 
    #try:
        # Отправка файла пользователю в режиме чтения
    # with open(data, 'r') as file:
    #     print("Ошибка номер 1")
    #     await query.message.answer_document(file)
    #     print("Ошибка номер 2")
    # #except Exception as e:
    #     # Обработка ошибки при отправке файла
    # print(f"Произошла ошибка при отправке файла:")
        
    #     # Отправка сообщения об ошибке
    # await query.message.answer(text="Произошла ошибка при отправке файла")

@router.callback_query(F.data == "get_users")
async def get_users(query: types.CallbackQuery):
    data = [['id', 'telegram_id', 'role'], (1, 12345, 1), (2, 5343, 2)]

    csv_file = 'users_list.csv'  # Название для файла CSV

    try:
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data[0])  # Записываем заголовок
            for row in data[1:]:
                writer.writerow(row)  # Записываем данные

        with open(csv_file, 'rb') as file:
            file_content = file.read()
            await query.о(query.from_user.id, document=file_content)
    except Exception as e:
        print(f"Произошла ошибка при отправке файла: {e}")
        await query.message.answer(text="Произошла ошибка при отправке файла")
    poebota = 0
    