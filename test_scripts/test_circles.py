import numpy as np
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import sys


class CustomGLViewWidget(gl.GLViewWidget):
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Q:  # The Q key
            # Clean up and quit the application
            QtCore.QCoreApplication.quit()
        else:
            super().keyPressEvent(event)


class MovingSpheres(object):
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = CustomGLViewWidget()
        self.window.setGeometry(0, 0, 1920, 1080)
        self.window.setCameraPosition(elevation=50, distance=70, azimuth=90)
        self.window.pan(50, 0, 0)
        self.framecount = 0

        # Number of spheres
        self.n_spheres = 10

        # List to hold our spheres
        self.spheres = []

        # Create our spheres and add them to the list and to the window
        for i in range(self.n_spheres):
            sphere = gl.MeshData.sphere(rows=10, cols=20)
            sphereItem = gl.GLMeshItem(meshdata=sphere, smooth=True, color=np.random.random(4), shader='balloon')
            
            # Set an initial position for the sphere
            sphereItem.translate(10*i, 0, 0)
            self.spheres.append(sphereItem)
            self.window.addItem(sphereItem)

        self.window.show()

    def update(self):
        self.framecount += 1
        
        """
        Update the position of the spheres each time
        """
        for i, sphere in enumerate(self.spheres):
            # We use a sine function for the up and down movement, and add i to give each sphere a different phase
            new_y = 10 * np.sin(self.framecount / 20. + i)
            sphere.resetTransform()
            sphere.translate(10*i, new_y, 0)

    def animation(self, frametime=10):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(frametime)
        self.start()

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtWidgets.QApplication.instance().exec()


if __name__ == '__main__':
    t = MovingSpheres()
    t.animation()