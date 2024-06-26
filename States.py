from aiogram.fsm.state import State, StatesGroup

class user_states(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_amount = State()
    waiting_for_picture = State()
    waiting_for_users_role = State()
    waiting_for_item_pick = State()
    waiting_for_product_search = State()
    waiting_for_promocode = State()
    waiting_for_role_change_password = State()
    waiting_for_admin_password = State()