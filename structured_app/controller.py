import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Screen dimensions
WIDTH = 450
HEIGHT = 600

CUBE_STATES = ['regular', 'multi', 'random', 'glitchy']
BACKGROUND_STATES = ['squares', 'particles', 'circles', 'waveform', 'triangles', 'tunnel']

BUTTON_WIDTH = 50
BUTTON_HEIGHT = 50

def draw_button(pygame, screen, text, x, y, color):
    pygame.draw.rect(screen, color, (x, y, BUTTON_WIDTH, BUTTON_HEIGHT))
    screen.blit(text, (x + BUTTON_WIDTH // 2 - text.get_width() // 2, y + BUTTON_HEIGHT // 2 - text.get_height() // 2))

class ControllerScreen:
    def __init__(self):
        pygame.init()
        self.pygame = pygame

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Visuals Controller')

        self.font = pygame.font.Font(None, 24)

        self.pressed = False
        self.closed = False

    def render(self, visuals_state):
        center_offset = (WIDTH - 230) // 2

        button_positions = {
            81: (0 + center_offset, 60), 82: (60 + center_offset, 60), 83: (120 + center_offset, 60), 84: (180 + center_offset, 60),
            71: (0 + center_offset, 120), 72: (60 + center_offset, 120), 73: (120 + center_offset, 120), 74: (180 + center_offset, 120),
            61: (0 + center_offset, 180), 62: (60 + center_offset, 180), 63: (120 + center_offset, 180), 64: (180 + center_offset, 180),
            51: (0 + center_offset, 240), 52: (60 + center_offset, 240), 53: (120 + center_offset, 240), 54: (180 + center_offset, 240),
            41: (0 + center_offset, 300), 42: (60 + center_offset, 300), 43: (120 + center_offset, 300), 44: (180 + center_offset, 300),
            31: (0 + center_offset, 360), 32: (60 + center_offset, 360), 33: (120 + center_offset, 360), 34: (180 + center_offset, 360),
            21: (0 + center_offset, 420), 22: (60 + center_offset, 420), 23: (120 + center_offset, 420), 24: (180 + center_offset, 420),
            11: (0 + center_offset, 480), 12: (60 + center_offset, 480), 13: (120 + center_offset, 480), 14: (180 + center_offset, 480)
        }

        button_states = {
            'cube': {
                'regular': 81,
                'multi': 82,
                'random': 83,
                'glitchy': 84
            },
            'background': {
                'squares': 41,
                'particles': 42,
                'circles': 43,
                'waveform': 44,
                'triangles': 31,
                'tunnel': 32
            }
        }

        for event in self.pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            elif event.type == MOUSEBUTTONDOWN:
                mouse = self.pygame.mouse.get_pos()
                for btn, pos in button_positions.items():
                    if pos[0] <= mouse[0] <= pos[0] + BUTTON_WIDTH and pos[1] <= mouse[1] <= pos[1] + BUTTON_HEIGHT:
                        # A button was clicked, now determine which one
                        for state_type, states in button_states.items():
                            if btn in states.values():
                                visuals_state[state_type] = list(states.keys())[list(states.values()).index(btn)]

        self.screen.fill(BLACK)
        labeled_buttons = []

        for state_type, states in button_states.items():
            for state, btn_num in states.items():
                labeled_buttons.append(btn_num)
                if btn_num in button_positions:
                    x, y = button_positions[btn_num]

                text = self.font.render(state[:4], True, WHITE)  # Use the first 4 characters of the state name
                color = BLUE if visuals_state[state_type] == state else RED
                draw_button(pygame=self.pygame, screen=self.screen, text=text, x=x, y=y, color=color)

        # Draw other buttons as gray
        for btn_num, (x, y) in button_positions.items():
            if btn_num not in labeled_buttons:
                text = self.font.render(str(btn_num), True, WHITE)
                draw_button(pygame=self.pygame, screen=self.screen, text=text, x=x, y=y, color=GRAY)

        self.pygame.display.flip()

    def switch_pressed(self):
        return self.pressed
    
    def close_pressed(self):
        return self.closed
    
    def close(self):
        pygame.quit()
