import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN

# from app import CUBE_STATES, BACKGROUND_STATES

# Initialize pygame
# pygame.init()

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)

RED = (255, 0, 0)
DARK_RED = (200, 0, 0)

# Screen dimensions
WIDTH = 400
HEIGHT = 600

# Button dimensions and position
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
BUTTON_X = (WIDTH - BUTTON_WIDTH) // 2
BUTTON_Y = (200 - BUTTON_HEIGHT) // 2

SWITCH_BG_X = (WIDTH - BUTTON_WIDTH) // 2
SWITCH_BG_Y = (200 - BUTTON_HEIGHT) // 2


SWITCH_CUBE_X = (WIDTH - BUTTON_WIDTH) // 2
SWITCH_CUBE_Y = (400 - BUTTON_HEIGHT) // 2

SWITCH_LIGHTING_X = (WIDTH - BUTTON_WIDTH) // 2
SWITCH_LIGHTING_Y = (800 - BUTTON_HEIGHT) // 2


CLOSE_X = (WIDTH - BUTTON_WIDTH) // 2
CLOSE_Y = (600 - BUTTON_HEIGHT) // 2


WIDTH, HEIGHT = 400, 600
screen = None

CUBE_STATES = [
    'regular',
    'multi',
    'random',
    'glitchy'
]

BACKGROUND_STATES = [
    'squares',
    'particles',
    'circles',
    'waveform',
    'triangles'
]



def draw_button(pygame, screen, text, x, y):
    mouse = pygame.mouse.get_pos()
    if x < mouse[0] < x + BUTTON_WIDTH and y < mouse[1] < y + BUTTON_HEIGHT:
        pygame.draw.rect(screen, DARK_RED, (x, y, BUTTON_WIDTH, BUTTON_HEIGHT))
    else:
        pygame.draw.rect(screen, RED, (x, y, BUTTON_WIDTH, BUTTON_HEIGHT))

    screen.blit(text, (x + BUTTON_WIDTH//2 - text.get_width()//2, y + BUTTON_HEIGHT//2 - text.get_height()//2))

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

        self.font = pygame.font.Font(None, 36)
        self.text = self.font.render('Click me', True, WHITE)

        self.switch_cube_text = self.font.render('Cube +', True, WHITE)
        self.switch_bg_text = self.font.render('BG +', True, WHITE)
        self.lighting_text = self.font.render('LIGHT +', True, WHITE)

        self.close_text = self.font.render('Close', True, WHITE)

        self.pressed = False

        self.closed = False

    def render(self, visuals_state):
        for event in self.pygame.event.get():
            if event.type == QUIT:
                # running = False
                pygame.quit()
            elif event.type == MOUSEBUTTONDOWN:
                mouse = self.pygame.mouse.get_pos()
                # if BUTTON_X < mouse[0] < BUTTON_X + BUTTON_WIDTH and BUTTON_Y < mouse[1] < BUTTON_Y + BUTTON_HEIGHT:
                #     print("Button clicked!")
                #     self.pressed = not self.pressed

                if SWITCH_CUBE_X < mouse[0] < SWITCH_CUBE_X + BUTTON_WIDTH and SWITCH_CUBE_Y < mouse[1] < SWITCH_CUBE_Y + BUTTON_HEIGHT:
                    print("switching cube...")
                    cur_cube_index = CUBE_STATES.index(visuals_state['cube'])
                    if cur_cube_index == len(CUBE_STATES) - 1:
                        visuals_state['cube'] = CUBE_STATES[0]
                    else:
                        visuals_state['cube'] = CUBE_STATES[cur_cube_index + 1]


                if SWITCH_BG_X < mouse[0] < SWITCH_BG_X + BUTTON_WIDTH and SWITCH_BG_Y < mouse[1] < SWITCH_BG_Y + BUTTON_HEIGHT:
                    print("switching bg...")

                    cur_background_index = BACKGROUND_STATES.index(visuals_state['background'])
                    if cur_background_index == len(BACKGROUND_STATES) - 1:
                        visuals_state['background'] = BACKGROUND_STATES[0]
                    else:
                        visuals_state['background'] = BACKGROUND_STATES[cur_background_index + 1]

                if CLOSE_X < mouse[0] < CLOSE_X + BUTTON_WIDTH and CLOSE_Y < mouse[1] < CLOSE_Y + BUTTON_HEIGHT:
                    print('closing app...')
                    self.closed = True

                if SWITCH_LIGHTING_X < mouse[0] < SWITCH_LIGHTING_X + BUTTON_WIDTH and SWITCH_LIGHTING_Y < mouse[1] < SWITCH_LIGHTING_Y + BUTTON_HEIGHT:
                    print('switching lighting')
                    self.pressed = not self.pressed


        self.screen.fill(WHITE)
        # draw_button(pygame=self.pygame, screen=self.screen, text=self.text, x=BUTTON_X, y=BUTTON_Y)
        # switch cube
        draw_button(pygame=self.pygame, screen=self.screen, text=self.switch_cube_text, x=SWITCH_CUBE_X, y=SWITCH_CUBE_Y)

        # switch bg
        draw_button(pygame=self.pygame, screen=self.screen, text=self.switch_bg_text, x=SWITCH_BG_X, y=SWITCH_BG_Y)

        
        # close button
        draw_button(pygame=self.pygame, screen=self.screen, text=self.close_text, x=CLOSE_X, y=CLOSE_Y)
        
        # lighting button
        draw_button(pygame=self.pygame, screen=self.screen, text=self.lighting_text, x=SWITCH_LIGHTING_X, y=SWITCH_LIGHTING_Y)

        self.pygame.display.flip()

    def switch_pressed(self):
        return self.pressed
    
    def close_pressed(self):
        return self.closed
    
    def close(self):
        pygame.quit()

