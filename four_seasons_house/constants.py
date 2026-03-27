from __future__ import annotations

TICKS_PER_BEAT = 480
DEFAULT_BPM = 92  # suite default (allegro-ish); legacy house used 124

# mido channels 0–15 → MIDI ports show as 1–16
DRUM_CH = 9  # channel 10 = General MIDI drums
BASS_CH = 0
LEAD_CH = 1
STAB_CH = 2
PAD_CH = 3
STRINGS_CH = 4  # orchestral ensemble layer (own channel for mixing)

# Full orchestral + modern aux layout (suite)
VIOLIN_CH = 0
VIOLA_CH = 1
CELLO_CH = 2
CONTRABASS_CH = 3
TUTTI_CH = 4  # string ensemble tutti (same role as legacy STRINGS_CH)
HARP_CH = 5
MODERN_CH = 6  # soft EP bed when groove is on

BEATS_PER_BAR = 4

# General MIDI (0-based program numbers)
GM_BASS_PROGRAM = 38  # Synth Bass 1 (legacy house)
GM_LEAD_PROGRAM = 81  # Lead 2 (legacy house)
GM_STAB_PROGRAM = 5  # Electric Piano 2 (legacy house)
GM_PAD_PROGRAM = 90  # Polysynth pad (legacy house)
GM_STRINGS_PROGRAM = 48  # String Ensemble 1 (sustained / orchestral)

# Suite / orchestral + modern
GM_VIOLIN_PROGRAM = 40
GM_VIOLA_PROGRAM = 41
GM_CELLO_PROGRAM = 42
GM_CONTRABASS_PROGRAM = 43
GM_ENSEMBLE_PROGRAM = 49  # Slow Strings — less "FM game" than default ensemble
GM_HARP_PROGRAM = 46
GM_MODERN_EP_PROGRAM = 4  # Electric Piano 1 — subtle hybrid color
