# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

LaTeX template for a Russian PhD dissertation (диссертация), its synopsis (автореферат), and defense presentation, conforming to ГОСТ Р 7.0.11-2011. All content is UTF-8 Russian; user-facing documentation (`README.md`, `Readme/*.md`, `CONTRIBUTING.md`) is in Russian — preserve that when editing. There is no application code — only `.tex` sources, `.mk` build glue, a `latexmkrc`, and a `Dockerfile`.

## Build commands

The Makefile is the canonical entry point. `make` invokes `latexmk` under the hood via `latexmkrc`. Run from the repository root.

- `make` — build dissertation + synopsis + presentation
- `make dissertation` / `make synopsis` / `make presentation` — single target
- `make dissertation-draft` / `make synopsis-draft` / `make draft` — fast draft mode (ГОСТ-incomplete, used during writing)
- `make synopsis-booklet` / `make presentation-booklet` / `make presentation-handout` — A4 print variants (depend on the corresponding main target)
- `make pdflatex` — build everything with pdfLaTeX instead of XeLaTeX
- `make tikz TIKZFILE=path/to/file.tikz` — isolated TikZ compile (uses LuaLaTeX, since some libs require it)
- `make clean` / `make distclean` — remove aux files (`clean`) or aux+PDF (`distclean`)
- `make indent` — run `latexindent` on `Dissertation/part*.tex`, `Synopsis/content.tex`, `Presentation/content.tex` using `indent.yaml`
- `make compress-lowdpi` / `make compress-cmyk` — Ghostscript postprocess (see `compress.mk`)
- `make examples` — full matrix build across 3 engines × 2 biblio backends × draft/non-draft × multiple fonts. This is the CI-equivalent gate `CONTRIBUTING.md` requires before opening a PR that touches the template. Slow.
- `make help` — auto-generated rule list (Unix only)

Build is serialized (`.NOTPARALLEL`) — do not try `make -j`.

## Build configuration model

The build behavior is controlled by a layered config system. Precedence (highest first):

1. Command-line variable: `make dissertation BACKEND=-pdf USEBIBER=0`
2. `usercfg.mk` (gitignored-style user overrides; committed but meant to be edited)
3. `unix.mk` (on Unix; sets `FONTFAMILY ?= 2`) or `windows.mk` (on Windows)
4. Defaults in `Makefile`

The Makefile `export`s these variables; `latexmkrc` reads them from the environment and translates each into `\newcounter{...}\setcounter{...}{N}` injected before `\input{%T}`. The same counters can also be set directly in `common/setup.tex` — that file documents the canonical meanings.

Key knobs:

- `BACKEND` — `-pdf` (pdfLaTeX), `-pdfxe` (XeLaTeX, **default**), `-xelatex`, `-pdflua` (LuaLaTeX), `-lualatex`. The `-pdfxe`/`-pdflua` forms route through DVI and are faster than the direct ones.
- `USEBIBER` — `0` = bibtex8, `1` = biber/biblatex (default in `common/setup.tex`). Selects `biblio/predefined.tex` vs `biblio/biblatex.tex`. If bibliography breaks, flipping this is the first thing to try.
- `FONTFAMILY` — XeLaTeX/LuaLaTeX font family: `0` CMU, `1` MS fonts, `2` Liberation (Unix default).
- `ALTFONT` — pdfLaTeX font: `0` Computer Modern, `1` PSCyr, `2` XCharter.
- `DRAFTON` — `1` skips ГОСТ-strict bibliography formatting; bibliography numbering may be wrong in this mode.
- `IMGCOMPILE` — `1` enables `-shell-escape` and uses precompiled `images/cache/*.pdf` instead of recompiling TikZ.
- `NOTESON` — presentation speaker-notes mode (`0` off, `1` separate slide, `2` same slide).
- `TIMERON=1` — print per-engine CPU time at the end.
- `USEDEV=1` — use `pdflatex-dev`/`xelatex-dev`/`lualatex-dev` binaries (experimental TeX Live).

