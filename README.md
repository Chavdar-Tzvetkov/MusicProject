# Four Seasons (MIDI)

Python builds **long-form, multi-movement MIDI** (~**224–276 bars per season**, ~**900+ bars** full suite) inspired by Vivaldi’s *The Four Seasons* (public domain), tuned for a **YouTube / streaming-era** listen: orchestral hooks + **new-age air** (wide pad washes, **celesta** sparkles) + drops that lean **Gen Z–friendly** (weighted kicks, **trap-style 16th hats**, rim ghosts, softer snare — think cinematic remix / study-beats energy, not chiptune). Style-wise it’s in the spirit of modern classical remix channels ([example vibe you sent](https://www.youtube.com/watch?v=Q5ZjZCLu610)), not a copy of that track.

**Default (`--vibe genz`, 0.7+):** extra tracks **Atmos pad** (GM 88) + **Celesta sparkle** (GM 8), **wider** string stacks, hybrid bed uses the **new-age pad** patch instead of bright EP, tempos scaled ~**4% slower** for a slightly dreamier feel, and **genz banger** drums on the drop. Use `--vibe classic` for the previous “heavier four-on-floor snare” kit and EP-only bed without the extra layers.

> **Note:** This is still **generated, condensed material** (phrase cells + AB alternation), not a full score. For the sound in your head, open the MIDI in a **DAW**: swap GM for **Spitfire / orchestral libraries**, **massive verbs**, and a **real 808** on the Sub track.

## Setup

```bash
pip install -e .
```

## Build (default: full suite, GenZ new-age)

```bash
python generate_midis.py
# or: four-seasons-house
```

```bash
python -m four_seasons_house.cli --vibe classic
```

Outputs in `output/`:

- `spring_suite.mid`, `summer_suite.mid`, `autumn_suite.mid`, `winter_suite.mid`
- `four_seasons_suite.mid` — all seasons (~900+ bars, tempo changes embedded)

**`--vibe genz` (default):** Violin, viola, cello, contrabass, ensemble, harp, **new-age pad bed (88)**, **atmos (88)**, **celesta (8)**, sub **(38)**, drums (intro pocket → **genz drop**). **`--vibe classic`:** EP bed **(4)**, no atmos/celesta tracks, original **banger** drum bar.

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
