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
import matplotlib.pyplot as plt

from constants import INPUT_DEVICE_INDEX


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

    def reset(self):
        self.buffer.clear()
        self.total = 0.0


class BandAverager:
    def __init__(self):
        self.max_values = {
            "low": float('-inf'),
            "mid": float('-inf'),
            "high": float('-inf')
        }
        self.min_values = {
            "low": float('inf'),
            "mid": float('inf'),
            "high": float('inf')
        }

    def scale_value(self, value, band):
        # Update the max and min values
        self.max_values[band] = max(self.max_values[band], value)
        self.min_values[band] = min(self.min_values[band], value)
        
        # Scale the value between 0 and 1 based on max/min
        if self.max_values[band] == self.min_values[band]:
            return 0  # Avoid division by zero
        return (value - self.min_values[band]) / (self.max_values[band] - self.min_values[band])

    def add(self, low, mid, high):
        return self.scale_value(low, "low"), self.scale_value(mid, "mid"), self.scale_value(high, "high")

def a_weighting(frequencies):
    """Compute A-weighting for given frequencies."""
    f2 = np.square(frequencies)
    f4 = np.square(f2)
    term1 = 12200**4 * f4
    term2 = (f2 + 20.6**2) * np.sqrt(f2 + 107.7**2) * (f2 + 737.9**2)
    term3 = f2 + 12200**2
    return 2.0 + 20 * np.log10(term1 / (term2 * term3))

def extract_bands(frequencies, magnitudes):
    low_band = (20, 250)
    mid_band = (250, 2000)
    high_band = (2000, 16384)

    low_mask = (frequencies >= low_band[0]) & (frequencies <= low_band[1])
    mid_mask = (frequencies >= mid_band[0]) & (frequencies <= mid_band[1])
    high_mask = (frequencies >= high_band[0]) & (frequencies <= high_band[1])

    low_magnitude = np.mean(magnitudes[low_mask])
    mid_magnitude = np.mean(magnitudes[mid_mask])
    high_magnitude = np.mean(magnitudes[high_mask])

    return low_magnitude, mid_magnitude, high_magnitude




