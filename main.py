import pygame
import sys
import time
import numpy as np
from audio_capture import AudioCapture
from audio_analysis import AudioAnalysis
from visualizer import Visualizer
import logging

logging.basicConfig(level=logging.INFO)

class VoiceArt:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Voice Art 2.0")
        self.fullscreen = False
        self.width, self.height = 1280, 720
        self.setup_display()
        self.analysis = AudioAnalysis()
        self.audio = AudioCapture(processor=self.analysis)
        self.visualizer = Visualizer(self.width, self.height)
        self.clock = pygame.time.Clock()
        self.fps_history = []
        self.last_time = time.time()
        self.running = True
        self.show_debug = False
        self.paused = False
        print("Starting Voice Art 2.0...")
        print("Calibrating audio - please make some noise...")
        self.analysis.calibrate(3)
        print("Calibration complete! Press 'D' for debug, 'F' for fullscreen, 'SPACE' to pause, 'ESC' to exit")

    def setup_display(self):
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.width, self.height = self.screen.get_size()
        else:
            self.screen = pygame.display.set_mode((self.width, self.height))
        self.buffer = pygame.Surface((self.width, self.height))

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.setup_display()
        self.visualizer.resize(self.width, self.height)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_f:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_d:
                    self.show_debug = not self.show_debug
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused

    def update(self):
        if not self.paused:
            volume = self.analysis.get_volume()
            freq_data = self.analysis.get_frequency_data()
            self.visualizer.update(volume, freq_data)

    def render(self):
        self.buffer.fill((0, 0, 0))
        self.visualizer.render(self.buffer)
        if self.show_debug:
            self.render_debug_info()
        self.screen.blit(self.buffer, (0, 0))
        pygame.display.flip()

    def render_debug_info(self):
        current_time = time.time()
        delta = current_time - self.last_time
        self.last_time = current_time
        fps = 1.0 / delta if delta > 0 else 0
        self.fps_history.append(fps)
        if len(self.fps_history) > 60:
            self.fps_history.pop(0)
        avg_fps = sum(self.fps_history) / len(self.fps_history)

        font = pygame.font.SysFont("monospace", 16)
        debug_texts = [
            f"FPS: {avg_fps:.1f}",
            f"Volume: {self.analysis.get_volume():.2f}/{self.analysis.max_volume:.2f}",
            f"Particles: {self.visualizer.particle_count}",
            f"Press 'F' for fullscreen",
            f"Press 'D' to hide debug",
            f"Press 'SPACE' to pause",
            f"Press 'ESC' to exit"
        ]
        y = 10
        for text in debug_texts:
            surface = font.render(text, True, (255, 255, 255))
            self.buffer.blit(surface, (10, y))
            y += 20

    def run(self):
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                self.clock.tick(60)
        finally:
            self.audio.close()
            pygame.quit()

if __name__ == "__main__":
    app = VoiceArt()
    app.run()