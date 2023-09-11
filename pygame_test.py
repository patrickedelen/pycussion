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

# import aubio
import random
import numpy as np
from collections import deque


ws_uri = "ws://localhost:8080"

"""
colors:

--licorice: hsla(5, 19%, 12%, 1);
--night: hsla(204, 12%, 8%, 1);
--auburn: hsla(6, 66%, 38%, 1);
--gunmetal: hsla(180, 7%, 18%, 1);
--night-2: hsla(180, 4%, 5%, 1);

"""


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

def mandelbrot(c,max_iter):
    z = c
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return max_iter

class Averager:
    def __init__(self, size):
        self.buffer = deque(maxlen=size)
        self.total = 0.0

    def add(self, value):
        if len(self.buffer) == self.buffer.maxlen:
            self.total -= self.buffer[0]
        self.buffer.append(value)
        self.total += value

    def average(self):
        if len(self.buffer) == 0:
            return 0.0
        return self.total / len(self.buffer)

class BPMAverage:
    def __init__(self, chunk, rate):
        # self.onset = aubio.onset("kl", chunk * 8, chunk, rate)

        self.chunk_count = 0
        self.frames = bytearray()

        self.time_since_last_tempo = time.time()

        # Store the last 100 onset times in a deque
        self.onset_times = deque(maxlen=20)

        self.count = 0

    def add(self, frame):
        self.chunk_count += 1
        wf_data_onset = np.frombuffer(frame, dtype=np.float32)
        onset = [0]
        if onset[0] > 1:
            print('got onset', onset)
            # Record the current time for this onset
            current_time = time.time()
            if current_time - self.time_since_last_tempo > 1:
                print('time', self.time_since_last_tempo)
                self.onset_times.clear()
                self.count = 0
            self.onset_times.append(current_time)
            self.time_since_last_tempo = current_time

            self.count += 1
            if self.count > 10:
                self.count = 0
                print('bpm', self.calculate_bpm())

    def calculate_bpm(self):
        # Get the time intervals between onsets
        intervals = [self.onset_times[i+1] - self.onset_times[i] for i in range(len(self.onset_times)-1)]
        if not intervals:
            return 0.0

        # Calculate the average interval
        avg_interval = sum(intervals) / len(intervals)

        # Convert the average interval to BPM
        bpm = 60 / avg_interval
        return bpm
    

# store the last 100 results from audio magnitude
class SpecHistory():
    def __init__(self):
        self.buffer = deque(maxlen=100)


particles = []
for i in range(400):
    particles.append([random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10)])

import asyncio
import websockets

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        await self.send(json.dumps({
            "role": "master"
        }))

    async def send(self, message):
        await self.websocket.send(message)
        print(f"> Sent: {message}")

    async def receive(self):
        response = await self.websocket.recv()
        print(f"< Received: {response}")

    async def close(self):
        await self.websocket.close()
        print("Connection closed.")

    async def run(self):
        await self.connect()
        await self.send(json.dumps({
            "role": "master"
        }))
        await self.receive()
        # await self.close()
    
    async def run_forever(self, onset_triggered):
        await self.connect()
        while True:
            if onset_triggered.value:
                print('got trigger')
                await self.send(json.dumps({
                    "type": "background",
                    "data": "red"
                }))
                await asyncio.sleep(0.25)




class AudioController():
    def __init__(self, shared_memory):
        # PyAudio Configuration
        self.RATE = 32768
        self.CHUNK = 256
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.RATE,
            input=True,
            input_device_index=2,
            frames_per_buffer=self.CHUNK
        )

        # self.onset = aubio.onset("energy", self.CHUNK, self.CHUNK, self.RATE)
        # self.onset.set_threshold(.1)
        self.onset_count = 0

        self.magnitude = 0

        self.avg = BPMAverage(self.CHUNK, self.RATE)

        self.second_data = np.frombuffer(shared_memory.get_obj(), dtype=np.float32)

        self.onset_triggered = False

    def update(self):

        wf_data = self.stream.read(self.CHUNK, exception_on_overflow=False)
        # self.avg.add(wf_data)
        wf_data_onset = np.frombuffer(wf_data, dtype=np.float32)

        # Update the 1-second buffer with the new audio data
        self.second_data[:-self.CHUNK] = self.second_data[self.CHUNK:]
        self.second_data[-self.CHUNK:] = wf_data_onset

        wf_data_full = np.frombuffer(wf_data, dtype=np.float32)


        self.magnitude = np.mean(np.abs(wf_data_full))
        # print('mag', self.magnitude)

        # print('len', len(wf_data_onset))

        # if self.onset(wf_data_onset):
        #     if self.magnitude > 0.15:
        #         self.onset_count += 1
        #         if self.onset_count % 2 == 0:
        #             print("trigger effect here")
        #             self.onset_triggered = True
        #             self.onset_count = 0
        #         else:
        #             self.onset_triggered = False
        #     else:
        #         self.onset_triggered = False

        # else:
        #     print('no trigger effect here')

        # print(f"data converted: {time.time() - start_time} seconds")
        # wf_data_div = np.divide(wf_data_full, 32767)  # Normalize to range [-1, 1]


    def get_magnitude(self):
        return self.magnitude

    def get_onset(self):
        return self.onset_triggered
    
    def get_buffer(self):
        return self.second_data


