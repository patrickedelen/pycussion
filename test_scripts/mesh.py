"""
This creates a 3D mesh with perlin noise to simulate
a terrain. The mesh is animated by shifting the noise
to give a "fly-over" effect.

If you don't have pyOpenGL or opensimplex, then:

    - conda install -c anaconda pyopengl
    - pip install opensimplex
"""

import numpy as np
from opensimplex import OpenSimplex
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import struct
import pyaudio
import sys
import time


class Terrain(object):
    def __init__(self):
        """
        Initialize the graphics window and mesh surface
        """

        # setup the view window
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = gl.GLViewWidget()
        self.window.setWindowTitle('Terrain')
        self.window.setGeometry(0, 110, 1920, 1080)
        self.window.setCameraPosition(distance=30, elevation=12)
        self.window.show()

        # constants and arrays
        self.nsteps = 1.3
        self.offset = 0
        self.ypoints = np.arange(-20, 20 + self.nsteps, self.nsteps)
        self.xpoints = np.arange(-20, 20 + self.nsteps, self.nsteps)
        self.nfaces = len(self.ypoints)

        self.RATE = 1000
        self.CHUNK = len(self.xpoints) * len(self.ypoints)

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            input_device_index=3,
            frames_per_buffer=self.CHUNK,
        )

        # perlin noise object
        self.noise = OpenSimplex(seed=1)

        # create the veritices array
        verts, faces, colors = self.mesh()

        self.mesh1 = gl.GLMeshItem(
            faces=faces,
            vertexes=verts,
            faceColors=colors,
            drawEdges=True,
            smooth=False,
        )
        self.mesh1.setGLOptions('additive')
        self.window.addItem(self.mesh1)

    def mesh(self, offset=0, height=2.5, wf_data=None):

        # wf fft algo
        if wf_data is not None:
            mag_data = struct.unpack(str(2 * self.CHUNK) + 'B', wf_data)
            mag_data = np.array(mag_data, dtype='int16')[::2] + 32768
            mag_data = mag_data - 32768

            # Apply FFT and obtain magnitude
            sp = np.abs(np.fft.fft(mag_data))
            freq = np.fft.fftfreq(len(mag_data), 1/self.RATE)

            # Select positive frequencies only
            mask = freq > 0
            freq = freq[mask]
            sp = sp[mask]

            # Reduce to 10 elements
            reduced_len = 10
            reduced_wf_data = np.zeros(reduced_len)
            bin_size = len(sp) // reduced_len

            for i in range(reduced_len):
                reduced_wf_data[i] = np.mean(sp[i*bin_size:(i+1)*bin_size])

            # Normalize to 0 - 1
            reduced_wf_data = (reduced_wf_data - np.min(reduced_wf_data)) / (np.max(reduced_wf_data) - np.min(reduced_wf_data))
            # Scale and shift to -10 - 10
            reduced_wf_data = reduced_wf_data * 10

            print(reduced_wf_data)

        if wf_data is not None:
            wf_data = struct.unpack(str(2 * self.CHUNK) + 'B', wf_data)
            wf_data = np.array(wf_data, dtype='int32')[::2] + 128
            wf_data = wf_data - 128
            wf_data = wf_data * 0.04
            wf_data = wf_data.reshape((len(self.xpoints), len(self.ypoints)))
        else:
            wf_data = np.array([1] * 1024)
            wf_data = wf_data.reshape((len(self.xpoints), len(self.ypoints)))
        
        print(wf_data.shape)

        faces = []
        colors = []
        verts = np.array([
            [
                x, y, wf_data[xid][yid] * self.noise.noise2(x=xid / 5 + offset, y=yid / 5 + offset)
            ] for xid, x in enumerate(self.xpoints) for yid, y in enumerate(self.ypoints)
        ], dtype=np.float32)

        for yid in range(self.nfaces - 1):
            yoff = yid * self.nfaces
            for xid in range(self.nfaces - 1):
                faces.append([
                    xid + yoff,
                    xid + yoff + self.nfaces,
                    xid + yoff + self.nfaces + 1,
                ])
                faces.append([
                    xid + yoff,
                    xid + yoff + 1,
                    xid + yoff + self.nfaces + 1,
                ])
                colors.append([
                    xid / self.nfaces, 1 - xid / self.nfaces, yid / self.nfaces, 0.7
                ])
                colors.append([
                    xid / self.nfaces, 1 - xid / self.nfaces, yid / self.nfaces, 0.8
                ])

        faces = np.array(faces, dtype=np.uint32)
        colors = np.array(colors, dtype=np.float32)

        return verts, faces, colors

    def update(self):
        """
        update the mesh and shift the noise each time
        """

        try:
            wf_data = self.stream.read(self.CHUNK)
        except Exception as e:
            print('could not read', e)
            exit(1)

        verts, faces, colors = self.mesh(offset=self.offset, wf_data=wf_data)
        self.mesh1.setMeshData(vertexes=verts, faces=faces, faceColors=colors)
        self.offset -= 0.05

    def start(self):
        """
        get the graphics window open and setup
        """

        try:
            while True:
                if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
                    QtWidgets.QApplication.instance().exec()

        except KeyboardInterrupt:
            print('terminating')
            exit(0)

    def animation(self, frametime=10):
        """
        calls the update method to run in a loop
        """
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(frametime)
        self.start()


if __name__ == '__main__':
    t = Terrain()
    t.animation()

