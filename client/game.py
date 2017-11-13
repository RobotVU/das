from __future__ import print_function
import math, json, socket, threading, select, sys, random, time
# from common.network_util import read_encoded

class Game:
    def __init__(self):
        self.row = 5
        self.col = 5

        self.map = [[0 for j in range(self.col)] for i in range(self.row)]

        self.commands = []
        self.users = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('localhost', 8081))
        threading.Thread(target=self.sock_check_for_update).start()

    def __str__(self):
        _str = ""
        for i in range(self.row):
            for j in range(self.col):
                _str += str(self.map[i][j])
                _str += "\t"
            _str += "\n"
        return _str

    def sock_check_for_update(self):
        print("Thread for listening is started\n")
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
                    print("received" , data)

    def add_user(self, p, r, c):
        if self.map[r][c] == 0:
            self.map[r][c] = p
            p.pos = [r, c]
            self.users.append(p)
            return True
        else:
            return False

    def remove_user(self, r, c):
        if self.map[r][c] == 0:
            return False
        else:
            self.users.remove(self.map[r][c])
            self.map[r][c] = 0
            return True

    def epoch(self):
        if len(self.commands):
            command = self.commands[0]
            command.apply(self)

            # Send the command to the server to be broadcasted to everyone
            self.sock.send(command.to_json())
            self.commands = self.commands[1:]
        else:
            return

    def emulate_all(self):
        """
        only for test.
        Run all commands in self.commands
        """
        i = 1
        while len(self.commands):
            print("###Epoch {0}".format(i))
            print(self.commands[0])
            i += 1
            self.epoch()
            print(self.__str__())

    def emulate(self, commands_per_second):
        """
        :param commands_per_second: number of commands per second
        run _emulate in a new thread
        """
        threading.Thread(target=self._emulate, args=(commands_per_second,)).start()

    def _emulate(self, command_per_second):
        while True:
            time.sleep(1/command_per_second)
            if len(self.commands):
                self.epoch()
            else:
                continue

    def simulate(self, iterations):
        """
        Run _simulate in a new thread
        """
        threading.Thread(target=self._simulate, args=(iterations,)).start()

    def _simulate(self, iterations):
        for iter in range(iterations):
            for i in range(self.row):
                for j in range(self.col):
                    if self.map[i][j] != 0 :
                        new_command = self.simulate_player(i,j)
                        self.commands.append(new_command)

    def simulate_player(self, r, c):
        value = random.choice([1, -1])
        direction = random.choice(['h', 'v'])
        return {'type': 'move', 'direction': direction, 'value': value, 'user': (self.map[r][c]).id}

    def simulate_dragon(self, e, c):
        pass
