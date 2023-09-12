import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
from PIL import Image

import pyaudio
import struct
import sys
import json
import time
from multiprocessing import Process, Value, Array
import multiprocessing as mp

import random
import numpy as np
from collections import deque

from cube import CubeRenderer
from scenes import SceneRenderer

CUBE_STATES = [
    'regular',
    'multi',
    'random',
    'glitchy'
]

BACKGROUND_STATES = [
    'squares',
    'particles',
    'circles'
]


# Define the vertices and edges for a cube
vertices = [
    [1, 1, -1], [1, -1, -1], [-1, -1, -1], [-1, 1, -1],
    [1, 1, 1], [1, -1, 1], [-1, -1, 1], [-1, 1, 1]
]
edges = [
    [0, 1], [1, 2], [2, 3], [3, 0],
    [0, 4], [4, 5], [5, 6], [6, 7],
    [7, 4], [7, 3], [6, 2], [5, 1]
]

faces = [
    [0, 1, 2, 3],  # Front face
    [4, 5, 6, 7],  # Back face
    [0, 4, 5, 1],  # Bottom face (changed)
    [2, 6, 7, 3],  # Top face (changed)
    [0, 3, 7, 4],  # Left face
    [1, 2, 6, 5]   # Right face
]

# Define light properties
light_position = [0.0, -10.0, 0.0, 1.0]  # Position at the bottom
light_2_position = [0.0, 10.0, 0.0, 1.0]  # Position at the top
light_diffuse = [1.0, 1.0, 1.0, 1.0]  # White light

class Triangle:
    def __init__(self, vertices, direction):
        self.vertices = vertices  # A 3x2 numpy array containing triangle vertices
        self.direction = direction  # A 2-element numpy array containing x and y direction