## Source layout (big picture)

Three independent documents share a common configuration core:

- `dissertation.tex`, `synopsis.tex`, `presentation.tex` are thin top-level files. They each `\input` `common/setup.tex` and `common/packages.tex`, then a per-document `<Dir>/dispackages.tex` (or `synpackages.tex` / `prespackages.tex`), then `<Dir>/setup.tex` for that document's user-friendly knobs, then `common/data.tex` (author/title/etc. — see below), then load styles, then `\include` the chapters from `<Dir>/`.
- `Dissertation/`, `Synopsis/`, `Presentation/` each hold their document-specific chapters and a `setup.tex` (simplified per-document config), `*packages.tex` / `userpackages.tex`, `*styles.tex` / `userstyles.tex`. The `user*.tex` files are reserved for the writer's own overrides — prefer editing those over the non-`user` variants when a customization is content-specific rather than template-wide.
- `common/` is shared logic. Notable files:
  - `common/setup.tex` — defines all the `\newcounter` knobs (draft, showmarkup, usealtfont, fontfamily, bibliosel, mediadisplay, imgprecompile). Default values live here; env-var injection overrides them.
  - `common/data.tex` — author name, title, advisor, organization, etc. All template values are wrapped in `\fixme{}` so they show up red until replaced.
  - `common/concl.tex`, `common/characteristic.tex` — shared between dissertation and synopsis per ГОСТ 5.3.3 / 9.2.3.
  - `common/renames.tex` — caption/label translation, applied to both `babel` and `polyglossia` via `\gappto\captionsrussian{...}`.
  - `common/fonts.tex` — engine-aware font selection (branches on `\ifxetexorluatex` and the counters above).
- `biblio/` — `author.bib`, `registered.bib`, `external.bib`, plus `predefined.tex` (bibtex8 path) and `biblatex.tex` (biber path). The dispatch is in the top-level `.tex` files via `\ifnumequal{\value{bibliosel}}{0}{...}{...}`.
- `BibTeX-Styles/` — Russian `.bst` files for the bibtex8 path.
- `PSCyr/` — bundled PSCyr font package + per-platform install instructions (not auto-installed).
- `Documents/` — reference PDFs of the GOST / regulations the template implements.
- `letters/` — separate document for envelope generation (independent build, not part of `make all`).
- `siunitx.cfg` — repo-local config for the `siunitx` package; picked up automatically when the project is the current directory.

## When changing the template

Template-level changes (anything in `common/`, the root `*.tex` dispatchers, `Makefile`/`*.mk`, `latexmkrc`) must work across all three engines (pdfLaTeX, XeLaTeX, LuaLaTeX) and both biblio backends. `CONTRIBUTING.md` mandates running `make examples` before submitting. If you only edit content under `Dissertation/`/`Synopsis/`/`Presentation/`, the engine the writer uses is sufficient.

Style for `.tex` files (per `.editorconfig` and `CONTRIBUTING.md`): UTF-8, LF line endings, 4-space indent, no trailing whitespace, trailing newline. Makefiles use tabs. `latexindent` reads `indent.yaml`.

## Debugging build failures

1. Read the `.log` of the failing job — the first error is almost always the root cause; later ones are usually cascades.
2. If references appear as `?` or bold titles: bibliography didn't run. Try flipping `USEBIBER`, then `make distclean` and rebuild. The full procedure is in `Readme/Installation.md` → "Простые ошибки".
3. Missing packages → install the appropriate `texlive-*` package (distro-specific guidance in `Readme/Installation.md`).
4. For reproducibility, the repo ships a `Dockerfile` based on `raabf/texstudio-versions:texlive2018`; `install-dockertex.sh` sets up `dockertex` / `dockertexstudio` wrappers. Use this when a build works locally for the writer but not for collaborators.
