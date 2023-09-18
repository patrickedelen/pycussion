import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Screen dimensions
# WIDTH = 450
# HEIGHT = 600
WIDTH = 400
HEIGHT = 800

CUBE_STATES = ['regular', 'multi', 'random', 'glitchy']
BACKGROUND_STATES = ['squares', 'particles', 'circles', 'waveform', 'triangles', 'tunnel']

BUTTON_WIDTH = 50
BUTTON_HEIGHT = 50

def draw_button(pygame, screen, text, x, y, color):
    pygame.draw.rect(screen, color, (x, y, BUTTON_WIDTH, BUTTON_HEIGHT))
    screen.blit(text, (x + BUTTON_WIDTH // 2 - text.get_width() // 2, y + BUTTON_HEIGHT // 2 - text.get_height() // 2))

SWITCH_BG_X = (WIDTH - BUTTON_WIDTH) // 2
SWITCH_BG_Y = (200 - BUTTON_HEIGHT) // 2


SWITCH_CUBE_X = (WIDTH - BUTTON_WIDTH) // 2
SWITCH_CUBE_Y = (400 - BUTTON_HEIGHT) // 2

CLOSE_X = (WIDTH - BUTTON_WIDTH) // 2
CLOSE_Y = (600 - BUTTON_HEIGHT) // 2

SWITCH_LIGHTING_X = (WIDTH - BUTTON_WIDTH) // 2
SWITCH_LIGHTING_Y = (800 - BUTTON_HEIGHT) // 2




LIGHT_MODE_X = (WIDTH - BUTTON_WIDTH) // 2
LIGHT_MODE_Y = (1000 - BUTTON_HEIGHT) // 2

LIGHT_MOVEMENT_X = (WIDTH - BUTTON_WIDTH) // 2
LIGHT_MOVEMENT_Y = (1200 - BUTTON_HEIGHT) // 2

LIGHT_COLOR_X = (WIDTH - BUTTON_WIDTH) // 2
LIGHT_COLOR_Y = (1400 - BUTTON_HEIGHT) // 2

WIDTH, HEIGHT = 400, 800
screen = None

CUBE_STATES = [
    'regular',
    'multi',
    'moving',
    'glitchy'
]

BACKGROUND_STATES = [
    'squares',
    'particles',
    'circles',
    'waveform',
    'triangles',
    'tunnel'
]

LIGHTING_MODES = [
    'on',
    'off',
    'strobe'
]
    
LIGHTING_MOVEMENTS = [
    'none',
    'only_left',
    'only_right'
]
    
LIGHTING_COLORS = [
    'white',
    'red'
]



# def draw_button(pygame, screen, text, x, y):
#     mouse = pygame.mouse.get_pos()
#     if x < mouse[0] < x + BUTTON_WIDTH and y < mouse[1] < y + BUTTON_HEIGHT:
#         pygame.draw.rect(screen, DARK_RED, (x, y, BUTTON_WIDTH, BUTTON_HEIGHT))
#     else:
#         pygame.draw.rect(screen, RED, (x, y, BUTTON_WIDTH, BUTTON_HEIGHT))

#     screen.blit(text, (x + BUTTON_WIDTH//2 - text.get_width()//2, y + BUTTON_HEIGHT//2 - text.get_height()//2))

# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == QUIT:
#             running = False
#         elif event.type == MOUSEBUTTONDOWN:
#             mouse = pygame.mouse.get_pos()
#             if BUTTON_X < mouse[0] < BUTTON_X + BUTTON_WIDTH and BUTTON_Y < mouse[1] < BUTTON_Y + BUTTON_HEIGHT:
#                 print("Button clicked!")

#     screen.fill(WHITE)
#     draw_button()
#     pygame.display.flip()

class ControllerScreen:
    def __init__(self):
        pygame.init()
        self.pygame = pygame

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Visuals Controller')

        self.font = pygame.font.Font(None, 24)

        self.light_mode = self.font.render('L-Mode', True, WHITE)
        self.light_movement = self.font.render('L-Move', True, WHITE)
        self.light_color = self.font.render('L-Color', True, WHITE)

        self.pressed = False
        self.closed = False

    def render(self, visuals_state, lighting_state):
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
                'moving': 83,
                'glitchy': 84
            },
            'background': {
                'squares': 71,
                'particles': 72,
                'circles': 73,
                'waveform': 74,
                'triangles': 61,
                'tunnel': 62,
                'black': 63,
                'plane': 64
            },
            'mode': {
                'on': 51,
                'off': 52,
                'strobe': 53,
                'wash': 54
            },
            'movement': {
                'all': 41,
                'left': 42,
                'right': 43,
                'front': 44,
                'ltr': 31,
                'rtl': 32,
                'ftb': 33,
                'btf': 34
            },
            'color': {
                'white': 21,
                'red': 22,
                'green': 23,
                'blue': 24
            },
            'speed': {
                'slow': 11,
                'med': 12,
                'fast': 13,
                'vfast': 14
            }
        }

        for event in self.pygame.event.get():
            if event.type == QUIT:
                self.closed = True
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
                #     cur_background_index = BACKGROUND_STATES.index(visuals_state['background'])
                #     if cur_background_index == len(BACKGROUND_STATES) - 1:
                #         visuals_state['background'] = BACKGROUND_STATES[0]
                #     else:
                #         visuals_state['background'] = BACKGROUND_STATES[cur_background_index + 1]

                # if CLOSE_X < mouse[0] < CLOSE_X + BUTTON_WIDTH and CLOSE_Y < mouse[1] < CLOSE_Y + BUTTON_HEIGHT:
                #     print('closing app...')
                #     self.closed = True

                # if SWITCH_LIGHTING_X < mouse[0] < SWITCH_LIGHTING_X + BUTTON_WIDTH and SWITCH_LIGHTING_Y < mouse[1] < SWITCH_LIGHTING_Y + BUTTON_HEIGHT:
                #     print('switching lighting')
                #     self.pressed = not self.pressed

                # if LIGHT_MODE_X < mouse[0] < LIGHT_MODE_X + BUTTON_WIDTH and LIGHT_MODE_Y < mouse[1] < LIGHT_MODE_Y + BUTTON_HEIGHT:
                #     print('switching light mode')
                #     cur_mode_index = LIGHTING_MODES.index(lighting_state['mode'])
                #     if cur_mode_index == len(LIGHTING_MODES) - 1:
                #         lighting_state['background'] = LIGHTING_MODES[0]
                #     else:
                #         lighting_state['background'] = LIGHTING_MODES[cur_mode_index + 1]


        # self.screen.fill(WHITE)
        # # draw_button(pygame=self.pygame, screen=self.screen, text=self.text, x=BUTTON_X, y=BUTTON_Y)
        # # switch cube
        # draw_button(pygame=self.pygame, screen=self.screen, text=self.switch_cube_text, x=SWITCH_CUBE_X, y=SWITCH_CUBE_Y)

        # # switch bg
        # draw_button(pygame=self.pygame, screen=self.screen, text=self.switch_bg_text, x=SWITCH_BG_X, y=SWITCH_BG_Y)

        
        # # close button
        # draw_button(pygame=self.pygame, screen=self.screen, text=self.close_text, x=CLOSE_X, y=CLOSE_Y)
        
        # # lighting button
        # draw_button(pygame=self.pygame, screen=self.screen, text=self.lighting_text, x=SWITCH_LIGHTING_X, y=SWITCH_LIGHTING_Y)

        # # lighting mode
        # draw_button(pygame=self.pygame, screen=self.screen, text=self.light_mode, x=LIGHT_MODE_X, y=LIGHT_MODE_Y)

        self.pygame.display.flip()

    def switch_pressed(self):
        return self.pressed
    
    def close_pressed(self):
        return self.closed
    
    def close(self):
        pygame.quit()
