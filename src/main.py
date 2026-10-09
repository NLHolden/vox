from __future__ import annotations

import logging
from collections.abc import Sequence

from cli import parse_args
from vox import run_vox

LOGGER = logging.getLogger("vox")


def main(argv: Sequence[str] | None = None) -> int:
    """Parse command-line options and run the renderer."""
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )
    try:
        run_vox(args.config, args.audio, args.output)
    except (OSError, ValueError, RuntimeError) as exc:
        LOGGER.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
