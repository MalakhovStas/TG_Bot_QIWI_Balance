from typing import Dict

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from aiogram.dispatcher.handler import CancelHandler
from config import FLOOD_CONTROL, FLOOD_CONTROL_STOP_TIME
import utils.exception_control
from loader import bot, security


class AccessControlMiddleware(BaseMiddleware):
    """ Класс предварительной обработки входящих сообщений для защиты от нежелательной нагрузки """
    def __init__(self) -> None:
        super().__init__()

    @utils.exception_control.exception_handler_wrapper
    async def on_pre_process_update(self, update: Update, data: Dict) -> None:
        update = update.message if update.message else update.callback_query

        user_data = self.manager.storage.data.get(str(update.from_user.id))

        if isinstance(update, CallbackQuery):
            await bot.answer_callback_query(callback_query_id=update.id)

        if not security.check_user(update, user_data):
            raise CancelHandler()

        if FLOOD_CONTROL:
            control = security.flood_control(update)
            if control in ['block', 'bad', 'blocked']:
                if control != 'blocked':
                    text = {'block': f'&#129302 Доступ ограничен на {FLOOD_CONTROL_STOP_TIME} секунд',
                            'bad': '&#129302 Не так быстро пожалуйста'}
                    await bot.send_message(chat_id=update.from_user.id, text=text[control])
                raise CancelHandler()

        import handlers

    @utils.exception_control.exception_handler_wrapper
    async def on_process_update(self, update: Update, data: Dict) -> None | Dict:
        pass

    @utils.exception_control.exception_handler_wrapper
    async def on_pre_process_message(self, update: Message, data: Dict) -> None:
        pass

    @utils.exception_control.exception_handler_wrapper
    async def on_pre_process_callback_query(self, update: CallbackQuery, data: Dict) -> None:
        pass
