# Four Seasons (MIDI)

Python builds **long-form, multi-movement MIDI** (~**224–276 bars per season**, ~**900+ bars** full suite) inspired by Vivaldi’s *The Four Seasons* (public domain), tuned for a **YouTube / streaming-era** listen: orchestral hooks + **new-age air** (wide pad washes, **celesta** sparkles) + drops that lean **Gen Z–friendly** (weighted kicks, **trap-style 16th hats**, rim ghosts, softer snare). Style-wise it’s in the spirit of modern classical remix channels ([example vibe you sent](https://www.youtube.com/watch?v=Q5ZjZCLu610)), not a copy of that track.

**v0.8:** **Continuo harpsichord** track (Baroque rhythm section), string ensemble on **GM 48** for better behaviour with sampled GM soundfonts, plus a **FluidSynth renderer** so you can hear **real .sf2 samples** instead of the Windows “toy” synth.

**v0.9:** **`--export-orchestral-stems`** — splits each `*_suite.mid` into **separate stem MIDIs** (solo, ripieno viola/tutti, bassi, continuo, harp, pads, sparkle, sub, drums). Melodic stems use **MIDI channel 0**; drums use **channel 9**, so you can audition each layer in **FluidSynth** (or any simple player) **without a DAW**.

**Default (`--vibe genz`):** Atmos (88), celesta (8), wider strings, new-age pad bed, genz drop drums. **`--vibe classic`:** EP bed, no atmos/celesta, heavier classic banger kit.

> MIDI files are **not** audio — they are a map. The **art** you’re chasing lives in **performance + samples** (or **live strings**). This repo gives structure; your **soundfont / DAW** gives the “original” warmth.

---

## What “the original sound” of *The Four Seasons* actually is

Vivaldi wrote these concerti in the **early Italian Baroque** (~1725). The **“authentic” sound world** is not Romantic Hollywood strings. It’s closer to:

- **Small string band** (not a 70-player symphony), **solo violin** out front — agile, **crisp**, a bit **raw**.
- **Basso continuo**: usually **harpsichord** (or organ) **plus** cello/bass **doubling the harmony** — a dry, articulate **plucked/struck** keyboard, not a giant ambient pad.
- **Gut strings** in historically informed recordings: **lighter**, **faster decay**, **clearer texture**; **dynamics** are often more **terraced** than late-Romantic swells.
- The music is **programmatic** (birds, storms, drunk dancing, chattering teeth) — so **character** and **articulation** matter as much as “lushness.”

Your hybrid arrangement adds **modern** layers (pads, drums, sub). That will never *be* Neville Marriner or Il Giardino Armonico — but **adding continuo** and **rendering with a decent orchestral SF2** moves the MIDI **toward** that Baroque backbone while keeping your remix idea.

---

## Real instrument samples (recommended path)

1. **Download a General MIDI `.sf2`** with real **strings + harpsichord** (avoid relying on FM synth). Good starting points to browse:
   - [Musical Artifacts — SF2](https://musical-artifacts.com/?formats=sf2) (filter by strings / classical / ensemble)
   - Community favourites people use with FluidSynth include large GM banks such as **FluidR3 GM** / **GeneralUser GS** (search for the project pages; both are widely linked from audio forums).

2. **Install [FluidSynth](https://www.fluidsynth.org/)** (command-line audio engine).

3. **Render WAVs from your generated MIDI:**

```bash
python generate_midis.py
python render_fluidsynth.py --sf2 "C:\path\to\your\soundfont.sf2"
```

WAV files appear under `output/wav/`. That playback is **sample-based**, not Winamp’s built-in GM.

4. **No DAW? Use orchestral stems + FluidSynth per part:**

```bash
python -m four_seasons_house.cli --export-orchestral-stems
```

This writes e.g. `output/stems/spring_suite/solo.mid`, `ripieno_tutti.mid`, `continuo.mid`, … (classic **genz** skips missing atmos/sparkle automatically). Render them all to WAV:

```bash
python render_fluidsynth.py --sf2 "C:\path\to\your\soundfont.sf2" --midi-dir output --recursive --out-dir output/wav_stems
```

You get one **.wav per stem**; listen in **VLC / foobar** or stitch later — still no producer software required.

4. **Best possible quality:** import the same `.mid` into **Reaper / FL / Ableton** and load **Spitfire BBC SO Discover** (free tier when available), **VSCO 2**, **labs** strings, etc. — then mute or replace the GM “Sub” track with a real 808 if you want.

---

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
- `four_seasons_suite.mid` — all seasons (~900+ bars)

**Tracks (typical `genz`):** violin, viola, cello, contrabass, **string ensemble (48)**, harp, **continuo harpsichord (6)** on its own channel, new-age pad / EP (classic), atmos, celesta, sub, drums.

## Legacy short house sketches

```bash
python -m four_seasons_house.cli --legacy-house --bpm 124
```

## Options

```bash
python -m four_seasons_house.cli --output ./out --vibe genz
python -m four_seasons_house.cli --legacy-house --output ./out --bpm 126
```

## Listening

**Winamp / Windows GS synth** = quick check only. For the sound you describe, use **`render_fluidsynth.py`** or a **DAW** with real libraries.
