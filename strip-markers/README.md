# strip-markers

Removes formation-marker comment lines from square dance module notes in an
Obsidian vault.

The following lines are removed when they appear as the **entire content** of a
line (whitespace-trimmed) in the body of a note (frontmatter is never touched):

| Marker      | Meaning                             |
|-------------|-------------------------------------|
| `(Zero Box)` | Module starts and ends in a box    |
| `(Zero Line)` | Module starts and ends in a line  |
| `(Home)`     | Module starts and ends at home     |

This information is already captured in the `start` / `end` frontmatter
properties, so these inline annotations are redundant.

## Setup

```bash
cd module-box-tools/strip-markers
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Usage

```bash
# Preview — show what would change without writing:
python -m stripmarkers.cli --dry-run

# Preview with per-file detail:
python -m stripmarkers.cli --dry-run --verbose

# Apply to the default vault (BDP-Obsidian/Module-Box):
python -m stripmarkers.cli

# Apply to a custom vault folder:
python -m stripmarkers.cli --vault /path/to/vault/Module-Box

# Apply with per-file output:
python -m stripmarkers.cli --verbose
```

## Tests

```bash
pytest
```
