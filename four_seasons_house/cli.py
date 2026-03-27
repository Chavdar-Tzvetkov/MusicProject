from __future__ import annotations

import argparse
from pathlib import Path

from .builder import build_all_house
from .suite import build_all_suites


def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate Vivaldi Four Seasons arrangements as MIDI (classical/modern suite by default).",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("output"),
        help="Directory for .mid files (default: ./output)",
    )
    p.add_argument(
        "--legacy-house",
        action="store_true",
        help="Emit short house/EDM loop sketches (*_house.mid) instead of the full orchestral suite.",
    )
    p.add_argument(
        "--bpm",
        type=float,
        default=124.0,
        help="Tempo for --legacy-house only (default: 124).",
    )
    args = p.parse_args()
    if args.legacy_house:
        build_all_house(args.output, bpm=args.bpm)
    else:
        build_all_suites(args.output)


if __name__ == "__main__":
    main()
