from aiogram.fsm.state import State, StatesGroup

class States(StatesGroup):
    got_password = State()
    admin = State()
    seller = State()