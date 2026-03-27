"""
Condensed, Vivaldi-flavored phrase cells for each movement (public domain source).
Phrases tile inside each movement; not a full score — long-form listening via repeats.
"""

from __future__ import annotations

from .constants import TICKS_PER_BEAT
from .midi_util import NoteEvent

B = TICKS_PER_BEAT
E8 = B // 2
E16 = B // 4
Q = B
H = 2 * B
W = 4 * B


def _run8(pitches: list[int], vel: int = 86, gate: int = E8 - 18) -> list[NoteEvent]:
    t = 0
    out: list[NoteEvent] = []
    for p in pitches:
        out.append(NoteEvent(t, gate, p, vel))
        t += E8
    return out


def _run16(pitches: list[int], vel: int = 82) -> list[NoteEvent]:
    g = E16 - 8
    t = 0
    out: list[NoteEvent] = []
    for p in pitches:
        out.append(NoteEvent(t, g, p, vel))
        t += E16
    return out


# --- Spring ---


def spring_i_allegro() -> list[NoteEvent]:
    """La primavera I — bright E-major ritornello gesture (treble register)."""
    return _run8(
        [
            76, 71, 76, 80, 76, 71, 76, 80, 76, 78, 80, 83, 80, 78, 76, 71,
            73, 76, 78, 80, 81, 80, 78, 76, 74, 76, 78, 81, 83, 81, 78, 76,
        ],
        vel=92,
    )


def spring_i_allegro_b() -> list[NoteEvent]:
    """Contrasting ritornello answer — more stepwise, sequence-like."""
    return _run8(
        [
            76, 78, 80, 83, 81, 80, 78, 76, 74, 71, 74, 76, 78, 76, 74, 73,
            71, 73, 74, 76, 78, 80, 78, 76, 74, 76, 78, 81, 83, 81, 80, 78,
        ],
        vel=90,
    )


def spring_ii_largo() -> list[NoteEvent]:
    """Slow movement — broad siciliano-style cantilena in high register."""
    out: list[NoteEvent] = []
    t = 0
    phrase = [
        (H - 50, 73, 78),
        (Q - 30, 76, 80),
        (Q - 28, 78, 82),
        (Q - 28, 73, 78),
        (H - 45, 71, 74),
        (Q - 28, 73, 78),
        (Q - 28, 76, 80),
        (H - 40, 78, 84),
        (H - 50, 76, 78),
        (Q - 28, 73, 76),
        (Q - 28, 71, 74),
        (W - 80, 73, 72),
    ]
    for dur, pit, vel in phrase:
        out.append(NoteEvent(t, dur, pit, vel))
        t += dur
    return out


def spring_ii_largo_b() -> list[NoteEvent]:
    """Answering phrase — slightly darker, more chromatic sidestep."""
    out: list[NoteEvent] = []
    t = 0
    for dur, pit, vel in [
        (H - 48, 71, 76),
        (Q - 28, 74, 80),
        (Q - 28, 76, 82),
        (Q - 28, 74, 80),
        (H - 44, 71, 76),
        (Q - 28, 69, 74),
        (Q - 28, 71, 78),
        (H - 42, 74, 82),
        (H - 48, 73, 78),
        (Q - 28, 71, 74),
        (Q - 28, 69, 72),
        (W - 85, 71, 70),
    ]:
        out.append(NoteEvent(t, dur, pit, vel))
        t += dur
    return out


def spring_iii_allegro_pastorale() -> list[NoteEvent]:
    """Rustic closing — lilting dotted figures, pastoral drone in melody."""
    p1 = _run8([74, 71, 74, 78, 76, 74, 73, 71, 73, 74, 76, 78, 76, 74, 73, 71], 88)
    p2 = _run8([78, 76, 78, 81, 80, 78, 76, 74, 74, 76, 78, 81, 80, 78, 76, 74], 86)
    t_off = max(n.start + n.duration for n in p1)
    return p1 + [NoteEvent(t_off + n.start, n.duration, n.pitch, n.velocity) for n in p2]


def spring_iii_allegro_pastorale_b() -> list[NoteEvent]:
    return _run8(
        [
            71, 74, 76, 78, 76, 74, 73, 71, 69, 71, 73, 74, 76, 74, 73, 71,
            73, 74, 76, 78, 81, 78, 76, 74, 73, 71, 73, 76, 78, 76, 74, 73,
        ],
        vel=86,
    )


# --- Summer ---


def summer_i_allegro() -> list[NoteEvent]:
    """L'estate I — weary, drooping lines in G minor."""
    return _run8(
        [
            67, 65, 67, 62, 63, 65, 67, 65, 63, 62, 60, 62, 63, 65, 67, 68,
            67, 65, 63, 62, 63, 65, 67, 65, 63, 62, 60, 58, 60, 63, 65, 67,
        ],
        vel=84,
    )


