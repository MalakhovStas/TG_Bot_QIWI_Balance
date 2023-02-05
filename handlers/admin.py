from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

import utils.exception_control
from loader import bot, dp, logger, dbase
from utils.states import FSMAdminStates
from config import PATH_USERS_INFO, PATH_FILE_DEBUG_LOGS, PATH_FILE_ERRORS_LOGS
from utils.misc import unload_users_to_xlsx


@dp.message_handler(commands='admin', state='*')
@utils.exception_control.exception_handler_wrapper
async def func_admin(message: Message, state: FSMContext) -> None:
    """ Обработчик команды admin, отправляет в чат кнопки:
        - выгрузка пользователей с их балансом
        - выгрузка логов
        - возможность изменить баланс пользователя
        - возможность заблокировать пользователя (бот перестает обрабатывать сообщение пользователя)
    """

    # Если возникнет необходимость ограничить доступ к команде admin только для администраторов
    # from config_data.config import ADMINS, TECH_ADMINS
    # if not message.from_user.id in set(ADMINS.extend(TECH_ADMINS)):
    #     return

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Выгрузка логов', callback_data='unloading_logs'))
    keyboard.add(InlineKeyboardButton(text='Выгрузка пользователей', callback_data='unloading_users'))
    keyboard.add(InlineKeyboardButton(text='Изменить баланс пользователя', callback_data='change_user_balance'))
    keyboard.add(InlineKeyboardButton(text='Заблокировать пользователя', callback_data='block_user'))

    await bot.send_message(chat_id=message.from_user.id, text='<b>Выберите действие:</b>', reply_markup=keyboard)
    logger.debug(f'OK -> send admin keyboard for user: {message.from_user.id}, username: {message.from_user.username}')


@dp.callback_query_handler(
    lambda cb: cb.data in ['unloading_logs', 'unloading_users', 'change_user_balance', 'block_user'], state='*')
@utils.exception_control.exception_handler_wrapper
async def func_admin_calls(call: CallbackQuery, state: FSMContext):
    """ Обработчик обратного вызова с клавиатуры администратора """
    if call.data == 'unloading_logs':

        await bot.send_document(chat_id=call.from_user.id, document=open(PATH_FILE_DEBUG_LOGS, 'rb'))
        await bot.send_document(chat_id=call.from_user.id, document=open(PATH_FILE_ERRORS_LOGS, 'rb'))

        logger.debug(f'OK -> send logs files -> user: {call.from_user.id}, username: {call.from_user.username}')

    elif call.data == 'unloading_users':
        await unload_users_to_xlsx(update=call)

        await bot.send_document(chat_id=call.from_user.id, document=open(PATH_USERS_INFO, 'rb'))
        logger.debug(f'OK -> send users_info file -> user: {call.from_user.id}, username: {call.from_user.username}')

    elif call.data == 'change_user_balance':
        next_state = FSMAdminStates.change_user_balance
        await state.set_state(next_state)

        text = '<b>Введите id пользователя и через пробел +сумму на которую хотите увеличить его баланс,' \
               ' или -сумму на которую хотите уменьшить, для обнуления баланса введите 0</b>'
        await bot.send_message(chat_id=call.from_user.id, text=text)
        logger.debug(f'OK -> set {next_state} for user: {call.from_user.id}, username: {call.from_user.username}')

    elif call.data == 'block_user':
        next_state = FSMAdminStates.block_user
        await state.set_state(next_state)

        text = '<b>Введите id пользователя</b>'
        await bot.send_message(chat_id=call.from_user.id, text=text)
        logger.debug(f'OK -> set {next_state} for user: {call.from_user.id}, username: {call.from_user.username}')


@dp.message_handler(state=FSMAdminStates.change_user_balance)
@utils.exception_control.exception_handler_wrapper
async def func_update_user_balance(message: Message, state: FSMContext):
    """ Обработчик команды изменения баланса пользователя """
    data = message.text.split(' ')
    if len(data) == 2 and data[0].isdigit() and data[1].startswith(('+', '-', '0')):
        update_user_id = data[0]
        up_balance = data[1][1:] if data[1].startswith('+') else None
        down_balance = data[1][1:] if data[1].startswith('-') else None
        zero_balance = True if data[1] == '0' else None

        if result := dbase.update_user_balance(user_id=update_user_id, up_balance=up_balance,
                                               down_balance=down_balance, zero_balance=zero_balance):

            if not result[0] and result[1] == 'bad data':
                text = f'Ошибка обновления баланса, возможно введены некорректные данные, ' \
                       f'баланс пользователя: <b>{update_user_id}</b> не изменён'
            else:
                text = f'Баланс пользователя: <b>id: {update_user_id}' \
                       f'{", username: "+result[2] if result[2] else ""}</b> ' \
                       f' успешно обновлен, новый баланс: <b>{result[1]}</b>'

                await state.reset_state()

        else:
            text = f'Пользователь: <b>{update_user_id}</b> в базе не зарегистрирован'

        await bot.send_message(chat_id=message.from_user.id, text=text)

    else:
        await bot.send_message(chat_id=message.from_user.id, text='Введены некорректные данные')


@dp.message_handler(state=FSMAdminStates.block_user)
@utils.exception_control.exception_handler_wrapper
async def func_block_user(message: Message, state: FSMContext):
    """ Обработчик команды блокировки пользователя """
    update_user_id = message.text.strip(' ')

    if update_user_id.isdigit():
        if result := dbase.update_user_access(update_user_id):
            text = f'Пользователь: <b>{update_user_id}{", username: "+result[1] if result[1] else ""}</b> заблокирован'
            await state.reset_state()
        else:
            text = f'Пользователь: <b>{update_user_id}</b> в базе не зарегистрирован'
    else:
        text = 'Введены некорректные данные'

    await bot.send_message(chat_id=message.from_user.id, text=text)