# def draw_point_cloud(points):


class GameController():
    def __init__(self):
        self.cur_rotate = 1

        # Initialize Pygame
        pygame.init()

        # Set the display mode with the OPENGL flag
        display = (1000, 800)
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

        self.avg = Averager(10)

        self.scene = 'plane'

        self.scenes = ['plane', 'cube', 'squares', 'circles', 'waveform']

        self.squares = []
        self.updates = 0

        self.triangle_verts = np.array([[400, 100], [100, 700], [700, 700]])

        self.num_circles = 50
        self.points = np.random.rand(self.num_circles, 2) * 10 - 5 # 2D random points in 5x5 space

        self.circles = np.random.rand(self.num_circles, 2) * 10 - 5 # Initial random positions in a 5x5 space
        self.radius = np.zeros(self.num_circles)  # Initial radius for each circle
        self.speeds = (np.random.rand(self.num_circles, 2) - 0.5) * 0.1  # Random speeds for x and y movement

        # # Enable back-face culling
        # glEnable(GL_CULL_FACE)
        # glCullFace(GL_FRONT)

    def render_plane(self, mangitude=0, onset_triggered=False, shared_memory=[]):
        points = np.random.rand(1000, 3) * 2 - 1

        second_data = np.frombuffer(shared_memory.get_obj(), dtype=np.float32)

        material_diffuse = [1.0, 1.0, 1.0, 1.0]  # White material
        material_specular = [1.0, 1.0, 1.0, 1.0]  # No specular reflection
        material_shininess = [50.0]  # No shininess

        glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

        glPushMatrix()
        glDisable(GL_LIGHTING)

        self.cur_rotate = self.cur_rotate + 1
        if self.cur_rotate == 1440:
            self.cur_rotate = 0

        glRotatef(self.cur_rotate / 4, 1, 1, 1)

        # Draw the particles
        glColor3f(0.3,0.3,0.3)
        glPointSize(3)
        glBegin(GL_POINTS)

        scaler = 5

        for x in range(256):
            for y in range(128):
                if x % 5 == 0:
                    x_val = (x / 256 - 0.5) * 5
                    y_val = (y / 64 - 0.75) * 5
                    glVertex3f(x_val, y_val, second_data[x * y] * 10)
        glEnd()

        glPopMatrix()

    def render_cube(self, magnitude=0, onset_triggered=False):
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
        for particle in particles:
            glVertex3fv(particle)
        glEnd()

        # Update the particle positions to move down the screen
        particle_speed_factor = 0.01 + self.avg.average() * 20
        for particle in particles:
            particle[1] -= particle_speed_factor
            if particle[1] < -10:
                particle[1] = random.uniform(1, 10)


        glPopMatrix()

        # glRotatef(1, 1, 1, 1)

        # Rotate the cube

        # Scale and center the cube based on magnitude
       
        scale_factor = self.avg.average() * 10 + 0.5
        glPushMatrix()
        glTranslatef(0, 0, 0)  # Translate to the origin
        glScalef(scale_factor, scale_factor, scale_factor)  # Scale the cube
        glTranslatef(0, 0, 0)  # Translate back to the original position

        self.cur_rotate = self.cur_rotate + 1
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

    def render_squares(self):




        
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
        speed = self.avg.average() * 50 + 0.5

        # Update current rotation angle
        self.cur_rotate += speed
        if self.cur_rotate >= 360.0:
            self.cur_rotate -= 360.0
        
        # Rotate the squares along the Z-axis
        glRotatef(self.cur_rotate, 0, 0, 1)
        
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

        factor = self.avg.average() * 20
        # print('factor', factor)

        if len(self.squares) > 0 and self.squares[-1] > 3 and factor > 0.1:
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

    # def draw_waveform(self, magnitude):

    def render_circles(self, magnitude=0, onset_triggered=False, shared_memory=[]):
        
        self.circles += self.speeds

        out_of_bounds = np.logical_or(self.circles < -5, self.circles > 5)
        respawn_indices = np.any(out_of_bounds, axis=1)
        self.circles[respawn_indices] = np.random.rand(np.sum(respawn_indices), 2) * 10 - 5

        # Assuming shared_memory is still used, though the function does not seem to do much with it
        second_data = np.frombuffer(shared_memory.get_obj(), dtype=np.float32) if shared_memory else []

        # Lighting settings remain unchanged
        material_diffuse = [1.0, 1.0, 1.0, 1.0]  # White material
        material_specular = [1.0, 1.0, 1.0, 1.0]  # No specular reflection
        material_shininess = [50.0]  # No shininess

        # magnitude *= 20

        self.radius = 0.9 * self.radius + 0.2 * magnitude * 10

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

    def render_waveform(self, magnitude, shared_memory):
        # Assuming shared_memory is still used to get the waveform data
        waveform_data = np.frombuffer(shared_memory.get_obj(), dtype=np.float32)

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
        glBegin(GL_LINE_STRIP)

        # print('cur magnitude', magnitude)

        # We'll skip some data points for performance and clarity in visualization
        skip = len(waveform_data) // 512

        magnitude = min(max(self.avg.average() * 40, 1), 2)

        for i in range(0, len(waveform_data), skip):
            x_val = ((i / len(waveform_data) - 0.5) * 10) * magnitude
            y_val = (((waveform_data[i] - 0.5) * 5) + 2.5) * magnitude
            glVertex2f(x_val, y_val)

        glEnd()

        glPopMatrix()

    # def render_



    def render_loop(self, magnitude=0, onset_triggered=False, second_data=[]):
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

        

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.avg.add(magnitude)

        zoom_factor = 1.0  # Starting zoom factor
        zoom_speed = 0.99  # Speed at which to zoom in

        # if True:
            # pass
            # self.render_squares()
            # self.render_cube(magnitude, onset_triggered)
            # self.draw_mandelbrot()
            # glDisable(GL_LIGHTING)
            # gluOrtho2D(0, 800, 0, 800)

            # # Update zoom factor
            # zoom_factor *= zoom_speed

            # # Update vertices for zoom
            # midpoints = [
            #     (self.triangle_verts[0] + self.triangle_verts[1]) / 2,
            #     (self.triangle_verts[1] + self.triangle_verts[2]) / 2,
            #     (self.triangle_verts[2] + self.triangle_verts[0]) / 2
            # ]
            # self.triangle_verts = np.array([self.triangle_verts[0], midpoints[0], midpoints[2]], dtype=np.float32)
            
            # # Generate fractal triangles
            # triangles = self.sierpinski_triangle(self.triangle_verts, 4)

            # # Flatten the list of triangles into a single array
            # vertex_data = np.array(triangles, dtype=np.float32).flatten()

            # # Clear and draw
            # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            # glEnableClientState(GL_VERTEX_ARRAY)
            # glVertexPointer(2, GL_FLOAT, 0, vertex_data)
            # glDrawArrays(GL_TRIANGLES, 0, len(vertex_data) // 2)
            # glDisableClientState(GL_VERTEX_ARRAY)

            # pygame.display.flip()
            # pygame.time.wait(100000)

            # self.sierpinski_triangle(self.triangle_verts, 10)

            # Update the display
            # pygame.display.flip()
            # pygame.time.wait(100000)
        glClearColor(0,0,0,1)
        if self.scene == 'plane':
            self.render_plane(magnitude, onset_triggered, second_data)

        elif self.scene == 'cube':
            self.render_cube(magnitude, onset_triggered)

        elif self.scene == 'squares':
            self.render_squares()
        elif self.scene == 'circles':
            self.render_circles(magnitude, onset_triggered, second_data)
        elif self.scene == 'waveform':
            self.render_waveform(magnitude, second_data)


        
        # print('rotating', self.cur_rotate)

        # Clear the screen
        pygame.display.flip()
        pygame.time.wait(16)














