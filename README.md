# Four Seasons (MIDI)

Python builds **multi-movement MIDI suites** inspired by Vivaldi’s *The Four Seasons* (public domain): **three movements per season**, **per-movement tempos**, **orchestral layout** (violin solo, viola, cello, contrabass, string ensemble, harp), plus a **soft electric-piano bed** and **light modern drums** only in groovier movements — so it reads as **classical first**, with a contemporary pulse underneath, not a 1980s GM “game” loop.

> **Note:** This is still **generated, condensed material** (phrase cells that repeat), not a full engraved score. For a convincing recording, open the MIDI in a **DAW** and replace GM sounds with orchestral libraries.

## Setup

```bash
pip install -e .
```

## Build (default: full suite)

```bash
python generate_midis.py
# or: four-seasons-house
```

Outputs in `output/`:

- `spring_suite.mid`, `summer_suite.mid`, `autumn_suite.mid`, `winter_suite.mid`
- `four_seasons_suite.mid` — all seasons (~318 bars, tempo changes embedded)

Tracks (General MIDI programs): **Violin solo (40)**, **Viola (41)**, **Cello (42)**, **Contrabass (43)**, **Slow strings (49)**, **Harp (46)**, **Electric Piano (4)** bed when drums are active, **drums** (`pulse` or `drive` per movement).

## Legacy short house sketches

```bash
python -m four_seasons_house.cli --legacy-house --bpm 124
```

Writes `*_house.mid` and `four_seasons_house.mid` (original loop-style project).

## Options

```bash
python -m four_seasons_house.cli --output ./out
python -m four_seasons_house.cli --legacy-house --output ./out --bpm 126
```

## Listening

**Winamp / Windows GS synth** will play it, but timbre stays basic. Use a **DAW** + orchestral samples for a result that matches what you hear in your head.
