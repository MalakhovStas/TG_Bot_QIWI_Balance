from datetime import datetime
from aiogram.types import Message, CallbackQuery
from peewee import *
from config import DATABASE_CONFIG
from loader import logger

databases = {
    'sqlite': SqliteDatabase,
    'postgres': PostgresqlDatabase,
}


db = databases[DATABASE_CONFIG[0]](**DATABASE_CONFIG[1])


class User(Model):
    """ Модель одноименной таблицы в базе данных """
    user_id = IntegerField(primary_key=True, unique=True)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    date_join = DateTimeField(default=datetime.now(), null=False)
    access = CharField(default='allowed', null=False)
    balance = DecimalField(max_digits=10, decimal_places=2, default=0, null=False)

    class Meta:
        database = db
        order_by = 'date_join'
        db_table = 'users'


class DBManager:
    """ Класс надстройка над ORM для соблюдения принципа DRY """

    def __init__(self):
        self.db = db

    def create_tables(self):
        with self.db:
            self.db.create_tables([User])
        logger.debug(f'DBManager: OK -> create tables in database')

    def get_or_create_user(self, data: Message | CallbackQuery) -> tuple:
        with self.db:
            result = User.get_or_create(
                user_id=int(data.from_user.id),
                defaults={
                    'username': data.from_user.username,
                    'first_name': data.from_user.first_name,
                    'last_name': data.from_user.last_name,
                }
            )
        text = 'created new user in' if result[1] else 'selected user from'
        logger.debug(f'DBManager: OK -> {text} database -> user_id:{result[0].user_id}, username: {result[0].username}')
        return result

    def get_all_users(self):
        with self.db:
            result = User.select()
        logger.debug(f'DBManager: OK -> selected all users from database')
        return result

    def update_user_balance(self, user_id: str, up_balance: str | None = None,
                            down_balance: str | None = None, zero_balance: bool = False) -> tuple | bool:
        with self.db:
            user = User.get_or_none(user_id=int(user_id))
            if not user:
                return False

            if up_balance and up_balance.isdigit():
                user.balance += int(up_balance)
            elif down_balance and down_balance.isdigit():
                user.balance -= int(down_balance)
            elif zero_balance:
                user.balance = 0
            else:
                return False, 'bad data'
            user.save()
        logger.debug(f'DBManager: OK -> update user balance from database')
        return True, user.balance, user.username

    def update_user_access(self, user_id: str) -> bool | tuple:
        with self.db:
            user = User.get_or_none(user_id=int(user_id))
            if not user:
                return False
            user.access = 'block'
            user.save()
            logger.debug(f'DBManager: OK -> update user access from database')
            return True, user.username

    def get_user(self, user_id):
        with self.db:
            logger.debug(f'DBManager: OK -> get user from database')
            return User.get_or_none(user_id=int(user_id))

