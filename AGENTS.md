# Repository Guidelines

## Project Structure & Module Organization

This repository is a LaTeX template for a Russian dissertation, synopsis, and presentation. Top-level entry points are `dissertation.tex`, `synopsis.tex`, and `presentation.tex`. Their content and settings live in `Dissertation/`, `Synopsis/`, and `Presentation/`; shared configuration is in `common/`. Bibliography files and related helpers are in `biblio/`, shared images are in `images/`, per-document images are under each document's `images/` directory, and reference standards are in `Documents/`. Build logic is split across `Makefile`, `latexmkrc`, `unix.mk`, `windows.mk`, `examples.mk`, and `compress.mk`.

## Build, Test, and Development Commands

- `make`: builds synopsis, dissertation, and presentation with the default XeLaTeX backend.
- `make dissertation`, `make synopsis`, `make presentation`: build one document.
- `make pdflatex`: builds all primary documents with `pdflatex`.
- `make examples`: broad validation across supported engines, bibliography modes, fonts, drafts, and presentation note modes.
- `make indent`: formats configured `.tex` files with `latexindent` and `indent.yaml`.
- `make clean` / `make distclean`: remove LaTeX build artifacts.
- `cd biblio && python3 check-bib-dupes-and-usage.py`: checks duplicate and unused bibliography entries.

## Coding Style & Naming Conventions

Use UTF-8, LF line endings, final newlines, and no trailing whitespace, as defined in `.editorconfig`. Use four spaces for TeX and documentation files; Makefiles and `*.mk` files use tabs. Format TeX sources with `make indent`; use `make indent-wrap` only when intentional line wrapping is desired. Keep document-specific content in its matching directory and place reusable definitions in `common/`.

## Testing Guidelines

There is no unit test suite; successful LaTeX compilation is the main test. For documentation-only changes, build the affected document. For template, bibliography, package, or style changes, run `make examples` before submitting. Inspect relevant `.log` files when a build fails, but do not commit auxiliary files such as `.aux`, `.log`, `.bcf`, `.xdv`, or generated cache output.

## Commit & Pull Request Guidelines

Recent history uses short, direct commit subjects in English or Russian, for example `Fix dissertation compilation for TexLive 2025` or `Обновить пайплайн сборки диссертации`. Conventional Commits are not required. Pull requests should describe the change, link related issues, note the test environment, confirm `make examples` when applicable, update documentation for user-visible behavior, and follow the checklist in `.github/PULL_REQUEST_TEMPLATE.md`.

## Agent-Specific Instructions

Avoid unrelated formatting churn and generated PDF changes unless preparing a release. Preserve Russian-language text, GOST-related behavior, and existing Makefile option names.

When the user does not specify a target document, treat `Dissertation/` and `dissertation.tex` as the primary work area. Edits to dissertation prose should keep a strict, official academic style without popular-science phrasing, inflated vocabulary, or unsupported conclusions. Write as a student author would: clear, direct, and technically accurate, using complex terminology only when it is necessary and has already been explained or is evident from context.

When adding or revising Russian text, make focused changes: prefer precise formulations over broad general statements, avoid repeated examples, quotations, and phrases across the dissertation, and do not introduce claims that are not present in the user's task. Every added or edited formula must be accompanied by a clear textual explanation, and every variable used in it must be defined near the formula.
