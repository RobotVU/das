import json
from .base_connection import BaseConnection
from common import command

import logging
logger = logging.getLogger("sys." + __name__.split(".")[-1])


class P2PConnection(BaseConnection):

    def __init__(self, socket, address, id, server):
        BaseConnection.__init__(self, socket, address, id)
        self.server = server
        self.heartbeat = 10000

    def __str__(self):
        return BaseConnection.__str__(self) + " [hb:{}]".format(self.heartbeat)


    def on_message(self, data):
        json_data = json.loads(data)

        if json_data['type'] == 'hb':
            self.heartbeat += 1000

        elif json_data['type'] == 'bc':
            # Put the message in the queue
            command_obj = command.Command.from_json(json_data['command'])
            self.server.request_queue.put(command_obj)

        elif json_data['type'] == 'init':
            #self.server.request_queue.put(json_data['initial_state'])
            pass
        else:
            logger.warning("Unrecognized message received from peer [{}]".format(data))

