import numpy as np
from scipy.io import wavfile

SR = 44100
DURATION = 24.2
N = int(SR * DURATION)

t = np.linspace(0, DURATION, N, endpoint=False)
out = np.zeros(N)

chords = [
    [220.00, 261.63, 329.63, 392.00, 493.88],   # Am9
    [174.61, 220.00, 261.63, 329.63],           # Fmaj7
    [130.81, 164.81, 196.00, 246.94],           # Cmaj7
    [196.00, 246.94, 293.66, 440.00],           # Gadd9 (lift into CTA)
]
seg = DURATION / len(chords)

def env_segment(local_t, seg_len, attack=0.6, release=0.9):
    e = np.ones_like(local_t)
    a_mask = local_t < attack
    e[a_mask] = local_t[a_mask] / attack
    r_start = seg_len - release
    r_mask = local_t > r_start
    e[r_mask] = np.clip((seg_len - local_t[r_mask]) / release, 0, 1)
    return e

pad = np.zeros(N)
for i, chord in enumerate(chords):
    start = i * seg
    end = start + seg
    mask = (t >= start) & (t < end)
    local_t = t[mask] - start
    envelope = env_segment(local_t, seg)
    chord_wave = np.zeros(local_t.shape[0])
    for note_hz in chord:
        chord_wave += np.sin(2 * np.pi * note_hz * local_t) * (1.0 / len(chord))
    pad[mask] += chord_wave * envelope

pad *= 0.16

# Sparse plucked "piano-like" notes: fundamental + light harmonics, exponential decay
pluck = np.zeros(N)
note_times = np.arange(0.4, DURATION - 0.5, 0.95)
rng = np.random.default_rng(42)
for i, nt in enumerate(note_times):
    chord_idx = min(int(nt // seg), len(chords) - 1)
    chord = chords[chord_idx]
    note_hz = chord[i % len(chord)] * (2 if i % 3 == 0 else 1)  # octave lift occasionally
    dur = 1.1
    start_i = int(nt * SR)
    end_i = min(start_i + int(dur * SR), N)
    local_n = end_i - start_i
    if local_n <= 0:
        continue
    local_t = np.linspace(0, dur, local_n, endpoint=False)[:local_n]
    decay = np.exp(-local_t * 3.2)
    tone = (
        np.sin(2 * np.pi * note_hz * local_t) * 1.0
        + np.sin(2 * np.pi * note_hz * 2 * local_t) * 0.25
        + np.sin(2 * np.pi * note_hz * 3 * local_t) * 0.08
    )
    pluck[start_i:end_i] += tone * decay * 0.09

mix = pad + pluck

# Master envelope: fade in / fade out
fade_in_len = int(1.0 * SR)
fade_out_len = int(1.5 * SR)
mix[:fade_in_len] *= np.linspace(0, 1, fade_in_len)
mix[-fade_out_len:] *= np.linspace(1, 0, fade_out_len)

# gentle limiter
mix = np.tanh(mix * 1.4) * 0.9

stereo = np.stack([mix, mix], axis=1)
stereo_int16 = np.clip(stereo * 32767, -32768, 32767).astype(np.int16)

wavfile.write("/Users/juliaknyazskaya/glp1-guide-site/ad-creatives/video/music.wav", SR, stereo_int16)
print("saved music.wav", DURATION, "s")
