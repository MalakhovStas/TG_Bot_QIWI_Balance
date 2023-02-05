import asyncio
import inspect
from os.path import basename

from config import ADMINS, TECH_ADMINS
from loader import bot, logger


async def func_admins_message(update=None, exc=None, message=None, disable_preview_page=None):
    """ Отправляет сообщения об ошибках и состоянии бота администраторам, если их id указаны в
        ADMINS или TECH_ADMINS файла .env """
    try:
        if ADMINS or TECH_ADMINS:
            if exc:
                if message:
                    for admin in TECH_ADMINS:
                        await asyncio.sleep(0.033)
                        await bot.send_message(chat_id=admin, text=message,
                                               disable_web_page_preview=disable_preview_page)
                else:
                    track = inspect.trace()[1] if len(inspect.trace()) > 1 else inspect.trace()[0]
                    file, func, line, code = \
                        basename(track.filename), track.function, track.lineno, "".join(track.code_context)

                    for admin in TECH_ADMINS:
                        await asyncio.sleep(0.033)
                        await bot.send_message(chat_id=admin,
                                               text='&#9888 <b><i>ERROR</i></b> &#9888\n'
                                                    f'<b>User_name</b>:    {update.from_user.first_name}\n'
                                                    f'<b>User_id</b>:    {update.from_user.id}\n'
                                                    f'<b>File</b>:    <i>{file}</i>\n'
                                                    f'<b>Func</b>:    <i>{func}</i>\n'
                                                    f'<b>Line</b>:    {line}\n'
                                                    f'<b>Exception</b>:    {exc.__class__.__name__}\n'
                                                    f'<b>Traceback</b>:    {exc}\n'
                                                    f'<b>Code</b>:    {code.strip()}\n')

                        logger.info(f'-> ADMIN SEND MESSAGE -> ERROR -> admin_id: {admin}')

            elif message and exc is None:
                for admin in ADMINS:
                    await asyncio.sleep(0.033)
                    await bot.send_message(chat_id=admin, text=message, disable_web_page_preview=disable_preview_page)
                    logger.info(f'-> ADMIN SEND MESSAGE -> admin_id: {admin}')

    except BaseException as i_exc:
        logger.critical(f'CRITICAL_ERROR(admins_send_message.py): {i_exc}')
