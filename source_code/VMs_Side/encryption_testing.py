from socket import socket, AF_INET, SOCK_STREAM
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
import base64
import os

from protocol import *

#### Utilities ####

PORT = 55667

#### Errors Handling ####

class ProtocolError(Exception):
    FLAWED = 'The given packet is flawed according to the protocol'
    BIGGER_THAN_MAX = 'Given data is bigger than the maximum data size'

    def __init__(self, err: str):
        super().__init__(err)

#### Server Side ####

def listening_socket(IP: str) -> socket:
    """Returns a socket listening to the given IP"""
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.bind((IP, PORT))
    except OSError as e:
        if e.errno == 48:
            print('Try again later')
        elif e.errno == 49:
            print('Cannot bind given IP address')
        sock.close()
        exit(0)
    print('Server is up and running')
    sock.listen()
    return sock

#### Client Side ####

def connected_socket(IP: str) -> socket:
    """Returns a socket connected to the given IP"""
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect((IP, PORT))
    except ConnectionRefusedError:
        print('The server is not running')
        exit(0)
    return sock

#### Packet Structure ####

# The structure:    DATA_SIZE|DATA

DELIMITER = '|'
EXACT_SIZE_LENGTH = 7   # Max amount of bytes is 1048576
MAX_DATA_LENGTH = 10 ** EXACT_SIZE_LENGTH - 1     # Max amount of bytes in data field
MAX_TOTAL_SIZE = EXACT_SIZE_LENGTH + len(DELIMITER) + MAX_DATA_LENGTH     # Max total size of packet

#### RSA Key Generation ####

keys_bits = 2048

def generate_rsa_keypair():
    return RSA.generate(keys_bits) # generates a key pair of public key and private key

#### RSA Encryption and Decryption ####

def rsa_encrypt(message: bytes, public_key: RSA.RsaKey) -> bytes:
    cipher = PKCS1_OAEP.new(public_key)
    return cipher.encrypt(message)

def rsa_decrypt(ciphertext: bytes, private_key: RSA.RsaKey) -> bytes:
    cipher = PKCS1_OAEP.new(private_key)
    return cipher.decrypt(ciphertext)

#### AES Encryption and Decryption ####

def aes_encrypt(message: bytes, key: bytes) -> bytes:
    iv = os.urandom(16)  # generate a random initialization vector
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(message, AES.block_size))
    return iv + encrypted

def aes_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    iv = ciphertext[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext[16:])
    return unpad(decrypted, AES.block_size)

#### Communication ####

def send(sock: socket, msg: str, key: bytes):
    """Sends the message to the socket"""
    encrypted_msg = aes_encrypt(msg.encode(), key)
    packet = build_packet(base64.b64encode(encrypted_msg).decode())
    sock.send(packet.encode())

def recv(sock: socket, key: bytes) -> str:
    """Recieves the message from the socket"""
    packet = sock.recv(MAX_TOTAL_SIZE).decode()
    size, data = parse_packet(packet)
    decrypted_msg = aes_decrypt(base64.b64decode(data.encode()), key)
    return decrypted_msg.decode()

# Key Exchange

def exchange_keys(sock: socket):
    # Generate RSA keypair
    keypair = generate_rsa_keypair()
    public_key = keypair.publickey().export_key()
    
    # Send public key to server
    send(sock, public_key.decode(), keypair.export_key())
    
    # Receive encrypted AES key from server
    encrypted_aes_key = recv(sock, keypair.export_key())
    
    # Decrypt AES key
    aes_key = rsa_decrypt(base64.b64decode(encrypted_aes_key.encode()), keypair)
    
    return aes_key

if __name__ == "__main__":
    # Server
    server_socket = listening_socket('localhost')
    client_socket, client_address = server_socket.accept()
    
    # Client
    client_socket = connected_socket('localhost')
    
    # Exchange keys
    server_aes_key = exchange_keys(client_socket)
    client_aes_key = exchange_keys(server_socket)

    # Now you can use server_aes_key and client_aes_key for further communication
