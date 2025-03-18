import pyaudio
import logging

logging.basicConfig(level=logging.INFO)

class AudioCapture:
    def __init__(self, rate=44100, chunk=1024, processor=None):
        self.rate = rate
        self.chunk = chunk
        self.p = pyaudio.PyAudio()
        self.processor = processor
        try:
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
                stream_callback=self._audio_callback if processor else None
            )
            logging.info("Audio stream opened successfully.")
            if not processor:
                self.stream.start_stream()
        except OSError as e:
            logging.error(f"Error opening audio stream: {e}")
            raise

    def _audio_callback(self, in_data, frame_count, time_info, status):
        if self.processor:
            self.processor.process_audio(in_data)
        return (in_data, pyaudio.paContinue)

    def read_chunk(self):
        try:
            return self.stream.read(self.chunk, exception_on_overflow=False)
        except OSError as e:
            logging.error(f"Error reading audio stream: {e}")
            return b''

    def close(self):
        try:
            self.stream.stop_stream()
            self.stream.close()
            logging.info("Audio stream closed.")
        except OSError as e:
            logging.error(f"Error closing audio stream: {e}")
        finally:
            self.p.terminate()
            logging.info("PyAudio terminated.")