from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

from .automation import (
    add_filter_sweep_triangle,
    add_pad_sidechain_pump,
    add_program_change,
)
from .constants import (
    BASS_CH,
    BEATS_PER_BAR,
    DRUM_CH,
    DEFAULT_BPM,
    GM_BASS_PROGRAM,
    GM_LEAD_PROGRAM,
    GM_PAD_PROGRAM,
    GM_STAB_PROGRAM,
    GM_STRINGS_PROGRAM,
    LEAD_CH,
    PAD_CH,
    STAB_CH,
    STRINGS_CH,
    TICKS_PER_BEAT,
)
from .midi_util import NoteEvent, add_notes_to_events, merge_to_deltas
from .patterns import (
    bass_pattern_for_section,
    chord_stabs_for_section,
    pad_chords_for_section,
    section_drums,
    strings_classical_layer_for_section,
)
from .seasons import SeasonSpec, pad_voicings_for


def _lead_events_for_season(cursor: int, spec: SeasonSpec) -> list[NoteEvent]:
    hook = spec.lead_builder()
    if not hook:
        return []
    period = max(n.start + n.duration for n in hook)
    if period <= 0:
        return []
    section_len = spec.bars * BEATS_PER_BAR * TICKS_PER_BEAT
    out: list[NoteEvent] = []
    t = 0
    while t < section_len:
        for ne in hook:
            abs_start = cursor + t + ne.start
            if abs_start >= cursor + section_len:
                continue
            out.append(
                NoteEvent(
                    abs_start,
                    ne.duration,
                    ne.pitch,
                    ne.velocity,
                )
            )
        t += period
    return out


def compile_midi(
    path: Path | str,
    specs: Sequence[SeasonSpec],
    *,
    title: str,
    bpm: float = DEFAULT_BPM,
) -> int:
    """Write a Type-1 MIDI file. Returns total bar count."""
    path = Path(path)
    mid = MidiFile(type=1, ticks_per_beat=TICKS_PER_BEAT)
    tempo = bpm2tempo(round(bpm))

    meta = MidiTrack()
    meta.append(MetaMessage("set_tempo", tempo=tempo, time=0))
    meta.append(
        MetaMessage(
            "time_signature",
            numerator=4,
            denominator=4,
            clocks_per_click=24,
            notated_32nd_notes_per_beat=8,
            time=0,
        )
    )
    meta.append(MetaMessage("track_name", name=title, time=0))
    mid.tracks.append(meta)

    drums = MidiTrack()
    drums.append(MetaMessage("track_name", name="Drums (GM)", time=0))
    bass_t = MidiTrack()
    bass_t.append(MetaMessage("track_name", name="Bass", time=0))
    lead_t = MidiTrack()
    lead_t.append(MetaMessage("track_name", name="Lead", time=0))
    stab_t = MidiTrack()
    stab_t.append(MetaMessage("track_name", name="Stabs", time=0))
    pad_t = MidiTrack()
    pad_t.append(MetaMessage("track_name", name="Pad", time=0))
    strings_t = MidiTrack()
    strings_t.append(MetaMessage("track_name", name="Strings (GM)", time=0))

    drum_events: list[tuple[int, Message]] = []
    bass_events: list[tuple[int, Message]] = []
    lead_events: list[tuple[int, Message]] = []
    stab_events: list[tuple[int, Message]] = []
    pad_events: list[tuple[int, Message]] = []
    string_events: list[tuple[int, Message]] = []

    bar_len = BEATS_PER_BAR * TICKS_PER_BEAT
    total_bars = sum(s.bars for s in specs)
    total_len = total_bars * bar_len
    cursor = 0

    add_program_change(bass_events, BASS_CH, GM_BASS_PROGRAM, 0)
    add_program_change(lead_events, LEAD_CH, GM_LEAD_PROGRAM, 0)
    add_program_change(stab_events, STAB_CH, GM_STAB_PROGRAM, 0)
    add_program_change(pad_events, PAD_CH, GM_PAD_PROGRAM, 0)
    add_program_change(string_events, STRINGS_CH, GM_STRINGS_PROGRAM, 0)

    add_filter_sweep_triangle(lead_events, LEAD_CH, total_len)

    for spec in specs:
        drum_events.extend(section_drums(cursor, spec.bars))
        add_notes_to_events(
            bass_events,
            BASS_CH,
            bass_pattern_for_section(cursor, spec.bars, spec.bass_roots),
        )
        chord_stabs_for_section(
            stab_events,
            STAB_CH,
            cursor,
            spec.bars,
            list(spec.stab_voicings),
        )
        pad_chords_for_section(
            pad_events,
            PAD_CH,
            cursor,
            spec.bars,
            pad_voicings_for(spec),
        )
        strings_classical_layer_for_section(
            string_events,
            STRINGS_CH,
            cursor,
            spec.bars,
            list(spec.stab_voicings),
        )
        add_notes_to_events(lead_events, LEAD_CH, _lead_events_for_season(cursor, spec))
        cursor += spec.bars * bar_len

    add_pad_sidechain_pump(pad_events, PAD_CH, total_bars)

    drums.extend(merge_to_deltas(drum_events))
    bass_t.extend(merge_to_deltas(bass_events))
    lead_t.extend(merge_to_deltas(lead_events))
    stab_t.extend(merge_to_deltas(stab_events))
    pad_t.extend(merge_to_deltas(pad_events))
    strings_t.extend(merge_to_deltas(string_events))

    mid.tracks.extend([drums, bass_t, lead_t, stab_t, pad_t, strings_t])
    path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(str(path))
    return total_bars


def build_all(
    output_dir: Path | str,
    *,
    bpm: float = DEFAULT_BPM,
) -> None:
    """Write one MIDI per season plus the full suite."""
    from .seasons import ALL_SEASONS

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for spec in ALL_SEASONS:
        filename = f"{spec.slug}_house.mid"
        bars = compile_midi(
            output_dir / filename,
            [spec],
            title=f"{spec.display_name} - house sketch",
            bpm=bpm,
        )
        print(f"Wrote {output_dir / filename}  ({bars} bars @ {bpm:.0f} BPM)")

    suite_bars = compile_midi(
        output_dir / "four_seasons_house.mid",
        list(ALL_SEASONS),
        title="Four Seasons - house suite",
        bpm=bpm,
    )
    print(f"Wrote {output_dir / 'four_seasons_house.mid'}  ({suite_bars} bars @ {bpm:.0f} BPM)")
