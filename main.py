import asyncio
import time

from aiogram.types import BotCommand

from config import DEFAULT_COMMANDS, MAX_RESTART_BOT
from loader import logger, bot, dp, dbase
from utils.admins_send_message import func_admins_message
import middlewares


async def start(restart=0):
    """ Функция запуска приложения с механизмом автоматического перезапуска в случае завершения программы в
        результате непредвиденной ошибки """
    try:
        logger.info('-> START_BOT <-')
        await func_admins_message(message='&#128640 <b>START BOT</b> &#128640')

        dbase.create_tables()
        await bot.set_my_commands([BotCommand(command=item[0], description=item[1]) for item in DEFAULT_COMMANDS])

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as exc:
        logger.critical(f'CRITICAL_ERROR: {exc}')

        await func_admins_message(message=f'&#9762&#9760 <b>BOT CRITICAL ERROR</b> &#9760&#9762'
                                          f'\n<b>File</b>: main.py\n'
                                          f'<b>Exception</b>: {exc.__class__.__name__}\n'
                                          f'<b>Traceback</b>: {exc}', exc=True)

        if MAX_RESTART_BOT - restart:
            restart += 1
            await func_admins_message(message=f'&#9888<b>WARNING</b>&#9888\n'
                                              f'<b>10 seconds to {restart} restart BOT</b>!', exc=True)
            logger.warning(f'-> 10seconds to {restart} restart BOT <-')
            time.sleep(10)

            await start(restart=restart)
        else:
            await func_admins_message(message=f'&#9760<b>BOT IS DEAD</b>&#9760')
            logger.critical('-> BOT IS DEAD <-')


if __name__ == '__main__':
    asyncio.run(start())
