import math
from common.game import Game
from client.network.transport import ClientTransport
from common.constants import TRANSPORT, USERS, DIRECTIONS, init_logger, logger
from common.command import MoveCommand, HealCommand, AttackCommand
from common.visualizer import Visualizer
import threading, random, time


class ClientApp():
    def __init__(self):
        self.game = Game()
        self.transport_layer = ClientTransport(self.game, TRANSPORT.port, TRANSPORT.host)

        id, map = self.transport_layer.setup_client()
        self.id = id
        # replace json objects with user object (oh I miss you JS :( )
        self.game.from_serialized_map(map, id)
        logger.info("Setup data -> id: {0}".format(id))

        self.transport_layer.id = id
        self.transport_layer.listen()
        self.my_user = next(filter(lambda el: el.id == self.id, self.game.users))
        print("Self user is", self.my_user)

    def generate_commands(self, iterations):
        """
        Run _simulate in a new thread
        """
        threading.Thread(target=self._generate_commands, args=(iterations,)).start()


    def _generate_commands(self, iterations):
        """
        Generate simulation commands
        :param iterations: Number of iterations
        :return: None
        """
        logger.info("Generating commands for {} iterations".format(iterations))
        for i in range(iterations):
            new_command = random.choice([self.simulate_player(), self.simulate_dragon()])
            # If there is no dragon and no one with hp<50%, no commands will be generated. In that case do nothing
            if new_command:
                self.game.commands.append(new_command)

    def simulate_player(self):
        """
        Simulate the actions of the self player based on game spec
        :return: Command Object
        """

        ######## Option 1: heal a close-by player
        heal_candidates = self.get_users_in_range(self.my_user.pos, 5, USERS.PLAYER)
        for user in heal_candidates:
            if user.hp < user.MAX_HP/2:
                return HealCommand(self.id, user.id)

        ######## Option 2: Attack a close dragon if available
        attack_candidates = self.get_users_in_range(self.my_user.pos, 2, USERS.DRAGON)
        if len(attack_candidates):
            target = attack_candidates[0]
            return AttackCommand(self.id, target.id)

        ######## Option 3: Move toward the closest dragon
        dragons = list(filter(lambda _user: _user.type == USERS.DRAGON, self.game.users))
        if len(dragons):
            # sort dragons by distance
            # NOTE: we assume that the distance of the closest dragon is more than 2.
            # Because otherwise we would have returned with an attack command
            # TODO: this is the same as command.get_distance. make that a shared util function
            dragons.sort(key=lambda dragon: math.fabs(dragon.pos[0]-self.my_user.pos[0]) + math.fabs(dragon.pos[1]-self.my_user.pos[1]))

            # Move options: Move vertically toward that dragon or Horizontally
            # If they are in the same row/col we know what to do
            move_target = dragons[0]
            value = None
            move_direction = None

            if self.my_user.pos[0] == move_target.pos[0]:
                move_direction = DIRECTIONS.H
            elif self.my_user.pos[1] == move_target.pos[1]:
                move_direction = DIRECTIONS.V
            else:
                # If not, we choose randomly
                move_direction = random.choice([DIRECTIONS.H, DIRECTIONS.V])


            if move_direction == DIRECTIONS.H:
                value = 1 if move_target.pos[1] > self.my_user.pos[1] else -1
            else:
                value = 1 if move_target.pos[0] > self.my_user.pos[0] else -1

            if value and move_direction:
                return MoveCommand(self.id, value, move_direction)

        logger.warn("Failed to find a simulation for player")

    def simulate_dragon(self):
        """
        Simulate the behaviour of all dragons based on game spec
        :return: Command Object
        """
        attacker_candidates = self.get_users_in_range(self.my_user.pos, 2, USERS.DRAGON)
        if len(attacker_candidates):
            attacker = random.choice(attacker_candidates)
            return AttackCommand(attacker.id, self.id)


    def get_users_in_range(self, point, limit, type=-1):
        """
        Utility function for simulation. Return a list of all users (player and dragons) in a range
        if type is specified, only users from that type will be returned
        :param limit: distance limit
        :param point: the root point of the distance
        ":type: type of players to return
        :return: User[]
        """
        users = []
        for user in self.game.users:
            if (math.fabs(point[0] - user.pos[0])) + (math.fabs(point[1] - user.pos[1])) <= limit:
                if type == -1:
                    users.append(user)
                else:
                    if user.type == type:
                        users.append(user)

        return users

    def run(self, commands_per_second):
        """
        :param commands_per_second: number of commands per second
        run _run in a new thread
        """
        threading.Thread(target=self._run, args=(commands_per_second,)).start()

    def _run(self, command_per_second):
        while True:
            time.sleep(1/command_per_second)
            # Generate one or max two new commands that will be appended to the end of the list
            self._generate_commands(1)
            if len(self.game.commands):
                command_to_apply = self.game.commands.pop(0)
                logger.info("Apply command: " + str(command_to_apply))

                self.transport_layer.send_data(command_to_apply.to_json())
            else:
                continue

if __name__ == "__main__":
    # init_logger("log/client_{0}.log".format(time.time()))
    init_logger("log/client.log")
    client = ClientApp()

    # @Jonas note that we can no longer simulate alot of commands at onec because they depend on the new map
    # client.generate_commands(1000)

    client.run(.5)

    # start visualization
    # visualizer = Visualizer(client.game, client.id)
    # visualizer.visualize()
