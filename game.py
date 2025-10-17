from ursina import *
import random
from config import *
from player import Player
from entities import Obstacle, Coin

class Game:
    def __init__(self, ui):
        self.ui = ui
        self.player = None
        self.obstacles = []
        self.coins = []
        self.score = 0
        self.game_speed = INITIAL_GAME_SPEED
        self.spawn_timer = 2
        
        self.ui.start_button.on_click = self.start_game
        self.is_running = False

    def start_game(self):
        # Clean up from previous game if any
        for obj in self.obstacles + self.coins:
            destroy(obj)
        
        self.obstacles.clear()
        self.coins.clear()
        
        self.score = 0
        self.game_speed = INITIAL_GAME_SPEED
        self.spawn_timer = 2
        
        if self.player is None:
            self.player = Player(position=(0,0,0))
        else:
            self.player.position = (0,0,0)
            self.player.enable()

        self.ui.hide_main_menu()
        self.ui.score_text.text = 'Score: 0'
        self.is_running = True

    def end_game(self):
        self.is_running = False
        self.player.disable()
        self.ui.show_game_over(self.score)

    def update(self):
        if not self.is_running:
            return

        # Move and despawn objects
        for obj in self.obstacles + self.coins:
            obj.z += self.game_speed * time.dt
            if obj.z > 20:
                destroy(obj)
                if isinstance(obj, Obstacle): self.obstacles.remove(obj)
                else: self.coins.remove(obj)

        # Spawn new objects
        self.spawn_timer -= time.dt
        if self.spawn_timer <= 0:
            self._spawn_objects()
            self.spawn_timer = random.uniform(0.8, 1.5) / (self.game_speed / INITIAL_GAME_SPEED)
        
        # Increase speed
        self.game_speed += GAME_SPEED_INCREASE_RATE * time.dt
        
        # Collision detection
        self._check_collisions()

    def _spawn_objects(self):
        lane = random.choice(LANE_POSITIONS)
        spawn_type = random.random()

        if spawn_type < 0.6: # Spawn obstacle
            obstacle_type = random.choice(['full', 'low'])
            self.obstacles.append(Obstacle(position=(lane, 0, -50), o_type=obstacle_type))
        elif spawn_type < 0.9: # Spawn coin series
            for i in range(3):
                self.coins.append(Coin(position=(lane, 1, -50 - i * 2)))
    
    def _check_collisions(self):
        hit_info = self.player.intersects()
        if hit_info.hit:
            entity = hit_info.entity
            if isinstance(entity, Obstacle):
                self.end_game()
            elif isinstance(entity, Coin):
                self.score += 10
                self.ui.score_text.text = f'Score: {self.score}'
                destroy(entity)
                self.coins.remove(entity)
