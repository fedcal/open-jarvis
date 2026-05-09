"""Minimal CLI entrypoint exposed as the `jarvis` console script.

Currently provides a single subcommand (`version`) — extended in subsequent
phases with `enroll`, `db migrate`, `rag connect`, etc.
"""

from __future__ import annotations

import argparse
import sys

from jarvis_server import __version__


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jarvis",
        description="Open-Jarvis CLI",
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"jarvis {__version__}",
    )

    sub = parser.add_subparsers(dest="command", required=False)
    sub.add_parser("version", help="Print the running Jarvis version")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Console-script entrypoint."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "version" or args.command is None:
        sys.stdout.write(f"jarvis {__version__}\n")
        return 0

    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
