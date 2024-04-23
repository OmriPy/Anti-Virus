import scrypt, secrets, base64
from typing import Optional

class ScryptHash:

    _SALT_SIZE = 16
    _HASH_SIZE = 32
    _SEP = '|'

    def __init__(self, plaintext_password: str, salt: Optional[bytes] = None):
        self.salt = salt or self._generate_salt()
        self.hash = scrypt.hash(plaintext_password.encode(), self.salt, 32768, buflen=self._HASH_SIZE)


    @classmethod
    def _generate_salt(cls) -> bytes:
        return secrets.token_bytes(cls._SALT_SIZE)

    def create_b64_hash(self) -> str:
        b64_salt = base64.b64encode(self.salt).decode()
        b64_hash = base64.b64encode(self.hash).decode()
        return f'{b64_salt}{self._SEP}{b64_hash}'

    def compare(self, plaintext_password: str) -> bool:
        given_scrypt_hash = ScryptHash(plaintext_password, self.salt)
        return self.hash == given_scrypt_hash.hash

    @classmethod
    def create_from_b64(cls, b64_password: str) -> 'ScryptHash':
        b64_salt, b64_scrypt_hash = b64_password.split(cls._SEP, 1)
        scrypt_salt = base64.b64decode(b64_salt)
        scrypt_hash = base64.b64decode(b64_scrypt_hash)

        scrypt_hash_object = ScryptHash('', scrypt_salt)
        scrypt_hash_object.hash = scrypt_hash
        return scrypt_hash_object
