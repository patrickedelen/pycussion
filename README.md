# setup instructions
you will need to download black holehere to create a loopback audio interface:

https://github.com/ExistentialAudio/BlackHole

after that, create a combined MIDI audio interface with your external speakers and the blackhole input.

run the test script bh_test.py to figure out the blackhole interface you want to listen on, update that in waveform.py.

run waveform.py and check it out!



# to run
- activate the pipenv with `pipenv install` and then `pipenv shell`
- navigate to /structured_app and run `python app.py`
- comment out the lighting controller if you don't have one setup properly, you will need an OpenDMX controller
- need to add notes about dependencies for `pyftdi` for lighting control
- if you want audio reactive visuals, you will need to install BlackHole for Mac or use an audio interface
- run `/test_scripts/bh_test.py` to check audio interfaces available and set the index in the `audio_processing.py` file to the index of your interface


## current features
tbd

## upcoming features
- triangle background
- colliding planes background
- expanding particle cube
- cube textures
- make random movement cube smoother

