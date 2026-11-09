"""Tests for stripmarkers.stripper."""
from pathlib import Path

import pytest

from stripmarkers.stripper import strip_markers, process_file, run_strip, RunSummary


# ---------------------------------------------------------------------------
# strip_markers — unit tests
# ---------------------------------------------------------------------------


def _s(text: str) -> str:
    """Dedent helper: normalise leading newline from triple-quoted strings."""
    return text.lstrip("\n")


class TestStripMarkers:
    def test_removes_zero_box(self):
        text = _s("""
---
start: box
---
(Zero Box)
Circle Left
(Zero Box)
""")
        result, count = strip_markers(text)
        assert count == 2
        assert "(Zero Box)" not in result
        assert "Circle Left" in result

    def test_removes_zero_line(self):
        text = _s("""
---
start: lines
---
(Zero Line)
Pass Thru
(Zero Line)
""")
        result, count = strip_markers(text)
        assert count == 2
        assert "(Zero Line)" not in result

    def test_removes_home(self):
        text = _s("""
---
start: home
---
(Home)
Promenade
(Home)
""")
        result, count = strip_markers(text)
        assert count == 2
        assert "(Home)" not in result

    def test_removes_mixed_markers(self):
        text = _s("""
---
start: box
end: lines
---
(Zero Box)
Circle Left
Veer Left
(Zero Line)
""")
        result, count = strip_markers(text)
        assert count == 2
        assert "Circle Left" in result
        assert "Veer Left" in result

    def test_frontmatter_untouched(self):
        text = _s("""
---
start: box
note: (Zero Box) is a formation
---
(Zero Box)
Promenade
""")
        result, count = strip_markers(text)
        # The frontmatter line is kept; only the body line is removed.
        assert count == 1
        assert "note: (Zero Box) is a formation" in result

    def test_no_markers_returns_unchanged(self):
        text = _s("""
---
start: home
---
Circle Left
Swing
Promenade
""")
        result, count = strip_markers(text)
        assert count == 0
        assert result == text

    def test_file_without_frontmatter(self):
        text = "(Zero Box)\nCircle Left\n(Zero Box)\n"
        result, count = strip_markers(text)
        assert count == 2
        assert "(Zero Box)" not in result
        assert "Circle Left\n" == result

    def test_trailing_blank_lines_normalised(self):
        text = _s("""
---
start: box
---
(Zero Box)
Circle Left
(Zero Box)


""")
        result, _ = strip_markers(text)
        # Body should end with exactly one newline (no trailing blanks).
        assert result.endswith("Circle Left\n")

    def test_result_always_ends_with_newline(self):
        text = "---\nstart: box\n---\n(Zero Box)\nCircle Left"
        result, _ = strip_markers(text)
        assert result.endswith("\n")

    def test_partial_match_not_removed(self):
        """Lines that contain a marker as a substring are kept."""
        text = _s("""
---
start: box
---
This is not (Zero Box) exactly
(Zero Box)
Pass Thru
""")
        result, count = strip_markers(text)
        assert count == 1
        assert "This is not (Zero Box) exactly" in result

    def test_whitespace_only_line_around_marker(self):
        """Blank lines around a marker are preserved (not treated as markers)."""
        text = _s("""
---
start: box
---

(Zero Box)
Circle Left

""")
        result, count = strip_markers(text)
        assert count == 1
        assert "(Zero Box)" not in result
        # The blank line before is kept (it is body content, not a marker).
        assert "\n\n" in result


# ---------------------------------------------------------------------------
# process_file — filesystem integration
# ---------------------------------------------------------------------------


class TestProcessFile:
    def test_dry_run_does_not_write(self, tmp_path: Path):
        md = tmp_path / "test.md"
        original = "---\nstart: box\n---\n(Zero Box)\nCircle Left\n(Zero Box)\n"
        md.write_text(original, encoding="utf-8")

        result = process_file(md, dry_run=True)

        assert result.modified is True
        assert result.removed == 2
        # File on disk must be unchanged.
        assert md.read_text(encoding="utf-8") == original

    def test_writes_modified_file(self, tmp_path: Path):
        md = tmp_path / "test.md"
        md.write_text("---\nstart: box\n---\n(Zero Box)\nCircle Left\n", encoding="utf-8")

        result = process_file(md, dry_run=False)

        assert result.modified is True
        assert md.read_text(encoding="utf-8") == "---\nstart: box\n---\nCircle Left\n"

    def test_unmodified_file_not_written(self, tmp_path: Path, monkeypatch):
        md = tmp_path / "test.md"
        original = "---\nstart: box\n---\nCircle Left\n"
        md.write_text(original, encoding="utf-8")

        # Track write_text calls.
        written = []
        real_write = Path.write_text

        def spy_write(self, *args, **kwargs):
            written.append(self)
            real_write(self, *args, **kwargs)

        monkeypatch.setattr(Path, "write_text", spy_write)

        result = process_file(md, dry_run=False)

        assert result.modified is False
        assert result.removed == 0
        assert written == []  # write_text never called


# ---------------------------------------------------------------------------
# run_strip — directory recursion
# ---------------------------------------------------------------------------


class TestRunStrip:
    def _write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_processes_all_md_files(self, tmp_path: Path):
        self._write(tmp_path / "a.md", "---\nstart: box\n---\n(Zero Box)\nA\n")
        self._write(tmp_path / "sub" / "b.md", "---\nstart: home\n---\n(Home)\nB\n")
        self._write(tmp_path / "sub" / "c.md", "---\nstart: box\n---\nC\n")

        summary = run_strip(tmp_path)

        assert summary.visited == 3
        assert summary.modified == 2
        assert summary.total_removed == 2

    def test_non_md_files_skipped(self, tmp_path: Path):
        self._write(tmp_path / "note.md", "---\nstart: box\n---\n(Zero Box)\nA\n")
        self._write(tmp_path / "data.txt", "(Zero Box)\n")

        summary = run_strip(tmp_path)

        assert summary.visited == 1  # only the .md file

    def test_as_text_format(self, tmp_path: Path):
        self._write(tmp_path / "a.md", "---\nstart: box\n---\n(Zero Box)\nA\n(Zero Box)\n")

        summary = run_strip(tmp_path)

        text = summary.as_text()
        assert "1 files visited" in text
        assert "1 modified" in text
        assert "2 marker lines removed" in text
