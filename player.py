from ursina import *
from config import *
from vision import cv_input

class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(model='cube', scale=(1, 2, 1), collider='box', color=color.azure, **kwargs)
        
        self.is_jumping = False
        self.is_ducking = False

    def update(self):
        # 1. Handle Lane Movement
        target_x = cv_input['lane'] * PLAYER_LANE_WIDTH
        self.x = lerp(self.x, target_x, time.dt * 8)

        # 2. Handle Actions (Jump/Duck)
        action = cv_input.get('action')
        if action == 'jump' and not self.is_jumping:
            self.jump()
        elif action == 'duck' and not self.is_ducking:
            self.duck()

    def jump(self):
        if self.is_jumping:
            return
        self.is_jumping = True
        self.animate_y(PLAYER_JUMP_HEIGHT, duration=PLAYER_JUMP_DURATION/2, curve=curve.out_sine)
        self.animate_y(0, duration=PLAYER_JUMP_DURATION/2, delay=PLAYER_JUMP_DURATION/2, curve=curve.in_sine)
        invoke(setattr, self, 'is_jumping', False, delay=PLAYER_JUMP_DURATION)

    def duck(self):
        if self.is_ducking:
            return
        self.is_ducking = True
        # Duck by scaling down and moving down slightly
        self.animate_scale_y(1, duration=PLAYER_DUCK_DURATION, curve=curve.out_sine)
        self.animate_y(-0.5, duration=PLAYER_DUCK_DURATION, curve=curve.out_sine)
        
        # Return to normal
        invoke(self.stand_up, delay=PLAYER_DUCK_DURATION)

    def stand_up(self):
        self.animate_scale_y(2, duration=PLAYER_DUCK_DURATION, curve=curve.in_sine)
        self.animate_y(0, duration=PLAYER_DUCK_DURATION, curve=curve.in_sine)
        invoke(setattr, self, 'is_ducking', False, delay=PLAYER_DUCK_DURATION)
