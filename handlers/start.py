from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from decimal import Decimal
import utils.exception_control
from loader import bot, dp, dbase, logger, p2p
from utils.states import FSMClientStates
from config import LIFETIME


@dp.message_handler(commands='start', state='*')
@utils.exception_control.exception_handler_wrapper
async def func_start(message: Message, state: FSMContext) -> None:
    """ Обработчик команды старт """
    text_message = f'Привет, <b>{message.from_user.username}</b>' \
                   f'\nЯ - бот для пополнения баланса' \
                   f'\nНажмите на кнопку, чтобы пополнить баланс'

    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Пополнить баланс', callback_data='top_up_balance'))

    dbase.get_or_create_user(data=message)

    next_state = FSMClientStates.pre_top_up_balance
    await state.set_state(next_state)

    await bot.send_message(chat_id=message.from_user.id, text=text_message, reply_markup=keyboard)
    logger.debug(f'OK -> set {next_state} for user: {message.from_user.id}, username: {message.from_user.username}')


@dp.message_handler(lambda msg: msg.text not in ['/admin'], state=FSMClientStates.pre_top_up_balance)
@utils.exception_control.exception_handler_wrapper
async def message_pre_top_up_balance(message: Message, state: FSMContext):
    """ Обработчик сообщений вне сценария после команды старт """
    text = 'Если хотите пополнить баланс нажмите кнопку выше'
    await bot.send_message(chat_id=message.from_user.id, text=text)
    logger.debug(f'BAD -> received incorrect data from the user: {message.from_user.id}, '
                 f'username: {message.from_user.username}')


@dp.callback_query_handler(lambda cb: cb.data == 'top_up_balance', state=FSMClientStates.pre_top_up_balance)
@utils.exception_control.exception_handler_wrapper
async def call_pre_top_up_balance(call: CallbackQuery, state: FSMContext):
    """ Обработчик обратного вызова с кнопки пополнить баланс """
    next_state = FSMClientStates.top_up_balance
    await state.set_state(next_state)

    text = '<b>Введите сумму, на которую вы хотите пополнить баланс:</b>'
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=None)
    await bot.send_message(chat_id=call.from_user.id, text=text)

    logger.debug(f'OK -> set {next_state} for user: {call.from_user.id}, username: {call.from_user.username}')


@dp.message_handler(state=FSMClientStates.top_up_balance)
@utils.exception_control.exception_handler_wrapper
async def message_top_up_balance(message: Message, state: FSMContext):
    """ Обработчик сообщений внутри сценария ввода суммы к оплате """
    if message.text.isdigit():
        amount = Decimal(message.text)
        new_bill = await p2p.bill(amount=amount, lifetime=LIFETIME)

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Оплатить', url=new_bill.pay_url))
        keyboard.insert(InlineKeyboardButton(
            text='Проверить оплату', callback_data=f'check_top_up:bill_id={new_bill.bill_id}'))

        await bot.send_message(chat_id=message.from_user.id,
                               text=f'{new_bill.pay_url}\nВаш счет на оплату', reply_markup=keyboard)

        logger.debug(f'OK -> invoice and keyboard sent to user: '
                     f'{message.from_user.id}, username: {message.from_user.username}')
        await state.reset_state()

    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Сумма должна быть целым числом')

        logger.debug(f'BAD -> received incorrect data from the '
                     f'user: {message.from_user.id}, username: {message.from_user.username}')


@dp.callback_query_handler(lambda cb: cb.data.startswith('check_top_up:bill_id='), state='*')
@utils.exception_control.exception_handler_wrapper
async def call_top_up_balance(call: CallbackQuery, state: FSMContext):
    """ Обработчик обратного вызова с клавиатуры счета на оплату"""
    bill_id = call.data.lstrip('check_top_up:bill_id=')
    p2p_result = await p2p.check(bill_id=bill_id)

    if p2p_result.status == 'PAID':
        db_result = dbase.update_user_balance(user_id=call.from_user.id, up_balance=p2p_result.amount)
        if db_result[0]:
            await bot.edit_message_reply_markup(
                chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=None)
            await bot.send_message(chat_id=call.from_user.id, text=f'Счет оплачен, ваш баланс: {db_result[1]}')

    elif p2p_result.status == 'EXPIRED':
        await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            reply_markup=None)
        await p2p.reject(bill_id=bill_id)
        await bot.send_message(chat_id=call.from_user.id, text='Счет не оплачен и просрочен')

    else:
        await bot.send_message(chat_id=call.from_user.id, text='Счет не оплачен')
    logger.debug(f'OK -> the call from the keyboard of the invoice for payment was processed '
                 f'user: {call.from_user.id}, username: {call.from_user.username}')

