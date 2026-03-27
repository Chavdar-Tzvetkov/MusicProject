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


def tile_note_events(
    part: list[NoteEvent],
    section_abs_start: int,
    section_len_ticks: int,
) -> list[NoteEvent]:
    """Repeat a 0-based phrase along a section; trims overlapping the end."""
    if not part or section_len_ticks <= 0:
        return []
    period = max(ne.start + ne.duration for ne in part)
    if period <= 0:
        period = TICKS_PER_BEAT * BEATS_PER_BAR
    section_end = section_abs_start + section_len_ticks
    out: list[NoteEvent] = []
    offset = 0
    while offset < section_len_ticks:
        for ne in part:
            s = section_abs_start + offset + ne.start
            e = s + ne.duration
            if s >= section_end:
                break
            if e > section_end:
                e = section_end
            if e - s > 12:
                out.append(NoteEvent(s, e - s, ne.pitch, ne.velocity))
        offset += period
    return out


def tile_alternating_note_events(
    part_a: list[NoteEvent],
    part_b: list[NoteEvent] | None,
    section_abs_start: int,
    section_len_ticks: int,
) -> list[NoteEvent]:
    """ABAB… phrase layout for longer sections without a single looping cell."""
    if not part_b:
        return tile_note_events(part_a, section_abs_start, section_len_ticks)

    def span(part: list[NoteEvent]) -> int:
        return max((n.start + n.duration for n in part), default=TICKS_PER_BEAT)

    sa, sb = span(part_a), span(part_b)
    cap = section_abs_start + section_len_ticks
    out: list[NoteEvent] = []
    pos = 0
    use_a = True
    while pos < section_len_ticks:
        part = part_a if use_a else part_b
        seg = sa if use_a else sb
        base = section_abs_start + pos
        for ne in part:
            s = base + ne.start
            if s >= cap:
                continue
            e = s + ne.duration
            if e > cap:
                e = cap
            if e - s > 12:
                out.append(NoteEvent(s, e - s, ne.pitch, ne.velocity))
        pos += seg
        use_a = not use_a
    return out


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
