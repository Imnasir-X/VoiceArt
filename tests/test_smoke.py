"""Headless smoke tests: no microphone or display needed."""

import numpy as np
import pygame

from audio_analysis import AudioAnalysis
from visualizer import MAX_PARTICLES, Visualizer


def _tone(freq=440.0, amplitude=20000, chunk=1024, rate=44100):
    t = np.arange(chunk) / rate
    return (np.sin(2 * np.pi * freq * t) * amplitude).astype(np.int16).tobytes()


def test_loud_tone_gives_volume_and_spectrum():
    analysis = AudioAnalysis()
    for _ in range(10):
        analysis.process_audio(_tone())
    assert analysis.volume > analysis.noise_floor
    assert 0 < analysis.get_volume() <= 1
    freq = analysis.get_frequency_data()
    assert freq.shape == (analysis.freq_bands,)
    assert freq.max() > 0


def test_rms_does_not_overflow_int16():
    analysis = AudioAnalysis()
    for _ in range(10):
        analysis.process_audio(_tone(amplitude=32000))
    # A full-scale sine has an RMS of roughly amplitude / sqrt(2).
    assert 20000 < analysis.volume < 32768


def test_silent_calibration_keeps_sane_bounds():
    analysis = AudioAnalysis()
    analysis.calibrate(duration=0.3)
    assert analysis.noise_floor > 0
    assert analysis.max_volume > analysis.noise_floor
    assert analysis.get_volume() == 0


def test_visualizer_renders_frames_headless():
    pygame.init()
    try:
        surface = pygame.Surface((640, 360))
        vis = Visualizer(640, 360)
        freq = np.linspace(0.2, 1.0, 16)
        for _ in range(60):
            vis.update(1.0, freq)
            vis.render(surface)
        assert 0 < vis.particle_count <= MAX_PARTICLES
        vis.resize(320, 240)
        vis.update(0.0, np.zeros(16))
        vis.render(pygame.Surface((320, 240)))
    finally:
        pygame.quit()
