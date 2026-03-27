from __future__ import annotations

from mido import Message

from .constants import DRUM_CH, TICKS_PER_BEAT, BEATS_PER_BAR
from .midi_util import NoteEvent, add_chord_events


def house_drums_bar(start_tick: int) -> list[tuple[int, Message]]:
    e: list[tuple[int, Message]] = []
    beat = TICKS_PER_BEAT
    step = TICKS_PER_BEAT // 2
    kick, clap, ch, oh = 36, 39, 42, 46
    vel_k, vel_c, vel_hat = 110, 95, 70

    for b in range(4):
        t0 = start_tick + b * beat
        e.append((t0, Message("note_on", channel=DRUM_CH, note=kick, velocity=vel_k)))
        e.append((t0 + 10, Message("note_off", channel=DRUM_CH, note=kick, velocity=0)))
        if b in (1, 3):
            e.append((t0, Message("note_on", channel=DRUM_CH, note=clap, velocity=vel_c)))
            e.append((t0 + 20, Message("note_off", channel=DRUM_CH, note=clap, velocity=0)))

    for i in range(8):
        t = start_tick + i * step
        is_off = i % 2 == 1
        note = oh if is_off else ch
        vel = vel_hat + (18 if is_off else 0)
        e.append((t, Message("note_on", channel=DRUM_CH, note=note, velocity=min(127, vel))))
        e.append((t + 8, Message("note_off", channel=DRUM_CH, note=note, velocity=0)))
    return e


def section_drums(start: int, bars: int) -> list[tuple[int, Message]]:
    out: list[tuple[int, Message]] = []
    bar_len = BEATS_PER_BAR * TICKS_PER_BEAT
    for b in range(bars):
        out.extend(house_drums_bar(start + b * bar_len))
    return out


def _drum_pair(t: int, note: int, vel: int) -> list[tuple[int, Message]]:
    return [
        (t, Message("note_on", channel=DRUM_CH, note=note, velocity=vel)),
        (t + 14, Message("note_off", channel=DRUM_CH, note=note, velocity=0)),
    ]


def pulse_drums_bar(start_tick: int) -> list[tuple[int, Message]]:
    """Light downbeats 1 + 3, brushed hats — modern without arcade four-on-the-floor."""
    e: list[tuple[int, Message]] = []
    beat = TICKS_PER_BEAT
    step = beat // 2
    kick, ch = 36, 42
    for b in (0, 2):
        e.extend(_drum_pair(start_tick + b * beat, kick, 44))
    for i in range(8):
        t = start_tick + i * step
        e.extend(_drum_pair(t, ch, 26 + (6 if i % 2 else 0)))
    return e


def drive_drums_bar(start_tick: int) -> list[tuple[int, Message]]:
    """Clearer pulse for storm / finale energy; still restrained velocities."""
    e: list[tuple[int, Message]] = []
    beat = TICKS_PER_BEAT
    step = beat // 2
    kick, ch, clap = 36, 42, 39
    for b in range(4):
        t0 = start_tick + b * beat
        e.extend(_drum_pair(t0, kick, 62 if b % 2 == 0 else 54))
        if b in (1, 3):
            e.extend(_drum_pair(t0, clap, 48))
    for i in range(8):
        t = start_tick + i * step
        e.extend(_drum_pair(t, ch, 34 + (10 if i % 2 else 0)))
    return e


def banger_drums_bar(start_tick: int) -> list[tuple[int, Message]]:
    """Four-on-the-floor + snare/clap + bright hats — club impact under strings."""
    e: list[tuple[int, Message]] = []
    beat = TICKS_PER_BEAT
    step = beat // 2
    kick, snare, clap, ch, oh = 36, 38, 39, 42, 46
    for b in range(4):
        t0 = start_tick + b * beat
        e.extend(_drum_pair(t0, kick, 110 if b == 0 else 104))
        if b in (1, 3):
            e.extend(_drum_pair(t0, snare, 90))
            e.extend(_drum_pair(t0 + 10, clap, 62))
    for i in range(8):
        t = start_tick + i * step
        vel = 58 + (16 if i % 2 else 0)
        e.extend(_drum_pair(t, oh if i % 2 else ch, min(127, vel)))
    return e


