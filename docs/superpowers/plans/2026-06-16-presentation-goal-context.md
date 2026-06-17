# Presentation Goal Context Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the project presentation so it explicitly contains relevance, goal, tasks, and a short description of the work completed to achieve the goal.

**Architecture:** Keep the existing Beamer presentation structure. Add the missing introductory context to `Presentation/preamble.tex`, align technical slides in `Presentation/content.tex`, and keep speech materials synchronized in `Presentation/speech.md` and `Presentation/speech_cards.md`.

**Tech Stack:** LaTeX Beamer, Markdown speech notes, existing dissertation figures and data.

---

### Task 1: Update Introductory Slides

**Files:**
- Modify: `Presentation/preamble.tex`

- [ ] Add an explicit `Актуальность` slide after `Проблема и ограничения`.
- [ ] Rewrite `Цель и задачи работы` so the goal and tasks match `common/characteristic.tex`.
- [ ] Add a `Краткое описание проекта` slide summarizing the completed pipeline: local synchronization, normalization, embeddings, clustering, manual verification, prototype classifier, and evaluation.

### Task 2: Align Technical Slides

**Files:**
- Modify: `Presentation/content.tex`
- Modify: `Presentation/conclusion.tex`

- [ ] Remove `ok` and `too_short` from the data slide.
- [ ] Replace `Optuna` with random-search wording.
- [ ] Replace `Argilla` with an abstract manual verification interface.
- [ ] Replace `инференс` with `применение классификатора`.
- [ ] Update final results so they reference the completed work and avoid naming removed tools.

### Task 3: Synchronize Speaker Notes

**Files:**
- Modify: `Presentation/speech.md`
- Modify: `Presentation/speech_cards.md`

- [ ] Update slide numbering and notes for the new intro slides.
- [ ] Remove `Argilla`, `Optuna`, `ok`, `too_short`, and `инференс`.
- [ ] Add concise phrasing for relevance, goal, tasks, and completed work.

### Task 4: Verify

**Files:**
- Inspect: `Presentation/*.tex`
- Inspect: `Presentation/*.md`

- [ ] Run a text search to confirm required phrases are present and removed terms are absent.
- [ ] Run `make presentation`.
- [ ] Report any existing warnings only if they affect this task.
