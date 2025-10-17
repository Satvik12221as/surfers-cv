import cv2
import mediapipe as mp
import threading
import time
from ursina import *

# --- Computer Vision Thread ---
# This part handles the webcam and pose detection.
# It runs in a separate thread to not slow down the game.

# Global dictionary to share data from the CV thread to the game thread
cv_input = {'lane': 0, 'action': None, 'initial_head_y': 0.5}
is_camera_running = True

def run_computer_vision():
    """
    Function to run the computer vision part of the game using OpenCV and MediaPipe.
    This will run in a separate thread.
    """
    global cv_input, is_camera_running

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open camera.")
        is_camera_running = False
        return

    # A flag to capture the initial head position once
    initial_position_captured = False

    while cap.isOpened() and is_camera_running:
        success, image = cap.read()
        if not success:
            continue

        # Flip the image horizontally for a later selfie-view display
        # and convert the BGR image to RGB.
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Get necessary landmarks
            nose = landmarks[mp_pose.PoseLandmark.NOSE]
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

            shoulder_midpoint_x = (left_shoulder.x + right_shoulder.x) / 2
            shoulder_midpoint_y = (left_shoulder.y + right_shoulder.y) / 2

            if not initial_position_captured:
                cv_input['initial_head_y'] = shoulder_midpoint_y
                initial_position_captured = True

            # --- Control Logic ---
            # 1. Lane switching
            if shoulder_midpoint_x < 0.4:
                cv_input['lane'] = -1  # Left lane
            elif shoulder_midpoint_x > 0.6:
                cv_input['lane'] = 1  # Right lane
            else:
                cv_input['lane'] = 0   # Middle lane
            
            # 2. Jumping
            hands_up = left_wrist.y < nose.y and right_wrist.y < nose.y
            if hands_up:
                cv_input['action'] = 'jump'
            # 3. Ducking
            elif shoulder_midpoint_y > cv_input['initial_head_y'] + 0.1:
                cv_input['action'] = 'duck'
            else:
                cv_input['action'] = None # No action
        
        time.sleep(0.02) # To prevent CPU overload

    pose.close()
    cap.release()
    cv2.destroyAllWindows()


# --- Ursina Game ---
# This is the main game logic part using the Ursina engine.

class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'cube'
        self.color = color.azure
        self.scale = (1, 2, 1)
        self.collider = 'box'
        
        self.target_lane = 0
        self.lane_width = 4
        self.is_jumping = False
        self.is_ducking = False
        self.jump_height = 4
        self.jump_duration = 0.6
        self.duck_duration = 0.5

    def update(self):
        # Smoothly move player between lanes
        self.target_lane = cv_input['lane']
        target_x = self.target_lane * self.lane_width
        self.x = lerp(self.x, target_x, time.dt * 8)

        # Handle actions from CV
        action = cv_input['action']
        if action == 'jump' and not self.is_jumping:
            self.jump()
        elif action == 'duck' and not self.is_ducking:
            self.duck()

    def jump(self):
        if self.is_jumping:
            return
        self.is_jumping = True
        self.animate_y(self.jump_height, duration=self.jump_duration/2, curve=curve.out_sine)
        self.animate_y(0, duration=self.jump_duration/2, delay=self.jump_duration/2, curve=curve.in_sine)
        invoke(setattr, self, 'is_jumping', False, delay=self.jump_duration)

    def duck(self):
        if self.is_ducking:
            return
        self.is_ducking = True
        self.animate_scale_y(1, duration=self.duck_duration, curve=curve.out_sine)
        self.animate_scale_y(2, duration=self.duck_duration, delay=self.duck_duration, curve=curve.in_sine)
        invoke(setattr, self, 'is_ducking', False, delay=self.duck_duration*2)

class Obstacle(Entity):
    def __init__(self, position=(0,0,0), o_type='full'):
        super().__init__(
            model='cube',
            collider='box',
            position=position,
            rotation=(0,0,0)
        )
        if o_type == 'full':
            self.scale = (4, 6, 1)
            self.color = color.red
            self.y = -0.5 # Align with ground
        else: # low obstacle
            self.scale = (4, 2, 1)
            self.color = color.orange
            self.y = 2 # Higher up for ducking under


