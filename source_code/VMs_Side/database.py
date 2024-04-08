from protocol import *
from sqlalchemy import create_engine, MetaData, Table, Column, String, LargeBinary
from sqlalchemy.orm import mapper, sessionmaker
import scrypt, secrets


class ScryptHash:

    SALT_SIZE = 16
    HASH_SIZE = 32

    def __init__(self, password: str, salt: bytes = None):
        if salt == None:
            self.salt = self._generate_salt()
        else:
            self.salt = salt
        self.hash = scrypt.hash(password.encode(), self.salt, 32768, buflen=self.HASH_SIZE)
    
    def __new__(cls, password: str, salt: bytes = None) -> bytes:
        obj = super().__new__(cls)
        obj.__init__(password, salt)
        return obj.hash
    
    @classmethod
    def _generate_salt(cls) -> bytes:
        return secrets.token_bytes(cls.SALT_SIZE)
    
    def compare(self, other_password: str) -> bool:
        other_hash = ScryptHash(other_password, self.salt)
        return self.hash == other_hash.hash


class User:

    def __init__(self, user: Tuple[str, str]):
        self.username = user[0]
        self.password_hash = ScryptHash(user[1])


class Database:

    db_file = 'database.db'

    @classmethod
    def init(cls):
        cls.engine = create_engine(f'sqlite:///{cls.db_file}')
        
        cls.metadata = MetaData()

        cls.users_table = Table('users', cls.metadata,
                            Column('username', String, primary_key=True),
                            Column('password', LargeBinary))
        
        mapper(User, cls.users_table)

        cls.metadata.create_all(cls.engine)

        cls.session = sessionmaker(bind=cls.engine)()

    @classmethod
    def add_user(cls, user: Tuple[str, str]):
        new_user = User(user)
        cls.session.add(new_user)
        cls.session.commit()


if __name__ == '__main__':
    Database.init()
    #Database.add_user(('asaf', 'hi12',))