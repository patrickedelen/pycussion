import numpy as np
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import pyqtgraph.opengl as gl
import pyaudio
import struct
import sys
import time

import aubio
import random

"""
rgba(28, 0, 208, 1)
rgba(0, 206, 69, 1)
rgba(255, 255, 0, 1)
"""

# color_options = [
#     (1, 1, 1, 1),  # white
#     (1, 0, 0, 1),  # red
#     (0, 1, 0, 1),  # green
#     (0, 0, 1, 1),  # blue
#     (1, 1, 0, 1),  # yellow
#     (0, 1, 1, 1),  # cyan
#     (1, 0, 1, 1),  # magenta
#     (0.5, 0.5, 0.5, 1),  # grey
#     (0.75, 0, 0.75, 1),  # purple
#     (0.5, 0.5, 0, 1),  # olive
#     (0, 0.5, 0.5, 1),  # teal
#     (0.5, 0, 0, 1),  # maroon
#     (0, 0.5, 0, 1),  # dark green
#     (0, 0, 0.5, 1),  # navy
# ]
color_options = [(random.random(), random.random(), random.random(), 1) for _ in range(100)]

cube_color_options = [(random.random()*255, random.random()*255, random.random()*255,100) for _ in range(100)]

# cube_color_options = [
#     (255,255,255,1),
#     (255,0,0,1),
#     (0,255,0,1)
# ]




x, y, z = -1.2601932287216187, -7.956546783447266, -2.617464065551758

class CubeWithOpaqueFaces(gl.GLMeshItem):
    def __init__(self, size=1, color=(1, 1, 1, 1)):
        # Define the cube vertices
        vertices = np.array([
            [-0.5, -0.5, -0.5],
            [0.5, -0.5, -0.5],
            [0.5, 0.5, -0.5],
            [-0.5, 0.5, -0.5],
            [-0.5, -0.5, 0.5],
            [0.5, -0.5, 0.5],
            [0.5, 0.5, 0.5],
            [-0.5, 0.5, 0.5]
        ]) * size
        
        # Define the cube faces
        faces = np.array([
            [0, 1, 2, 3],  # Front face
            [4, 5, 6, 7],  # Back face
            [0, 1, 5, 4],  # Bottom face
            [2, 3, 7, 6],  # Top face
            [0, 3, 7, 4],  # Left face
            [1, 2, 6, 5]   # Right face
        ])
        
        # Create the GLMeshItem
        super().__init__(vertexes=vertices, faces=faces, color=color, drawEdges=True, drawFaces=True)

    def color(self, rgba):
        self.color = rgba



class CustomGLViewWidget(gl.GLViewWidget):
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Q:  # The Q key
            # Clean up and quit the application
            QtCore.QCoreApplication.quit()
        if event.key() == QtCore.Qt.Key.Key_R:
            self.setBackgroundColor((255,0,0,1))
        if event.key() == QtCore.Qt.Key.Key_W:
            self.setBackgroundColor((255,255,255,1))
        if event.key() == QtCore.Qt.Key.Key_B:
            self.setBackgroundColor((0,0,0,1))
        else:
            super().keyPressEvent(event)

    def mouseMoveEvent(self, ev):

        pos = self.cameraPosition()
        print(f"camera position: {pos}")

        return super().mouseMoveEvent(ev)
    


