import pyaudio
import numpy as np
import aubio

# PyAudio Configuration
buffer_size = 2048  # You might need to adjust this value depending on your system
pyaudio_format = pyaudio.paFloat32
n_channels = 2
samplerate = 32768

p = pyaudio.PyAudio()

# Loop through the number of available audio devices
for i in range(p.get_device_count()):
    # Get the device info
    info = p.get_device_info_by_index(i)
    # Check if this device supports input (i.e., can be used as a microphone)
    print("Input Device id ", i, " - ", info["name"], " - ", info["maxOutputChannels"])

info = p.get_device_info_by_index(3)

print("Device name: ", info["name"])
print("Device maxInputChannels: ", info["maxInputChannels"])


# # # Clean up PyAudio
# p.terminate()

# Create a PyAudio object
# p = pyaudio.PyAudio()

# Create a stream
stream = p.open(format=pyaudio_format,
                rate=samplerate,
                channels=2,
                input=True,
                input_device_index=5,
                frames_per_buffer=buffer_size)

# Create an aubio tempo detection object
tempo = aubio.tempo("default", 4096, 4096, samplerate)
onset = aubio.onset("energy", buffer_size, buffer_size, samplerate)
onset.set_threshold(.01)

tempo_count = 0

onset_count = 0

while True:
    try:
        # Read data from the audio input stream
        audiobuffer = stream.read(buffer_size)
        signal = np.frombuffer(audiobuffer, dtype=np.float32)

        # resize = signal[:1024]
        # Execute tempo detection on the signal
        # tempo(signal)
        
        # print(onset.get_last())
        # exit(0)

        # If a beat is found, print the BPM
        tempo_count += 1
        # if tempo.get_confidence() > .1 and tempo_count % 100 == 0:
            # print(f"Estimated BPM: {tempo.get_bpm():.2f}")

        if onset(signal):
            onset_count += 1
            if onset_count % 4 == 0:
                print("trigger effect here")
            print("onset detected", onset.get_last())
        
    except KeyboardInterrupt:
        print("\nStopping")
        break

# Close the stream
stream.stop_stream()
stream.close()

# Terminate the PyAudio object
p.terminate()