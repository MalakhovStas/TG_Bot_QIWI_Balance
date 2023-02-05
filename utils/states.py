from aiogram.dispatcher.filters.state import StatesGroup, State
""" Параметры машины состояний пользователя и администратора """


class FSMClientStates(StatesGroup):
    pre_top_up_balance = State()
    top_up_balance = State()


class FSMAdminStates(StatesGroup):
    change_user_balance = State()
    block_user = State()