def summer_i_allegro_b() -> list[NoteEvent]:
    return _run8(
        [
            65, 63, 62, 63, 65, 67, 68, 67, 65, 63, 60, 58, 60, 63, 65, 63,
            62, 63, 65, 67, 69, 67, 65, 63, 62, 60, 62, 63, 65, 67, 65, 63,
        ],
        vel=82,
    )


def summer_ii_adagio() -> list[NoteEvent]:
    """Adagio — sparse, humid tranquillo."""
    out: list[NoteEvent] = []
    t = 0
    for dur, pit, vel in [
        (H - 40, 70, 70),
        (Q - 26, 68, 72),
        (Q - 26, 67, 70),
        (H - 36, 65, 68),
        (Q - 26, 67, 72),
        (Q - 26, 68, 74),
        (H - 40, 70, 76),
        (H - 44, 68, 72),
        (H - 44, 65, 68),
        (W - 70, 63, 66),
    ]:
        out.append(NoteEvent(t, dur, pit, vel))
        t += dur
    return out


def summer_ii_adagio_b() -> list[NoteEvent]:
    out: list[NoteEvent] = []
    t = 0
    for dur, pit, vel in [
        (H - 42, 68, 71),
        (Q - 26, 67, 70),
        (Q - 26, 65, 68),
        (H - 38, 63, 66),
        (Q - 26, 65, 70),
        (Q - 26, 67, 72),
        (H - 40, 69, 74),
        (H - 44, 67, 70),
        (H - 44, 64, 68),
        (W - 72, 62, 65),
    ]:
        out.append(NoteEvent(t, dur, pit, vel))
        t += dur
    return out


def summer_iii_presto() -> list[NoteEvent]:
    """Storm finale — chromatic whirl (short cell, high energy)."""
    return _run16(
        [
            67, 65, 67, 63, 62, 65, 67, 65, 63, 62, 60, 62, 63, 65, 67, 70,
            68, 67, 65, 63, 62, 60, 58, 60, 62, 63, 65, 67, 65, 63, 62, 63,
            65, 67, 68, 70, 68, 67, 65, 63, 62, 63, 65, 67, 65, 63, 62, 60,
        ],
        vel=92,
    )


def summer_iii_presto_b() -> list[NoteEvent]:
    return _run16(
        [
            63, 65, 67, 68, 67, 65, 63, 62, 60, 62, 63, 65, 67, 68, 67, 65,
            63, 62, 60, 58, 60, 62, 63, 65, 67, 65, 63, 62, 63, 65, 67, 70,
            72, 70, 68, 67, 65, 63, 62, 60, 58, 57, 58, 60, 62, 63, 65, 67,
        ],
        vel=91,
    )


# --- Autumn ---


def autumn_i_allegro() -> list[NoteEvent]:
    """L'autunno I — dancing F-major thirds/sixths."""
    return _run8(
        [
            65, 69, 67, 71, 69, 72, 71, 74, 72, 69, 67, 65, 64, 67, 65, 62,
            65, 67, 69, 72, 74, 72, 69, 67, 65, 67, 69, 71, 72, 71, 69, 67,
        ],
        vel=90,
    )


def autumn_i_allegro_b() -> list[NoteEvent]:
    return _run8(
        [
            64, 67, 65, 62, 64, 65, 67, 69, 71, 69, 67, 65, 64, 65, 67, 69,
            72, 74, 72, 69, 67, 65, 64, 62, 65, 67, 69, 72, 74, 72, 71, 69,
        ],
        vel=88,
    )


def autumn_ii_adagio() -> list[NoteEvent]:
    """Drunken / sleeping interlude — slurred quarter motion."""
    out: list[NoteEvent] = []
    t = 0
    for dur, pit, vel in [
        (Q - 28, 72, 76),
        (Q - 28, 71, 74),
        (H - 40, 69, 72),
        (Q - 28, 71, 76),
        (Q - 28, 74, 80),
        (H - 42, 76, 82),
        (Q - 28, 74, 78),
        (Q - 28, 71, 74),
        (H - 44, 69, 72),
        (H - 46, 67, 70),
        (W - 80, 65, 68),
    ]:
        out.append(NoteEvent(t, dur, pit, vel))
        t += dur
    return out


