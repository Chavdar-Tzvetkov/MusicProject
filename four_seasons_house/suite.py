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
    CONTINUO_CH,
    GM_CELESTA_PROGRAM,
    GM_CELLO_PROGRAM,
    GM_CONTRABASS_PROGRAM,
    GM_ENSEMBLE_PROGRAM,
    GM_FLUTE_PROGRAM,
    GM_HARP_PROGRAM,
    GM_HARPSICHORD_PROGRAM,
    GM_MODERN_EP_PROGRAM,
    GM_NEWAGE_PAD_PROGRAM,
    GM_SUB_BASS_PROGRAM,
    GM_TIMPANI_PROGRAM,
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
    *,
    sparse: bool = False,
) -> None:
    s16 = beat // 4
    for bar in range(bars):
        if sparse and bar % 3 != 0:
            continue
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
                (48 - i * 8) if sparse else (60 - i * 10),
            )


def _timpani_movement(
    start: int,
    bars: int,
    roots: tuple[int, ...],
    intro_orchestral_bars: int,
    banger: bool,
    drum_mode: str,
    bar_len: int,
) -> list[NoteEvent]:
    if drum_mode == "none":
        return []
    beat = TICKS_PER_BEAT
    out: list[NoteEvent] = []
    for bar in range(bars):
        r = roots[bar % len(roots)]
        pitch = max(43, min(60, r))
        t0 = start + bar * bar_len
        in_intro = bar < intro_orchestral_bars
        drop = banger and not in_intro
        if in_intro:
            out.append(NoteEvent(t0, beat - 52, pitch, 52))
        else:
            v1 = 76 if drop else 64
            v2 = 56 if drop else 48
            d1 = max(72, beat // 2 - 28)
            out.append(NoteEvent(t0, d1, pitch, v1))
            p2 = pitch - 1 if pitch > 44 else pitch
            out.append(NoteEvent(t0 + 2 * beat, max(56, beat // 2 - 36), p2, v2))
            if drop and drum_mode == "drive":
                out.append(
                    NoteEvent(t0 + beat + beat // 2, beat // 3, min(58, pitch + 3), v2 - 10)
                )
    return out


def _acoustic_flute_doubling(
    events: list[tuple[int, Message]],
    start: int,
    bars: int,
    harmony: tuple[tuple[int, int, int], ...],
    bar_len: int,
    beat: int,
) -> None:
    for bar in range(bars):
        if bar % 2:
            continue
        triad = harmony[bar % len(harmony)]
        n = min(80, max(66, triad[2] + 12))
        t_bar = start + bar * bar_len
        hold = int(bar_len * 0.74)
        add_chord_events(events, ATMOS_CH, t_bar + beat // 2, hold, (n,), 36)
        if bar % 6 == 0:
            n2 = min(84, triad[1] + 19)
            add_chord_events(events, ATMOS_CH, t_bar + 2 * beat, max(beat, hold // 2), (n2,), 28)


def _continuo_voicing(triad: tuple[int, int, int]) -> tuple[int, int, int]:
    """Close-position continuo chunk in Baroque keyboard register (not too muddy)."""
    a, b, c = triad
    r0 = max(47, min(56, a))
    r1 = max(52, min(60, b))
    r2 = max(56, min(64, c))
    return (r0, r1, r2)


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
    hip = 0.96 if vibe == "genz" else 1.0  # acoustic + classic use written tempo
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
    vibe: str = "acoustic",
) -> tuple[int, int]:
    """acoustic = natural orchestra only (strings, harp, continuo, timpani, sparse flute/celesta)."""
    if vibe not in ("genz", "classic", "acoustic"):
        vibe = "acoustic"
    path = Path(path)
    tempo_points, total_ticks, total_bars = _flatten_tempo_points(seasons, vibe)
    genz = vibe == "genz"
    acoustic = vibe == "acoustic"

    mid = MidiFile(type=1, ticks_per_beat=TICKS_PER_BEAT)
    disp = title + (
        " - GenZ new age"
        if genz
        else (" - Acoustic orchestra" if acoustic else "")
    )
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
    continuo_t = MidiTrack()
    continuo_t.append(MetaMessage("track_name", name="Continuo harpsichord", time=0))

    modern_t: MidiTrack | None = None
    atmos_t: MidiTrack | None = None
    sparkle_t: MidiTrack | None = None
    flute_t: MidiTrack | None = None
    timpani_t: MidiTrack | None = None
    sub_t: MidiTrack | None = None
    drums_t: MidiTrack | None = None

    ae: list[tuple[int, Message]] = []
    se: list[tuple[int, Message]] = []
    fe: list[tuple[int, Message]] = []
    tmp_e: list[tuple[int, Message]] = []
    ve: list[tuple[int, Message]] = []
    vae: list[tuple[int, Message]] = []
    ce: list[tuple[int, Message]] = []
    cbe: list[tuple[int, Message]] = []
    te: list[tuple[int, Message]] = []
    he: list[tuple[int, Message]] = []
    qe: list[tuple[int, Message]] = []
    me: list[tuple[int, Message]] = []
    sube: list[tuple[int, Message]] = []
    de: list[tuple[int, Message]] = []

    if acoustic:
        flute_t = MidiTrack()
        flute_t.append(MetaMessage("track_name", name="Flute doubling", time=0))
        sparkle_t = MidiTrack()
        sparkle_t.append(MetaMessage("track_name", name="Celesta sparkle", time=0))
        timpani_t = MidiTrack()
        timpani_t.append(MetaMessage("track_name", name="Timpani", time=0))
        add_program_change(fe, ATMOS_CH, GM_FLUTE_PROGRAM, 0)
        add_program_change(se, SPARKLE_CH, GM_CELESTA_PROGRAM, 0)
        add_program_change(tmp_e, MODERN_CH, GM_TIMPANI_PROGRAM, 0)
    elif genz:
        modern_t = MidiTrack()
        modern_t.append(MetaMessage("track_name", name="New-age bed", time=0))
        atmos_t = MidiTrack()
        atmos_t.append(MetaMessage("track_name", name="Atmos pad", time=0))
        sparkle_t = MidiTrack()
        sparkle_t.append(MetaMessage("track_name", name="Celesta sparkle", time=0))
        sub_t = MidiTrack()
        sub_t.append(MetaMessage("track_name", name="Sub (map to 808)", time=0))
        drums_t = MidiTrack()
        drums_t.append(MetaMessage("track_name", name="Drums", time=0))
        add_program_change(ae, ATMOS_CH, GM_NEWAGE_PAD_PROGRAM, 0)
        add_program_change(se, SPARKLE_CH, GM_CELESTA_PROGRAM, 0)
        add_program_change(me, MODERN_CH, GM_NEWAGE_PAD_PROGRAM, 0)
        add_program_change(sube, SUB_CH, GM_SUB_BASS_PROGRAM, 0)
    else:
        modern_t = MidiTrack()
        modern_t.append(MetaMessage("track_name", name="Modern bed (EP)", time=0))
        sub_t = MidiTrack()
        sub_t.append(MetaMessage("track_name", name="Sub (map to 808)", time=0))
        drums_t = MidiTrack()
        drums_t.append(MetaMessage("track_name", name="Drums", time=0))
        add_program_change(me, MODERN_CH, GM_MODERN_EP_PROGRAM, 0)
        add_program_change(sube, SUB_CH, GM_SUB_BASS_PROGRAM, 0)

    add_program_change(ve, VIOLIN_CH, GM_VIOLIN_PROGRAM, 0)
    add_program_change(vae, VIOLA_CH, GM_VIOLA_PROGRAM, 0)
    add_program_change(ce, CELLO_CH, GM_CELLO_PROGRAM, 0)
    add_program_change(cbe, CONTRABASS_CH, GM_CONTRABASS_PROGRAM, 0)
    add_program_change(te, TUTTI_CH, GM_ENSEMBLE_PROGRAM, 0)
    add_program_change(he, HARP_CH, GM_HARP_PROGRAM, 0)
    add_program_change(qe, CONTINUO_CH, GM_HARPSICHORD_PROGRAM, 0)

    spread_fn = (
        _open_string_voicing
        if acoustic
        else (_open_string_voicing_wide if genz else _open_string_voicing)
    )
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
                    acoustic=acoustic,
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
            if not acoustic:
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
            if acoustic:
                _acoustic_flute_doubling(fe, cursor, mov.bars, mov.harmony, bar_len, beat)
                _sparkle_celesta(se, cursor, mov.bars, mov.harmony, bar_len, beat, sparse=True)
                add_notes_to_events(
                    tmp_e,
                    MODERN_CH,
                    _timpani_movement(
                        cursor,
                        mov.bars,
                        mov.cello_roots,
                        mov.intro_orchestral_bars,
                        mov.banger,
                        mov.drum_mode,
                        bar_len,
                    ),
                )
            elif genz:
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
                if acoustic:
                    vel_t = 66 if drop else 50
                    vv1 = 60 if drop else 54
                elif genz:
                    vel_t = 54 if drop else 43
                    vv1 = 56 if drop else 50
                else:
                    vel_t = 58 if drop else 45
                    vv1 = 60 if drop else 52
                add_chord_events(te, TUTTI_CH, t_bar, bar_len - 28, spread, vel_t)
                i1 = min(76, triad[1] + 12)
                i2 = min(78, triad[2] + 12)
                add_chord_events(vae, VIOLA_CH, t_bar, 2 * beat - 22, (i1,), vv1)
                add_chord_events(vae, VIOLA_CH, t_bar + 2 * beat, 2 * beat - 22, (i2,), vv1 - 4)
                a, b, c = triad
                chips = [(a + 24), (b + 24), (c + 24), (b + 24), (c + 28), (a + 28)]
                if acoustic:
                    h_boost = 3
                    hv = (46 if drop else 38) + h_boost
                else:
                    h_boost = 4 if genz else 0
                    hv = (40 if drop else 34) + h_boost
                for i, p in enumerate(chips):
                    ht = t_bar + i * e8
                    if ht >= t_bar + bar_len:
                        break
                    add_chord_events(he, HARP_CH, ht, e8 - 14, (min(90, p),), min(90, hv))
                if not acoustic and mov.drum_mode != "none":
                    v_ep = (32 if drop else 22) if genz else (36 if drop else 26)
                    voicing = _modern_hybrid_voicing(triad, genz)
                    hold = bar_len - (12 if genz else 24)
                    add_chord_events(me, MODERN_CH, t_bar, hold, voicing, v_ep)
                cv = _continuo_voicing(triad)
                if acoustic:
                    if mov.drum_mode == "none":
                        v_q = 52
                    else:
                        v_q = 48 if drop else 44
                elif mov.drum_mode == "none":
                    v_q = 40 if genz else 44
                else:
                    v_q = (18 if drop else 26) if genz else (22 if drop else 30)
                add_chord_events(qe, CONTINUO_CH, t_bar, bar_len - 36, cv, v_q)

            cursor += section_len

    violin_t.extend(merge_to_deltas(ve))
    viola_t.extend(merge_to_deltas(vae))
    cello_t.extend(merge_to_deltas(ce))
    cb_t.extend(merge_to_deltas(cbe))
    tutti_t.extend(merge_to_deltas(te))
    harp_t.extend(merge_to_deltas(he))
    continuo_t.extend(merge_to_deltas(qe))

    tracks_order: list[MidiTrack] = [
        violin_t,
        viola_t,
        cello_t,
        cb_t,
        tutti_t,
        harp_t,
        continuo_t,
    ]
    if acoustic:
        if flute_t is not None:
            flute_t.extend(merge_to_deltas(fe))
        if sparkle_t is not None:
            sparkle_t.extend(merge_to_deltas(se))
        if timpani_t is not None:
            timpani_t.extend(merge_to_deltas(tmp_e))
        tracks_order.extend(
            [t for t in (flute_t, sparkle_t, timpani_t) if t is not None]
        )
    else:
        if modern_t is not None:
            modern_t.extend(merge_to_deltas(me))
            tracks_order.append(modern_t)
        if genz and atmos_t is not None and sparkle_t is not None:
            atmos_t.extend(merge_to_deltas(ae))
            sparkle_t.extend(merge_to_deltas(se))
            tracks_order.extend([atmos_t, sparkle_t])
        if sub_t is not None:
            sub_t.extend(merge_to_deltas(sube))
        if drums_t is not None:
            drums_t.extend(merge_to_deltas(de))
        tracks_order.extend([t for t in (sub_t, drums_t) if t is not None])

    mid.tracks.extend(tracks_order)
    path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(str(path))
    return total_bars, total_ticks


_VIBE_TAGS = {
    "acoustic": "acoustic orchestra",
    "genz": "GenZ new-age",
    "classic": "classic hybrid",
}


def build_all_suites(output_dir: Path | str, *, vibe: str = "acoustic") -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tag = _VIBE_TAGS.get(vibe, vibe)

    for season in ALL_SUITE_SEASONS:
        path = output_dir / f"{season.slug}_suite.mid"
        bars, _ticks = compile_suite_midi(
            path,
            [season],
            title=f"{season.display_name} - suite",
            vibe=vibe,
        )
        print(f"Wrote {path}  ({bars} bars, {tag})")

    full_path = output_dir / "four_seasons_suite.mid"
    bars, _ticks = compile_suite_midi(
        full_path,
        list(ALL_SUITE_SEASONS),
        title="The Four Seasons - suite",
        vibe=vibe,
    )
    print(f"Wrote {full_path}  ({bars} bars total)")
