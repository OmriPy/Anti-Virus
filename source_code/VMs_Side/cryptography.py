# RSA
from Crypto.PublicKey import RSA as rsa
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Cipher import PKCS1_OAEP as OAEP

# AES
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from base64 import b64encode, b64decode

# utils
from utils import *


####    RSA Encryption & Decryption    ####
class RSA:

    @classmethod
    def get_keys(cls, private_key_size: int) -> Tuple[RsaKey, RsaKey]:
        """
        Generates a pair of RSA keys (public and private) with a specified size.

        Parameters:
        - private_key_size (int): The size of the private key in bits. The minimum size is 1024 bits.
        If a size less than 1024 is provided, it defaults to 1024.

        Returns:
        Tuple[RsaKey, RsaKey]: A tuple containing the RSA public key and private key objects.
        """

        private_key_size = 1024 if private_key_size < 1024 else private_key_size
        private_key = rsa.generate(private_key_size)
        public_key = private_key.publickey()
        return public_key, private_key

    @classmethod
    def encrypt(cls, public_key: RsaKey, msg: str) -> str:
        msg = msg.encode()
        encryptor = OAEP.new(public_key)
        encrypted = encryptor.encrypt(msg)
        return encrypted.decode()

    @classmethod
    def decrypt(cls, private_key: RsaKey, encrypted: str) -> str:
        decryptor = OAEP.new(private_key)
        decrypted = decryptor.decrypt(encrypted.encode())
        return decrypted.decode()


####    AES Encryption & Decryption    ####
class AESCipher:

    def __init__(self, key: str):
        self.block_size = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, plain_text: str) -> str:
        plain_text = self.__pad(plain_text)
        iv = Random.new().read(self.block_size)    # IV = Initialization Vector
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        encrypted_text = cipher.encrypt(plain_text.encode())
        return b64encode(iv + encrypted_text).decode()

    def decrypt(self, encrypted_text: str) -> str:
        encrypted_text = b64decode(encrypted_text)
        iv = encrypted_text[:self.block_size]    # IV = Initialization Vector
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        plain_text = cipher.decrypt(encrypted_text[self.block_size:]).decode()
        return self.__unpad(plain_text)

    def __pad(self, plain_text: str) -> str:
        number_of_bytes_to_pad = self.block_size - len(plain_text) % self.block_size
        ascii_string = chr(number_of_bytes_to_pad)
        padding = number_of_bytes_to_pad * ascii_string
        padded_plain_text = plain_text + padding
        return padded_plain_text

    @staticmethod
    def __unpad(plain_text: str) -> str:
        last_character = plain_text[len(plain_text) - 1:]
        return plain_text[:-ord(last_character)]