def genz_banger_drums_bar(start_tick: int) -> list[tuple[int, Message]]:
    """YouTube-era remix pocket: weighted kicks, softer snare, trap 16th hats + end-of-bar lift."""
    e: list[tuple[int, Message]] = []
    beat = TICKS_PER_BEAT
    s16 = beat // 4
    kick, snare, clap, ch, oh, rim = 36, 38, 39, 42, 46, 37
    accents = (118, 82, 112, 88)
    for b in range(4):
        t0 = start_tick + b * beat
        e.extend(_drum_pair(t0, kick, accents[b]))
        if b in (1, 3):
            e.extend(_drum_pair(t0, snare, 72))
            e.extend(_drum_pair(t0 + 11, clap, 48))
    for b in (0, 2):
        e.extend(_drum_pair(start_tick + b * beat + beat // 2, rim, 34))
    for i in range(16):
        t = start_tick + i * s16
        roll = 12 if i >= 12 else 0
        sw = i % 4 == 3
        note = oh if sw else ch
        vel = 34 + roll + (12 if i % 2 else 0)
        e.extend(_drum_pair(t, note, min(121, vel)))
    return e


def movement_drums(start: int, bars: int, mode: str) -> list[tuple[int, Message]]:
    if mode not in ("pulse", "drive"):
        return []
    bar_len = BEATS_PER_BAR * TICKS_PER_BEAT
    fn = pulse_drums_bar if mode == "pulse" else drive_drums_bar
    out: list[tuple[int, Message]] = []
    for b in range(bars):
        out.extend(fn(start + b * bar_len))
    return out


def suite_movement_drums(
    start: int,
    bars: int,
    mode: str,
    *,
    banger: bool = False,
    intro_orchestral_bars: int = 0,
    genz: bool = False,
    acoustic: bool = False,
) -> list[tuple[int, Message]]:
    """Intro stays orchestral-light drums; after that optional banger kit."""
    if acoustic or mode not in ("pulse", "drive"):
        return []
    bar_len = BEATS_PER_BAR * TICKS_PER_BEAT
    out: list[tuple[int, Message]] = []
    for b in range(bars):
        tbar = start + b * bar_len
        in_intro = b < intro_orchestral_bars
        if in_intro:
            fn = pulse_drums_bar if mode == "pulse" else drive_drums_bar
        elif banger and genz:
            fn = genz_banger_drums_bar
        elif banger:
            fn = banger_drums_bar
        else:
            fn = pulse_drums_bar if mode == "pulse" else drive_drums_bar
        out.extend(fn(tbar))
    return out


def bass_pattern_for_section(
    start: int, bars: int, roots: list[int],
) -> list[NoteEvent]:
    beat = TICKS_PER_BEAT
    eighth = beat // 2
    out: list[NoteEvent] = []
    for bar in range(bars):
        root = roots[bar % len(roots)]
        t0 = start + bar * BEATS_PER_BAR * beat
        pattern = [
            (0, eighth + eighth // 2),
            (beat + eighth, eighth),
            (3 * beat + eighth, eighth),
        ]
        for off, dur in pattern:
            out.append(NoteEvent(t0 + off, max(1, dur - 15), root, 104))
    return out


def chord_stabs_for_section(
    events: list[tuple[int, Message]],
    channel: int,
    start: int,
    bars: int,
    voicings: list[tuple[int, ...]],
    velocity: int = 78,
) -> None:
    """Short stabs on beats 2 and 4 — classic house pocket."""
    beat = TICKS_PER_BEAT
    bar_len = BEATS_PER_BAR * beat
    stab_len = beat // 4  # sixteenth, tight

    for bar in range(bars):
        voicing = voicings[bar % len(voicings)]
        t_bar = start + bar * bar_len
        for beat_index in (1, 3):  # beats 2 and 4
            t = t_bar + beat_index * beat
            add_chord_events(events, channel, t, stab_len, voicing, velocity)


def pad_chords_for_section(
    events: list[tuple[int, Message]],
    channel: int,
    start: int,
    bars: int,
    voicings: list[tuple[int, ...]],
    velocity: int = 42,
) -> None:
    """Warm whole-bar pad: chord on 1, release just before next bar."""
    beat = TICKS_PER_BEAT
    bar_len = BEATS_PER_BAR * beat
    hold = bar_len - 24

    for bar in range(bars):
        voicing = voicings[bar % len(voicings)]
        t_bar = start + bar * bar_len
        add_chord_events(events, channel, t_bar, hold, voicing, velocity)


def _open_string_voicing(triad: tuple[int, ...]) -> tuple[int, ...]:
    """Spread triad into an orchestral string choir register (~48-86)."""
    a, b, c = triad[0], triad[1], triad[2]
    n1 = max(48, min(56, a - 12))
    n2 = max(55, min(67, a + 4))
    n3 = max(60, min(76, b + 12))
    n4 = max(64, min(86, c + 12))
    return tuple(sorted({n1, n2, n3, n4}))


def _open_string_voicing_wide(triad: tuple[int, ...]) -> tuple[int, ...]:
    """Extra width + high shimmer for cinematic / new-age stacks."""
    a, b, c = triad[0], triad[1], triad[2]
    n1 = max(45, min(54, a - 12))
    n2 = max(55, min(67, a + 4))
    n3 = max(60, min(76, b + 12))
    n4 = max(64, min(88, c + 12))
    n5 = min(90, c + 24)
    return tuple(sorted({n1, n2, n3, n4, n5}))


def strings_classical_layer_for_section(
    events: list[tuple[int, Message]],
    channel: int,
    start: int,
    bars: int,
    voicings: list[tuple[int, ...]],
) -> None:
    """
    Intermittent 'original strings' flavor: sustained tutti, light offbeat
    bumps, and a short cantabile fragment — phased so the groove stays house-forward.
    Pattern each 4 bars: bars 0-1 sustained, bar 2 pizz-style, bar 3 simple line.
    """
    beat = TICKS_PER_BEAT
    bar_len = BEATS_PER_BAR * beat

    for bar in range(bars):
        phrase = bar % 4
        voicing = voicings[bar % len(voicings)]
        spread = _open_string_voicing(voicing)
        t_bar = start + bar * bar_len

        if phrase in (0, 1):
            hold = int(3.45 * beat)
            vel = 60 if phrase == 0 else 54
            add_chord_events(events, channel, t_bar, hold, spread, vel)
        elif phrase == 2:
            plen = max(50, beat // 4)
            add_chord_events(events, channel, t_bar, plen, spread, 46)
            add_chord_events(events, channel, t_bar + 2 * beat, plen, spread, 40)
        else:
            root = voicing[0]
            base = max(67, min(72, root + 12))
            pitches = [base + 2, base + 4, base + 5, base + 7]
            for i, p in enumerate(pitches):
                t = t_bar + i * beat
                dur = beat - 36
                add_chord_events(
                    events,
                    channel,
                    t,
                    dur,
                    (min(86, p),),
                    52 - i * 2,
                )
