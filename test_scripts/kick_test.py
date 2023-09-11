import pyaudio
import numpy as np
import aubio
from scipy.signal import butter, lfilter
import random
from collections import deque

# Initialize PyAudio
p = pyaudio.PyAudio()

# Constants
BUFFER_SIZE = 1024  # Audio buffer size
CHANNELS = 1  # Mono audio
FORMAT = pyaudio.paFloat32  # Format
RATE = 32768  # Sampling rate
THRESHOLD = 0.5  # Onset detection threshold

# # Create an onset detector
onset_detector = aubio.onset("energy", BUFFER_SIZE, BUFFER_SIZE, RATE)
# onset_detector.set_threshold(THRESHOLD)


def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_highpass(start, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = start / nyquist
    b, a = butter(order, normal_cutoff, btype='highpass')
    return b, a

def run_highpass(data, cutoff, fs, order=5):
    b, a = butter_highpass(2000.0, fs, order=order)
    y = lfilter(b, a ,data)
    return y

CUTOFF_FREQUENCY = 200.0  # Cutoff frequency in Hz
energy_window = np.zeros(50)


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
        return self.total / self.buffer.maxlen
    
    def reset(self):
        self.buffer.clear()
        self.total = 0.0

a = Averager(size=10)

def detect_onset_energy(audio_data, threshold=0.2, window_size=50):
    """
    Detect onset in an audio signal based on energy.

    Parameters:
        audio_data (numpy.array): The audio data.
        threshold (float): The energy threshold for onset detection.
        window_size (int): The size of the window used to compute the energy.

    Returns:
        onset_detected (bool): True if an onset is detected, False otherwise.
    """
    
    # Compute the short-time energy of the audio signal
    energy = np.sum(audio_data ** 2)
    a.add(energy)


    # print('energy', energy, 'average', a.average())

    # print('energy', energy)
    
    # Check if the energy exceeds the threshold
    if a.average() > 1.8:
        # print('got energy', energy)
        # print('got average', a.average())
        print('kick drum detected', a.average())
        a.reset()
        return True
    
    return False

snare_avg = Averager(size=10)
def check_snare_hit(audio_data):
    energy = np.sum(audio_data ** 2)
    snare_avg.add(energy)

    # print('snare energy', snare_avg.average())

    if snare_avg.average() > 0.1:
        print('snare detected', snare_avg.average())
        snare_avg.reset()


def callback(in_data):
    # Convert audio data to NumPy array
    audio_data = np.frombuffer(in_data, dtype=np.float32)
    
    # Apply low-pass filter
    audio_data_low_passed = butter_lowpass_filter(audio_data, CUTOFF_FREQUENCY, RATE)
    audio_data_low_passed = np.array(audio_data_low_passed, dtype=np.float32)
    
    # Use aubio to detect the onset (kick drum)
    is_onset = onset_detector(audio_data_low_passed)

    is_onset_all_data = onset_detector(audio_data)

    # energy_window[:-1] = 
    
    # if is_onset:
    #     print("Kick drum detected!", is_onset)
    
    # if is_onset_all_data:
    #     print('all data detected', is_onset_all_data)

    # simple = 
    detect_onset_energy(audio_data_low_passed)

    audio_data_high_passed = run_highpass(audio_data, 8000.0, RATE)
    audio_data_high_passed = np.array(audio_data_high_passed, dtype=np.float32)

    # check_snare_hit(audio_data_high_passed)

    # if simple:
    #     print('simple onset detected', random.random())
    
    # return (in_data, pyaudio.paContinue)

# Open audio stream
# stream = p.open(format=FORMAT,
#                 channels=CHANNELS,
#                 rate=RATE,
#                 input=True,
#                 input_device_index=5,
#                 frames_per_buffer=BUFFER_SIZE)

# RATE = 32768
# CHUNK = 256
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paFloat32,
    channels=1,
    rate=RATE,
    input=True,
    input_device_index=4,
    frames_per_buffer=BUFFER_SIZE
)

# Start audio stream

while True:
    try:
        audio_data = stream.read(BUFFER_SIZE, exception_on_overflow=False)
        audio_data = np.frombuffer(audio_data, dtype=np.float32)

        callback(audio_data)
    except KeyboardInterrupt:
        # Stop the stream when KeyboardInterrupt is received
        print("Stream stopped")
        stream.stop_stream()
        stream.close()
        p.terminate()
