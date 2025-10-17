import cv2
import mediapipe as mp
import threading
import time
from config import *

# This dictionary will be shared with the main game thread
# to pass user actions.
cv_input = {'lane': 0, 'action': None}
is_camera_running = True

def computer_vision_thread():
    """
    This function runs in a separate thread to handle all computer vision tasks,
    preventing the game from lagging.
    """
    global is_camera_running
    
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open camera.")
        is_camera_running = False
        return

    initial_head_y = None

    while cap.isOpened() and is_camera_running:
        success, image = cap.read()
        if not success:
            continue

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Key landmarks for game control
            nose = landmarks[mp_pose.PoseLandmark.NOSE]
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

            shoulder_midpoint_x = (left_shoulder.x + right_shoulder.x) / 2
            shoulder_midpoint_y = (left_shoulder.y + right_shoulder.y) / 2

            if initial_head_y is None:
                initial_head_y = shoulder_midpoint_y

            # --- Control Logic ---
            # 1. Lane switching based on shoulder position
            if shoulder_midpoint_x < VISION_LANE_LEFT_THRESHOLD:
                cv_input['lane'] = -1
            elif shoulder_midpoint_x > VISION_LANE_RIGHT_THRESHOLD:
                cv_input['lane'] = 1
            else:
                cv_input['lane'] = 0
            
            # 2. Jumping: Are both hands above the nose?
            hands_up = left_wrist.y < nose.y and right_wrist.y < nose.y
            if hands_up:
                cv_input['action'] = 'jump'
            # 3. Ducking: Has the head position dropped significantly?
            elif shoulder_midpoint_y > initial_head_y + VISION_DUCK_THRESHOLD:
                cv_input['action'] = 'duck'
            else:
                cv_input['action'] = None
        
        time.sleep(0.02) # Prevent CPU overload

    pose.close()
    cap.release()
