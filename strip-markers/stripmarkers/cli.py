"""Command-line entry point for the strip-markers tool.

Example:
    # Preview changes without writing:
    python -m stripmarkers.cli --dry-run

    # Apply changes to the default vault:
    python -m stripmarkers.cli

    # Target a specific folder:
    python -m stripmarkers.cli --vault /path/to/vault/Module-Box
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from .stripper import run_strip

# Default vault target: BDP-Obsidian/Module-Box relative to the workspace root.
# strip-markers/stripmarkers/cli.py → workspace root is parents[3].
_REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_VAULT = _REPO_ROOT / "BDP-Obsidian" / "Module-Box"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stripmarkers",
        description=(
            "Remove formation-marker lines — (Zero Box), (Zero Line), (Home) —"
            " from square dance module notes."
        ),
    )
    p.add_argument(
        "--vault",
        type=Path,
        default=DEFAULT_VAULT,
        help=f"Vault folder to process (default: {DEFAULT_VAULT}).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without writing any files.",
    )
    p.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print each modified file path.",
    )
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    vault: Path = args.vault
    if not vault.exists():
        print(f"error: vault path does not exist: {vault}", file=sys.stderr)
        return 2

    summary = run_strip(vault, dry_run=args.dry_run)

    mode = " (dry run)" if args.dry_run else ""
    print(f"{summary.as_text()}{mode}")
    print(f"vault: {vault}")

    if args.verbose:
        for result in summary.results:
            if result.modified:
                print(f"  modified ({result.removed} removed): {result.path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
