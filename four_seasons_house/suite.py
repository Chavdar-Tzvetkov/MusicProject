from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

from .constants import (
    BEATS_PER_BAR,
    CELLO_CH,
    CONTRABASS_CH,
    HARP_CH,
    MODERN_CH,
    TICKS_PER_BEAT,
    TUTTI_CH,
    VIOLA_CH,
    VIOLIN_CH,
    GM_CELLO_PROGRAM,
    GM_CONTRABASS_PROGRAM,
    GM_ENSEMBLE_PROGRAM,
    GM_HARP_PROGRAM,
    GM_MODERN_EP_PROGRAM,
    GM_VIOLA_PROGRAM,
    GM_VIOLIN_PROGRAM,
)
from .automation import add_program_change
from .midi_util import NoteEvent, add_chord_events, add_notes_to_events, merge_to_deltas, tile_note_events
from .patterns import _open_string_voicing, movement_drums
from .suite_seasons import ALL_SUITE_SEASONS, SeasonSuiteSpec


def _build_meta_track(title: str, tempo_points: list[tuple[int, float]]) -> MidiTrack:
    items: list[tuple[int, int, MetaMessage]] = []
    items.append((0, 0, MetaMessage("track_name", name=title, time=0)))
    items.append(
        (
            0,
            1,
            MetaMessage(
                "time_signature",
                numerator=4,
                denominator=4,
                clocks_per_click=24,
                notated_32nd_notes_per_beat=8,
                time=0,
            ),
        )
    )
    for tick, bpm in tempo_points:
        items.append(
            (tick, 2, MetaMessage("set_tempo", tempo=bpm2tempo(round(bpm)), time=0))
        )
    items.sort(key=lambda x: (x[0], x[1]))
    track = MidiTrack()
    last = 0
    for tick, _pri, msg in items:
        track.append(msg.copy(time=tick - last))
        last = tick
    return track


def _cello_bassline(start: int, bars: int, roots: tuple[int, ...]) -> list[NoteEvent]:
    bl = BEATS_PER_BAR * TICKS_PER_BEAT
    out: list[NoteEvent] = []
    for bar in range(bars):
        r = roots[bar % len(roots)]
        out.append(NoteEvent(start + bar * bl, bl - 32, r, 80))
    return out


def _contrabass_doubles(start: int, bars: int, roots: tuple[int, ...]) -> list[NoteEvent]:
    beat = TICKS_PER_BEAT
    bl = BEATS_PER_BAR * beat
    out: list[NoteEvent] = []
    for bar in range(bars):
        r = roots[bar % len(roots)] - 12
        r = max(28, min(50, r))
        out.append(NoteEvent(start + bar * bl, 2 * beat - 24, r, 72))
    return out


def _viola_inner(
    events: list[tuple[int, Message]],
    start: int,
    bars: int,
    harmony: tuple[tuple[int, int, int], ...],
) -> None:
    beat = TICKS_PER_BEAT
    bl = BEATS_PER_BAR * beat
    for bar in range(bars):
        triad = harmony[bar % len(harmony)]
        i1 = min(76, triad[1] + 12)
        i2 = min(78, triad[2] + 12)
        add_chord_events(events, VIOLA_CH, start + bar * bl, 2 * beat - 22, (i1,), 52)
        add_chord_events(events, VIOLA_CH, start + bar * bl + 2 * beat, 2 * beat - 22, (i2,), 48)


def _harp_arpeggios(
    events: list[tuple[int, Message]],
    start: int,
    bars: int,
    harmony: tuple[tuple[int, int, int], ...],
) -> None:
    e8 = TICKS_PER_BEAT // 2
    bl = BEATS_PER_BAR * TICKS_PER_BEAT
    for bar in range(bars):
        triad = harmony[bar % len(harmony)]
        a, b, c = triad
        chips = [(a + 24), (b + 24), (c + 24), (b + 24), (c + 28), (a + 28)]
        t = start + bar * bl
        for i, p in enumerate(chips):
            if t + i * e8 >= start + (bar + 1) * bl:
                break
            add_chord_events(events, HARP_CH, t + i * e8, e8 - 14, (min(88, p),), 40)


def _modern_ep_bed(
    events: list[tuple[int, Message]],
    start: int,
    bars: int,
    harmony: tuple[tuple[int, int, int], ...],
) -> None:
    bl = BEATS_PER_BAR * TICKS_PER_BEAT
    for bar in range(bars):
        triad = harmony[bar % len(harmony)]
        voicing = tuple(min(74, n + 7) for n in triad)
        add_chord_events(events, MODERN_CH, start + bar * bl, bl - 24, voicing, 26)


def _flatten_tempo_points(seasons: Sequence[SeasonSuiteSpec]) -> tuple[list[tuple[int, float]], int, int]:
    bar_len = BEATS_PER_BAR * TICKS_PER_BEAT
    tempo_points: list[tuple[int, float]] = []
    cursor = 0
    total_bars = 0
    for season in seasons:
        for mov in season.movements:
            tempo_points.append((cursor, mov.bpm))
            cursor += mov.bars * bar_len
            total_bars += mov.bars
    return tempo_points, cursor, total_bars


