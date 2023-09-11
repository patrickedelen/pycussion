import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

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



class CubeRenderer:
    def __init__(self):
        self.cur_rotate = 0

        self.trigger_time = time.time() - 10
        self.pos_x = 5
        self.pos_y = 5

    def render_regular_cube(self, magnitude, rotate=0.3, scale=0.5):

        glDisable(GL_LIGHTING)


        scale_factor = magnitude + scale
        glPushMatrix()
        glTranslatef(0, 0, 0)  # Translate to the origin
        glScalef(scale_factor, scale_factor, scale_factor)  # Scale the cube
        glTranslatef(0, 0, 0)  # Translate back to the original position

        self.cur_rotate = self.cur_rotate + rotate
        if self.cur_rotate == 360:
            self.cur_rotate = 0

        glRotatef(self.cur_rotate, 1, 1, 1)
        # glRotatef(90, 1, 1, 1)


        # Set material properties
        material_diffuse = [0.45, 0.45, 0.45, 1.0]  # White material
        material_specular = [0.0,0.0,0.0, 1.0]  # Specular reflection
        material_shininess = [20.0]  # Shininess

        glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

        # Draw the cube
        glColor3f(0.3,0.3,0.3)
        glBegin(GL_QUADS)
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()

        # Set material properties
        material_diffuse = [0.0, 0.0, 0.0, 1.0]  # White material
        material_specular = [0.0,0.0,0.0, 1.0]  # Specular reflection
        material_shininess = [50.0]  # Shininess

        glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)


        glColor3f(0,0,0)
        glBegin(GL_LINES)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()

        glPopMatrix()

    def render_multi_cube(self, magnitude):
        cube_distance = 2.5  # Adjust as necessary for spacing between cubes
        
        # Loop over 2 rows
        for i in range(2):
            # Loop over 3 columns
            for j in range(3):
                x_position = (j - 1) * cube_distance  # The "-1" centers the cubes around the origin in X-axis
                y_position = (i - 0.5) * cube_distance  # The "-0.5" centers the cubes around the origin in Y-axis
                
                glPushMatrix()
                glTranslatef(x_position, y_position, 0)
                self.render_regular_cube(magnitude=magnitude * 0.5, rotate=0.1, scale=0.2)
                glPopMatrix()

    def render_random_cube(self, magnitude):
        cur_time = time.time()

        if cur_time - self.trigger_time >= 1:
            self.pos_x = (random.random() - 0.5) * 5
            self.pos_y = (random.random() - 0.5) * 3

            self.trigger_time = time.time()

        glPushMatrix()
        glTranslate(self.pos_x, self.pos_y, 0)
        self.render_regular_cube(magnitude=magnitude, rotate=0.3, scale=0.4)
        glPopMatrix()
