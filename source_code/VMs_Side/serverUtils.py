from protocol import *

class SocketID:

    def __init__(self, sock: socket, id: int):
        self.sock = sock
        self.sock_id = id


class Sockets:

    def __init__(self):
        """Management of list of sockets"""

        self.sockets: List[SocketID] = []
        self.current_id = 1


    def add(self, sock: socket) -> int:
        sock_id = self.current_id
        self.sockets.append(SocketID(sock, sock_id))
        self.current_id += 1
        return sock_id

    def get_index(self, sock_id: int) -> int:
        for i in range(len(self.sockets)):
            if self.sockets[i].sock_id == sock_id:
                return i
        print_colored('error', 'Socket was not found in the list and could not be removed')
        return -1

    def remove(self, sock_id: int):
        index = self.get_index(sock_id)
        if index == -1:
            return
        sock = self.sockets[index].sock
        self.sockets.pop(index)
        sock.close()