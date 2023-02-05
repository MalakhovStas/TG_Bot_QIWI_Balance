from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger
from config import BOT_TOKEN, QIWI_PRIV_KEY, LOGGER_ERRORS, LOGGER_DEBUG
from database.db_utils import DBManager
from pyqiwip2p import AioQiwiP2P
from utils.security import Security

""" Модуль загрузки основных инструментов приложения """

dbase = DBManager()

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)

storage = MemoryStorage()


dp = Dispatcher(bot=bot, storage=storage)

p2p = AioQiwiP2P(auth_key=QIWI_PRIV_KEY)

logger.add(**LOGGER_ERRORS)
logger.add(**LOGGER_DEBUG)

security = Security(db=dbase, logger=logger)
