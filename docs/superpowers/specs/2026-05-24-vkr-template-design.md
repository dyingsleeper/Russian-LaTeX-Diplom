# VKR Template Design

## Goal

Prepare the LaTeX project for writing a bachelor's final qualifying work
(VKR) for Volgograd State University, Department of Fundamental Informatics
and Artificial Intelligence, using the local university rules and the supplied
title/task page samples.

## Sources

- `graduate_work_rules.pdf`: university formatting rules for VKR, NIR reports,
  practice reports, and related documents.
- `graduate_work_title_page.pdf`: title page sample.
- `graduate_work_task_list.pdf`: two-page assignment sheet sample.

## Chosen Approach

Adapt the existing `dissertation` document into the main VKR document rather
than adding a separate entry point.

This keeps the current build workflow: `make dissertation` remains the command
for producing the main PDF. The old PhD-oriented template structure is reused
where it helps, but the visible dissertation-specific pages and labels are
replaced with VKR-specific pages and terminology.

## Document Structure

The generated VKR PDF must start with:

1. Title page.
2. Assignment sheet, page 1.
3. Assignment sheet, page 2.
4. Contents, starting with printed page number 4.
5. Introduction.
6. Main chapters and sections.
7. Conclusion.
8. List of literature.
9. Appendices, if needed.

The title page is counted as page 1. The two assignment pages are counted as
pages 2 and 3. Page numbers are not printed on those first three pages.

The contents must list chapters, sections, subsections, Introduction,
Conclusion, List of literature, and Appendices. The unnumbered structural parts
must appear in the contents but must not have section numbers.

## Page Layout

The VKR uses A4 pages printed on one side.

Margins:

- left: 30 mm;
- right: 10 mm;
- top: 20 mm;
- bottom: 20 mm.

Main text:

- Times New Roman, 14 pt, when XeLaTeX/LuaLaTeX is used;
- one-and-a-half line spacing;
- first-line paragraph indent: 1.25 cm;
- no extra spacing between paragraphs of the main text;
- justified alignment;
- automatic hyphenation may be used in the main text.

Page numbers:

- Arabic numerals;
- bottom center;
- continuous numbering;
- hidden on the title page and the two assignment pages.

## Headings

The document is divided into chapters and sections.

Rules:

- chapter headings start on a new page;
- headings are bold;
- headings are numbered hierarchically with Arabic numerals;
- "Contents", "Introduction", "Conclusion", "List of literature", and
  "Appendices" are not numbered;
- no period is printed at the end of a heading;
- heading line breaks must not use word hyphenation;
- a heading must be followed by text, not immediately by a figure, table,
  formula, or a new page;
- headings of the same level must be formatted consistently.

The rules PDF allows chapter labels in the form "Глава 1. Название". The
existing template already supports this style, so the VKR configuration should
keep it unless it conflicts with the title/task page samples.

## Numbering

Figures, tables, and formulas should be numbered with Arabic numerals. The
rules allow continuous numbering across the document or numbering within
chapters/sections. Use continuous numbering by default because it matches the
examples for figures and tables in `graduate_work_rules.pdf`.

Formula numbers are printed at the right edge in parentheses, for example
`(1)`. Figure and table captions use the forms shown in the rules:

- `Рисунок 1 - Название рисунка`
- `Таблица 1 - Название таблицы`

The final implementation should use the typographic dash already present in
the template settings rather than a literal hyphen when that is more consistent
with the existing LaTeX code.

## Figures

Figures may appear close to the relevant text or in appendices. They should be
readable without rotating the document where possible.

Figure captions:

- are placed below the figure;
- are centered relative to the figure;
- contain "Рисунок", the number, a dash, and the caption text;
- do not end with a period;
- must not be separated from the figure.

Every figure must be referenced in the text.

## Tables

Table captions:

- are placed above the table;
- are aligned to the right according to the rules PDF;
- contain "Таблица", the number, a dash, and the caption text;
- do not end with a period;
- must not be separated from the table.

Every table must be referenced in the text.

## Footnotes

Footnotes are placed at the bottom of the page where they are referenced. They
are separated from the text by a short horizontal line on the left and numbered
independently on each page.

The implementation should preserve the current LaTeX defaults unless a visible
problem appears during verification.

## Bibliography

The list of literature is placed after the conclusion and before appendices.

Rules:

- entries are ordered alphabetically by the first author's surname;
- Russian-language entries come before foreign-language entries;
- references in the text are placed in square brackets, for example `[5]`.

The existing bibliography layer uses `biblatex-gost`/BibTeX GOST styles. The
implementation should switch the main bibliography path to alphabetical sorting
for VKR output and keep numeric square-bracket citations.

## Title Page

The title page must be recreated as editable LaTeX, not included as a static
PDF image.

It must match `graduate_work_title_page.pdf` structurally:

- Ministry and university block;
- department line;
- work title;
- "ВЫПУСКНАЯ КВАЛИФИКАЦИОННАЯ РАБОТА";
- work type, for example "(бакалаврская работа)";
- training direction `01.03.02 "Прикладная математика и информатика"`;
- profile `Создание и применение технологий больших данных`;
- student block with group and full name;
- supervisor block with degree, position, and full name;
- admission-to-defense block for the department head;
- date/protocol fields;
- city and year at the bottom.

All variable text should come from macros in `common/data.tex` or a nearby
project data file, not be hard-coded inside layout commands.

## Assignment Sheet

The assignment sheet must be recreated as editable LaTeX, not included as a
static PDF image.

It must match the two pages in `graduate_work_task_list.pdf` structurally:

- university, institute, and department block;
- approval block for the department head;
- centered "ЗАДАНИЕ" title;
- work type selection text;
- student and group line;
- topic;
- goal;
- main tasks;
- main stages of work;
- recommended literature;
- issue date and deadline fields;
- supervisor signature line;
- student acceptance signature line.

Highlighted example text from the PDF sample is placeholder content. The LaTeX
version should use normal text and `\fixme{...}` placeholders for values that
the student must replace.

## Data Model

Add VKR-specific data macros for:

- ministry;
- full university name;
- institute;
- department;
- department short name;
- department head title and full name;
- department head short name, if needed;
- student full name;
- student group;
- work type;
- direction code and title;
- profile;
- title;
- supervisor degree;
- supervisor position;
- supervisor full name;
- issue date;
- deadline;
- defense admission date/protocol fields;
- assignment goal;
- assignment tasks;
- assignment stages;
- assignment recommended literature.

Existing thesis macros may remain for compatibility, but the main VKR pages
should use the VKR names to avoid mixing PhD and bachelor's terminology.

## Build And Verification

The primary verification command is:

```bash
make dissertation
```

If the local environment lacks required fonts or bibliography tools, verify as
much as possible with the available engine and report the limitation.

The resulting PDF must be checked for:

- successful compilation;
- first three pages present and without printed page numbers;
- contents starts on page 4 with a printed bottom-center page number;
- page margins and font settings applied to the body text;
- title and assignment pages visually follow the supplied samples;
- figures, tables, and bibliography still compile.

## Out Of Scope

This design does not require rewriting the presentation template, synopsis
template, or envelope generator. They may remain in the repository unchanged.

This design does not require filling in the student's final real topic,
supervisor, or literature list beyond editable placeholders.
