import soundcard as sc
import soundfile as sf
import queue
import threading
import numpy as np
import time
from typing import Optional




class SystemAudioRecorder:
    def __init__(
        self,
        filename: str,
        samplerate: int = 48000,
        channels: int = 2,
        blocksize: int = 1024,
        subtype: str = "PCM_16",
        logger=print,
    ):
        self.filename = filename
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.subtype = subtype
        self.logger = logger

        self._queue: queue.Queue[np.ndarray | None] = queue.Queue(maxsize=50)
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()
        
        self._writer_thread: Optional[threading.Thread] = None

        self._mic = self._init_loopback_mic()

    # ---------- device init ----------

    def _init_loopback_mic(self):
        try:
            speaker = sc.default_speaker()
            if speaker is None:
                raise RuntimeError("No default speaker found")

            mic = sc.get_microphone(speaker.name, include_loopback=True)
            if mic is None:
                raise RuntimeError("Loopback microphone not found")

            return mic

        except Exception as e:
            raise RuntimeError(
                "Failed to initialize system audio loopback device"
            ) from e

    # ---------- writer thread ----------

    def _writer(self):
        try:
            with sf.SoundFile(
                self.filename,
                mode="w",
                samplerate=self.samplerate,
                channels=self.channels,
                subtype=self.subtype,
            ) as f:

                while not self._stop_event.is_set():
                    block = self._queue.get()
                    if block is None:
                        break
                    f.write(block)

                while not self._queue.empty():
                    block = self._queue.get_nowait()
                    if block is not None:
                        f.write(block)

        except Exception as e:
            self.logger(f"[Writer error] {e}")

    # ---------- public API ----------
    
    def pause(self):
        self.logger("Recording paused")
        self._pause_event.clear()

    def resume(self):
        self.logger("Recording resumed")
        self._pause_event.set()

    def start(self):
        self.logger("Starting system audio recording...")

        self._stop_event.clear()
        self._writer_thread = threading.Thread(
            target=self._writer,
            name="AudioWriter",
            daemon=True,
        )
        self._writer_thread.start()

        try:
            with self._mic.recorder(
                samplerate=self.samplerate,
                channels=self.channels,
            ) as rec:

                while not self._stop_event.is_set():
                    self._pause_event.wait()
                    
                    data = rec.record(self.blocksize)
                    
                    try:
                        self._queue.put(data.copy(), timeout=0.5)
                    except queue.Full:
                        self.logger("Audio queue overflow — dropping frame")

                    if not isinstance(data, np.ndarray):
                        raise RuntimeError("Invalid audio buffer received")

        except KeyboardInterrupt:
            self.logger("Recording interrupted by user")

        except Exception as e:
            self.logger(f"[Recorder error] {e}")

        finally:
            self.stop()

    def stop(self):
        if self._stop_event.is_set():
            return

        self.logger("Stopping recording...")
        self._stop_event.set()

        self._queue.put(None)

        if self._writer_thread:
            self._writer_thread.join(timeout=5)

        self.logger(f"Saved audio to: {self.filename}")
