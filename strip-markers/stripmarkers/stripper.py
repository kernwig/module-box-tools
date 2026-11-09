"""Core logic for stripping formation-marker lines from module note bodies.

Lines that consist solely of ``(Zero Box)``, ``(Zero Line)``, or ``(Home)``
(after stripping leading/trailing whitespace) are removed from the body of each
Obsidian markdown file.  The YAML frontmatter block (between the ``---``
delimiters) is left completely untouched.

Trailing blank lines at the end of the body are normalised to a single newline
so the file always ends with exactly one ``\\n``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# Lines whose entire stripped content matches one of these patterns are removed.
_MARKER_RE = re.compile(r"^\(Zero Box\)$|^\(Zero Line\)$|^\(Home\)$")


def strip_markers(text: str) -> tuple[str, int]:
    """Return *(new_text, removed_count)* after removing marker lines.

    The YAML frontmatter (the region between the first and second ``---``
    lines, inclusive) is passed through verbatim.  Only the body after the
    closing ``---`` is processed.

    A trailing newline is always present in the returned string.
    """
    # Split preserving line endings so we can reconstruct exactly.
    lines = text.splitlines(keepends=True)

    # Locate the frontmatter delimiters.
    # A valid Obsidian note starts with "---\n" and has a second "---" line.
    fm_end: int = -1  # index of the closing "---" line (inclusive)
    if lines and lines[0].rstrip() == "---":
        for i in range(1, len(lines)):
            if lines[i].rstrip() == "---":
                fm_end = i
                break

    # Partition: frontmatter lines + body lines.
    if fm_end == -1:
        # No frontmatter — process the whole file.
        fm_lines: list[str] = []
        body_lines: list[str] = list(lines)
    else:
        fm_lines = lines[: fm_end + 1]
        body_lines = lines[fm_end + 1 :]

    # Remove marker lines from the body.
    removed = 0
    filtered: list[str] = []
    for line in body_lines:
        if _MARKER_RE.match(line.rstrip("\r\n")):
            removed += 1
        else:
            filtered.append(line)

    # Normalise: strip trailing blank lines, then guarantee a final newline.
    while filtered and filtered[-1].strip() == "":
        filtered.pop()

    new_text = "".join(fm_lines) + "".join(filtered)
    if new_text and not new_text.endswith("\n"):
        new_text += "\n"

    return new_text, removed


@dataclass
class ProcessResult:
    """Summary of processing a single file."""

    path: Path
    removed: int
    modified: bool


@dataclass
class RunSummary:
    """Aggregate summary across all files."""

    visited: int = 0
    modified: int = 0
    total_removed: int = 0
    results: list[ProcessResult] = field(default_factory=list)

    def record(self, result: ProcessResult) -> None:
        self.visited += 1
        self.total_removed += result.removed
        if result.modified:
            self.modified += 1
        self.results.append(result)

    def as_text(self) -> str:
        return (
            f"{self.visited} files visited, "
            f"{self.modified} modified, "
            f"{self.total_removed} marker lines removed"
        )


def process_file(path: Path, *, dry_run: bool = False) -> ProcessResult:
    """Strip marker lines from *path*.  Returns a :class:`ProcessResult`.

    When *dry_run* is ``True`` the file is parsed but not written.
    """
    try:
        original = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"Cannot read {path}: {exc}") from exc

    new_text, removed = strip_markers(original)
    modified = removed > 0 and new_text != original

    if modified and not dry_run:
        path.write_text(new_text, encoding="utf-8")

    return ProcessResult(path=path, removed=removed, modified=modified)


def run_strip(vault: Path, *, dry_run: bool = False) -> RunSummary:
    """Recursively process all ``.md`` files under *vault*.

    Returns a :class:`RunSummary` with aggregate counts.
    """
    summary = RunSummary()
    for md_path in sorted(vault.rglob("*.md")):
        result = process_file(md_path, dry_run=dry_run)
        summary.record(result)
    return summary
