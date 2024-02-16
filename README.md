# Backing up a Pokemon Red save file with ACE and a Microphone

## What is this?

For a complete explanation and guide, see [the writeup](https://xlixic.github.io/poke-save-backup)

## How do I use the code?

The `sending` folder contains the assembly code to read and send a save file over audio. If you have RGBDS installed you can compile it into a standalone ROM using `make`.

The `receiving` folder contains the Python script to decode an audio recording. If you have a wav file called `recording.wav` you can decode it using `python decode_save_file.py recording.wav`.