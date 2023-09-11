import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import gluOrtho2D
import numpy as np
import pyaudio

# PyAudio setup
RATE = 44100
BUFFER_SIZE = 512
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paFloat32,
    channels=1,
    rate=RATE,
    input=True,
    input_device_index=4,
    frames_per_buffer=BUFFER_SIZE
)

# Pygame setup
pygame.init()
display = (800, 800)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
gluOrtho2D(0, 800, 0, 800)

def draw_fft_bars(fft_magnitudes):
    bin_width = display[0] / len(fft_magnitudes)
    for index, magnitude in enumerate(fft_magnitudes):
        x = index * bin_width
        glColor3f(0.0, 0.5, 1.0)  # Set color to blue
        glBegin(GL_QUADS)  # Drawing rectangles
        glVertex2f(x, 0)
        glVertex2f(x + bin_width, 0)
        glVertex2f(x + bin_width, magnitude * 3000)  # Scale the magnitude for better visualization
        glVertex2f(x, magnitude * 3000)
        glEnd()

previous_fft_magnitudes = np.zeros(BUFFER_SIZE // 2)

# def db_scale(magnitude):
#     """Convert magnitude to decibel scale."""
#     magnitude = np.abs(magnitude)
#     magnitude = np.where(magnitude == 0, 1e-7, magnitude)  # Avoid log(0)
#     return 10 * np.log10(magnitude)

# def draw_fft_line(fft_magnitudes):
#     global previous_fft_magnitudes

#     fft_magnitudes = db_scale(fft_magnitudes)

#     # Interpolation between previous and current magnitudes
#     alpha = 0.2  # Interpolation factor (adjust for more/less smoothing)
#     fft_magnitudes = alpha * fft_magnitudes + (1 - alpha) * previous_fft_magnitudes
#     previous_fft_magnitudes = fft_magnitudes

#     bin_width = display[0] / (2 * len(fft_magnitudes))  # Only half the window width since we're drawing symmetrically
#     glColor3f(0.0, 0.5, 1.0)  # Set color to blue

#     # Draw left side (low frequencies to high)
#     glBegin(GL_LINE_STRIP)
#     for index, magnitude in enumerate(fft_magnitudes):
#         x = display[0] / 2 - (index * bin_width)  # Start from the center and move leftwards
#         y = display[1] / 2 + magnitude * 10  # Center vertically and adjust with magnitude
#         glVertex2f(x, y)
#     glEnd()

#     # Draw right side (low frequencies to high)
#     glBegin(GL_LINE_STRIP)
#     for index, magnitude in enumerate(fft_magnitudes):
#         x = display[0] / 2 + (index * bin_width)  # Start from the center and move rightwards
#         y = display[1] / 2 + magnitude * 10  # Center vertically and adjust with magnitude
#         glVertex2f(x, y)
#     glEnd()

def db_scale(magnitude):
    """Convert magnitude to decibel scale."""
    magnitude = np.abs(magnitude)
    magnitude = np.where(magnitude == 0, 1e-7, magnitude)  # Avoid log(0)
    return 10 * np.log10(magnitude)

def draw_fft_line(fft_magnitudes):
    global previous_fft_magnitudes

    # Convert magnitudes to decibel scale
    fft_magnitudes = db_scale(fft_magnitudes)

    # Interpolation between previous and current magnitudes
    alpha = 0.2
    fft_magnitudes = alpha * fft_magnitudes + (1 - alpha) * previous_fft_magnitudes
    previous_fft_magnitudes = fft_magnitudes

    bin_width = display[0] / len(fft_magnitudes)
    glColor3f(0.6, 0.6, 0.6)  # Set color to blue

    # Draw left side (low frequencies to high)
    glBegin(GL_LINE_STRIP)
    for index, magnitude in enumerate(fft_magnitudes):
        x = display[0] / 2 - (index * bin_width)
        y = display[1] / 2 + magnitude * 10  # Adjust scaling factor as needed
        glVertex2f(x, y)
    glEnd()

    # Draw right side (low frequencies to high)
    glBegin(GL_LINE_STRIP)
    for index, magnitude in enumerate(fft_magnitudes):
        x = display[0] / 2 + (index * bin_width)
        y = display[1] / 2 + magnitude * 10 # Adjust scaling factor as needed
        glVertex2f(x, y)
    glEnd()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            stream.stop_stream()
            stream.close()
            p.terminate()
            quit()

    audio_data = stream.read(BUFFER_SIZE, exception_on_overflow=False)
    audio_data = np.frombuffer(audio_data, dtype=np.float32)
    fft_values = np.fft.rfft(audio_data)
    fft_magnitudes = np.abs(fft_values)[:BUFFER_SIZE // 2]  # Only take the positive frequency components

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_fft_line(fft_magnitudes)

    pygame.display.flip()
    pygame.time.wait(16)  # ~60 frames per second
