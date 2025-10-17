from ursina import *
import threading
from game import Game
from vision import computer_vision_thread, is_camera_running
from ui import UIManager
from config import *

def setup_scene(app):
    """Sets up the static game environment."""
    camera.position = CAMERA_POSITION
    camera.rotation_x = CAMERA_ROTATION
    
    ground = Entity(model='plane', scale=(30, 1, 200), color=color.gray, texture='white_cube', texture_scale=(30, 200), collider='box')
    
    # Lane markers
    for i in range(-1, 2):
        Entity(model='quad', scale=(0.1, 1, 200), position=(i * PLAYER_LANE_WIDTH - 2, 0.01, 0), color=color.dark_gray)
        Entity(model='quad', scale=(0.1, 1, 200), position=(i * PLAYER_LANE_WIDTH + 2, 0.01, 0), color=color.dark_gray)

if __name__ == '__main__':
    app = Ursina(borderless=False)
    window.title = 'CV Body Surfer'
    window.fullscreen = True

    # Setup the static scene elements
    setup_scene(app)

    # Initialize UI and Game logic
    ui = UIManager()
    game = Game(ui)
    
    # Set the main update function to be the game's update method
    app.update = game.update

    # Start the computer vision in a separate thread
    cv_thread = threading.Thread(target=computer_vision_thread, daemon=True)
    cv_thread.start()

    # Run the Ursina application
    app.run()
    
    # Signal the CV thread to stop when the app closes
    is_camera_running = False
    cv_thread.join()
