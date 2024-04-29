from protocol import *
from hashing import ScryptHash
from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session


class User:

    def __init__(self, username: str, password: str, email: str, phone_number: str):
        self.username = username
        self.base64_password = ScryptHash(password).create_b64_hash()
        self.email = email
        self.phone_number = phone_number


class Database:

    @classmethod
    def init(cls, db_file: str = 'database.db'):
        cls.engine = create_engine(f'sqlite:///{db_file}')
        metadata = MetaData()

        users_table = Table('users', metadata,
            Column('username', String, primary_key=True),
            Column('base64_password', String),
            Column('email', String),
            Column('phone_number', String),
        )

        mapper(User, users_table)
        metadata.create_all(cls.engine)
    

    @classmethod
    def _find_user(cls, primary_key: str) -> Tuple[User | None, Session]:
        session = sessionmaker(bind=cls.engine)()
        wanted_user = session.query(User).get(primary_key)
        return wanted_user, session


    @classmethod
    def register(cls, user_details: Tuple[str, str, str, str]) -> bool:
        session = sessionmaker(bind=cls.engine)()
        username, password, email, phone_number = user_details
        new_user = User(username, password, email, phone_number)
        session.add(new_user)
        try:
            session.commit()
        except IntegrityError:
            print_colored(Prefixes.WARNING, UserMessages.Register.Errors.USER_EXISTS)
            session.close()
            return False
        print_colored(Prefixes.DATABASE, UserMessages.Register.added(username))
        session.close()
        return True
    
    @classmethod
    def sign_in(cls, user_details: Tuple[str, str]) -> Tuple[bool, str]:
        username, password = user_details
        wanted_user, session = cls._find_user(username)
        session.close()

        if not wanted_user:
            return False, UserMessages.SignIn.Errors.NO_EXISTING_USER
        elif ScryptHash.create_from_b64(wanted_user.base64_password).compare(password):
            return True, ''
        else:
            return False, UserMessages.SignIn.Errors.INCORRECT_PASS

    @classmethod
    def sign_out(cls, username: str) -> Tuple[bool, str]:
        wanted_user, session = cls._find_user(username)
        session.close()
        if not wanted_user:
            return False, UserMessages.SignOut.Errors.USER_NOT_FOUND
        return True, ''


    '''@classmethod
    def remove_user(cls, username: str):
        session = sessionmaker(bind=cls.engine)()
        wanted_user = cls._find_user(username)
        if wanted_user:
            session.delete(wanted_user)
            session.commit()
            print_colored(Prefixes.DATABASE, UserMessages.removed(username))
        else:
            print_colored(Prefixes.ERROR, 'User could not be removed')
        session.close()'''
