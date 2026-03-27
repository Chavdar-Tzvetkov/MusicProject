from __future__ import annotations

from mido import Message

from .constants import BEATS_PER_BAR, TICKS_PER_BEAT


def add_program_change(
    events: list[tuple[int, Message]],
    channel: int,
    program: int,
    tick: int = 0,
) -> None:
    events.append(
        (tick, Message("program_change", channel=channel, program=max(0, min(127, program))))
    )


def add_filter_sweep_triangle(
    events: list[tuple[int, Message]],
    channel: int,
    duration_ticks: int,
    *,
    control: int = 74,
    low: int = 36,
    high: int = 120,
) -> None:
    """
    CC triangle over the piece length (GM2/Roland-style cutoff on CC 74 — map in your DAW if needed).
    low → high → low.
    """
    if duration_ticks <= 0:
        return
    half = max(1, duration_ticks // 2)
    step = max(TICKS_PER_BEAT // 8, 30)  # 32nd-note grid, not too dense for file size
    t = 0
    prev_v: int | None = None
    while t <= duration_ticks:
        if t <= half:
            v = int(low + (high - low) * (t / half))
        else:
            rest = duration_ticks - half
            v = int(high - (high - low) * ((t - half) / max(1, rest)))
        v = max(0, min(127, v))
        if prev_v != v:
            events.append(
                (t, Message("control_change", channel=channel, control=control, value=v))
            )
            prev_v = v
        t += step


def add_pad_sidechain_pump(
    events: list[tuple[int, Message]],
    channel: int,
    total_bars: int,
) -> None:
    """
    Duck pad with CC 11 (Expression) on every downbeat (4-on-the-floor) for a sidechain-like pocket.
    """
    beat = TICKS_PER_BEAT

    for bar in range(total_bars):
        for beat_i in range(BEATS_PER_BAR):
            t = (bar * BEATS_PER_BAR + beat_i) * beat
            rel = int(beat * 0.24)
            events.append((t, Message("control_change", channel=channel, control=11, value=18)))
            events.append(
                (t + max(20, rel // 4), Message("control_change", channel=channel, control=11, value=58))
            )
            events.append(
                (t + rel, Message("control_change", channel=channel, control=11, value=102))
            )
            events.append(
                (t + int(rel * 1.45), Message("control_change", channel=channel, control=11, value=127))
            )