class AudioVisualizer(object):
    def __init__(self):
        # PyAudio Configuration
        self.RATE = 32768
        self.CHUNK = 256
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.RATE,
            input=True,
            input_device_index=3,
            frames_per_buffer=self.CHUNK
        )

        self.onset = aubio.onset("specflux", self.CHUNK, self.CHUNK, self.RATE)
        self.onset.set_threshold(.1)
        self.onset_count = 0

        self.inverted = False
        self.bg_color = 0.0 # RGBA format, initial background color is black
        self.line_color = color_options[0] # RGBA format, initial line color is white
        self.line_state = 0

        # PyQtGraph Configuration
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = CustomGLViewWidget()
        self.window.setWindowTitle('Waveform')
        self.window.setGeometry(0, 110, 1920, 1080)
        # self.window.opts['center'] = QtGui.QVector3D(x, y, z)
        self.window.setCameraPosition(distance=5, elevation=90, azimuth=90)
        self.window.show()

        # self.window2  = CustomGLViewWidget()
        # self.window2.setWindowTitle('Interface')
        # self.window2.setGeometry(0, 110, 1920, 1080)
        # self.window2.show()

        self.window.setBackgroundColor(self.bg_color)

        # Mesh Configuration
        self.x = np.linspace(-3,3,self.CHUNK)
        self.y = np.array([0 for _ in range(self.CHUNK)])
        self.z = np.array([0 for _ in range(self.CHUNK)])
        self.verts = np.vstack([self.x,self.y,self.z]).transpose()
        self.plot = gl.GLLinePlotItem(pos=self.verts, color=self.line_color, width=5, antialias=False)
        # self.window.addItem(self.plot)

            # Create a cube
        self.cube = gl.GLBoxItem(glOptions='opaque', color=(200,100,100,70))
        # self.cube.setGLOptions({
        #     "drawFaces": True,
        #     "color": (1.,.5,.5,1.)
        # })
        self.cube.setSize(10, 10, 10)
        self.cube.translate(0, 0, 0)
        self.window.addItem(self.cube)
        print(self.verts)

        # cube = CubeWithOpaqueFaces(size=1, color=(random.random(), random.random(), random.random(), 1))
        self.window.addItem(self.cube)

    def update(self):
        start_time = time.time()

        wf_data = self.stream.read(self.CHUNK, exception_on_overflow=False)
        wf_data_onset = np.frombuffer(wf_data, dtype=np.float32)
        if self.onset(wf_data_onset):
            self.onset_count += 1
            if self.onset_count % 4 == 0:
                print("trigger effect here")
                self.invert_colors()
        # else:
        #     print('no trigger effect here')

        wf_data_full = np.frombuffer(wf_data, dtype=np.float32)
        # print(f"data converted: {time.time() - start_time} seconds")
        # wf_data_div = np.divide(wf_data_full, 32767)  # Normalize to range [-1, 1]
        end_time = time.time()
        # print(f"data calculation: {end_time - start_time} seconds")
        self.y = wf_data_full
        self.verts = np.vstack([self.x,self.y,self.z]).transpose()
        # self.plot.setData(pos=self.verts)

        self.cube.translate(0,0,0)

        # Scale the cube based on the audio magnitude
        magnitude = np.mean(np.abs(self.y)) * 5 + 5
        self.cube.setSize(magnitude, magnitude, magnitude)

        translate_factor = magnitude / 2

        self.cube.translate(0,0,0)
        self.cube.translate(-translate_factor, -translate_factor, -translate_factor)

        # Rotate the cube in random 3D directions
        rotation_angle_x = random.uniform(0, 2)
        rotation_angle_y = random.uniform(0, 2)
        rotation_angle_z = random.uniform(0, 2)
        self.cube.rotate(rotation_angle_x, 1, 0, 0)
        self.cube.rotate(rotation_angle_y, 0, 1, 0)
        self.cube.rotate(rotation_angle_z, 0, 0, 1)

        self.cube.translate(translate_factor, translate_factor, translate_factor)



        end_time = time.time()
        # print(f"Frame time: {end_time - start_time} seconds")

    def invert_colors(self):
        if self.line_state < len(cube_color_options) - 1:
            self.line_state += 1
            self.line_color = cube_color_options[self.line_state]
        else:
            self.line_state = 0
            self.line_color = cube_color_options[self.line_state]

        # self.plot.color = self.line_color

        self.cube.setColor(self.line_color)
        # self.window.setBackgroundColor(tuple(map(lambda i: 255 - i, self.line_color)))
        # if self.inverted:
        #     self.window.setBackgroundColor((0,0,0,255))

        #     self.inverted = False
        # else:
        #     self.window.setBackgroundColor((255,255,255,255))
        #     self.inverted = True

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(1)
        QtWidgets.QApplication.instance().exec()


if __name__ == '__main__':
    vis = AudioVisualizer()
    vis.animation()
