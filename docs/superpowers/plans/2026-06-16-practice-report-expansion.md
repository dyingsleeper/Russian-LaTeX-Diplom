# Practice Report Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the pre-diploma practice report DOCX with a contents section, practice-style goals and relevance, chapter 2 design material, and a rewritten chapter 3 implementation report.

**Architecture:** Treat the DOCX as the source artifact and edit it with `python-docx`. Preserve the existing formal template elements, replace only the appendix body, assign heading styles to generated report sections, and insert a Word TOC field before the appendix section.

**Tech Stack:** Python 3, `python-docx`, OOXML field elements, LibreOffice headless verification.

---

### Task 1: Generate Expanded Appendix Text

**Files:**
- Modify: `Савкин преддипломная практика.docx`
- Read: `common/characteristic.tex`
- Read: `Dissertation/part2.tex`
- Read: `Dissertation/part3.tex`

- [ ] **Step 1: Build the replacement section list**

Use these section headings for `Приложение 1. Содержательный отчет о выполненных работах`:

```text
Введение
Актуальность, цель и задачи практики
Проектные решения, подготовленные в ходе практики
Требования и ограничения системы
Архитектура и основной цикл обработки
Синхронизация и нормализация писем
Построение эмбеддингов
Кластеризация и ручная проверка
Классификатор, порог уверенности и обновление
Хранение данных и воспроизводимость
Реализация и экспериментальная проверка
Организация кода и среда реализации
Результаты обработки корпуса
Результаты кластеризации и формирования классов
Оценка классификатора
Итоги практики
```

- [ ] **Step 2: Preserve useful tables**

Retain these existing appendix tables and place them near matching sections:

```text
Пакеты приложения и их назначение
Состав корпуса писем
Сравнение алгоритмов кластеризации
Сформированные классы и их размеры
Сводные метрики классификатора
```

- [ ] **Step 3: Replace appendix body**

Use a Python script based on `python-docx` to find the paragraph `Приложение 1. Содержательный отчет о выполненных работах`, delete the old appendix body after it, and insert the expanded section sequence with headings, paragraphs, and retained tables.

### Task 2: Add Table Of Contents

**Files:**
- Modify: `Савкин преддипломная практика.docx`

- [ ] **Step 1: Insert TOC heading and field**

Insert a contents block before the existing `2. Приложения` paragraph:

```text
Содержание
```

Below the heading, insert a Word field:

```text
TOC \o "1-2" \h \z \u
```

- [ ] **Step 2: Apply heading styles**

Apply `Заголовок 1` to `Содержание`, `2. Приложения`, and `Приложение 1. Содержательный отчет о выполненных работах`. Apply `Заголовок 2` to appendix section headings.

### Task 3: Verify Result

**Files:**
- Inspect: `Савкин преддипломная практика.docx`

- [ ] **Step 1: Validate DOCX can be opened**

Run LibreOffice in headless conversion/check mode:

```bash
mkdir -p /tmp/practice-report-check
libreoffice --headless --convert-to pdf --outdir /tmp/practice-report-check "Савкин преддипломная практика.docx"
```

Expected result: exit code 0 and a generated PDF in `/tmp/practice-report-check`.

- [ ] **Step 2: Inspect text**

Run a `python-docx` inspection that confirms the text contains:

```text
Содержание
Актуальность, цель и задачи практики
Проектные решения, подготовленные в ходе практики
Хранение данных и воспроизводимость
Реализация и экспериментальная проверка
```

Expected result: all required strings are found.

- [ ] **Step 3: Check scope**

Run:

```bash
git status --short
```

Expected result: modified/created files are limited to the target DOCX and the two superpowers markdown files.
