import time
from collections import namedtuple

from aiogram.types import CallbackQuery, Message

from config import FLOOD_CONTROL_TIME, FLOOD_CONTROL_STOP_TIME, FLOOD_CONTROL_NUM_ALERTS


class Security:
    """ Класс обеспечивающий контроль доступа к боту и механизм защиты от флуда """

    def __init__(self, db, logger):
        self.db = db
        self.logger = logger
        self.__flood_control_data: dict = {}

    def update_informer(self, update: CallbackQuery | Message, user_data: dict | None) -> None:
        """ Логирование информации о входящем сообщении от пользователя"""
        state_user, data_user = self.__get_data_from_user_data(update, user_data)

        message = f'INCOMING: {("callback:", update.data) if isinstance(update, CallbackQuery) else ("message:", update.text)}' \
                  f' -> from USER -> full_name: {update.from_user.full_name}, user_id: {update.from_user.id}, ' \
                  f'@username: {update.from_user.username}, state_user: {state_user}, data_user: {data_user}'

        self.logger.info(message)

    def __get_data_from_user_data(self, update: CallbackQuery | Message, user_data: dict | None) -> tuple:
        """ Метод представления данных в нужном виде """
        state_user = None
        data_user = None
        if user_data:
            if data := user_data.get(str(update.from_user.id)):
                state_user = data.get('state')
                data_user = data.get('data')
        return state_user, data_user

    def check_user(self, update: CallbackQuery | Message, user_data: dict | None) -> bool:
        """ Для проверки пользователя на предмет блокировки """
        user = self.db.get_user(update.from_user.id)

        self.update_informer(update, user_data)

        user_status = user.access if user else 'new user'

        self.logger.info(f'SECURITY: user_status: {user_status.upper()} -> user: {update.from_user.id}')
        return False if user_status == 'block' else True

    def flood_control(self, update: CallbackQuery | Message) -> str:
        """ Механизм защиты от флуда с возможностью временной блокировки пользователя """
        user_id = update.from_user.id
        FloodData = namedtuple('FloodData', ['last_time', 'num_alerts', 'time_block'])
        flood_data: FloodData | None = self.__flood_control_data.get(user_id)

        if not flood_data:
            self.__flood_control_data[user_id] = FloodData(time.time(), 0, 0)
            result = 'ok'

        else:
            if flood_data.time_block != 0 and flood_data.time_block - time.time() > 0:
                result = 'blocked'

            elif flood_data.num_alerts == FLOOD_CONTROL_NUM_ALERTS:
                flood_data = flood_data._replace(num_alerts=0, time_block=time.time() + FLOOD_CONTROL_STOP_TIME)
                result = 'block'

            elif time.time() - flood_data.last_time < FLOOD_CONTROL_TIME:
                flood_data = flood_data._replace(last_time=time.time(), num_alerts=flood_data.num_alerts + 1)
                result = 'bad'

            else:
                flood_data = flood_data._replace(last_time=time.time(), num_alerts=0)
                result = 'ok'

            self.__flood_control_data[user_id] = flood_data

        self.logger.info(f'SECURITY: {result.upper()} -> flood control -> user: {user_id}')
        return result