class Coin(Entity):
    def __init__(self, position=(0,0,0)):
        super().__init__(
            model='sphere',
            collider='sphere',
            color=color.gold,
            scale=1,
            position=position
        )

def game_loop():
    global game_speed, score, spawn_timer, obstacles, coins

    # Move obstacles and coins
    for obj in obstacles + coins:
        obj.z += game_speed * time.dt
        if obj.z > 20: # Despawn if off-screen
            destroy(obj)
            if obj in obstacles: obstacles.remove(obj)
            if obj in coins: coins.remove(obj)

    # Spawn new objects
    spawn_timer -= time.dt
    if spawn_timer <= 0:
        spawn_objects()
        spawn_timer = random.uniform(0.8, 1.5) / (game_speed / 5)

    # Collision detection
    hit_info = player.intersects()
    if hit_info.hit:
        entity = hit_info.entity
        if isinstance(entity, Obstacle):
            end_game()
        elif isinstance(entity, Coin):
            score += 10
            score_text.text = f'Score: {score}'
            destroy(entity)
            coins.remove(entity)
    
    # Increase speed over time
    game_speed += time.dt * 0.1

def spawn_objects():
    global obstacles, coins
    lane = random.choice([-1, 0, 1]) * 4
    spawn_type = random.random()

    if spawn_type < 0.6: # Spawn obstacle
        obstacle_type = random.choice(['full', 'low'])
        obstacles.append(Obstacle(position=(lane, 0, -50), o_type=obstacle_type))
    elif spawn_type < 0.9: # Spawn coin
        coins.append(Coin(position=(lane, 1, -50)))


def start_game():
    global player, game_speed, score, obstacles, coins, spawn_timer
    
    # Clear old entities if restarting
    for obj in obstacles + coins:
        destroy(obj)
    
    game_speed = 15
    score = 0
    obstacles = []
    coins = []
    spawn_timer = 2
    
    if player is None:
        player = Player(position=(0,1,0))
    else:
        player.position=(0,1,0)
        
    player.visible = True
    player.enable()

    start_button.disable()
    title_text.disable()
    instructions_text.disable()
    score_text.enable()
    score_text.text = 'Score: 0'

    # Set the main update loop
    app.update = game_loop

def end_game():
    player.disable()
    start_button.text = 'Play Again'
    start_button.enable()
    title_text.text = 'Game Over!'
    title_text.enable()
    instructions_text.text = f'Final Score: {score}'
    instructions_text.enable()
    app.update = None # Stop the game loop

# --- App Setup ---
app = Ursina(borderless=False)
window.title = 'CV Body Surfer'
window.fullscreen = True

# --- Global Game State Variables --- 
obstacles = []
coins = []
player = None
# --- End of Added Section --- 

# Ground
ground = Entity(model='plane', scale=(30, 1, 200), color=color.gray, texture='white_cube', texture_scale=(30,200), collider='box')
for i in range(-1, 2):
    Entity(model='quad', scale=(0.1, 1, 200), position=(i*4 - 2, 0.01, 0), color=color.dark_gray)
    Entity(model='quad', scale=(0.1, 1, 200), position=(i*4 + 2, 0.01, 0), color=color.dark_gray)

# Camera
camera.position = (0, 8, -15)
camera.rotation_x = 20

# UI
title_text = Text('CV Body Surfer', scale=3, origin=(0,0), y=0.2)
instructions_text = Text('Move your body to switch lanes.\nRaise hands to jump, duck down to roll.', scale=1.5, origin=(0,0), y=0.05)
start_button = Button('Start Game', color=color.azure, scale=(0.2, 0.075), y=-0.1)
start_button.on_click = start_game

score_text = Text('Score: 0', position=(-0.8, 0.45), scale=2, origin=(-0.5, 0), color=color.white)
score_text.disable()

# Stop the game loop initially
app.update = None

if __name__ == '__main__':
    # Start the computer vision thread
    cv_thread = threading.Thread(target=run_computer_vision, daemon=True)
    cv_thread.start()

    # Run the Ursina app
    app.run()
    is_camera_running = False # Signal CV thread to stop when app closes
    cv_thread.join()