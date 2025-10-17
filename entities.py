from ursina import *

class Obstacle(Entity):
    def __init__(self, position=(0,0,0), o_type='full'):
        super().__init__(model='cube', collider='box', position=position)
        
        if o_type == 'full':
            # A tall obstacle to jump over
            self.scale = (4, 6, 1)
            self.color = color.red
            self.y = -0.5 # Align with ground
        else:
            # A high obstacle to duck under
            self.scale = (4, 2, 1)
            self.color = color.orange
            self.y = 2

class Coin(Entity):
    def __init__(self, position=(0,0,0)):
        super().__init__(
            model='sphere',
            collider='sphere',
            color=color.gold,
            scale=1,
            position=position
        )
