"""Command-line argument parsing and dispatch for Vox."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """Build the Vox command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="vox",
        description=(
            "Create an MP4 video by synchronizing an audio file with the "
            "configured NLHolden animations."
        ),
    )
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        required=True,
        help="JSON file containing the static image and animation paths.",
    )
    parser.add_argument(
        "--audio",
        "-i",
        type=Path,
        required=True,
        help="Input audio file.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        required=True,
        help="Output video file (must use the .mp4 extension).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show progress and informational messages.",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the Vox application."""
    return build_parser().parse_args(argv)
