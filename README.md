# Interaction Language
Chinese (Using SimHei.ttf for support)

# Purpose
It is a **curriculum design** for data structures and algorithms by **Pygame**. 

# Functions description
Users can adjust the number of the police, the density of the barriers, police's catching algorithms and FPS.
<img width="300" height="384" alt="image" src="https://github.com/user-attachments/assets/74423665-a874-4ab2-9518-d886b89a0b4a" />

Then the GUI will show how police catch the thief cooperatively **step by step**.
<img width="300" height="384" alt="image" src="https://github.com/user-attachments/assets/0010a1c4-6454-483a-a409-5eb4b33481da" />

# Structure
## main.py
Run main.py to **start** the game.

## constants.py
constants.py is for global variables, you are recommended to change the size, the colors and the font path.

## ui_elements.py
ui_elements.py is used to describe elements like **Button** for ui. You can add more elements into this file.

## map.py
map.py is to initialize a map, randomly setting barriers by density setting.
It also ensures basic movement rules including moving *UDLR(Up, Down, Left, Right)* and no collision.

## utils.py
It is the most important file for the curriculum design.
It contains algorithms for police and thief respectively.
### FOR THE POLICE TEAM
There are __A*, DFS, BFS, GREEDY__ algorithms.
It also descirbes how to move collaboratively.
### FOR THE THIEF
The game is designed for **only one thief**.
The thief moves by **Maximin Strategy**.

## experiment_runner.py
It is being developed...
(The aim is to write the report.)
