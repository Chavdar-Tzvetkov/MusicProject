# Four Seasons House (MIDI)

Python generates **house/EDM-style MIDI**: drums (General MIDI), bass, chord stabs, pad, **orchestral strings** (phased classical-style layers), and simplified seasonal lead hooks inspired by Vivaldi’s *Four Seasons* (public domain).

## Setup

```bash
pip install -e .
```

(or `pip install -r requirements.txt` and run from the project root so `four_seasons_house` imports)

## Build MIDI files

```bash
python generate_midis.py
```

or

```bash
four-seasons-house
```

Outputs go to `output/`:

- `spring_house.mid`
- `summer_house.mid`
- `autumn_house.mid`
- `winter_house.mid`
- `four_seasons_house.mid` (full suite)

Open in any DAW; assign drum kit, bass, piano/stack for stabs, pad, a **string ensemble** on the Strings track, and a lead synth.

The MIDI also includes **General MIDI program changes** (bass / lead / stabs / pad), a **CC 74 cutoff sweep** on the lead (map to your synth’s filter if it uses a different CC), and **CC 11 expression dips** on the pad in sync with four-on-the-floor kicks for a sidechain-style pump.

## Options

```bash
python -m four_seasons_house.cli --output ./out --bpm 126
```

## Note

Melodies are **short arrangements in the spirit** of each concerto, not literal transcriptions.