class Visuals():
    def __init__(self):
        self.cur_rotate = 1

        self.bg_rotate = 365.0

        # Initialize Pygame
        pygame.init()

        # Set the display mode with the OPENGL flag
        # set to fullscreen here by adding to mode options
        # pygame.FULLSCREEN |

        display = (1920, 1080)
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

        # Set the perspective for the camera
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -8)

        # Enable lighting
        glEnable(GL_LIGHTING)

        # Enable light source 0
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)

        glEnable(GL_DEPTH_TEST)

        self.scale_factor = 1

        self.scene = 'plane'

        self.scenes = ['plane', 'cube', 'squares', 'circles', 'waveform']

        self.squares = []
        self.updates = 0

        # self.triangle_verts = np.array([[400, 100], [100, 700], [700, 700]])
        self.triangle_verts = np.array([[0, -0.5], [-0.5, 0.5], [0.5, 0.5]])

        self.num_circles = 50
        self.points = np.random.rand(self.num_circles, 2) * 10 - 5 # 2D random points in 5x5 space

        self.cur_rotate

        self.circles = np.random.rand(self.num_circles, 2) * 10 - 5 # Initial random positions in a 5x5 space
        self.radius = np.zeros(self.num_circles)  # Initial radius for each circle
        self.speeds = (np.random.rand(self.num_circles, 2) - 0.5) * 0.1  # Random speeds for x and y movement

        self.particles = []
        for _ in range(400):
            self.particles.append([random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10)])


        self.cr = CubeRenderer()
        self.sr = SceneRenderer()

        self.triangles = []

    def render_triangle_bg(self, magnitude):
        # Parameters for triangle generation
        triangle_base_size = 0.5
        
        # Generate triangles
        if magnitude > 0.25 and random.random() > 0.5:
            # Generate triangle vertices around the center with some random offset
            offset = (np.random.rand(3, 2) - 0.5) * triangle_base_size
            triangle_verts = self.triangle_verts + offset

            # Assign random direction for triangle movement
            direction = (np.random.rand(2) - 0.5) * 0.3  # Random direction in x and y
            self.triangles.append(Triangle(triangle_verts, direction))
            
        # Update triangle positions and remove triangles out of viewport
        new_triangles = []
        for triangle in self.triangles:
            triangle.vertices += triangle.direction * (magnitude * 0.5 + 0.25)
            # Check if triangle is still in viewport (assuming viewport size is 10x10 units)
            if np.any(triangle.vertices[:, 0] > 10) or np.any(triangle.vertices[:, 0] < -10) or \
            np.any(triangle.vertices[:, 1] > 10) or np.any(triangle.vertices[:, 1] < -10):
                continue
            new_triangles.append(triangle)
        self.triangles = new_triangles
        
        # Render triangles
        glPushMatrix()
        glDisable(GL_LIGHTING)
        glLineWidth(4)
        for triangle in self.triangles:
            glBegin(GL_LINE_LOOP)
            glColor3f(0.3, 0.3, 0.3)  # Triangle color
            for vertex in triangle.vertices:
                glVertex3f(vertex[0], vertex[1], 0)
            glEnd()
        glPopMatrix()


    def render_square_bg(self, magnitude):
        
        glPushMatrix()
        
        # Set light properties
        # glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 1.0, 0.0])
        # glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        
        # glLightfv(GL_LIGHT1, GL_POSITION, light_2_position)
        # glLightfv(GL_LIGHT1, GL_DIFFUSE, light_diffuse)
        
        glDisable(GL_LIGHTING)
        # glDisable(GL_LIGHT1)

        material_diffuse = [0.45, 0.08, 0.07, 1.0]  # White material
        material_specular = [0.0,0.0,0.0, 1.0]  # Specular reflection
        material_shininess = [20.0]  # Shininess

        glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

        # Control speed of rotation
        # speed = self.avg.average()
        # speed = magnitude * 0.05 + 0.01
        speed = 0.2 * magnitude + 0.01

        # Update current rotation angle
        self.bg_rotate -= speed
        if self.bg_rotate <= 0.0:
            self.bg_rotate = 360.0
        
        # Rotate the squares along the Z-axis
        glRotatef(self.bg_rotate, 0, 0, 1)
        
        # Create squares
        num_squares = 10  # Number of squares to be drawn
        square_size = 0.2  # Initial size of the smallest square
        square_growth = 0.2  # Growth rate of squares

        # Set material properties
        # material_diffuse = [1.0, 1.0, 1.0, 1.0]  # White material
        # material_specular = [1.0, 1.0, 1.0, 1.0]  # No specular reflection
        # material_shininess = [50.0]  # No shininess

        # glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
        # glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
        # glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

        factor = magnitude * 0.2
        # print('factor', factor)

        if len(self.squares) > 0 and self.squares[-1] > 5 and factor > 0.1:
            # self.updates = 0
            self.squares.append(0.1)
            # print('adding square', self.squares)
        elif len(self.squares) == 0:
            # self.updates += 1
            self.squares.append(0.2)
        elif self.squares[-1] > 10:
            self.squares.append(0.1)
            
        # print('got average', self.avg.average())
        self.squares = [i + factor + 0.05 for i in self.squares if i < 50]
        
        
        glLineWidth(3)
        for i in self.squares:
            glBegin(GL_LINE_LOOP)  # Draw only the perimeter
            glColor3f(0.3,0.3,0.3)
            size = square_size + i * square_growth
            
            glVertex3f(-size, -size, 0)
            glVertex3f( size, -size, 0)
            glVertex3f( size,  size, 0)
            glVertex3f(-size,  size, 0)
            
            glEnd()
        
        glPopMatrix()

    def render_particle_bg(self, magnitude):
        # Set material properties
        material_diffuse = [1.0, 1.0, 1.0, 1.0]  # White material
        material_specular = [1.0, 1.0, 1.0, 1.0]  # No specular reflection
        material_shininess = [50.0]  # No shininess

        glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

        glPushMatrix()

        # Set light properties
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)

        glLightfv(GL_LIGHT1, GL_POSITION, light_2_position)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, light_diffuse)



        # Draw the particles
        glColor3f(0.6,0.6,0.6)
        glPointSize(5)
        glBegin(GL_POINTS)
        for particle in self.particles:
            glVertex3fv(particle)
        glEnd()

        # Update the particle positions to move down the screen
        particle_speed_factor = 0.01 + (magnitude - 0.5) * 0.5
        for particle in self.particles:
            particle[1] -= particle_speed_factor
            if particle[1] < -10 or particle[1] > 10:
                particle[1] = random.uniform(-10, 10)


        glPopMatrix()

    def render_circles(self, magnitude=0, onset_triggered=False, shared_memory=[]):
        
        self.circles += self.speeds

        out_of_bounds = np.logical_or(self.circles < -5, self.circles > 5)
        respawn_indices = np.any(out_of_bounds, axis=1)
        self.circles[respawn_indices] = np.random.rand(np.sum(respawn_indices), 2) * 10 - 5

        # Assuming shared_memory is still used, though the function does not seem to do much with it
        # second_data = np.frombuffer(shared_memory.get_obj(), dtype=np.float32) if shared_memory else []

        # Lighting settings remain unchanged
        material_diffuse = [1.0, 1.0, 1.0, 1.0]  # White material
        material_specular = [1.0, 1.0, 1.0, 1.0]  # No specular reflection
        material_shininess = [50.0]  # No shininess

        # magnitude *= 20

        self.radius = 0.9 * self.radius + 0.2 * magnitude * 2

        glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

        glPushMatrix()
        glDisable(GL_LIGHTING)
        # self.cur_rotate = (self.cur_rotate + 1) % 1440
        # glRotatef(self.cur_rotate / 4, 1, 1, 1)

        glColor3f(0.3, 0.3, 0.3)

        for point, r in zip(self.circles, self.radius):
            x, y = point
            self.draw_circle(x, y, r)  # Draw the circle # Draw the circle

        glPopMatrix()

    def draw_circle(self, x, y, r):
        num_segments = 100  # Number of line segments for the circle
        glLineWidth(3)
        glBegin(GL_LINE_LOOP)
        for i in range(num_segments):
            theta = 2.0 * 3.1415926 * float(i) / float(num_segments)  # Current angle
            dx = r * np.cos(theta)
            dy = r * np.sin(theta)
            glVertex2f(x + dx, y + dy)
        glEnd()

    def render_waveform(self, magnitude, second_buffer):
        # Assuming shared_memory is still used to get the waveform data
        waveform_data = np.frombuffer(second_buffer.get_obj(), dtype=np.float32)

        material_diffuse = [1.0, 1.0, 1.0, 1.0]  # White material
        material_specular = [1.0, 1.0, 1.0, 1.0]  # No specular reflection
        material_shininess = [50.0]  # No shininess

        glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

        glPushMatrix()
        glDisable(GL_LIGHTING)

        # self.cur_rotate = (self.cur_rotate + 1) % 1440
        # glRotatef(self.cur_rotate / 4, 1, 1, 1)

        glColor3f(0.3, 0.3, 0.3)

        # Draw the waveform
        glLineWidth(3)
        glBegin(GL_LINE_STRIP)

        # print('cur magnitude', magnitude)

        # We'll skip some data points for performance and clarity in visualization
        skip = len(waveform_data) // 512

        # magnitude = min(max(self.avg.average() * 40, 1), 2)

        for i in range(0, len(waveform_data), skip):
            x_val = ((i / len(waveform_data) - 0.5) * 15)
            y_val = (((waveform_data[i] - 0.5) * 8) + 4)
            glVertex2f(x_val, y_val)

        glEnd()

        glPopMatrix()


    def render(self, magnitude=0.5, magnitude_mid=0.5, switch=False, visuals_state={'cube': 'regular', 'background': 'squares'}, second_buffer=None):
        # print('got visuals render request')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    cur_index = self.scenes.index(self.scene)
                    cur_index += 1
                    if cur_index == len(self.scenes):
                        cur_index = 0
                    self.scene = self.scenes[cur_index]

        
        glClearColor(0,0,0,1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        cube_state = visuals_state['cube']
        background_state = visuals_state['background']

        match cube_state:
            case 'regular':
                self.cr.render_regular_cube(magnitude=magnitude)
            case 'multi':
                self.cr.render_multi_cube(magnitude=magnitude)
            case 'random':
                self.cr.render_random_cube(magnitude=magnitude)
            case 'glitchy':
                self.cr.render_glitchy_cube(magnitude=magnitude)

        self.render_triangle_bg(magnitude=magnitude)

        # match background_state:
        #     case 'squares':
        #         self.render_square_bg(magnitude=magnitude_mid)
        #     case 'particles':
        #         self.render_particle_bg(magnitude=magnitude_mid)
        #     case 'circles':
        #         self.render_circles(magnitude=magnitude_mid)
        #     case 'waveform':
        #         self.render_waveform(magnitude=magnitude, second_buffer=second_buffer)

        # self.sr.render_plane(magnitude=magnitude, onset_triggered=False, second_buffer=second_buffer)
        


        # if switch:
        #     self.render_square_bg(magnitude=magnitude_mid)
        # else:
        #     self.render_circles(magnitude=magnitude_mid)

        # # self.render_cube(magnitude=magnitude)
        # # self.cr.render_regular_cube(magnitude=magnitude)
        # self.cr.render_multi_cube(magnitude=magnitude)
        # # self.cr.render_random_cube(magnitude=magnitude)

        pygame.display.flip()

    def close(self):
        pygame.quit()