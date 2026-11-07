import logging
import math
import time

import numpy as np

logger = logging.getLogger(__name__)

# Lower bounds that keep the normalisation maths away from zero when the
# calibration window is completely silent (muted mic, no input device).
MIN_NOISE_FLOOR = 50.0
MIN_DYNAMIC_SPAN = 500.0

class AudioAnalysis:
    def __init__(self, chunk=1024, rate=44100):
        self.rate = rate
        self.chunk = chunk
        self.max_volume = 5000
        self.noise_floor = 500
        self.volume_history = [0] * 10
        self.fft_size = self.chunk
        self.freq_bands = 16
        self.band_history = np.zeros((self.freq_bands, 5))
        self.audio_data = np.zeros(self.chunk, dtype=np.int16)
        self.volume = 0
        self.freq_data = np.zeros(self.freq_bands)
        self.dynamic_range = 1.0  # New: Adjusts sensitivity dynamically

    def process_audio(self, in_data):
        """Process audio data with improved accuracy."""
        try:
            audio_array = np.frombuffer(in_data, dtype=np.int16)
            self.audio_data = audio_array
            if audio_array.size == 0:
                return
            # Square in float64: squaring int16 samples overflows and wraps.
            rms = float(np.sqrt(np.mean(np.square(audio_array.astype(np.float64)))))
            self.volume_history.pop(0)
            self.volume_history.append(rms)
            self.volume = sum(self.volume_history) / len(self.volume_history)

            # Dynamic range adjustment
            if self.volume > self.noise_floor and self.max_volume > 0:
                self.dynamic_range = max(0.5, min(2.0, self.volume / self.max_volume))

            if len(audio_array) >= self.fft_size:
                window = np.hanning(self.fft_size)
                windowed = audio_array[:self.fft_size] * window
                spectrum = np.abs(np.fft.rfft(windowed))
                spectrum_len = len(spectrum)
                freq_data = np.zeros(self.freq_bands)

                for i in range(self.freq_bands):
                    start = int(math.pow(spectrum_len, i / self.freq_bands))
                    end = int(math.pow(spectrum_len, (i + 1) / self.freq_bands))
                    if end > start:
                        freq_data[i] = np.mean(spectrum[start:end])

                if np.max(freq_data) > 0:
                    freq_data = freq_data / np.max(freq_data) * self.dynamic_range
                self.band_history = np.roll(self.band_history, 1, axis=1)
                self.band_history[:, 0] = freq_data
                self.freq_data = np.mean(self.band_history, axis=1)
        except (ValueError, FloatingPointError) as e:
            logger.error("Audio processing error: %s", e)

    def calibrate(self, duration=3, stream=None):
        """Calibrate with tighter noise floor."""
        print(f"Calibrating for {duration} seconds...")
        volumes = []
        start_time = time.time()

        while time.time() - start_time < duration:
            if stream:
                audio_data = stream.read(self.chunk, exception_on_overflow=False)
                self.process_audio(audio_data)
            volumes.append(self.volume)
            time.sleep(0.1)

        if volumes:
            volumes.sort()
            noise_floor = volumes[int(len(volumes) * 0.2)] * 1.3  # Higher threshold
            max_volume = volumes[int(len(volumes) * 0.9)] * 1.5  # Increased range
            self.noise_floor = max(MIN_NOISE_FLOOR, noise_floor)
            self.max_volume = max(max_volume, self.noise_floor + MIN_DYNAMIC_SPAN)
            print(f"Calibration complete: max_volume={self.max_volume:.2f}, noise_floor={self.noise_floor:.2f}")
        else:
            self.max_volume = 5000
            self.noise_floor = 500
            print("Calibration failed, using default values")

    def get_volume(self):
        """Return tighter normalized volume."""
        if self.volume < self.noise_floor * 1.2:  # Stricter noise gate
            return 0
        span = max(self.max_volume - self.noise_floor, 1e-6)
        normalized = (self.volume - self.noise_floor) / span
        return max(0, min(1, normalized * self.dynamic_range))

    def get_frequency_data(self):
        """Return enhanced frequency data."""
        return self.freq_data
