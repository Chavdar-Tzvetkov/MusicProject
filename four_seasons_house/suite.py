from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

from .automation import add_program_change
from .constants import (
    ATMOS_CH,
    BEATS_PER_BAR,
    CELLO_CH,
    CONTRABASS_CH,
    GM_CELESTA_PROGRAM,
    GM_CELLO_PROGRAM,
    GM_CONTRABASS_PROGRAM,
    GM_ENSEMBLE_PROGRAM,
    GM_HARP_PROGRAM,
    GM_MODERN_EP_PROGRAM,
    GM_NEWAGE_PAD_PROGRAM,
    GM_SUB_BASS_PROGRAM,
    GM_VIOLA_PROGRAM,
    GM_VIOLIN_PROGRAM,
    HARP_CH,
    MODERN_CH,
    SPARKLE_CH,
    SUB_CH,
    TICKS_PER_BEAT,
    TUTTI_CH,
    VIOLA_CH,
    VIOLIN_CH,
)
from .midi_util import (
    NoteEvent,
    add_chord_events,
    add_notes_to_events,
    merge_to_deltas,
    tile_alternating_note_events,
    tile_note_events,
)
from .patterns import (
    _open_string_voicing,
    _open_string_voicing_wide,
    suite_movement_drums,
)
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


def _sub_808_line(
    start: int,
    bars: int,
    roots: tuple[int, ...],
    intro_orchestral_bars: int,
    banger: bool,
    drum_mode: str,
    *,
    genz: bool,
) -> list[NoteEvent]:
    if not banger or drum_mode == "none":
        return []
    beat = TICKS_PER_BEAT
    bl = BEATS_PER_BAR * beat
    snap = beat // 4 + 8
    v_long, v_snap = (108, 92) if genz else (118, 102)
    out: list[NoteEvent] = []
    for bar in range(bars):
        if bar < intro_orchestral_bars:
            continue
        r = roots[bar % len(roots)]
        sub = max(33, min(44, r - 12))
        t0 = start + bar * bl
        out.append(NoteEvent(t0, int(beat * 2.42), sub, v_long))
        out.append(NoteEvent(t0 + 3 * beat + beat // 2, snap, sub, v_snap))
    return out


def _atmos_newage_wash(
    events: list[tuple[int, Message]],
    start: int,
    bars: int,
    harmony: tuple[tuple[int, int, int], ...],
    bar_len: int,
) -> None:
    beat = TICKS_PER_BEAT
    for bar in range(bars):
        triad = harmony[bar % len(harmony)]
        a, b, c = triad
        t_bar = start + bar * bar_len
        low = max(58, a + 12)
        mid = min(76, b + 24)
        hi = min(82, c + 24)
        air = min(88, c + 31)
        pitches = tuple(sorted({low, mid, hi, air}))
        add_chord_events(events, ATMOS_CH, t_bar, bar_len - 18, pitches, 42)


def _sparkle_celesta(
    events: list[tuple[int, Message]],
    start: int,
    bars: int,
    harmony: tuple[tuple[int, int, int], ...],
    bar_len: int,
    beat: int,
) -> None:
    s16 = beat // 4
    for bar in range(bars):
        triad = harmony[bar % len(harmony)]
        r = triad[0]
        base = max(84, r + 31)
        t0 = start + bar * bar_len + beat + beat // 2
        if bar % 2:
            t0 += s16
        for i, off in enumerate((0, 2, 5)):
            p = min(96, base + off)
            add_chord_events(
                events,
                SPARKLE_CH,
                t0 + i * s16,
                max(24, s16 - 10),
                (p,),
                60 - i * 10,
            )


def _modern_hybrid_voicing(triad: tuple[int, int, int], genz: bool) -> tuple[int, ...]:
    base = tuple(min(74, n + 7) for n in triad)
    if genz:
        return base + (min(84, triad[2] + 16),)
    return base


def _flatten_tempo_points(
    seasons: Sequence[SeasonSuiteSpec],
    vibe: str,
) -> tuple[list[tuple[int, float]], int, int]:
    bar_len = BEATS_PER_BAR * TICKS_PER_BEAT
    tempo_points: list[tuple[int, float]] = []
    cursor = 0
    total_bars = 0
    hip = 0.96 if vibe == "genz" else 1.0
    for season in seasons:
        for mov in season.movements:
            tempo_points.append((cursor, mov.bpm * hip))
            cursor += mov.bars * bar_len
            total_bars += mov.bars
    return tempo_points, cursor, total_bars


def compile_suite_midi(
    path: Path | str,
    seasons: Sequence[SeasonSuiteSpec],
    *,
    title: str,
    vibe: str = "genz",
) -> tuple[int, int]:
    """vibe: genz = new-age pad + celesta + trap-influenced drops; classic = prior hybrid."""
    if vibe not in ("genz", "classic"):
        vibe = "genz"
    path = Path(path)
    tempo_points, total_ticks, total_bars = _flatten_tempo_points(seasons, vibe)
    genz = vibe == "genz"

    mid = MidiFile(type=1, ticks_per_beat=TICKS_PER_BEAT)
    disp = title + (" - GenZ new age" if genz else "")
    mid.tracks.append(_build_meta_track(disp, tempo_points))

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
    bed_name = "New-age bed" if genz else "Modern bed (EP)"
    modern_t.append(MetaMessage("track_name", name=bed_name, time=0))
    ae: list[tuple[int, Message]] = []
    se: list[tuple[int, Message]] = []
    atmos_t: MidiTrack | None = None
    sparkle_t: MidiTrack | None = None
    if genz:
        atmos_t = MidiTrack()
        atmos_t.append(MetaMessage("track_name", name="Atmos pad", time=0))
        sparkle_t = MidiTrack()
        sparkle_t.append(MetaMessage("track_name", name="Celesta sparkle", time=0))
        add_program_change(ae, ATMOS_CH, GM_NEWAGE_PAD_PROGRAM, 0)
        add_program_change(se, SPARKLE_CH, GM_CELESTA_PROGRAM, 0)

    sub_t = MidiTrack()
    sub_t.append(MetaMessage("track_name", name="Sub (map to 808)", time=0))
    drums_t = MidiTrack()
    drums_t.append(MetaMessage("track_name", name="Drums", time=0))

    ve: list[tuple[int, Message]] = []
    vae: list[tuple[int, Message]] = []
    ce: list[tuple[int, Message]] = []
    cbe: list[tuple[int, Message]] = []
    te: list[tuple[int, Message]] = []
    he: list[tuple[int, Message]] = []
    me: list[tuple[int, Message]] = []
    sube: list[tuple[int, Message]] = []
    de: list[tuple[int, Message]] = []

    add_program_change(ve, VIOLIN_CH, GM_VIOLIN_PROGRAM, 0)
    add_program_change(vae, VIOLA_CH, GM_VIOLA_PROGRAM, 0)
    add_program_change(ce, CELLO_CH, GM_CELLO_PROGRAM, 0)
    add_program_change(cbe, CONTRABASS_CH, GM_CONTRABASS_PROGRAM, 0)
    add_program_change(te, TUTTI_CH, GM_ENSEMBLE_PROGRAM, 0)
    add_program_change(he, HARP_CH, GM_HARP_PROGRAM, 0)
    modern_prog = GM_NEWAGE_PAD_PROGRAM if genz else GM_MODERN_EP_PROGRAM
    add_program_change(me, MODERN_CH, modern_prog, 0)
    add_program_change(sube, SUB_CH, GM_SUB_BASS_PROGRAM, 0)

    spread_fn = _open_string_voicing_wide if genz else _open_string_voicing
    bar_len = BEATS_PER_BAR * TICKS_PER_BEAT
    beat = TICKS_PER_BEAT
    e8 = beat // 2
    cursor = 0

    for season in seasons:
        for mov in season.movements:
            section_len = mov.bars * bar_len
            de.extend(
                suite_movement_drums(
                    cursor,
                    mov.bars,
                    mov.drum_mode,
                    banger=mov.banger,
                    intro_orchestral_bars=mov.intro_orchestral_bars,
                    genz=genz,
                )
            )
            alt = mov.viol_alt
            vnotes = (
                tile_alternating_note_events(mov.viol_part(), alt(), cursor, section_len)
                if alt
                else tile_note_events(mov.viol_part(), cursor, section_len)
            )
            add_notes_to_events(ve, VIOLIN_CH, vnotes)
            add_notes_to_events(ce, CELLO_CH, _cello_bassline(cursor, mov.bars, mov.cello_roots))
            add_notes_to_events(cbe, CONTRABASS_CH, _contrabass_doubles(cursor, mov.bars, mov.cello_roots))
            add_notes_to_events(
                sube,
                SUB_CH,
                _sub_808_line(
                    cursor,
                    mov.bars,
                    mov.cello_roots,
                    mov.intro_orchestral_bars,
                    mov.banger,
                    mov.drum_mode,
                    genz=genz,
                ),
            )
            if genz:
                _atmos_newage_wash(ae, cursor, mov.bars, mov.harmony, bar_len)
                _sparkle_celesta(se, cursor, mov.bars, mov.harmony, bar_len, beat)

            for bar in range(mov.bars):
                t_bar = cursor + bar * bar_len
                triad = mov.harmony[bar % len(mov.harmony)]
                spread = spread_fn(triad)
                drop = (
                    mov.banger
                    and bar >= mov.intro_orchestral_bars
                    and mov.drum_mode != "none"
                )
                vel_t = (54 if drop else 43) if genz else (58 if drop else 45)
                add_chord_events(te, TUTTI_CH, t_bar, bar_len - 28, spread, vel_t)
                i1 = min(76, triad[1] + 12)
                i2 = min(78, triad[2] + 12)
                vv1 = (56 if drop else 50) if genz else (60 if drop else 52)
                add_chord_events(vae, VIOLA_CH, t_bar, 2 * beat - 22, (i1,), vv1)
                add_chord_events(vae, VIOLA_CH, t_bar + 2 * beat, 2 * beat - 22, (i2,), vv1 - 4)
                a, b, c = triad
                chips = [(a + 24), (b + 24), (c + 24), (b + 24), (c + 28), (a + 28)]
                h_boost = 4 if genz else 0
                for i, p in enumerate(chips):
                    ht = t_bar + i * e8
                    if ht >= t_bar + bar_len:
                        break
                    hv = (40 if drop else 34) + h_boost
                    add_chord_events(he, HARP_CH, ht, e8 - 14, (min(90, p),), min(88, hv))
                if mov.drum_mode != "none":
                    v_ep = (32 if drop else 22) if genz else (36 if drop else 26)
                    voicing = _modern_hybrid_voicing(triad, genz)
                    hold = bar_len - (12 if genz else 24)
                    add_chord_events(me, MODERN_CH, t_bar, hold, voicing, v_ep)

            cursor += section_len

    violin_t.extend(merge_to_deltas(ve))
    viola_t.extend(merge_to_deltas(vae))
    cello_t.extend(merge_to_deltas(ce))
    cb_t.extend(merge_to_deltas(cbe))
    tutti_t.extend(merge_to_deltas(te))
    harp_t.extend(merge_to_deltas(he))
    modern_t.extend(merge_to_deltas(me))
    sub_t.extend(merge_to_deltas(sube))
    drums_t.extend(merge_to_deltas(de))
    if genz and atmos_t is not None and sparkle_t is not None:
        atmos_t.extend(merge_to_deltas(ae))
        sparkle_t.extend(merge_to_deltas(se))

    tracks_order: list[MidiTrack] = [
        violin_t,
        viola_t,
        cello_t,
        cb_t,
        tutti_t,
        harp_t,
        modern_t,
    ]
    if genz and atmos_t is not None and sparkle_t is not None:
        tracks_order.extend([atmos_t, sparkle_t])
    tracks_order.extend([sub_t, drums_t])
    mid.tracks.extend(tracks_order)
    path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(str(path))
    return total_bars, total_ticks


def build_all_suites(output_dir: Path | str, *, vibe: str = "genz") -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for season in ALL_SUITE_SEASONS:
        path = output_dir / f"{season.slug}_suite.mid"
        bars, _ticks = compile_suite_midi(
            path,
            [season],
            title=f"{season.display_name} - suite",
            vibe=vibe,
        )
        tag = "GenZ new-age" if vibe == "genz" else "classic hybrid"
        print(f"Wrote {path}  ({bars} bars, {tag})")

    full_path = output_dir / "four_seasons_suite.mid"
    bars, _ticks = compile_suite_midi(
        full_path,
        list(ALL_SUITE_SEASONS),
        title="The Four Seasons - suite",
        vibe=vibe,
    )
    print(f"Wrote {full_path}  ({bars} bars total)")
