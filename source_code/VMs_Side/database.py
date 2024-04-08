from protocol import *
from hashing import *
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.exc import IntegrityError


class User:

    def __init__(self, username: str, password: str, email: str, phone_number: str):
        self.username = username
        self.base64_password = ScryptHash(password).create_b64_hash()
        self.email = email
        self.phone_number = phone_number


class Database:

    db_file = 'database.db'

    @classmethod
    def init(cls):
        cls.engine = create_engine(f'sqlite:///{cls.db_file}')

        metadata = MetaData()

        users_table = Table('users', metadata,
            Column('username', String, primary_key=True),
            Column('base64_password', String),
            Column('email', String),
            Column('phone_number', String)
        )

        mapper(User, users_table)

        metadata.create_all(cls.engine)
    

    @classmethod
    def _find_user(cls, primary_key: str):
        session = sessionmaker(bind=cls.engine)()
        wanted_user = session.query(User).get(primary_key)
        session.close()
        return wanted_user


    @classmethod
    def add_user(cls, user_details: Tuple[str, str, str, str]) -> bool:
        session = sessionmaker(bind=cls.engine)()
        username, password, email, phone_number = user_details
        new_user = User(username, password, email, phone_number)
        session.add(new_user)
        try:
            session.commit()
        except IntegrityError:
            print_colored('error', UserMessages.USER_EXISTS)
            session.close()
            return False
        print_colored('database', UserMessages.added(username))
        session.close()
        return True
    
    @classmethod
    def sign_in_check(cls, user_details: Tuple[str, str]) -> Tuple[bool, str]:
        username, password = user_details
        wanted_user: User = cls._find_user(username)

        if wanted_user == None:
            return False, UserMessages.NO_EXISTING_USER
        if ScryptHash.create_from_b64(wanted_user.base64_password).compare(password):
            return True, ''
        else:
            return False, UserMessages.INCORRECT_PASS

    @classmethod
    def remove_user(cls, username: str):
        session = sessionmaker(bind=cls.engine)()
        wanted_user = cls._find_user(username)
        if wanted_user:
            session.delete(wanted_user)
            session.commit()
            print_colored('database', UserMessages.removed(username))
        else:
            print_colored('error', 'User could not be removed')
        session.close()


if __name__ == '__main__':
    Database.init()
    #Database.add_user(('omri', 'cyber', 'omri@cyber.org', '050-7266030',))
    #Database.remove_user('omri')
    #print(Database.sign_in_check(('fsdf', 'niger',)))
