from database import *

class _Socket:

    def __init__(self, sock: socket, id: int, aes: AESCipher):
        self.sock = sock
        self.sock_id = id
        self.aes = aes


class SocketsList:

    def __init__(self):
        """Management of list of sockets"""

        self._sockets: List[_Socket] = []
        self._current_id = 1


    def _get_index(self, sock_id: int) -> int:
        for i in range(len(self._sockets)):
            if self._sockets[i].sock_id == sock_id:
                return i
        print_colored(Prefixes.ERROR, f'Socket with ID {sock_id} was not found in the list and could not be removed')
        return -1

    def exists(self, sock_id: int, ret_index: bool = False) -> bool | int:
        index = self._get_index(sock_id)
        if ret_index:
            return index
        return index != -1

    def add(self, sock: socket, aes: AESCipher) -> int:
        sock_id = self._current_id
        self._sockets.append(_Socket(sock, sock_id, aes))
        self._current_id += 1
        return sock_id

    def remove(self, sock_id: int, close: bool = True):
        index = self.exists(sock_id, True)
        if index == -1:
            return
        sock = self._sockets[index].sock
        self._sockets.pop(index)
        if close:
            sock.close()

    def send_to_all(self, data: str):
        for socket in self._sockets:
            Network.send(socket.sock, data, socket.aes)
