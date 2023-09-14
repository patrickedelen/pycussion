"""
multiprocessing base, import other packages from here


shared data:
- close app
- app state: cube scene, background scene, override for 3d scene
    - controller should set these, game processor handles rendering
- audio magnitude: processor should handle averaging, magnitudes for low, mid, high, overall
- kick onset detection: game loop should ack this and set to false
- different kick onset for lighting
- color scheme from controller
- current bpm / start of beat based on manual input

undecided
- lighting fixtures list: show in controller
- lighting mode: tbd

main game loop
- render 3d scene override
- render background first
- render cube after

controller loop
- render ui for selecting scenes

lighting loop
- get current magnitude, onset
- get current lighting mode from controller

"""

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

from audio_processing import AudioProcessor
from controller import ControllerScreen
from visuals import Visuals
from launchpad import LaunchPadController
from lighting import Lighting


CUBE_STATES = [
    'regular',
    'multi',
    'random'
]

BACKGROUND_STATES = [
    'squares',
    'particles',
    'circles'
]


def audio_check_loop(magnitude, onset_triggered, shared_memory, magnitude_mid, close):
    audio_controller = AudioProcessor(shared_memory)

    while True:
        if close.value:
            print('closing audio')
            audio_controller.close()
            exit(0)

        audio_controller.update_data()
        magnitude.value = audio_controller.get_magnitude()
        magnitude_mid.value = audio_controller.get_magnitude_mid()
        time.sleep(0.001)

        # if random.random() < 0.2:
        #     print('magnitude', magnitude.value)
        # print('mag', magnitude.value)
        # print('magnitude', magnitude.value)
        # onset_triggered.value = audio_controller.get_onset()
        # second_data.value = audio_controller.get_buffer()

def visuals_render_loop(magnitude, onset_triggered, shared_memory, magnitude_mid, switch, close, visuals_state):
    visuals = Visuals()

    print('test')

    while True:
        if close.value:
            print('closing visuals')
            visuals.close()
            exit(0)

        visuals.render(magnitude=magnitude.value, magnitude_mid=magnitude_mid.value, switch=switch.value, visuals_state=visuals_state, second_buffer=shared_memory)
    # if random.random() < 0.05:
        # print('got magnitude', magnitude.value)
        time.sleep(0.0016)

def controller_render_loop(magnitude, onset_triggered, shared_memory, magnitude_mid, switch, close, visuals_state):
    controller = ControllerScreen()
    while True:
        controller.render(visuals_state)
        switch.value = controller.switch_pressed()
        close.value = controller.close_pressed()

        if close.value:
            controller.close()
            time.sleep(0.5)
            exit(0)

        time.sleep(0.016)

def lighting_render_loop(magnitude, onset_triggered, shared_memory, magnitude_mid, switch, close):
    lighting = Lighting()

    while True:
        if close.value:
            print('closing lighting')
            lighting.close()
            exit(0)

        lighting.render(magnitude=magnitude.value, close=close.value, switch=switch.value)
        time.sleep(0.05)

def launchpad_controller_loop(visuals_state):
    controller = LaunchPadController(visuals_state)
    controller.run()
    time.sleep(0.1)


if __name__ == '__main__':
    magnitude = Value('d', 0.0)
    magnitude_mid = Value('d', 0.0)
    onset_triggered = Value('b', False)
    close = Value('b', False)

    switch = Value('b', False)

    shared_memory = Array('f', 32768 * 2)


    manager = mp.Manager()
    visuals_state = manager.dict({
        'cube': 'regular',
        'background': 'squares'
    })

    t1 = Process(target=audio_check_loop, args=(magnitude, onset_triggered, shared_memory, magnitude_mid, close))
    t2 = Process(target=controller_render_loop, args=(magnitude, onset_triggered, shared_memory, magnitude_mid, switch, close, visuals_state))
    t3 = Process(target=visuals_render_loop, args=(magnitude, onset_triggered, shared_memory, magnitude_mid, switch, close, visuals_state))
    t4 = Process(target=launchpad_controller_loop, args=(visuals_state,))

    light_process = Process(target=lighting_render_loop, args=(magnitude, onset_triggered, shared_memory, magnitude_mid, switch, close))

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    # light_process.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    # light_process.join()
