from __future__ import annotations

import argparse
from pathlib import Path

from .builder import build_all
from .constants import DEFAULT_BPM


def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate house/EDM MIDI inspired by Vivaldi's Four Seasons.",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("output"),
        help="Directory for .mid files (default: ./output)",
    )
    p.add_argument(
        "--bpm",
        type=float,
        default=DEFAULT_BPM,
        help=f"Tempo (default: {DEFAULT_BPM})",
    )
    args = p.parse_args()
    build_all(args.output, bpm=args.bpm)


if __name__ == "__main__":
    main()
