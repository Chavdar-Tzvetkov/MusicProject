#!/usr/bin/env python3
"""
Render MIDI from output/ to WAV using FluidSynth + a sampled .sf2 soundfont.
This is how you get *real instrument samples* from the same MIDI the generator writes.

Requirements:
  - FluidSynth on PATH: https://www.fluidsynth.org/
  - A General MIDI-compatible .sf2 (orchestral fonts work best). Browse:
    https://musical-artifacts.com/?formats=sf2

Example:
  python render_fluidsynth.py --sf2 "C:\\Sounds\\GeneralUser_GS.sf2"
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser(description="MIDI -> WAV via FluidSynth + SF2")
    p.add_argument(
        "--sf2",
        type=Path,
        required=True,
        help="Path to a .sf2 soundfont (e.g. GeneralUser GS, FluidR3_GM, or an orchestral SF2)",
    )
    p.add_argument(
        "--midi-dir",
        type=Path,
        default=Path("output"),
        help="Folder containing .mid files (default: ./output). Use output/stems/spring_suite for one stem set.",
    )
    p.add_argument(
        "--recursive",
        action="store_true",
        help="Also render every .mid under subfolders (e.g. output/stems/*/).",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("output") / "wav",
        help="Where to write .wav files (default: ./output/wav)",
    )
    p.add_argument("--rate", type=int, default=48000, help="Sample rate (default 48000)")
    args = p.parse_args()

    if not args.sf2.is_file():
        print(f"Soundfont not found: {args.sf2}", file=sys.stderr)
        sys.exit(1)

    fs = shutil.which("fluidsynth")
    if not fs:
        print(
            "fluidsynth is not on PATH. Install FluidSynth, then retry.\n"
            "  Windows: https://github.com/FluidSynth/fluidsynth/releases or a package manager\n"
            "  macOS: brew install fluidsynth\n"
            "  Linux: apt install fluidsynth",
            file=sys.stderr,
        )
        sys.exit(1)

    args.midi_dir = args.midi_dir.resolve()
    args.out_dir = args.out_dir.resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.recursive:
        mids = sorted(args.midi_dir.rglob("*.mid"))
    else:
        mids = sorted(args.midi_dir.glob("*.mid"))
    if not mids:
        print(f"No .mid files in {args.midi_dir}", file=sys.stderr)
        sys.exit(1)

    for mid in mids:
        rel = mid.relative_to(args.midi_dir) if mid.is_relative_to(args.midi_dir) else mid.name
        wav = args.out_dir / rel.with_suffix(".wav")
        wav.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            fs,
            "-ni",
            str(args.sf2.resolve()),
            str(mid.resolve()),
            "-F",
            str(wav),
            "-r",
            str(args.rate),
        ]
        print(" ".join(cmd))
        subprocess.run(cmd, check=True)
        print(f"OK {wav}")


if __name__ == "__main__":
    main()
