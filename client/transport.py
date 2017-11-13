import socket, threading, select, sys

class ClientTransport:
    def __init__(self, game):
        self.game = game

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('localhost', 8081))
        threading.Thread(target=self.check_recv).start()

    def check_recv(self):
        while True:
            socket_list = [self.sock]
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
            for sock in read_sockets:
                # incoming message from remote server
                data = sock.recv(1024)
                # data = read_encoded(sock)
                if not data:
                    print('\nDisconnected from server')
                    sys.exit()
                else:
                    # TODO: create a new Command object from Command.from_json and append to game.commands
                    print("received", data)

    def send_data(self, data):
        try:
            self.sock.sendall(data)
        except Exception as e:
            print("Error while sending data ", str(e))

