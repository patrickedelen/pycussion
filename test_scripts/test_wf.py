import numpy as np
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import pyqtgraph.opengl as gl
import pyaudio
import struct
import sys
import time

import aubio

"""
rgba(28, 0, 208, 1)
rgba(0, 206, 69, 1)
rgba(255, 255, 0, 1)
"""

color_options = [
    (1, 1, 1, 1),
    (0, 206 / 256.0, 69 / 256.0, 1),
    (255 / 256.0 , 255 / 256.0 , 0, 1),
    (28 / 256.0 , 0, 208 / 256.0, 1),
]

x, y, z = -1.2601932287216187, -7.956546783447266, -2.617464065551758


class CustomGLViewWidget(gl.GLViewWidget):
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Q:  # The Q key
            # Clean up and quit the application
            QtCore.QCoreApplication.quit()
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
        self.CHUNK = 1024
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.RATE,
            input=True,
            input_device_index=2,
            frames_per_buffer=self.CHUNK
        )

        self.onset = aubio.onset("energy", 1024, 1024, self.RATE)
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

        self.window.setBackgroundColor(self.bg_color)

        # Mesh Configuration
        self.x = np.linspace(-3,3,self.CHUNK)
        self.y = np.array([0 for _ in range(self.CHUNK)])
        self.z = np.array([0 for _ in range(self.CHUNK)])
        self.verts = np.vstack([self.x,self.y,self.z]).transpose()
        self.plot = gl.GLLinePlotItem(pos=self.verts, color=self.line_color, width=5, antialias=False)
        self.window.addItem(self.plot)

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
        self.plot.setData(pos=self.verts)

        end_time = time.time()
        print(f"Frame time: {end_time - start_time} seconds")

    def invert_colors(self):
        if self.line_state < 3:
            self.line_state += 1
            self.line_color = color_options[self.line_state]
        else:
            self.line_state = 0
            self.line_color = color_options[self.line_state]

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(1)
        QtWidgets.QApplication.instance().exec()

if __name__ == '__main__':
    vis = AudioVisualizer()
    vis.animation()
