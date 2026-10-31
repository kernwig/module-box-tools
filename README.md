# module-box-tools

Tooling for building a library of square-dance **choreography modules**
stored as Obsidian markdown files, for use with the
[Square Dance Module Box](https://github.com/kernwig/module-box) Obsidian
plugin. Each sub-project is independent and has its own README.

| Sub-project | Language | What it does |
|---|---|---|
| [`sd-choreo-importer`](sd-choreo-importer/) | Python | Imports choreography modules into the vault from external sources (currently [ceder.net](https://www.ceder.net/choreodb/)), conforming to the module schema. |
| [`level-classifier`](level-classifier/) | Python | Detects the program level (Mainstream / Plus / A1 / A2) of a module from the calls in its body, and reconciles its `level` frontmatter and folder. |
| [`square-caller-plugin`](square-caller-plugin/) | TypeScript / Obsidian | **Archived.** The private beta of the calling plugin. It is replaced by [Module Box](https://github.com/kernwig/module-box). |

A **module** is a markdown file with `start`, `end`, and `level` frontmatter
(plus optional `difficulty` / `author` / boolean flags) and a call-list body.
`sd-choreo-importer` creates them, `level-classifier` keeps their level correct,
and [Module Box](https://github.com/kernwig/module-box) shows them while you
call a dance.

## License

[GPL-3.0](LICENSE).