def autumn_ii_adagio_b() -> list[NoteEvent]:
    out: list[NoteEvent] = []
    t = 0
    for dur, pit, vel in [
        (Q - 28, 74, 78),
        (Q - 28, 72, 76),
        (H - 38, 70, 73),
        (Q - 28, 72, 78),
        (Q - 28, 76, 81),
        (H - 42, 78, 83),
        (Q - 28, 76, 79),
        (Q - 28, 73, 75),
        (H - 44, 70, 72),
        (H - 46, 68, 70),
        (W - 82, 66, 68),
    ]:
        out.append(NoteEvent(t, dur, pit, vel))
        t += dur
    return out


def autumn_iii_allegro() -> list[NoteEvent]:
    """Hunt — galloping figures."""
    return _run16(
        [
            65, 67, 69, 72, 74, 72, 69, 67, 65, 64, 65, 67, 69, 71, 69, 65,
            64, 65, 67, 69, 72, 74, 76, 74, 72, 69, 67, 65, 64, 67, 69, 72,
        ],
        vel=90,
    )


def autumn_iii_allegro_b() -> list[NoteEvent]:
    return _run16(
        [
            67, 69, 71, 72, 71, 69, 67, 65, 64, 65, 67, 69, 72, 74, 72, 69,
            67, 65, 64, 65, 67, 69, 72, 74, 76, 74, 72, 71, 69, 67, 65, 64,
        ],
        vel=89,
    )


# --- Winter ---


def winter_i_allegro() -> list[NoteEvent]:
    """L'inverno I — shivering staccato chatter."""
    return _run16(
        [
            63, 65, 63, 60, 58, 60, 63, 65, 63, 60, 58, 56, 55, 56, 58, 60,
            63, 65, 63, 60, 58, 56, 55, 53, 55, 56, 58, 60, 63, 65, 66, 65,
            63, 60, 58, 60, 63, 65, 63, 60, 58, 56, 58, 60, 62, 63, 65, 63,
        ],
        vel=88,
    )


def winter_i_allegro_b() -> list[NoteEvent]:
    return _run16(
        [
            60, 62, 63, 65, 63, 60, 58, 56, 55, 56, 58, 60, 63, 65, 63, 60,
            58, 56, 55, 53, 55, 58, 60, 63, 65, 63, 60, 58, 56, 55, 56, 58,
            60, 63, 65, 66, 65, 63, 60, 58, 56, 58, 60, 63, 65, 63, 60, 58,
        ],
        vel=86,
    )


def winter_ii_largo() -> list[NoteEvent]:
    """Largo — icy, stepping bass with plaintive upper line."""
    out: list[NoteEvent] = []
    t = 0
    for dur, pit, vel in [
        (H - 45, 73, 76),
        (Q - 30, 75, 78),
        (Q - 30, 73, 76),
        (H - 42, 70, 74),
        (Q - 30, 68, 72),
        (Q - 30, 70, 74),
        (H - 40, 73, 78),
        (H - 44, 75, 80),
        (Q - 30, 73, 76),
        (Q - 30, 70, 72),
        (H - 46, 68, 70),
        (W - 85, 65, 68),
    ]:
        out.append(NoteEvent(t, dur, pit, vel))
        t += dur
    return out


def winter_ii_largo_b() -> list[NoteEvent]:
    out: list[NoteEvent] = []
    t = 0
    for dur, pit, vel in [
        (H - 46, 71, 74),
        (Q - 30, 74, 79),
        (Q - 30, 72, 77),
        (H - 44, 69, 74),
        (Q - 30, 67, 72),
        (Q - 30, 69, 74),
        (H - 42, 72, 78),
        (H - 46, 74, 80),
        (Q - 30, 72, 76),
        (Q - 30, 69, 73),
        (H - 48, 67, 70),
        (W - 88, 64, 67),
    ]:
        out.append(NoteEvent(t, dur, pit, vel))
        t += dur
    return out


def winter_iii_allegro() -> list[NoteEvent]:
    """Final allegro — hectic chase in the snow."""
    return _run16(
        [
            60, 63, 65, 67, 68, 67, 65, 63, 60, 58, 60, 63, 65, 67, 68, 70,
            68, 67, 65, 63, 60, 58, 56, 55, 56, 58, 60, 63, 65, 67, 65, 63,
            60, 63, 65, 67, 68, 67, 65, 63, 62, 63, 65, 67, 68, 70, 68, 67,
        ],
        vel=92,
    )


def winter_iii_allegro_b() -> list[NoteEvent]:
    return _run16(
        [
            63, 65, 67, 68, 67, 65, 63, 60, 58, 56, 55, 56, 58, 60, 63, 65,
            67, 68, 70, 68, 67, 65, 63, 60, 58, 60, 62, 63, 65, 67, 65, 63,
            60, 62, 63, 65, 67, 68, 70, 72, 70, 68, 67, 65, 63, 60, 58, 56,
        ],
        vel=91,
    )
