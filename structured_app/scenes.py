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


class SceneRenderer:
    def __init__(self):
        self.cur_rotate = 0

    def render_plane(self, magnitude=0, onset_triggered=False, second_buffer=[]):

        second_data = np.frombuffer(second_buffer.get_obj(), dtype=np.float32)


        material_diffuse = [1.0, 1.0, 1.0, 1.0]  # White material
        material_specular = [1.0, 1.0, 1.0, 1.0]  # No specular reflection
        material_shininess = [50.0]  # No shininess

        glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

        glPushMatrix()
        glDisable(GL_LIGHTING)

        self.cur_rotate = self.cur_rotate + 0.5 + magnitude * 2
        if self.cur_rotate == 1440:
            self.cur_rotate = 0

        glRotatef(self.cur_rotate / 4, 1, 1, 1)

        # Draw the particles
        glColor3f(0.3,0.3,0.3)
        glPointSize(3)
        glBegin(GL_POINTS)

        scaler = 5

        # particle cube
        # for x in range(32):
        #     for y in range(32):
        #         for z in range(32):
        #             if x % 4 and y % 4 and z % 4:
        #                 x_val = (x / 32 - 0.5) * 5 + ((second_data[x * y * z] - 0.5) * 5)
        #                 y_val = (y / 32 - 0.5) * 5 + ((second_data[x * y * z] - 0.5) * 5)
        #                 z_val = (z / 32 - 0.5) * 5 + ((second_data[x * y * z] - 0.5) * 5)
        #                 glVertex3f(x_val, y_val, z_val)

        for x in range(256):
            for y in range(128):
                if x % 5 == 0:
                    x_val = (x / 256 - 0.5) * 5
                    y_val = (y / 64 - 0.75) * 5
                    glVertex3f(x_val, y_val, second_data[x * y] * 10)
        glEnd()

        glPopMatrix()
