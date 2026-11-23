"""Make the Reels' sound from scratch (no samples, so no licensing questions):
  public/audio/music.wav   15 s: plucked guitar-like arpeggios over C-G-Am-F, soft bass and shaker
  public/audio/pop.wav     a soft wooden "pop" as each stop appears
  public/audio/whoosh.wav  a gentle airy swish when the finished poster appears
  python3 design/video/sound.py
"""
import numpy as np, wave, os

SR = 44100
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "audio")
rng = np.random.default_rng(7)

def save(name, x):
    x = np.clip(x, -1, 1)
    st = np.stack([x, x], axis=1) if x.ndim == 1 else x
    with wave.open(os.path.join(OUT, name), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())

def pluck(freq, dur, bright=0.5, decay=0.996):
    """Karplus-Strong plucked string."""
    n = int(SR * dur); p = int(SR / freq)
    buf = rng.uniform(-1, 1, p) * (0.5 + bright / 2)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = decay * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out * np.exp(-np.linspace(0, 3.2, n))

def note(m):  # midi -> Hz
    return 440 * 2 ** ((m - 69) / 12)

def lowpass(x, a=0.08):
    y = np.zeros_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc); y[i] = acc
    return y

# ---------------------------------------------------------------- music bed
BPM, DUR = 96, 15.0
beat = 60 / BPM
total = int(SR * DUR)
mix = np.zeros(total)
chords = [[48, 55, 60, 64, 67], [43, 55, 59, 62, 67], [45, 52, 57, 60, 64], [41, 53, 57, 60, 65]]  # C G Am F
pattern = [0, 2, 3, 4, 3, 2, 3, 4]  # which chord note on each eighth
t = 0.0; bar = 0
while t < DUR - 1.2:
    ch = chords[bar % 4]
    # bass on beats 1 and 3
    for b in (0, 2):
        s = int(SR * (t + b * beat))
        if s < total:
            bs = pluck(note(ch[0] - 12 + 12), 1.2, bright=0.2, decay=0.998) * 0.55
            mix[s:s + len(bs)] += bs[: total - s]
    # arpeggio, eighths, with a little swing and velocity variation
    for k, idx in enumerate(pattern):
        when = t + k * beat / 2 + (0.018 if k % 2 else 0)
        s = int(SR * when)
        if s >= total:
            break
        pl = pluck(note(ch[idx] + 12), 0.9, bright=0.65) * (0.32 if k % 2 else 0.4)
        mix[s:s + len(pl)] += pl[: total - s]
    # shaker on the off-beats
    for k in range(4):
        s = int(SR * (t + k * beat + beat / 2))
        n = int(SR * 0.06)
        if s + n < total:
            sh = rng.uniform(-1, 1, n) * np.exp(-np.linspace(0, 6, n))
            mix[s:s + n] += (sh - lowpass(sh, 0.3)) * 0.05
    t += 4 * beat; bar += 1
# the last chord rings out under the end card
s = int(SR * (DUR - 2.4))
for m in chords[0][1:]:
    pl = pluck(note(m + 12), 2.4, bright=0.5, decay=0.9985) * 0.28
    mix[s:s + len(pl)] += pl[: total - s]
# gentle fade in/out, then level
fade = np.ones(total)
fade[: int(SR * 0.4)] = np.linspace(0, 1, int(SR * 0.4))
fade[-int(SR * 1.0):] = np.linspace(1, 0, int(SR * 1.0))
mix *= fade
mix = lowpass(mix, 0.35) * 0.6 + mix * 0.4  # soften the top end
mix /= np.max(np.abs(mix))
mix = np.tanh(mix * 3.0) / np.tanh(3.0) * 0.8  # gentle compression: fuller, still no clipping
# a touch of stereo width: a few ms delay on one side
right = np.concatenate([np.zeros(int(SR * 0.012)), mix[: -int(SR * 0.012)]])
save("music.wav", np.stack([mix, right * 0.95 + mix * 0.05], axis=1))

# ---------------------------------------------------------------- pop
n = int(SR * 0.18)
tt = np.linspace(0, 0.18, n)
f = 520 * np.exp(-tt * 9) + 380
pop = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 28) * 0.5
pop += rng.uniform(-1, 1, n) * np.exp(-tt * 120) * 0.08
save("pop.wav", pop)

# ---------------------------------------------------------------- whoosh
n = int(SR * 0.9)
tt = np.linspace(0, 1, n)
noise = rng.uniform(-1, 1, n)
env = np.sin(np.pi * tt) ** 2
wh = np.zeros(n); acc = 0.0
for i in range(n):  # a sweeping low-pass: brighter in the middle
    a = 0.02 + 0.25 * env[i]
    acc += a * (noise[i] - acc); wh[i] = acc
save("whoosh.wav", wh * env * 0.45 / max(1e-6, np.max(np.abs(wh * env))))
print("made", os.listdir(OUT))
