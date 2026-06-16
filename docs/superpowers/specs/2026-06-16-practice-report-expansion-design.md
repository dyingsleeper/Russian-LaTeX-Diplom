# Practice Report Expansion Design

## Goal

Expand `Савкин преддипломная практика.docx` while preserving the university report template. The title pages, individual assignment, supervisor review, and practice progress table stay structurally unchanged. The main edited area is `Приложение 1. Содержательный отчет о выполненных работах`.

## Source Material

Use these dissertation files as sources:

- `common/characteristic.tex` for актуальность, цель, and задачи.
- `Dissertation/part2.tex` for project design material: requirements, architecture, processing cycle, email synchronization, normalization, embeddings, clustering, annotation, classifier, update loop, and storage.
- `Dissertation/part3.tex` for implementation and experiment material, rewritten as a practice report rather than copied as dissertation prose.

## Document Structure

Add a table of contents after the formal pages and before the appendix section. The table of contents should be built from Word/LibreOffice heading styles so it can be updated by the editor.

Replace the current appendix body with an expanded report:

1. Introduction to the practice work.
2. Relevance, goal, and tasks.
3. Project decisions prepared during practice, based on approximately 80 percent of chapter 2.
4. Implementation and experiment, based on chapter 3 but rewritten in completed-work style.
5. Results and limitations.

## Style Requirements

Write in formal Russian academic style suitable for a practice report. Use completed-work formulations: `в ходе практики было определено`, `была разработана схема`, `реализован этап`, `проведена проверка`. Avoid direct dissertation phrasing where it reads as chapter exposition. Keep technical terms already used in the dissertation and do not introduce new claims.

## Verification

After editing, verify that the file opens with LibreOffice in headless mode and inspect the document text programmatically to confirm that the appendix contains the added sections and the current report sections were replaced.
