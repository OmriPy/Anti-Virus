from database import *

class _SocketID:

    def __init__(self, sock: socket, id: int):
        self.sock = sock
        self.sock_id = id


class SocketsList:

    def __init__(self):
        """Management of list of sockets"""

        self._sockets: List[_SocketID] = []
        self._current_id = 1


    def add(self, sock: socket) -> int:
        sock_id = self._current_id
        self._sockets.append(_SocketID(sock, sock_id))
        self._current_id += 1
        return sock_id

    def _get_index(self, sock_id: int) -> int:
        for i in range(len(self._sockets)):
            if self._sockets[i].sock_id == sock_id:
                return i
        print_colored('error', 'Socket was not found in the list and could not be removed')
        return -1

    def remove(self, sock_id: int):
        index = self._get_index(sock_id)
        if index == -1:
            return
        sock = self._sockets[index].sock
        self._sockets.pop(index)
        sock.close()

    def send_to_all(self, data: str):
        for sockID in self._sockets:
            Network.send(sockID.sock, data)