class AudioProcessor:
    def __init__(self, shared_memory):
        # PyAudio Configuration
        self.RATE = 32768
        self.CHUNK = 512
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.RATE,
            input=True,
            input_device_index=1,
            frames_per_buffer=self.CHUNK
        )

        # self.onset = aubio.onset("energy", self.CHUNK, self.CHUNK, self.RATE)
        # self.onset.set_threshold(.1)
        self.onset_count = 0

        self.magnitude = 0

        self.magnitude_mid = 0

        # self.avg = BPMAverage(self.CHUNK, self.RATE)

        self.second_data = np.frombuffer(shared_memory.get_obj(), dtype=np.float32)

        self.onset_triggered = False
        self.channel1_averager = Averager(self.RATE)
        self.channel2_averager = Averager(self.RATE)

        self.magnitude_averager = Averager(8)

        self.initial_averager_low = Averager(4)
        self.initial_averager_mid = Averager(8)

        self.mid_averager = Averager(32)

        self.band_averager = BandAverager()

        # Set up the plot
        # self.fig, self.ax = plt.subplots()
        self.x = np.linspace(0, self.RATE // 2, self.CHUNK // 2)
        # self.line, = self.ax.plot(self.x, np.random.rand(self.CHUNK // 2))
        # self.ax.set_xlim(20, self.RATE // 2)  # Display frequencies from 20Hz to Nyquist frequency
        # self.ax.set_ylim(-1, 1)
        # self.ax.set_xscale('log')
        # # self.ax.set_yscale('log')
        # self.ax.set_title("FFT of Audio Signal")
        # self.ax.set_xlabel("Frequency (Hz)")
        # self.ax.set_ylabel("Magnitude")

        # self.run()

        self.closing = False

    def close(self):
        self.stream.close()

    def update_data(self):

        # # Read audio data
        wf_data = self.stream.read(self.CHUNK, exception_on_overflow=False)
        wf_data_array = np.frombuffer(wf_data, dtype=np.float32)

        # shift over data 1 chunk in array, fill first chunk with new data
        self.second_data[:-self.CHUNK] = self.second_data[self.CHUNK:]
        self.second_data[-self.CHUNK:] = wf_data_array

        # # Compute FFT and update the plot
        # fft_data = np.fft.fft(wf_data_array)[:self.CHUNK // 2]
        # magnitude = np.abs(fft_data)

                
        fft_data = np.fft.fft(wf_data_array)[:self.CHUNK // 2]
        magnitude = np.abs(fft_data)
        # a_weighted_magnitude = magnitude * a_weighting(self.x)
        # self.line.set_ydata(a_weighted_magnitude)

        fft_data = np.fft.fft(wf_data_array)[:self.CHUNK // 2]
        magnitude = np.abs(fft_data)
        low_magnitude, mid_magnitude, high_magnitude = extract_bands(self.x, magnitude)
        self.initial_averager_low.add(low_magnitude)

        self.initial_averager_mid.add(mid_magnitude)

        scaled_low, scaled_mid, scaled_high = self.band_averager.add(self.initial_averager_low.average(), self.initial_averager_mid.average(), high_magnitude)



        if random.random() < 0.05:
            print("-----------------")
            print("Low:", scaled_low)
            print("Mid:", scaled_mid)
            print("High:", scaled_high)


        self.magnitude_averager.add(scaled_low)
        self.magnitude = self.magnitude_averager.average()

        self.mid_averager.add(scaled_mid)
        self.magnitude_mid = self.mid_averager.average()

        # print('magnitude', magnitude)
        # self.line.set_ydata(magnitude)




    # UNUSED
    def update(self, frame):

        # # Read audio data
        wf_data = self.stream.read(self.CHUNK, exception_on_overflow=False)
        wf_data_array = np.frombuffer(wf_data, dtype=np.float32)

        # # Compute FFT and update the plot
        # fft_data = np.fft.fft(wf_data_array)[:self.CHUNK // 2]
        # magnitude = np.abs(fft_data)

                
        fft_data = np.fft.fft(wf_data_array)[:self.CHUNK // 2]
        magnitude = np.abs(fft_data)
        # a_weighted_magnitude = magnitude * a_weighting(self.x)
        # self.line.set_ydata(a_weighted_magnitude)

        fft_data = np.fft.fft(wf_data_array)[:self.CHUNK // 2]
        magnitude = np.abs(fft_data)
        low_magnitude, mid_magnitude, high_magnitude = extract_bands(self.x, magnitude)

        scaled_low, scaled_mid, scaled_high = self.band_averager.add(low_magnitude, mid_magnitude, high_magnitude)


        if random.random() < 0.05:
            print("Low:", scaled_low)
            print("Mid:", scaled_mid)
            print("High:", scaled_high)


        self.magnitude_averager.add(scaled_low)
        self.magnitude = self.magnitude_averager.average()

        # print('magnitude', magnitude)
        # self.line.set_ydata(magnitude)
        return self.line,
    

        wf_data = self.stream.read(self.CHUNK, exception_on_overflow=False)
        wf_data_array = np.frombuffer(wf_data, dtype=np.float32)

        # Split the data into two channels
        channel1_data = wf_data_array  # Even indices: 0, 2, 4, ...
        # channel2_data = wf_data_array[1::2]  # Odd indices: 1, 3, 5, ...

        # Update averagers with new data
        self.magnitude = np.mean(np.abs(wf_data_array))

        # Update the 1-second buffer with the new audio data
        # self.second_data[:-self.CHUNK] = self.second_data[self.CHUNK:]
        # self.second_data[-self.CHUNK:] = wf_data_array
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

    def run(self):
        from matplotlib.animation import FuncAnimation
        ani = FuncAnimation(self.fig, self.update, interval=10, blit=True)
        plt.show()


    def get_magnitude(self):
        return self.magnitude
    
    def get_magnitude_mid(self):
        return self.magnitude_mid

    def get_onset(self):
        return self.onset_triggered
    
    def get_buffer(self):
        return self.second_data

