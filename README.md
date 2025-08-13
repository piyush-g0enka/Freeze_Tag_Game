 # Distributed Freeze Tag Game

 ## Overview
 A Python-based simulation of the Freeze Tag game using **LCM** (Lightweight Communications and Marshalling) for inter-node communication and **OpenCV** for visualization.  
 Multiple agents interact on a grid:
 - **GameNode** – Central controller and visualization
 - **ItNode** – Chaser that freezes others
 - **NotItNode** – Random movers avoiding being frozen

 ---

 ## Requirements
 - Python 3.8+
 - `lcm`, `opencv-python`, `numpy`

 Install:
 ```bash
 pip install lcm opencv-python numpy
 ```

 ---

 ## Run from Source
 ```bash
 python3 game.py --width 20 --height 15 --num-not-it 3 --position 10 3 5 5 10 12 0 0
 ```

 ---

 ## Run from Docker (Ubuntu)
 ```bash
 docker load -i freeze-tag-game.tar
 xhost +local:docker
 docker run -it --rm \
   --network=host \
   -e DISPLAY=$DISPLAY \
   -v /tmp/.X11-unix:/tmp/.X11-unix \
   freeze-tag-game --width 20 --height 15 --num-not-it 3 --position 10 3 5 5 10 12 0 0
 ```

 ---

 ## Controls
 - Press **Ctrl+C** to exit the game.
