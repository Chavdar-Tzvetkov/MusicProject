from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from mido import Message

from .constants import BEATS_PER_BAR, TICKS_PER_BEAT


@dataclass(frozen=True)
class NoteEvent:
    start: int
    duration: int
    pitch: int
    velocity: int = 90


def bar_ticks(bars: float = 1) -> int:
    return int(TICKS_PER_BEAT * BEATS_PER_BAR * bars)


def merge_to_deltas(events: Iterable[tuple[int, Message]]) -> list[Message]:
    """Sort by time; program/CC before notes; note_on before note_off (chord-safe)."""

    def sort_key(item: tuple[int, Message]) -> tuple[int, int, int, str]:
        t, msg = item
        if msg.type == "program_change":
            phase = 0
            sub = 0
        elif msg.type == "control_change":
            phase = 1
            sub = getattr(msg, "control", 0)
        elif msg.type == "note_on":
            phase = 2
            sub = getattr(msg, "note", 0)
        elif msg.type == "note_off":
            phase = 3
            sub = getattr(msg, "note", 0)
        else:
            phase = 4
            sub = 0
        return (t, phase, sub, msg.type)

    ordered = sorted(events, key=sort_key)
    out: list[Message] = []
    last = 0
    for abs_tick, msg in ordered:
        delta = abs_tick - last
        msg = msg.copy(time=delta)
        out.append(msg)
        last = abs_tick
    return out


def add_notes_to_events(
    events: list[tuple[int, Message]],
    channel: int,
    note_events: Iterable[NoteEvent],
) -> None:
    for ne in note_events:
        events.append(
            (ne.start, Message("note_on", channel=channel, note=ne.pitch, velocity=ne.velocity))
        )
        events.append(
            (
                ne.start + ne.duration,
                Message("note_off", channel=channel, note=ne.pitch, velocity=0),
            )
        )


def add_chord_events(
    events: list[tuple[int, Message]],
    channel: int,
    start: int,
    duration: int,
    pitches: tuple[int, ...],
    velocity: int,
) -> None:
    for p in pitches:
        events.append(
            (start, Message("note_on", channel=channel, note=p, velocity=velocity))
        )
    for p in pitches:
        events.append(
            (
                start + duration,
                Message("note_off", channel=channel, note=p, velocity=0),
            )
        )
