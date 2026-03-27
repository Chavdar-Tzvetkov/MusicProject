from __future__ import annotations

TICKS_PER_BEAT = 480
DEFAULT_BPM = 124

# mido channels 0–15 → MIDI ports show as 1–16
DRUM_CH = 9  # channel 10 = General MIDI drums
BASS_CH = 0
LEAD_CH = 1
STAB_CH = 2
PAD_CH = 3
STRINGS_CH = 4  # orchestral ensemble layer (own channel for mixing)

BEATS_PER_BAR = 4

# General MIDI (0-based program numbers)
GM_BASS_PROGRAM = 38  # Synth Bass 1
GM_LEAD_PROGRAM = 81  # Lead 2 (sawtooth)
GM_STAB_PROGRAM = 5  # Electric Piano 2
GM_PAD_PROGRAM = 90  # Polysynth pad
GM_STRINGS_PROGRAM = 48  # String Ensemble 1 (sustained / orchestral)
