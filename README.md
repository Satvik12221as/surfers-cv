## CV Body Surfer 🏄‍♂️

This is an interactive 3D runner game where you control the player using your own body movements through your webcam.

# Key Features

Gesture-Based Control: Use your body to dodge, jump, and roll.

3D Endless Runner: A classic game format in a 3D environment.

Dynamic Obstacles: Obstacles and coins are randomly generated which makes game more interesting.

# Tech Stack

Python: The programming language.

Ursina Engine: A user-friendly 3D game engine for fast and fun development.

OpenCV: The standard for capturing and processing the live webcam feed.

MediaPipe: For high-performance, real-time body pose detection.

# ▶ How to Play

The goal is to run as far as possible, dodge obstacles, and collect coins to get the highest score.

Move Left/Right: Physically lean your body to the left or right to switch lanes.

Jump: Raise both of your hands above your head to jump over low obstacles.

Roll/Duck: Physically duck down to roll under high obstacles.

#  Setup and Installation

1. Get the Code

        git clone [https://github.com/Satvik12221as/surfers-cv.git]
        ```cd surfers-cv```

2. Create a Virtual Environment

        Create the environment
        ```python -m venv venv```

        Activate it
        ```.\venv\Scripts\activate```

3. Install the Required Libraries

        ```pip install -r requirements.txt```


# How to Run the Game

Start the game using this command in your terminal:

    ```python main.py```

# Project Structure

This project is organized into several files:

main.py: The main file you run to start the game.

game.py: Contains the core game logic (scoring, spawning objects, etc.).

player.py: Defines the player character and its actions.

vision.py: Handles all the computer vision code to detect your movements.

entities.py: Defines the obstacles and coins.

ui.py: Manages the start menu, game over screen, and score display.

config.py: Stores all the game settings, like speed and jump height.

requirements.txt: Lists all the libraries needed for the project.