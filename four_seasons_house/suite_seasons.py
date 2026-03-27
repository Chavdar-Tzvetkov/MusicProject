from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from . import suite_notes as N


@dataclass(frozen=True)
class MovementSpec:
    title: str
    bars: int
    bpm: float
    drum_mode: str  # none | pulse | drive
    viol_part: Callable[[], list[NoteEvent]]
    harmony: tuple[tuple[int, int, int], ...]
    cello_roots: tuple[int, ...]


@dataclass(frozen=True)
class SeasonSuiteSpec:
    slug: str
    display_name: str
    movements: tuple[MovementSpec, ...]


SPRING_SUITE = SeasonSuiteSpec(
    slug="spring",
    display_name="Spring (La primavera)",
    movements=(
        MovementSpec(
            "I. Allegro",
            36,
            108.0,
            "pulse",
            N.spring_i_allegro,
            (
                (52, 56, 59),
                (49, 52, 56),
                (54, 57, 61),
                (56, 59, 64),
                (47, 51, 54),
                (52, 56, 59),
            ),
            (40, 47, 42, 39, 44, 40),
        ),
        MovementSpec(
            "II. Largo",
            20,
            52.0,
            "none",
            N.spring_ii_largo,
            (
                (49, 52, 56),
                (47, 50, 54),
                (44, 47, 51),
                (46, 49, 53),
            ),
            (37, 39, 36, 34),
        ),
        MovementSpec(
            "III. Allegro pastorale",
            28,
            96.0,
            "pulse",
            N.spring_iii_allegro_pastorale,
            (
                (52, 56, 59),
                (49, 52, 56),
                (54, 57, 61),
                (56, 59, 64),
            ),
            (40, 45, 42, 38, 43, 40),
        ),
    ),
)

SUMMER_SUITE = SeasonSuiteSpec(
    slug="summer",
    display_name="Summer (L'estate)",
    movements=(
        MovementSpec(
            "I. Allegro non molto",
            32,
            84.0,
            "pulse",
            N.summer_i_allegro,
            (
                (55, 58, 62),
                (53, 56, 60),
                (50, 53, 58),
                (51, 55, 58),
                (53, 56, 62),
            ),
            (43, 41, 38, 40, 36, 43),
        ),
        MovementSpec(
            "II. Adagio",
            16,
            58.0,
            "none",
            N.summer_ii_adagio,
            (
                (53, 56, 60),
                (51, 54, 59),
                (50, 53, 58),
                (48, 51, 55),
            ),
            (38, 41, 43, 36),
        ),
        MovementSpec(
            "III. Presto",
            28,
            132.0,
            "drive",
            N.summer_iii_presto,
            (
                (55, 58, 62),
                (53, 56, 60),
                (56, 59, 62),
                (50, 53, 58),
            ),
            (43, 46, 41, 38, 43, 41),
        ),
    ),
)

AUTUMN_SUITE = SeasonSuiteSpec(
    slug="autumn",
    display_name="Autumn (L'autunno)",
    movements=(
        MovementSpec(
            "I. Allegro",
            32,
            100.0,
            "pulse",
            N.autumn_i_allegro,
            (
                (53, 57, 60),
                (55, 59, 62),
                (50, 53, 57),
                (48, 52, 55),
                (52, 55, 60),
            ),
            (41, 43, 38, 36, 40, 41),
        ),
        MovementSpec(
            "II. Adagio molto",
            18,
            54.0,
            "none",
            N.autumn_ii_adagio,
            (
                (52, 55, 60),
                (50, 53, 57),
                (48, 51, 55),
                (46, 50, 53),
            ),
            (36, 38, 33, 41),
        ),
        MovementSpec(
            "III. Allegro (The Hunt)",
            30,
            112.0,
            "drive",
            N.autumn_iii_allegro,
            (
                (53, 57, 60),
                (55, 59, 62),
                (52, 55, 60),
                (48, 52, 55),
            ),
            (41, 36, 43, 38, 41, 39),
        ),
    ),
)

WINTER_SUITE = SeasonSuiteSpec(
    slug="winter",
    display_name="Winter (L'inverno)",
    movements=(
        MovementSpec(
            "I. Allegro non molto",
            32,
            80.0,
            "pulse",
            N.winter_i_allegro,
            (
                (53, 56, 60),
                (51, 54, 58),
                (48, 51, 55),
                (46, 50, 53),
                (50, 53, 56),
            ),
            (41, 39, 44, 36, 41, 43),
        ),
        MovementSpec(
            "II. Largo",
            18,
            48.0,
            "none",
            N.winter_ii_largo,
            (
                (51, 54, 58),
                (49, 52, 56),
                (46, 50, 53),
                (48, 51, 55),
            ),
            (39, 37, 42, 34),
        ),
        MovementSpec(
            "III. Allegro",
            28,
            120.0,
            "drive",
            N.winter_iii_allegro,
            (
                (53, 56, 60),
                (51, 54, 58),
                (55, 58, 62),
                (50, 53, 57),
            ),
            (41, 44, 39, 43, 41, 36),
        ),
    ),
)


ALL_SUITE_SEASONS: tuple[SeasonSuiteSpec, ...] = (
    SPRING_SUITE,
    SUMMER_SUITE,
    AUTUMN_SUITE,
    WINTER_SUITE,
)
