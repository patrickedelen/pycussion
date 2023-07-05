import pyaudio

p = pyaudio.PyAudio()

info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    if (p.get_device_info_by_index(i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", p.get_device_info_by_index(i).get('name'))

    if (p.get_device_info_by_index(i).get('maxOutputChannels')) > 0:
        print("Output Device id ", i, " - ", p.get_device_info_by_index(i).get('name'))


# exit(0)



import numpy as np

CHUNK = 1024  # Number of frames in the buffer
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Single channel for mono audio
RATE = 44100  # Sampling rate

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=3,  # Specify your input device here
                frames_per_buffer=CHUNK)

print("* Listening...")

counts = 0

while counts < 1000000:  # Use some condition to stop the listening loop when needed
    data = stream.read(CHUNK)  # Read data from audio input
    numpy_array = np.frombuffer(data, dtype=np.int16)  # Convert the data to a numpy array
    # Add code here to process the numpy array if needed
    if counts % 100 == 0:
        print('counts:', numpy_array.tolist())

    counts += 1


print("* Done listening")

stream.stop_stream()
stream.close()

p.terminate()

exit(0)




chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = sys.argv[1]

channel_map = (0, 1)

stream_info = pyaudio.PaMacCoreStreamInfo(
    flags = pyaudio.PaMacCoreStreamInfo.paMacCorePlayNice,
    channel_map = channel_map)

stream = p.open(format = FORMAT,
                rate = RATE,
                input = True,
                input_host_api_specific_stream_info = stream_info,
                channels = CHANNELS)

all = []
for i in range(0, RATE / chunk * RECORD_SECONDS):
        data = stream.read(chunk)
        all.append(data)
stream.close()
p.terminate()

data = ''.join(all)
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(data)
wf.close()