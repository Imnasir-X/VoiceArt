# Voice Art

Voice Art is an interactive, artistic project built with Python that visualizes sound input—such as your voice, claps, or any audio signal—as dynamic bubbles. These bubbles take on various shapes and structures, spreading across the screen while sound is active and halting when the sound stops. The background features a mesmerizing Three.js effect inspired by our solar system, adding a cosmic vibe to the experience.

## Features
- **Sound-to-Visual Magic**: Creates bubbles that change shape and spread based on real-time sound input.
- **Dynamic Response**: Visuals evolve with sound and pause when silence returns.
- **Cosmic Background**: A Three.js-powered solar system effect sets the stage.
- **Artistic Exploration**: Perfect for experimenting with sound and visuals.

## Files
- `voice_art.py`: The core Python script driving the project (assumed—update if different).
- (Additional files like `background.js`, audio assets, or HTML files will be added once you share the `dir` output.)

## Requirements
- **Python 3.x**: The main runtime.
- **Libraries**:
  - `pyaudio`: For capturing real-time audio input.
  - `numpy`: For processing sound frequencies.
  - `pygame`: For rendering visuals (assumed—adjust if you use something else).
  - `Three.js`: Integrated via a web component (assumed—confirm if pure Python).
- Install dependencies:
  ```bash
  pip install pyaudio numpy pygame
