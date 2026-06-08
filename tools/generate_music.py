from __future__ import annotations

import math
import struct
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.logger import get_logger, setup_logging


SAMPLE_RATE = 22050
VOLUME = 0.22
log = get_logger(__name__)


TRACKS = {
    "menu_loop.wav": {
        "bpm": 118,
        "bass": [110, 110, 146.83, 98, 110, 164.81, 146.83, 98],
        "lead": [440, 0, 493.88, 523.25, 659.25, 0, 587.33, 493.88],
    },
    "game_loop.wav": {
        "bpm": 142,
        "bass": [98, 130.81, 98, 146.83, 110, 146.83, 110, 164.81],
        "lead": [392, 440, 493.88, 587.33, 523.25, 493.88, 440, 392],
    },
    "result_loop.wav": {
        "bpm": 104,
        "bass": [130.81, 164.81, 196, 164.81, 146.83, 174.61, 220, 174.61],
        "lead": [523.25, 659.25, 783.99, 0, 587.33, 698.46, 880, 0],
    },
    "pause_loop.wav": {
        "bpm": 82,
        "bass": [73.42, 0, 87.31, 0, 98, 0, 87.31, 0],
        "lead": [293.66, 0, 329.63, 0, 392, 0, 329.63, 0],
    },
    "options_loop.wav": {
        "bpm": 112,
        "bass": [123.47, 146.83, 164.81, 146.83, 123.47, 185, 164.81, 146.83],
        "lead": [493.88, 554.37, 659.25, 0, 493.88, 739.99, 659.25, 0],
    },
}


def square(freq: float, t: float, duty: float = 0.5) -> float:
    if freq <= 0:
        return 0.0
    phase = (t * freq) % 1.0
    return 1.0 if phase < duty else -1.0


def envelope(step_pos: float) -> float:
    attack = 0.04
    release = 0.16
    if step_pos < attack:
        return step_pos / attack
    if step_pos > 1.0 - release:
        return max(0.0, (1.0 - step_pos) / release)
    return 1.0


def render_track(path: Path, bpm: int, bass: list[float], lead: list[float]) -> None:
    beat = 60.0 / bpm
    step_duration = beat / 2.0
    steps = len(bass) * 4
    total_samples = int(steps * step_duration * SAMPLE_RATE)
    frames = bytearray()

    for i in range(total_samples):
        t = i / SAMPLE_RATE
        step = int(t / step_duration) % len(bass)
        step_pos = (t % step_duration) / step_duration
        env = envelope(step_pos)
        bass_sample = square(bass[step], t, 0.38) * 0.45
        lead_freq = lead[step]
        lead_sample = square(lead_freq, t, 0.22) * 0.30
        pulse = 0.12 if int(t / (step_duration / 2.0)) % 2 == 0 else -0.04
        sample = (bass_sample + lead_sample + pulse) * env * VOLUME
        sample = max(-1.0, min(1.0, sample))
        frames.extend(struct.pack("<h", int(sample * 32767)))

    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(frames)


def main() -> None:
    setup_logging()
    out_dir = Path("assets/audio/music")
    for filename, spec in TRACKS.items():
        render_track(out_dir / filename, spec["bpm"], spec["bass"], spec["lead"])
        log.info("Wrote %s", out_dir / filename)


if __name__ == "__main__":
    main()
