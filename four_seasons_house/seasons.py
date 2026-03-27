from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .constants import TICKS_PER_BEAT
from .midi_util import NoteEvent


@dataclass(frozen=True)
class SeasonSpec:
    slug: str
    display_name: str
    bars: int
    bass_roots: list[int]
    stab_voicings: list[tuple[int, ...]]
    lead_builder: Callable[[], list[NoteEvent]]


def _spring_lead() -> list[NoteEvent]:
    beat = TICKS_PER_BEAT
    q = beat // 2
    pit_a = [64, 59, 64, 68, 64, 59, 64, 68, 64, 66, 68, 71, 68, 66, 64, 59]
    pit_b = [64, 66, 71, 68, 66, 64, 68, 71, 73, 71, 68, 64, 66, 64, 59, 57]
    out: list[NoteEvent] = []
    t = 0
    for pit in (pit_a, pit_b):
        for p in pit:
            out.append(NoteEvent(t, q - 10, p, 102))
            t += q
    return out


def _summer_lead() -> list[NoteEvent]:
    beat = TICKS_PER_BEAT
    s16 = beat // 4
    pit_a = [67, 65, 67, 62, 65, 63, 60, 63, 65, 67, 65, 63, 62, 60]
    pit_b = [60, 62, 63, 65, 67, 65, 63, 62, 67, 65, 63, 60, 58, 60]
    out: list[NoteEvent] = []
    t = 0
    for pit in (pit_a, pit_b):
        for p in pit:
            out.append(NoteEvent(t, s16 * 2 - 8, p, 96))
            t += s16 * 2
    return out


def _autumn_lead() -> list[NoteEvent]:
    beat = TICKS_PER_BEAT
    eighth = beat // 2
    pit_a = [65, 69, 67, 71, 69, 72, 71, 74, 72, 69, 67, 65, 64, 67, 65, 62]
    pit_b = [65, 67, 69, 72, 74, 72, 69, 67, 65, 64, 65, 67, 69, 71, 69, 65]
    out: list[NoteEvent] = []
    t = 0
    for pit in (pit_a, pit_b):
        for p in pit:
            out.append(NoteEvent(t, eighth - 10, p, 100))
            t += eighth
    return out


def _winter_lead() -> list[NoteEvent]:
    beat = TICKS_PER_BEAT
    q = beat // 2
    pit_a = [63, 65, 63, 60, 58, 63, 65, 68, 65, 63, 60, 58, 56, 58, 60, 63]
    pit_b = [60, 58, 60, 63, 65, 63, 60, 58, 55, 58, 60, 63, 65, 63, 60, 58]
    out: list[NoteEvent] = []
    t = 0
    for idx, pit in enumerate((pit_a, pit_b)):
        for i, p in enumerate(pit):
            stretch = (idx == 1) and i in (4, 9, 14)
            dur = q + (q // 2) if i in (4, 8, 12) and idx == 0 else (q + q // 2 if stretch else q - 8)
            out.append(NoteEvent(t, dur, p, 88 if idx == 0 else 86))
            t += dur
    return out


def _pad_voicings_from_stabs(stabs: list[tuple[int, ...]]) -> list[tuple[int, ...]]:
    """Pads an octave below stabs for weight (clamped MIDI 36–84)."""
    out: list[tuple[int, ...]] = []
    for chord in stabs:
        shifted = tuple(max(36, min(84, n - 12)) for n in chord)
        out.append(shifted)
    return out


SPRING = SeasonSpec(
    slug="spring",
    display_name="Spring (La primavera)",
    bars=16,
    bass_roots=[40, 45, 40, 45],
    stab_voicings=[
        (52, 56, 59),
        (57, 61, 64),
        (54, 57, 61),
        (56, 59, 64),
    ],
    lead_builder=_spring_lead,
)

SUMMER = SeasonSpec(
    slug="summer",
    display_name="Summer (L'estate)",
    bars=16,
    bass_roots=[43, 41, 43, 46],
    stab_voicings=[
        (55, 58, 62),
        (53, 56, 60),
        (55, 58, 63),
        (50, 53, 58),
    ],
    lead_builder=_summer_lead,
)

AUTUMN = SeasonSpec(
    slug="autumn",
    display_name="Autumn (L'autunno)",
    bars=16,
    bass_roots=[41, 46, 43, 48],
    stab_voicings=[
        (53, 57, 60),
        (58, 62, 65),
        (55, 59, 62),
        (53, 56, 60),
    ],
    lead_builder=_autumn_lead,
)

WINTER = SeasonSpec(
    slug="winter",
    display_name="Winter (L'inverno)",
    bars=16,
    bass_roots=[51, 50, 48, 43],
    stab_voicings=[
        (51, 54, 58),
        (50, 53, 57),
        (48, 51, 55),
        (46, 50, 53),
    ],
    lead_builder=_winter_lead,
)


ALL_SEASONS: tuple[SeasonSpec, ...] = (SPRING, SUMMER, AUTUMN, WINTER)


def pad_voicings_for(spec: SeasonSpec) -> list[tuple[int, ...]]:
    return _pad_voicings_from_stabs(list(spec.stab_voicings))
