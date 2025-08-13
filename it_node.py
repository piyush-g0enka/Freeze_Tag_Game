#!/usr/bin/env python3

# it_node.py
import random
import time
from node import Node
from messages.position_t import position_t
from messages.start_t import start_t
from messages.freeze_t import freeze_t
from messages.gameover_t import gameover_t
from messages.alive_t import alive_t


class ItNode(Node):
    """
    Represents the 'It' node in the Freeze Tag game.
    This node chases NotItNodes using a greedy nearest-neighbor strategy,
    and publishes its position and alive status to the game network.
    """

    def __init__(self, width, height, initial_position):
        """
        Initialize the ItNode.

        Args:
            width (int): Width of the game grid.
            height (int): Height of the game grid.
            initial_position (tuple): Starting (x, y) position of the node.
        """
        super().__init__()

        self.width = width
        self.height = height
        # Mutable list for position updates
        self.position = list(initial_position)
        self.idx = "it"

    def on_start(self):
        """
        Subscribe to all relevant LCM channels when the node starts.
        """
        self.start = False   # Indicates if the game has started
        self.game = True     # Controls main loop
        self.notit_positions = {}  # Track positions of all NotItNodes
        self.captured_notit_nodes = []  # List of captured (frozen) NotItNodes

        self.subscribe("START", self.handle_start)
        self.subscribe("POSITION", self.handle_position)
        self.subscribe("GAMEOVER", self.handle_gameover)

    def handle_position(self, channel, msg):
        """
        Callback for handling POSITION messages from NotItNodes.

        Args:
            channel (str): LCM channel name.
            msg (bytes): Encoded message data.
        """
        msg = position_t.decode(msg)

        if "notit_" in msg.name:
            if msg.active:
                self.notit_positions[msg.name] = (msg.x, msg.y)
            else:
                # Remove inactive (frozen) nodes from tracking
                self.notit_positions.pop(msg.name, None)

    def handle_start(self, channel, msg):
        """
        Callback for handling the START message.

        Args:
            channel (str): LCM channel name.
            msg (bytes): Encoded message data.
        """
        self.start = True
        print(f"{self.idx} started...")

    def handle_gameover(self, channel, msg):
        """
        Callback for handling the GAMEOVER message.

        Args:
            channel (str): LCM channel name.
            msg (bytes): Encoded message data.
        """
        self.game = False

    def move(self):
        """
        Move towards the nearest NotItNode using a greedy algorithm.
        If no targets are available, remain stationary.
        """
        if not self.notit_positions:
            # No targets to pursue
            return

        # Identify nearest NotItNode by Manhattan distance
        target_name, target_pos = min(
            self.notit_positions.items(),
            key=lambda item: self.manhattan_distance(self.position, item[1])
        )

        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]

        # Move step-by-step towards target
        if abs(dx) > abs(dy):
            self.position[0] += 1 if dx > 0 else -1
        elif dy != 0:
            self.position[1] += 1 if dy > 0 else -1

        # Enforce boundary constraints
        self.position[0] = max(0, min(self.position[0], self.width - 1))
        self.position[1] = max(0, min(self.position[1], self.height - 1))

    def manhattan_distance(self, p1, p2):
        """
        Compute Manhattan distance between two points.

        Args:
            p1 (tuple): Point 1 (x, y).
            p2 (tuple): Point 2 (x, y).

        Returns:
            int: Manhattan distance between p1 and p2.
        """
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def publish_position(self):
        """
        Publish the current position of the ItNode to the POSITION topic.
        """
        msg = position_t()
        msg.name = self.idx
        msg.active = True
        msg.x, msg.y = self.position
        self.lc.publish("POSITION", msg.encode())
        print(f"{msg.name} : x: {msg.x} | y: {msg.y}")

    def publish_alive_status(self):
        """
        Publish the alive status of the ItNode to the ALIVE topic.
        """
        msg = alive_t()
        msg.name = self.idx
        self.lc.publish("ALIVE", msg.encode())

    def run(self):
        """
        Main loop of the ItNode.
        Periodically moves and publishes position if the game is active.
        """
        while self.game:
            self.publish_alive_status()

            if self.start:
                self.move()
                self.publish_position()
                time.sleep(0.5)  # Control movement rate

    def on_stop(self):
        """
        Clean-up function when the node is stopped.
        """
        print(f"{self.idx} stopped...")


if __name__ == "__main__":
    # For testing: start node at position (5, 6)
    n = ItNode(20, 30, (5, 6))