def compile_suite_midi(
    path: Path | str,
    seasons: Sequence[SeasonSuiteSpec],
    *,
    title: str,
) -> tuple[int, int]:
    """Returns (total_bars, total_ticks)."""
    path = Path(path)
    tempo_points, total_ticks, total_bars = _flatten_tempo_points(seasons)

    mid = MidiFile(type=1, ticks_per_beat=TICKS_PER_BEAT)
    mid.tracks.append(_build_meta_track(title, tempo_points))

    violin_t = MidiTrack()
    violin_t.append(MetaMessage("track_name", name="Violin solo", time=0))
    viola_t = MidiTrack()
    viola_t.append(MetaMessage("track_name", name="Viola", time=0))
    cello_t = MidiTrack()
    cello_t.append(MetaMessage("track_name", name="Cello", time=0))
    cb_t = MidiTrack()
    cb_t.append(MetaMessage("track_name", name="Contrabass", time=0))
    tutti_t = MidiTrack()
    tutti_t.append(MetaMessage("track_name", name="String ensemble", time=0))
    harp_t = MidiTrack()
    harp_t.append(MetaMessage("track_name", name="Harp", time=0))
    modern_t = MidiTrack()
    modern_t.append(MetaMessage("track_name", name="Modern bed (EP)", time=0))
    drums_t = MidiTrack()
    drums_t.append(MetaMessage("track_name", name="Pulse drums", time=0))

    ve: list[tuple[int, Message]] = []
    vae: list[tuple[int, Message]] = []
    ce: list[tuple[int, Message]] = []
    cbe: list[tuple[int, Message]] = []
    te: list[tuple[int, Message]] = []
    he: list[tuple[int, Message]] = []
    me: list[tuple[int, Message]] = []
    de: list[tuple[int, Message]] = []

    add_program_change(ve, VIOLIN_CH, GM_VIOLIN_PROGRAM, 0)
    add_program_change(vae, VIOLA_CH, GM_VIOLA_PROGRAM, 0)
    add_program_change(ce, CELLO_CH, GM_CELLO_PROGRAM, 0)
    add_program_change(cbe, CONTRABASS_CH, GM_CONTRABASS_PROGRAM, 0)
    add_program_change(te, TUTTI_CH, GM_ENSEMBLE_PROGRAM, 0)
    add_program_change(he, HARP_CH, GM_HARP_PROGRAM, 0)
    add_program_change(me, MODERN_CH, GM_MODERN_EP_PROGRAM, 0)

    bar_len = BEATS_PER_BAR * TICKS_PER_BEAT
    cursor = 0

    for season in seasons:
        for mov in season.movements:
            section_len = mov.bars * bar_len
            de.extend(movement_drums(cursor, mov.bars, mov.drum_mode))
            add_notes_to_events(
                ve,
                VIOLIN_CH,
                tile_note_events(mov.viol_part(), cursor, section_len),
            )
            add_notes_to_events(ce, CELLO_CH, _cello_bassline(cursor, mov.bars, mov.cello_roots))
            add_notes_to_events(cbe, CONTRABASS_CH, _contrabass_doubles(cursor, mov.bars, mov.cello_roots))
            for bar in range(mov.bars):
                triad = mov.harmony[bar % len(mov.harmony)]
                spread = _open_string_voicing(triad)
                add_chord_events(te, TUTTI_CH, cursor + bar * bar_len, bar_len - 28, spread, 46)
            _viola_inner(vae, cursor, mov.bars, mov.harmony)
            _harp_arpeggios(he, cursor, mov.bars, mov.harmony)
            if mov.drum_mode != "none":
                _modern_ep_bed(me, cursor, mov.bars, mov.harmony)
            cursor += section_len

    violin_t.extend(merge_to_deltas(ve))
    viola_t.extend(merge_to_deltas(vae))
    cello_t.extend(merge_to_deltas(ce))
    cb_t.extend(merge_to_deltas(cbe))
    tutti_t.extend(merge_to_deltas(te))
    harp_t.extend(merge_to_deltas(he))
    modern_t.extend(merge_to_deltas(me))
    drums_t.extend(merge_to_deltas(de))

    mid.tracks.extend(
        [violin_t, viola_t, cello_t, cb_t, tutti_t, harp_t, modern_t, drums_t]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(str(path))
    return total_bars, total_ticks


def build_all_suites(output_dir: Path | str) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for season in ALL_SUITE_SEASONS:
        path = output_dir / f"{season.slug}_suite.mid"
        bars, ticks = compile_suite_midi(
            path,
            [season],
            title=f"{season.display_name} - suite",
        )
        print(f"Wrote {path}  ({bars} bars, movement tempos in file)")

    full_path = output_dir / "four_seasons_suite.mid"
    bars, ticks = compile_suite_midi(
        full_path,
        list(ALL_SUITE_SEASONS),
        title="The Four Seasons - classical / modern suite",
    )
    print(f"Wrote {full_path}  ({bars} bars total)")