def audio_check_loop(magnitude, onset_triggered, shared_memory):
    audio_controller = AudioController(shared_memory)
    while True:
        audio_controller.update()
        magnitude.value = audio_controller.get_magnitude()
        # print('magnitude', magnitude.value)
        onset_triggered.value = audio_controller.get_onset()
        # second_data.value = audio_controller.get_buffer()


def game_render_loop(magnitude, onset_triggered, shared_memory):
    game_controller = GameController()
    while True:
        time.sleep(0.001)
        game_controller.render_loop(magnitude.value, onset_triggered.value, shared_memory)

def websocket_loop(onset_triggered):
    return
    ws_client = WebSocketClient(ws_uri)
    asyncio.get_event_loop().run_until_complete(ws_client.run_forever(onset_triggered))

    # while True:
    #     if onset_triggered.value:
    #         print('got trigger')
    #         ws_client.send(json.dumps({
    #             "type": "background",
    #             "data": "red"
    #         }))
    #         time.sleep(0.25)
            

# game_render_loop()

if __name__ == '__main__':
    magnitude = Value('d', 0.0)
    onset_triggered = Value('b', False)

    shared_memory = Array('f', 32768)

    t1 = Process(target=audio_check_loop, args=(magnitude, onset_triggered, shared_memory))
    t2 = Process(target=game_render_loop, args=(magnitude, onset_triggered, shared_memory))
    t3 = Process(target=websocket_loop, args=(onset_triggered,))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

print('finished')
