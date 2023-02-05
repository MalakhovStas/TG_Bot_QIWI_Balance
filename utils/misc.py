import utils.exception_control
from loader import dbase, logger
from config import PATH_USERS_INFO
import openpyxl


@utils.exception_control.exception_handler_wrapper
async def unload_users_to_xlsx(update):
    """ Преобразует таблицу USERS из базы данных в excel таблицу"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['User_id', 'Username', 'First_name', 'Last_name', 'Date_join', 'Balance', 'Access'])
    for user in dbase.get_all_users():
        ws.append([user.user_id, user.username, user.first_name,
                   user.last_name, user.date_join, user.balance, user.access])
    wb.save(PATH_USERS_INFO)
    logger.debug(f'OK -> create file: {PATH_USERS_INFO}')
