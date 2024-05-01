from aiogram.fsm.state import State, StatesGroup

class user_states(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_amount = State()
    waiting_for_users_role =State()

