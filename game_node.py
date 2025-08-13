# game_node.py
import random
import time
import cv2
import signal
import sys
from node import Node
from messages.position_t import position_t
from messages.start_t import start_t
from messages.freeze_t import freeze_t
from messages.gameover_t import gameover_t
from messages.alive_t import alive_t
import numpy as np

class GameNode(Node):
    """
    Central game controller node.
    Visualizes the game state, coordinates start of the game,
    checks freeze conditions, and publishes GAMEOVER when the game ends.
    """

    def __init__(self, width, height, notit_count):
        """
        Initialize the GameNode.

        Args:
            width (int): Width of the game grid.
            height (int): Height of the game grid.
            notit_count (int): Number of NotIt nodes expected in the game.
        """
        super().__init__()

        self.width = width
        self.height = height
        self.notit_count = notit_count

        self.alive_nodes = set()
        self.running = True  # Add running flag for graceful shutdown

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """
        Handle termination signals for graceful shutdown.
        """
        print(f"Received termination signal ({signum}). Shutting down gracefully...")
        self.game = False


    def on_start(self):
        """
        Subscribe to all relevant LCM channels and initialize canvas.
        """
        self.start = False
        self.game = True
        self.positions = {}
        self.active_nodes = set()
        self.captured_notit_nodes = []

        self.subscribe("ALIVE", self.handle_alive)
        self.subscribe("POSITION", self.handle_position)
        self.subscribe("GAMEOVER", self.handle_gameover)

        self.init_canvas()

    def init_canvas(self):
        """
        Initialize the game visualization canvas using OpenCV.
        Dynamically adjusts size to fit on screen.
        """
        max_window_size = 800
        self.cell_size = max(10, min(max_window_size // self.width, max_window_size // self.height))

        self.canvas_height = self.height * self.cell_size
        self.canvas_width = self.width * self.cell_size
        self.canvas = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)

    def handle_position(self, channel, msg):
        """
        Callback for POSITION messages.

        Args:
            channel (str): LCM channel name.
            msg (bytes): Encoded position_t message.
        """
        msg = position_t.decode(msg)
        self.positions[msg.name] = (msg.x, msg.y)

        self.check_freeze_condition()

        if msg.active:
            self.active_nodes.add(msg.name)
        else:
            self.active_nodes.discard(msg.name)

    def handle_alive(self, channel, msg):
        """
        Callback for ALIVE messages.

        Args:
            channel (str): LCM channel name.
            msg (bytes): Encoded alive_t message.
        """
        msg = alive_t.decode(msg)
        self.alive_nodes.add(msg.name)

    def handle_gameover(self, channel, msg):
        """
        Callback for GAMEOVER message to gracefully stop the game.
        """
        print("GameNode: Received GAMEOVER message. Shutting down...")
        self.running = False


    def publish_start_message(self):
        """
        Wait until all nodes have published ALIVE messages, then publish START message.
        """
        while not self.start and self.running:
            if len(self.alive_nodes) == self.notit_count + 1:
                self.start = True
                msg = start_t()
                self.lc.publish("START", msg.encode())
                print("Published START message.")
            time.sleep(1.0)

    def draw_grid(self, canvas):
        """
        Draw grid lines on the canvas.

        Args:
            canvas (np.ndarray): OpenCV canvas to draw on.
        """
        for x in range(0, self.canvas_width, self.cell_size):
            cv2.line(canvas, (x, 0), (x, self.canvas_height), (50, 50, 50), 1)
        for y in range(0, self.canvas_height, self.cell_size):
            cv2.line(canvas, (0, y), (self.canvas_width, y), (50, 50, 50), 1)

    def update_canvas(self):
        """
        Redraw the canvas with updated positions of all nodes.
        Draw NotIt nodes first, then It node on top.
        """
        # Clear canvas
        self.canvas[:] = (0, 0, 0)

        # Draw grid
        self.draw_grid(self.canvas)

        # Step 1: Draw NotItNodes
        for name, (x, y) in self.positions.items():
            if name == "it":
                continue  # Skip ItNode for now

            y_inverted = self.height - 1 - y
            top_left = (x * self.cell_size, y_inverted * self.cell_size)
            bottom_right = ((x + 1) * self.cell_size, (y_inverted + 1) * self.cell_size)

            color = (255, 0, 0)  # Blue for NotIt
            cv2.rectangle(self.canvas, top_left, bottom_right, color, -1)

        # Step 2: Draw ItNode on top
        it_position = self.positions.get("it")
        if it_position:
            x, y = it_position
            y_inverted = self.height - 1 - y
            top_left = (x * self.cell_size, y_inverted * self.cell_size)
            bottom_right = ((x + 1) * self.cell_size, (y_inverted + 1) * self.cell_size)

            color = (0, 0, 255)  # Red for It
            cv2.rectangle(self.canvas, top_left, bottom_right, color, -1)


    def check_freeze_condition(self):
        """
        Check if any NotIt node is at the same position as ItNode.
        If so, publish a FREEZE message.
        """
        it_position = self.positions.get("it")
        if not it_position:
            return

        for name, pos in self.positions.items():
            if name.startswith("notit") and pos == it_position:
                freeze_msg = freeze_t()
                freeze_msg.name = name
                self.lc.publish("FREEZE", freeze_msg.encode())

    def run(self):
        """
        Main game loop.
        Visualizes the game and ends when all NotIt nodes are frozen or on termination.
        """
        self.publish_start_message()

        while self.running and self.game:
            self.update_canvas()
            cv2.imshow("Freeze Tag Game", self.canvas)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.25)

            if len(self.active_nodes) <= 1:
                self.game = False

        

    def on_stop(self):
        """
        Clean-up and signal GAMEOVER to all nodes.
        """
        gameover_msg = gameover_t()
        self.lc.publish("GAMEOVER", gameover_msg.encode())
        cv2.destroyAllWindows()
        print ("Game stopped...")

if __name__ == "__main__":
    n = GameNode(20, 30, 4)
    n.launch_node()
