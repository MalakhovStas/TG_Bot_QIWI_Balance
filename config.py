import os
import ast
from dotenv import load_dotenv, find_dotenv

""" Модуль основной конфигурации приложения """

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env\n'
         'Необходимо верно заполнить данные в файле .env.template и переименовать его в .env')
else:
    load_dotenv()


""" Количество перезапусков бота в случае падения """
MAX_RESTART_BOT = 3

""" Токен телеграм бота """
BOT_TOKEN = os.getenv('BOT_TOKEN')

""" QIWI """
# https://developer.qiwi.com/ru/payments/#test_data_card
# https://pyqiwip2p.readthedocs.io/ru/latest/Use.html#id3
QIWI_PRIV_KEY = os.getenv('QIWI_PRIV_KEY')
LIFETIME = 5

""" Список администраторов и ссылка на чат поддержки """
ADMINS = os.getenv('ADMINS').split(', ')
TECH_ADMINS = os.getenv('ADMINS').split(', ')
SUPPORT = os.getenv('SUPPORT')

""" Команды бота """
DEFAULT_COMMANDS = (
    ('start', 'запустить бота'),
    ('admin', 'команды администратора')
)

""" Конфигурация базы данных """
if not os.getenv('PG_DATABASE'):
    DATABASE_CONFIG = ('sqlite', {'database': 'database/database.db'})
else:
    DATABASE_CONFIG = ('postgres', ast.literal_eval(os.getenv('PG_DATABASE')))


""" Конфигурация логирования """

errors_format = '{time:DD-MM-YYYY at HH:mm:ss} | {level: <8} | {file: ^20} | {message}'
debug_format = '{time:DD-MM-YYYY at HH:mm:ss} | {level: <8} | file: {file: ^30} | ' \
               'func: {function: ^30} | line: {line: >3} | message: {message}'

logger_common_args = {
    'diagnose': True,
    'backtrace': False,
    'rotation': '500 kb',
    'retention': 1,
    'compression': 'zip'
}

PATH_FILE_DEBUG_LOGS = 'logs/debug.log'
PATH_FILE_ERRORS_LOGS = 'logs/errors.log'

LOGGER_DEBUG = {'sink': PATH_FILE_DEBUG_LOGS, 'level': 'DEBUG', 'format': debug_format} | logger_common_args
LOGGER_ERRORS = {'sink': PATH_FILE_ERRORS_LOGS, 'level': 'WARNING', 'format': errors_format} | logger_common_args


""" Файл информации о пользователях по команде admin """
PATH_USERS_INFO = 'users_info.xlsx'

""" Включение / отключение механизма защиты от флуда """
FLOOD_CONTROL = True

""" Время между сообщениями от пользователя для защиты от флуда в секундах """
FLOOD_CONTROL_TIME = 0.3

""" Количество предупреждений перед блокировкой для защиты от флуда"""
FLOOD_CONTROL_NUM_ALERTS = 10

""" Время остановки обслуживания пользователя для защиты от флуда в секундах """
FLOOD_CONTROL_STOP_TIME = 60

