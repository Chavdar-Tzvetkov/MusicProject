from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .midi_util import NoteEvent
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
    banger: bool = False
    intro_orchestral_bars: int = 0
    viol_alt: Callable[[], list[NoteEvent]] | None = None


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
            92,
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
            banger=True,
            intro_orchestral_bars=16,
            viol_alt=N.spring_i_allegro_b,
        ),
        MovementSpec(
            "II. Largo",
            56,
            50.0,
            "none",
            N.spring_ii_largo,
            (
                (49, 52, 56),
                (47, 50, 54),
                (44, 47, 51),
                (46, 49, 53),
            ),
            (37, 39, 36, 34),
            viol_alt=N.spring_ii_largo_b,
        ),
        MovementSpec(
            "III. Allegro pastorale",
            76,
            98.0,
            "pulse",
            N.spring_iii_allegro_pastorale,
            (
                (52, 56, 59),
                (49, 52, 56),
                (54, 57, 61),
                (56, 59, 64),
            ),
            (40, 45, 42, 38, 43, 40),
            banger=True,
            intro_orchestral_bars=10,
            viol_alt=N.spring_iii_allegro_pastorale_b,
        ),
    ),
)

SUMMER_SUITE = SeasonSuiteSpec(
    slug="summer",
    display_name="Summer (L'estate)",
    movements=(
        MovementSpec(
            "I. Allegro non molto",
            84,
            86.0,
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
            banger=True,
            intro_orchestral_bars=12,
            viol_alt=N.summer_i_allegro_b,
        ),
        MovementSpec(
            "II. Adagio",
            48,
            56.0,
            "none",
            N.summer_ii_adagio,
            (
                (53, 56, 60),
                (51, 54, 59),
                (50, 53, 58),
                (48, 51, 55),
            ),
            (38, 41, 43, 36),
            viol_alt=N.summer_ii_adagio_b,
        ),
        MovementSpec(
            "III. Presto",
            100,
            138.0,
            "drive",
            N.summer_iii_presto,
            (
                (55, 58, 62),
                (53, 56, 60),
                (56, 59, 62),
                (50, 53, 58),
            ),
            (43, 46, 41, 38, 43, 41),
            banger=True,
            intro_orchestral_bars=8,
            viol_alt=N.summer_iii_presto_b,
        ),
    ),
)

AUTUMN_SUITE = SeasonSuiteSpec(
    slug="autumn",
    display_name="Autumn (L'autunno)",
    movements=(
        MovementSpec(
            "I. Allegro",
            88,
            102.0,
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
            banger=True,
            intro_orchestral_bars=14,
            viol_alt=N.autumn_i_allegro_b,
        ),
        MovementSpec(
            "II. Adagio molto",
            48,
            52.0,
            "none",
            N.autumn_ii_adagio,
            (
                (52, 55, 60),
                (50, 53, 57),
                (48, 51, 55),
                (46, 50, 53),
            ),
            (36, 38, 33, 41),
            viol_alt=N.autumn_ii_adagio_b,
        ),
        MovementSpec(
            "III. Allegro (The Hunt)",
            92,
            118.0,
            "drive",
            N.autumn_iii_allegro,
            (
                (53, 57, 60),
                (55, 59, 62),
                (52, 55, 60),
                (48, 52, 55),
            ),
            (41, 36, 43, 38, 41, 39),
            banger=True,
            intro_orchestral_bars=8,
            viol_alt=N.autumn_iii_allegro_b,
        ),
    ),
)

WINTER_SUITE = SeasonSuiteSpec(
    slug="winter",
    display_name="Winter (L'inverno)",
    movements=(
        MovementSpec(
            "I. Allegro non molto",
            86,
            82.0,
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
            banger=True,
            intro_orchestral_bars=12,
            viol_alt=N.winter_i_allegro_b,
        ),
        MovementSpec(
            "II. Largo",
            52,
            46.0,
            "none",
            N.winter_ii_largo,
            (
                (51, 54, 58),
                (49, 52, 56),
                (46, 50, 53),
                (48, 51, 55),
            ),
            (39, 37, 42, 34),
            viol_alt=N.winter_ii_largo_b,
        ),
        MovementSpec(
            "III. Allegro",
            84,
            126.0,
            "drive",
            N.winter_iii_allegro,
            (
                (53, 56, 60),
                (51, 54, 58),
                (55, 58, 62),
                (50, 53, 57),
            ),
            (41, 44, 39, 43, 41, 36),
            banger=True,
            intro_orchestral_bars=6,
            viol_alt=N.winter_iii_allegro_b,
        ),
    ),
)


ALL_SUITE_SEASONS: tuple[SeasonSuiteSpec, ...] = (
    SPRING_SUITE,
    SUMMER_SUITE,
    AUTUMN_SUITE,
    WINTER_SUITE,
)
