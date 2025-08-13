#!/usr/bin/env python3

# game.py
import multiprocessing
import argparse
from node import Node
from notit_node import NotItNode
from it_node import ItNode
from game_node import GameNode

def main():
    """
    Main function to parse arguments and launch the required nodes.
    """
    parser = argparse.ArgumentParser(description="Distributed Freeze Tag Game")
    parser.add_argument("--width", type=int, required=True, help="Width of the board")
    parser.add_argument("--height", type=int, required=True, help="Height of the board")
    parser.add_argument("--num-not-it", type=int, required=True, help="Number of NotIt nodes")
    parser.add_argument("--positions", nargs="+", type=int,
                        help="Positions of NotIt nodes and It node: x1 y1 x2 y2 ... x_it y_it")

    args = parser.parse_args()

    expected_positions = (args.num_not_it + 1) * 2
    if len(args.positions) != expected_positions:
        parser.error(f"Expected {expected_positions} position values, got {len(args.positions)}.")

    # Extract positions
    notit_positions = [tuple(args.positions[i:i + 2]) for i in range(0, args.num_not_it * 2, 2)]
    it_position = tuple(args.positions[-2:])


    processes = []

    # Start NotIt nodes
    for idx, (x, y) in enumerate(notit_positions):
        node = NotItNode(args.width, args.height, (x, y))
        node_process = multiprocessing.Process(target=node.launch_node, name=f"NotItNode_{idx}")
        processes.append(node_process)

    # Start ItNode
    it_node = ItNode(args.width, args.height, it_position)
    it_node_process = multiprocessing.Process(target=it_node.launch_node, name="ItNode")
    processes.append(it_node_process)

    # Start GameNode
    game_node = GameNode(args.width, args.height, args.num_not_it)
    game_node_process = multiprocessing.Process(target=game_node.launch_node, name="GameNode")
    processes.append(game_node_process)

    # Start all processes
    for p in processes:
        p.start()

    for p in processes:
        p.join()


if __name__ == "__main__":
    main()
