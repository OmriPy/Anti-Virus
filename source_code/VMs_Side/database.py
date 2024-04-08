from protocol import *
from hashing import *
from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.exc import IntegrityError


class User:

    def __init__(self, user: Tuple[str, str]):
        username, password = user
        self.username = username
        self.base64_password = ScryptHash(password).create_b64_hash()


class Database:

    db_file = 'database.db'

    @classmethod
    def init(cls):
        cls.engine = create_engine(f'sqlite:///{cls.db_file}')

        cls.metadata = MetaData()

        cls.users_table = Table('users', cls.metadata,
                            Column('username', String, primary_key=True),
                            Column('base64_password', String))

        mapper(User, cls.users_table)

        cls.metadata.create_all(cls.engine)

        cls.session = sessionmaker(bind=cls.engine)()

    @classmethod
    def add_user(cls, user: Tuple[str, str]):
        new_user = User(user)
        cls.session.add(new_user)
        cls.session.commit()

    @classmethod
    def close(cls):
        cls.session.close()


if __name__ == '__main__':
    Database.init()
    try:
        Database.add_user(('nadav', 'sex',))
    except IntegrityError:
        print_colored('error', 'User already exists')
    Database.close()
