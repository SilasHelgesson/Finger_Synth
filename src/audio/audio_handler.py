import threading
import numpy as np
import sounddevice as sd
import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

audio_config_path = BASE_DIR / "config" / "audio_config.yaml"
with open(audio_config_path, "r") as file:
    audio_config = yaml.safe_load(file)


def semitone_to_hz(n):
    return 440.0 * (2.0 ** ((n - 69) / 12.0))


class Voice:
    """Richer synth voice: harmonics + vibrato + smooth envelope."""

    def __init__(self, freq):
        self.freq       = freq
        self.phase      = 0.0
        self.amp        = 0.0
        self.target_amp = 0.0

        self.vibrato_phase = 0.0

    def render(self, n_frames):
        vib = 0.003 * np.sin(self.vibrato_phase)
        self.vibrato_phase += 0.04 * n_frames

        freq = self.freq * (1.0 + vib)

        phases = self.phase + 2 * np.pi * freq * np.arange(n_frames) / audio_config["sample_rate"]

        sine  = np.sin(phases)
        sine2 = np.sin(2 * phases)
        saw   = 2.0 * (phases / (2*np.pi) % 1.0) - 1.0

        samples = (
            0.5 * sine +
            0.25 * sine2 +
            0.25 * saw
        )

        samples = np.tanh(samples * 1.3)

        ATTACK  = 1.0 / 120.0
        RELEASE = 1.0 / 400.0

        amps = np.empty(n_frames, dtype=np.float32)
        amp  = self.amp
        t    = self.target_amp

        for i in range(n_frames):
            if amp < t:
                amp += ATTACK * (t - amp)
            else:
                amp += RELEASE * (t - amp)
            amps[i] = amp

        self.amp   = amp
        self.phase = phases[-1] % (2 * np.pi)

        return (samples * amps).astype(np.float32)


class AudioEngine:
    def __init__(self):
        self.voices = {}
        self.lock   = threading.Lock()

        for hand, fingers in audio_config["note_semitones"].items():
            for finger, semitone in fingers.items():
                self.voices[(hand, finger)] = Voice(semitone_to_hz(semitone))

        self.stream = sd.OutputStream(
            samplerate=audio_config["sample_rate"],
            blocksize=audio_config["block_size"],
            channels=1,
            dtype="float32",
            callback=self._callback,
        )
        self.stream.start()

    def _callback(self, outdata, frames, time_info, status):
        """Called by sounddevice on a high-priority audio thread."""
        mixed = np.zeros(frames, dtype=np.float32)
        with self.lock:
            for voice in self.voices.values():
                mixed += voice.render(frames)

        # Soft clip to prevent any clipping distortion
        np.tanh(mixed, out=mixed)
        outdata[:, 0] = mixed

    def set_note(self, hand, finger, on: bool, volume: float):
        key = (hand, finger)
        if key not in self.voices:
            return
        target = volume * 0.28 if on else 0.0
        with self.lock:
            self.voices[key].target_amp = target

    def stop(self):
        self.stream.stop()
        self.stream.close()