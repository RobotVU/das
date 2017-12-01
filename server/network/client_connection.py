from .base_connection import BaseConnection
from common import command

class ClientConnection(BaseConnection):
    """
    A wrapper for a TCP socket.
    Runs in separate thread and listens for input of the socket.
    """

    def __init__(self, connection, address, id, server):
        BaseConnection.__init__(self, connection, address, id)
        self.server = server

    def on_message(self, data):
        command_obj = command.Command.from_json(data)
        self.server.request_command(command_obj)


    def setup_client(self, id):
        """
        set up the client. blocking. the client should call a function with the same name first thing it connects.
        Server should send this data first thing
        :param map: map of the game
        :param id: id of the client
        :return: None
        """
        self.send(id)

    def shutdown(self):
        BaseConnection.shutdown(self)
        self.server.remove_connection(self.id)