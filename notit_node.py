#!/usr/bin/env python3

import random
import time
from node import Node
from messages.position_t import position_t
from messages.start_t import start_t
from messages.freeze_t import freeze_t
from messages.gameover_t import gameover_t
from messages.alive_t import alive_t


class NotItNode(Node):
    """
    Represents a NotIt node in the Freeze Tag game.
    The node moves randomly within the grid until it is frozen.
    It publishes its position and alive status to the game network.
    """

    count = 0  # Class-level counter for NotItNode instances

    def __init__(self, width, height, initial_position):
        """
        Initialize the NotItNode.

        Args:
            width (int): Width of the game grid.
            height (int): Height of the game grid.
            initial_position (tuple): Starting (x, y) position of the node.
        """
        super().__init__()

        self.width = width
        self.height = height
        self.position = initial_position

        # Assign a unique identifier to the node
        self.idx = f"notit_{NotItNode.count}"
        NotItNode.count += 1

    def on_start(self):
        """
        Subscribe to all relevant LCM channels when the node starts.
        """
        self.frozen = False  # Indicates if node is frozen
        self.start = False   # Indicates if game has started
        self.game = True     # Controls main loop

        self.subscribe("START", self.handle_start)
        self.subscribe("FREEZE", self.handle_freeze)
        self.subscribe("GAMEOVER", self.handle_gameover)

    def handle_start(self, channel, msg):
        """
        Callback for handling the START message.

        Args:
            channel (str): LCM channel name.
            msg (bytes): Encoded message data.
        """
        self.start = True
        print(f"{self.idx} started...")

    def handle_freeze(self, channel, msg):
        """
        Callback for handling the FREEZE message.

        Args:
            channel (str): LCM channel name.
            msg (bytes): Encoded message data.
        """
        msg = freeze_t.decode(msg)
        if msg.name == self.idx:
            self.frozen = True
            

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
        Move the node to a random adjacent cell in the grid.
        Ensures the node stays within grid boundaries.
        """
        dx, dy = random.choice([
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ])

        # Update position with boundary checks
        self.position = (
            max(0, min(self.position[0] + dx, self.width - 1)),
            max(0, min(self.position[1] + dy, self.height - 1))
        )

    def publish_position(self):
        """
        Publish the current position of the node to the POSITION topic.
        """
        msg = position_t()
        msg.name = self.idx
        msg.active = not self.frozen
        msg.x, msg.y = self.position
        self.lc.publish("POSITION", msg.encode())
        print(f"{msg.name} : x: {msg.x} | y: {msg.y}")

    def publish_alive_status(self):
        """
        Publish the alive status of the node to the ALIVE topic.
        """
        msg = alive_t()
        msg.name = self.idx
        self.lc.publish("ALIVE", msg.encode())

    def run(self):
        """
        Main loop of the NotItNode.
        Periodically publishes alive status and position if the game is active.
        """
        while self.game:
            self.publish_alive_status()

            if self.start:
                if not self.frozen:
                    self.move()
                self.publish_position()

                # Move every 1 second
                time.sleep(1.0)

    def on_stop(self):
        """
        Clean-up function when the node is stopped.
        Decrements the class-level instance counter.
        """
        print(f"{self.idx} stopped...")
        NotItNode.count -= 1


if __name__ == "__main__":
    # For testing: start node at position (5,6)
    n = NotItNode(20, 30, (5, 6))
