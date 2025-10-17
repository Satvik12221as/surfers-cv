from ursina import *

class UIManager:
    def __init__(self):
        self.title_text = Text('CV Body Surfer', scale=3, origin=(0,0), y=0.2)
        self.instructions_text = Text('Move your body to switch lanes.\nRaise hands to jump, duck down to roll.', scale=1.5, origin=(0,0), y=0.05)
        self.start_button = Button('Start Game', color=color.azure, scale=(0.2, 0.075), y=-0.1)
        self.score_text = Text('Score: 0', position=(-0.8, 0.45), scale=2, origin=(-0.5, 0), color=color.white)
        self.score_text.disable()

    def show_main_menu(self):
        self.title_text.enable()
        self.instructions_text.enable()
        self.start_button.enable()
        self.score_text.disable()

    def hide_main_menu(self):
        self.title_text.disable()
        self.instructions_text.disable()
        self.start_button.disable()
        self.score_text.enable()

    def show_game_over(self, final_score):
        self.title_text.text = 'Game Over!'
        self.instructions_text.text = f'Final Score: {final_score}'
        self.start_button.text = 'Play Again'
        self.show_main_menu()
