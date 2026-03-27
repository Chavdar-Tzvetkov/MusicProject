"""
Split a finished *_suite.mid into individual stem files.

Each stem is a valid Type-1 MIDI: meta (tempo map) + one instrument track with all
messages moved to channel 0 (except drums → channel 9). That helps:

- FluidSynth / simple players that behave best with “one sound per file”
- Loading different non-GM / multi-timbral setups without a DAW
"""

from __future__ import annotations

from pathlib import Path

from mido import MetaMessage, MidiFile, MidiTrack


# Output filename → track_name substring(s) from compile_suite_midi (exact match)
STEM_DEFINITIONS: list[tuple[str, tuple[str, ...]]] = [
    ("solo.mid", ("Violin solo",)),
    ("ripieno_viola.mid", ("Viola",)),
    ("ripieno_tutti.mid", ("String ensemble",)),
    ("bassi_cello.mid", ("Cello",)),
    ("bassi_contrabass.mid", ("Contrabass",)),
    ("continuo.mid", ("Continuo harpsichord",)),
    ("harp.mid", ("Harp",)),
    ("pads_modern.mid", ("New-age bed", "Modern bed (EP)")),
    ("pads_atmos.mid", ("Atmos pad",)),
    ("sparkle.mid", ("Celesta sparkle",)),
    ("sub.mid", ("Sub (map to 808)",)),
    ("drums.mid", ("Drums",)),
]


def _track_name(track: MidiTrack) -> str:
    for msg in track:
        if msg.type == "track_name":
            return str(msg.name)
    return ""


def _clone_track(track: MidiTrack) -> MidiTrack:
    out = MidiTrack()
    for msg in track:
        out.append(msg.copy())
    return out


def _remap_channel_track(src: MidiTrack, target_ch: int, stem_label: str) -> MidiTrack:
    """Drop original track_name meta; prepends new name; remaps channel on channel messages."""
    out = MidiTrack()
    out.append(MetaMessage("track_name", name=stem_label, time=0))
    for msg in src:
        if msg.is_meta:
            if msg.type == "track_name":
                continue
            out.append(msg.copy())
        elif hasattr(msg, "channel"):
            out.append(msg.copy(channel=target_ch))
        else:
            out.append(msg.copy())
    return out


def _index_tracks_by_name(mid: MidiFile) -> dict[str, MidiTrack]:
    out: dict[str, MidiTrack] = {}
    for tr in mid.tracks[1:]:
        n = _track_name(tr)
        if n:
            out[n] = tr
    return out


def export_stems_from_suite_mid(mid_path: Path, out_dir: Path) -> list[Path]:
    mid = MidiFile(mid_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    by_name = _index_tracks_by_name(mid)
    meta = mid.tracks[0]
    written: list[Path] = []

    for filename, aliases in STEM_DEFINITIONS:
        src: MidiTrack | None = None
        for a in aliases:
            if a in by_name:
                src = by_name[a]
                break
        if src is None:
            continue
        target_ch = 9 if filename == "drums.mid" else 0
        stem_label = filename.replace(".mid", "").replace("_", " ")
        music = _remap_channel_track(src, target_ch, stem_label)
        out_mid = MidiFile(type=1, ticks_per_beat=mid.ticks_per_beat)
        out_mid.tracks.append(_clone_track(meta))
        out_mid.tracks.append(music)
        dest = out_dir / filename
        out_mid.save(str(dest))
        written.append(dest)
    return written


def export_stems_for_output_folder(output_dir: Path | str) -> None:
    """For each *_suite.mid in output_dir, write output_dir/stems/<stem_name>/*.mid"""
    output_dir = Path(output_dir)
    mids = sorted(output_dir.glob("*_suite.mid"))
    if not mids:
        return
    for mid in mids:
        sub = output_dir / "stems" / mid.stem
        files = export_stems_from_suite_mid(mid, sub)
        print(f"Orchestral stems ({len(files)} files) -> {sub}")
