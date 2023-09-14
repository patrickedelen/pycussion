import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (0, 0, 0)
TEXT_COLOR = (50, 200, 50)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Random Code Background")

# Load a font
font = pygame.font.SysFont("monospace", 15)

# Generate random code text
def generate_random_code():
    # Here's a simple random code generator. You can enhance this to make it look more like code.
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789{}();"
    return ''.join(random.choice(chars) for _ in range(random.randint(5, 100)))

def create_text_texture(text, font, color=(255, 255, 255)):
    # Render the text using Pygame
    text_surface = font.render(text, True, color)
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    
    # Create an OpenGL texture
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_surface.get_width(), text_surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    return texture_id, text_surface.get_width(), text_surface.get_height()

def render_text_in_3d(text_texture, width, height, position=(0, 0, -2)):
    x, y, z = position
    glBindTexture(GL_TEXTURE_2D, text_texture)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1); glVertex3f(x - width/2, y - height/2, z)
    glTexCoord2f(1, 1); glVertex3f(x + width/2, y - height/2, z)
    glTexCoord2f(1, 0); glVertex3f(x + width/2, y + height/2, z)
    glTexCoord2f(0, 0); glVertex3f(x - width/2, y + height/2, z)
    glEnd()

# List to store rendered text surfaces and their positions
texts = []

# Main loop
running = True
clock = pygame.time.Clock()
while running:
    screen.fill(BACKGROUND_COLOR)

    # Add new random code text to the top of the screen
    if random.random() < 0.2:
        new_text_surface = font.render(generate_random_code(), True, TEXT_COLOR)
        texts.append([new_text_surface, new_text_surface.get_rect(topleft=(random.randint(0, 50), 0))])

        for text_surface, rect in texts:
            # screen.blit(text_surface, rect.topleft)
            rect.move_ip(0, 30)  # Move downward by 1 pixel
    
    # Draw and move each text downward
    for text_surface, rect in texts:
        screen.blit(text_surface, rect.topleft)
        # rect.move_ip(0, 20)  # Move downward by 1 pixel

    # Remove texts that are off the screen
    texts = [t for t in texts if t[1].top < HEIGHT]
    
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    clock.tick(60)  # 60 frames per second

    """
        # Set up your OpenGL context here (camera, lighting, etc.)

        font = pygame.font.SysFont("monospace", 30)
        text_texture, text_width, text_height = create_text_texture("Your 3D Text Here", font)

        # In your main render loop:
        render_text_in_3d(text_texture, text_width, text_height)
    """

pygame.quit()
