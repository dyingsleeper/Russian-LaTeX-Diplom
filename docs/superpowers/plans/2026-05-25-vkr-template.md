# VKR Template Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the main `dissertation` build into an editable VKR template that follows the university PDF rules and samples.

**Architecture:** Keep `dissertation.tex` as the main entry point and reuse the existing memoir-based style stack. Add VKR data macros in `common/data.tex`, rewrite the visible title page, add a two-page assignment sheet, and adjust dissertation-specific styles for VKR margins, page numbering, captions, contents naming, and bibliography sorting.

**Tech Stack:** LaTeX `memoir`, XeLaTeX via `latexmk`, `biblatex-gost` with `biber`, shell checks for source-level verification.

---

## File Structure

- Modify `common/data.tex`: append VKR-specific macros and document PDF metadata helper macros.
- Modify `common/styles.tex`: use the VKR metadata helper macros and set the paragraph indent to `1.25cm`.
- Modify `common/renames.tex`: rename contents to `Содержание`.
- Modify `Dissertation/title.tex`: replace the PhD title page with the editable VKR title page.
- Create `Dissertation/task.tex`: add the editable two-page assignment sheet.
- Modify `Dissertation/setup.tex`: set continuous figure/table/equation numbering and right-aligned table captions.
- Modify `Dissertation/disstyles.tex`: set VKR margins and move page numbers to the bottom center.
- Modify `dissertation.tex`: insert the assignment sheet after the title page and remove PhD-only structural pages from the default VKR output.
- Modify `biblio/biblatex.tex`: switch the main bibliography to alphabetical sorting and enable Russian-first ordering.
- Create `scripts/check-vkr-template.sh`: source checks plus full `make dissertation` verification.

## Task 1: Add VKR Data Macros

**Files:**
- Modify: `common/data.tex`
- Test: source grep and `make dissertation`

- [ ] **Step 1: Verify VKR macros are currently absent**

Run:

```bash
grep -F '\newcommand{\vkrTitle}' common/data.tex
```

Expected: FAIL with no output and exit code 1.

- [ ] **Step 2: Append VKR data block to `common/data.tex`**

Add this block after the existing `\providecommand{\keywords}` definition:

```tex

%%% Данные выпускной квалификационной работы %%%
\newcommand{\vkrMinistry}{Министерство науки и высшего образования Российской Федерации}
\newcommand{\vkrUniversity}{Федеральное государственное автономное образовательное учреждение высшего образования <<Волгоградский государственный университет>>}
\newcommand{\vkrInstitute}{институт Математики и информационных технологий}
\newcommand{\vkrDepartment}{кафедра Фундаментальной информатики и искусственного интеллекта}
\newcommand{\vkrDepartmentShort}{ФИИИ}
\newcommand{\vkrDepartmentHeadTitle}{Зав. каф. \vkrDepartmentShort}
\newcommand{\vkrDepartmentHeadDegree}{д.ф.-м.н., профессор}
\newcommand{\vkrDepartmentHead}{Воронин Александр Александрович}
\newcommand{\vkrDepartmentHeadShort}{А.\,А.~Воронин}
\newcommand{\vkrStudentFullName}{\fixme{Фамилия Имя Отчество}}
\newcommand{\vkrStudentGroup}{\fixme{ПМИб-181}}
\newcommand{\vkrWorkType}{бакалаврская работа}
\newcommand{\vkrWorkKind}{ВЫПУСКНАЯ КВАЛИФИКАЦИОННАЯ РАБОТА}
\newcommand{\vkrDirectionCode}{01.03.02}
\newcommand{\vkrDirectionTitle}{Прикладная математика и информатика}
\newcommand{\vkrProfile}{Создание и применение технологий больших данных}
\newcommand{\vkrTitle}{\fixme{НАЗВАНИЕ ТЕМЫ РАБОТЫ}}
\newcommand{\vkrSupervisorDegree}{\fixme{ученая степень}}
\newcommand{\vkrSupervisorPosition}{\fixme{должность}}
\newcommand{\vkrSupervisorFullName}{\fixme{Фамилия Имя Отчество}}
\newcommand{\vkrSupervisorShort}{\fixme{И.\,О.~Фамилия}}
\newcommand{\vkrCity}{Волгоград}
\newcommand{\vkrYear}{\the\year}
\newcommand{\vkrDefenseDay}{\fixme{ДД}}
\newcommand{\vkrDefenseMonth}{\fixme{месяца}}
\newcommand{\vkrDefenseProtocol}{\fixme{номер}}
\newcommand{\vkrAssignmentApprovedDay}{\fixme{ДД}}
\newcommand{\vkrAssignmentApprovedMonth}{\fixme{месяца}}
\newcommand{\vkrAssignmentApprovedYear}{\the\year}
\newcommand{\vkrAssignmentIssueDate}{\fixme{ДД.ММ.ГГГГ}}
\newcommand{\vkrAssignmentDeadline}{\fixme{ДД.ММ.ГГГГ}}
\newcommand{\vkrAssignmentGoal}{\fixme{Сформулировать цель выпускной квалификационной работы.}}
\newcommand{\vkrAssignmentTasks}{%
    \item \fixme{Сформулировать первую основную задачу.}
    \item \fixme{Сформулировать вторую основную задачу.}
    \item \fixme{Сформулировать третью основную задачу.}
}
\newcommand{\vkrAssignmentStages}{%
    \item \fixme{Изучение предметной области и постановка задачи.}
    \item \fixme{Проектирование и реализация решения.}
    \item \fixme{Проведение экспериментов и анализ результатов.}
    \item \fixme{Оформление текста ВКР и подготовка к защите.}
}
\newcommand{\vkrAssignmentLiterature}{%
    \item \fixme{Автор И.\,О. Название источника. - Город: Издательство, год.}
}

\providecommand{\documentPdfTitle}{\thesisTitle}
\providecommand{\documentPdfAuthor}{\thesisAuthor}
\providecommand{\documentPdfSubject}{\thesisSpecialtyNumber\ \thesisSpecialtyTitle}
\renewcommand{\documentPdfTitle}{\vkrTitle}
\renewcommand{\documentPdfAuthor}{\vkrStudentFullName}
\renewcommand{\documentPdfSubject}{\vkrDirectionCode\ \vkrDirectionTitle}
```

- [ ] **Step 3: Verify VKR macros are present**

Run:

```bash
grep -F '\newcommand{\vkrTitle}' common/data.tex
grep -F '\newcommand{\vkrAssignmentTasks}' common/data.tex
grep -F '\renewcommand{\documentPdfTitle}{\vkrTitle}' common/data.tex
```

Expected: PASS and print the matching lines.

- [ ] **Step 4: Build to make sure the data block does not break the current document**

Run:

```bash
make dissertation
```

Expected: PASS, with `dissertation.pdf` produced.

- [ ] **Step 5: Commit**

```bash
git add common/data.tex
git commit -m "feat: add vkr data macros"
```

## Task 2: Update PDF Metadata And Shared Names

**Files:**
- Modify: `common/styles.tex`
- Modify: `common/renames.tex`
- Test: source grep and `make dissertation`

- [ ] **Step 1: Verify old metadata and contents name are still present**

Run:

```bash
grep -F 'pdftitle={\thesisTitle}' common/styles.tex
grep -F '\renewcommand{\contentsname}{Оглавление}' common/renames.tex
grep -F '\setlength{\parindent}{2.5em}' common/styles.tex
```

Expected: PASS before the change.

- [ ] **Step 2: Change metadata and paragraph indent in `common/styles.tex`**

Replace the paragraph indent block with:

```tex
\AtBeginDocument{%
    \setlength{\parindent}{1.25cm}                   % Абзацный отступ по правилам оформления ВКР.
}
```

In the `\hypersetup` block, replace:

```tex
    pdftitle={\thesisTitle},
    pdfauthor={\thesisAuthor},
    pdfsubject={\thesisSpecialtyNumber\ \thesisSpecialtyTitle},
```

with:

```tex
    pdftitle={\documentPdfTitle},
    pdfauthor={\documentPdfAuthor},
    pdfsubject={\documentPdfSubject},
```

- [ ] **Step 3: Change contents name in `common/renames.tex`**

Replace:

```tex
\renewcommand{\contentsname}{Оглавление}% (ГОСТ Р 7.0.11-2011, 4)
```

with:

```tex
\renewcommand{\contentsname}{Содержание}%
```

- [ ] **Step 4: Verify updated source**

Run:

```bash
grep -F '\setlength{\parindent}{1.25cm}' common/styles.tex
grep -F 'pdftitle={\documentPdfTitle}' common/styles.tex
grep -F '\renewcommand{\contentsname}{Содержание}' common/renames.tex
```

Expected: PASS and print the matching lines.

- [ ] **Step 5: Build**

Run:

```bash
make dissertation
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add common/styles.tex common/renames.tex
git commit -m "style: use vkr metadata and contents naming"
```

## Task 3: Rebuild The Title Page In LaTeX

**Files:**
- Modify: `Dissertation/title.tex`
- Test: source grep and `make dissertation`

- [ ] **Step 1: Verify the title page still uses PhD wording**

Run:

```bash
grep -F 'Диссертация на соискание учёной степени' Dissertation/title.tex
```

Expected: PASS before the change.

- [ ] **Step 2: Replace `Dissertation/title.tex`**

Replace the full file with:

```tex
% Титульный лист выпускной квалификационной работы
\thispagestyle{empty}
\begingroup
\setlength{\parindent}{0pt}
\begin{center}
\vkrMinistry\\
\vkrUniversity\\
\vkrDepartment

\vfill

\textbf{\MakeUppercase{\vkrTitle}}\\[0.35cm]
{\MakeUppercase{\vkrWorkKind}}\\
(\vkrWorkType)\\[0.35cm]
по направлению подготовки \vkrDirectionCode\ <<\vkrDirectionTitle>>\\
профиль <<\vkrProfile>>
\end{center}

\vfill

\begin{flushright}
\begin{minipage}{0.43\textwidth}
\textbf{ВЫПОЛНИЛ(А):}\\
студент(ка) гр. \vkrStudentGroup\\
\vkrStudentFullName\\[0.55cm]
\rule{\linewidth}{0.4pt}\\[0.9cm]

\textbf{НАУЧНЫЙ РУКОВОДИТЕЛЬ:}\\
\vkrSupervisorDegree,\\
\vkrSupervisorPosition,\\
\vkrSupervisorFullName\\[0.55cm]
\rule{\linewidth}{0.4pt}\\[0.9cm]

\textbf{РАБОТА ДОПУЩЕНА К ЗАЩИТЕ:}\\
\vkrDepartmentHeadTitle\\
\vkrDepartmentHeadDegree,\\
\vkrDepartmentHead\\[0.55cm]
\rule{\linewidth}{0.4pt}\\
<<\vkrDefenseDay>> \rule{2.8cm}{0.4pt} \vkrYear~г.\\
(протокол № \vkrDefenseProtocol\ заседания кафедры)
\end{minipage}
\end{flushright}

\vfill

\begin{center}
\vkrCity\ \vkrYear
\end{center}
\endgroup
```

- [ ] **Step 3: Verify the new title source**

Run:

```bash
grep -F '\vkrWorkKind' Dissertation/title.tex
grep -F 'РАБОТА ДОПУЩЕНА К ЗАЩИТЕ' Dissertation/title.tex
grep -F '\vkrCity\ \vkrYear' Dissertation/title.tex
```

Expected: PASS and print the matching lines.

- [ ] **Step 4: Build**

Run:

```bash
make dissertation
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add Dissertation/title.tex
git commit -m "feat: add editable vkr title page"
```

## Task 4: Add The Editable Assignment Sheet

**Files:**
- Create: `Dissertation/task.tex`
- Modify: `dissertation.tex`
- Test: source grep and `make dissertation`

- [ ] **Step 1: Verify the assignment sheet is not wired**

Run:

```bash
test ! -f Dissertation/task.tex
grep -F '\include{Dissertation/task}' dissertation.tex
```

Expected: first command PASS, second command FAIL with no output.

- [ ] **Step 2: Create `Dissertation/task.tex`**

Create the file with:

```tex
% Лист задания на выполнение выпускной квалификационной работы
\thispagestyle{empty}
\begingroup
\setlength{\parindent}{0pt}
\begin{center}
\vkrUniversity\\[0.35cm]
\vkrInstitute\\
\vkrDepartment
\end{center}

\vspace{1.2cm}

\begin{flushright}
\begin{minipage}{0.35\textwidth}
Утвердить\\[0.5cm]
\vkrDepartmentHeadTitle\\[0.55cm]
\rule{3.5cm}{0.4pt}~\vkrDepartmentHeadShort\\[0.35cm]
<<\vkrAssignmentApprovedDay>> \rule{2.0cm}{0.4pt} \vkrAssignmentApprovedYear~г.
\end{minipage}
\end{flushright}

\vspace{1.0cm}

\begin{center}
{\Large ЗАДАНИЕ}\\
на выполнение выпускной квалификационной работы\\
(\vkrWorkType)\\[0.7cm]
студента(ки) \vkrStudentFullName\ группы \vkrStudentGroup
\end{center}

\begin{enumerate}[leftmargin=*, label=\arabic*.]
    \item Тема: \vkrTitle
    \item Цель: \vkrAssignmentGoal
    \item Основные задачи:
    \begin{enumerate}[label=\asbuk*)]
        \vkrAssignmentTasks
    \end{enumerate}
    \item Основные этапы выполнения работы:
    \begin{enumerate}[label=\asbuk*)]
        \vkrAssignmentStages
    \end{enumerate}
\end{enumerate}
\endgroup
\clearpage

\thispagestyle{empty}
\begingroup
\setlength{\parindent}{0pt}
\begin{enumerate}[leftmargin=*, label=\arabic*., start=5]
    \item Рекомендуемая литература:
    \begin{enumerate}[label=\arabic*)]
        \vkrAssignmentLiterature
    \end{enumerate}
\end{enumerate}

\vfill

\noindent
Дата выдачи \rule{4.5cm}{0.4pt}
\hfill
Срок исполнения \rule{4.5cm}{0.4pt}

\vspace{1.5cm}

\noindent
Руководитель \rule{6.5cm}{0.4pt}
\hfill
\vkrSupervisorDegree, \vkrSupervisorPosition\ \vkrSupervisorShort

\vspace{0.2cm}
\hspace*{3.5cm}{\small (подпись)}

\vspace{1.2cm}

\noindent
Задание принял к исполнению \rule{8.5cm}{0.4pt}

\vspace{0.2cm}
\hspace*{10.0cm}{\small (подпись)}
\endgroup
```

- [ ] **Step 3: Wire the task sheet in `dissertation.tex`**

Change the document structure around the title/contents includes from:

```tex
\include{Dissertation/title}           % Титульный лист
\include{Dissertation/contents}        % Оглавление
```

to:

```tex
\include{Dissertation/title}           % Титульный лист
\include{Dissertation/task}            % Лист задания
\include{Dissertation/contents}        % Содержание
```

- [ ] **Step 4: Verify source wiring**

Run:

```bash
grep -F '\include{Dissertation/task}' dissertation.tex
grep -F 'на выполнение выпускной квалификационной работы' Dissertation/task.tex
grep -F 'start=5' Dissertation/task.tex
```

Expected: PASS and print the matching lines.

- [ ] **Step 5: Build**

Run:

```bash
make dissertation
```

Expected: PASS. The resulting PDF has title page, two assignment pages, then contents.

- [ ] **Step 6: Commit**

```bash
git add dissertation.tex Dissertation/task.tex
git commit -m "feat: add editable vkr assignment sheet"
```

## Task 5: Simplify The Main VKR Document Structure

**Files:**
- Modify: `dissertation.tex`
- Test: source grep and `make dissertation`

- [ ] **Step 1: Verify PhD-only sections are still included**

Run:

```bash
grep -F '\include{Dissertation/acronyms}' dissertation.tex
grep -F '\include{Dissertation/dictionary}' dissertation.tex
grep -F '\include{Dissertation/lists}' dissertation.tex
```

Expected: PASS before the change.

- [ ] **Step 2: Remove PhD-only includes from the default structure**

Replace:

```tex
\include{Dissertation/acronyms}        % Список сокращений и условных обозначений
\include{Dissertation/dictionary}      % Словарь терминов
\include{Dissertation/references}      % Список литературы
\include{Dissertation/lists}           % Списки таблиц и изображений (иллюстративный материал)
```

with:

```tex
% При необходимости можно включить дополнительные структурные части:
%\include{Dissertation/acronyms}        % Список сокращений и условных обозначений
%\include{Dissertation/dictionary}      % Словарь терминов
\include{Dissertation/references}      % Список литературы
```

- [ ] **Step 3: Verify optional sections are commented out**

Run:

```bash
grep -F '%\include{Dissertation/acronyms}' dissertation.tex
grep -F '%\include{Dissertation/dictionary}' dissertation.tex
grep -F '\include{Dissertation/references}' dissertation.tex
test "$(grep -F -c '\include{Dissertation/lists}' dissertation.tex)" -eq 0
```

Expected: PASS.

- [ ] **Step 4: Build**

Run:

```bash
make dissertation
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add dissertation.tex
git commit -m "refactor: simplify vkr document structure"
```

## Task 6: Apply VKR Page Layout And Numbering

**Files:**
- Modify: `Dissertation/disstyles.tex`
- Modify: `Dissertation/setup.tex`
- Test: source grep and `make dissertation`

- [ ] **Step 1: Verify old layout settings are present**

Run:

```bash
grep -F 'left=2.5cm' Dissertation/disstyles.tex
grep -F '\makeoddhead{plain}{}{\rmfamily\thepage}{}' Dissertation/disstyles.tex
grep -F '\setcounter{contnumeq}{0}' Dissertation/setup.tex
grep -F '\setcounter{contnumfig}{0}' Dissertation/setup.tex
grep -F '\newcommand{\tabjust}{justified}' Dissertation/setup.tex
```

Expected: PASS before the change.

- [ ] **Step 2: Change margins in `Dissertation/disstyles.tex`**

Replace:

```tex
\geometry{a4paper, top=2cm, bottom=2cm, left=2.5cm, right=1cm, nofoot, nomarginpar} %, heightrounded, showframe
```

with:

```tex
\geometry{a4paper, top=2cm, bottom=2cm, left=3cm, right=1cm, nomarginpar} %, heightrounded, showframe
```

- [ ] **Step 3: Move page numbers to bottom center in `Dissertation/disstyles.tex`**

Replace:

```tex
\makeevenhead{plain}{}{\rmfamily\thepage}{}
\makeoddhead{plain}{}{\rmfamily\thepage}{}
\makeevenfoot{plain}{}{}{}
\makeoddfoot{plain}{}{}{}
```

with:

```tex
\makeevenhead{plain}{}{}{}
\makeoddhead{plain}{}{}{}
\makeevenfoot{plain}{}{\rmfamily\thepage}{}
\makeoddfoot{plain}{}{\rmfamily\thepage}{}
```

- [ ] **Step 4: Set continuous numbering and right-aligned table captions in `Dissertation/setup.tex`**

Replace:

```tex
\setcounter{contnumeq}{0}
\setcounter{contnumfig}{0}
\newcommand{\tabjust}{justified}
```

with:

```tex
\setcounter{contnumeq}{1}
\setcounter{contnumfig}{1}
\newcommand{\tabjust}{raggedleft}
```

Keep `\setcounter{contnumtab}{1}` unchanged.

- [ ] **Step 5: Verify source settings**

Run:

```bash
grep -F 'left=3cm, right=1cm' Dissertation/disstyles.tex
grep -F '\makeoddfoot{plain}{}{\rmfamily\thepage}{}' Dissertation/disstyles.tex
grep -F '\setcounter{contnumeq}{1}' Dissertation/setup.tex
grep -F '\setcounter{contnumfig}{1}' Dissertation/setup.tex
grep -F '\newcommand{\tabjust}{raggedleft}' Dissertation/setup.tex
```

Expected: PASS.

- [ ] **Step 6: Build**

Run:

```bash
make dissertation
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add Dissertation/disstyles.tex Dissertation/setup.tex
git commit -m "style: apply vkr page layout"
```

## Task 7: Switch Bibliography To Alphabetical Ordering

**Files:**
- Modify: `biblio/biblatex.tex`
- Test: source grep and `make dissertation`

- [ ] **Step 1: Verify current biblatex sorting is citation order**

Run:

```bash
grep -F 'sorting=none,% настройка сортировки списка литературы' biblio/biblatex.tex
```

Expected: PASS before the change.

- [ ] **Step 2: Change biblatex sorting option**

Replace both occurrences of:

```tex
sorting=none,% настройка сортировки списка литературы
```

with:

```tex
sorting=nty,% алфавитная сортировка списка литературы для ВКР
```

- [ ] **Step 3: Enable Russian-first source map**

Uncomment the Russian-English sorting block near the end of `biblio/biblatex.tex` so it becomes:

```tex
\DeclareSourcemap{
    \maps[datatype=bibtex]{
        \map{
            \step[fieldset=langid, fieldvalue={tempruorder}]
        }
        \map[overwrite]{
            \step[fieldsource=langid, match=russian, final]
            \step[fieldsource=presort,
            match=\regexp{(.+)},
            replace=\regexp{aa$1}]
        }
        \map{
            \step[fieldsource=langid, match=russian, final]
            \step[fieldset=presort, fieldvalue={az}]
        }
        \map[overwrite]{
            \step[fieldsource=langid, notmatch=russian, final]
            \step[fieldsource=presort,
            match=\regexp{(.+)},
            replace=\regexp{za$1}]
        }
        \map{
            \step[fieldsource=langid, notmatch=russian, final]
            \step[fieldset=presort, fieldvalue={zz}]
        }
        \map{
            \step[fieldsource=langid, match={tempruorder}, final]
            \step[fieldset=langid, null]
        }
    }
}
```

- [ ] **Step 4: Verify bibliography source settings**

Run:

```bash
grep -F 'sorting=nty,% алфавитная сортировка списка литературы для ВКР' biblio/biblatex.tex
grep -F '\DeclareSourcemap{' biblio/biblatex.tex
grep -F 'fieldvalue={tempruorder}' biblio/biblatex.tex
```

Expected: PASS.

- [ ] **Step 5: Clean old bibliography artifacts and build**

Run:

```bash
make clean
make dissertation
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add biblio/biblatex.tex
git commit -m "style: sort vkr bibliography alphabetically"
```

## Task 8: Add Final Verification Script

**Files:**
- Create: `scripts/check-vkr-template.sh`
- Test: `scripts/check-vkr-template.sh`

- [ ] **Step 1: Verify no project verification script exists**

Run:

```bash
test ! -f scripts/check-vkr-template.sh
```

Expected: PASS before the change.

- [ ] **Step 2: Create `scripts/check-vkr-template.sh`**

Create the file with:

```bash
#!/usr/bin/env bash
set -euo pipefail

fail() {
    printf 'FAIL: %s\n' "$1" >&2
    exit 1
}

grep -F '\newcommand{\vkrTitle}' common/data.tex >/dev/null || fail 'missing VKR title macro'
grep -F '\newcommand{\vkrAssignmentTasks}' common/data.tex >/dev/null || fail 'missing VKR assignment tasks macro'
grep -F 'pdftitle={\documentPdfTitle}' common/styles.tex >/dev/null || fail 'PDF metadata does not use documentPdfTitle'
grep -F '\setlength{\parindent}{1.25cm}' common/styles.tex >/dev/null || fail 'paragraph indent is not 1.25cm'
grep -F '\renewcommand{\contentsname}{Содержание}' common/renames.tex >/dev/null || fail 'contents name is not Содержание'
grep -F '\vkrWorkKind' Dissertation/title.tex >/dev/null || fail 'title page does not use VKR work kind'
grep -F '\include{Dissertation/task}' dissertation.tex >/dev/null || fail 'assignment sheet is not included'
grep -F 'left=3cm, right=1cm' Dissertation/disstyles.tex >/dev/null || fail 'VKR margins are not configured'
grep -F '\makeoddfoot{plain}{}{\rmfamily\thepage}{}' Dissertation/disstyles.tex >/dev/null || fail 'page number is not in bottom center footer'
grep -F '\setcounter{contnumeq}{1}' Dissertation/setup.tex >/dev/null || fail 'equation numbering is not continuous'
grep -F '\setcounter{contnumfig}{1}' Dissertation/setup.tex >/dev/null || fail 'figure numbering is not continuous'
grep -F '\setcounter{contnumtab}{1}' Dissertation/setup.tex >/dev/null || fail 'table numbering is not continuous'
grep -F '\newcommand{\tabjust}{raggedleft}' Dissertation/setup.tex >/dev/null || fail 'table captions are not right aligned'
grep -F 'sorting=nty,% алфавитная сортировка списка литературы для ВКР' biblio/biblatex.tex >/dev/null || fail 'bibliography sorting is not alphabetical'

if [[ "${SKIP_BUILD:-0}" != "1" ]]; then
    make dissertation
fi

printf 'VKR template checks passed.\n'
```

- [ ] **Step 3: Make the script executable**

Run:

```bash
chmod +x scripts/check-vkr-template.sh
```

- [ ] **Step 4: Run final verification**

Run:

```bash
scripts/check-vkr-template.sh
```

Expected: PASS and print `VKR template checks passed.`

- [ ] **Step 5: Commit**

```bash
git add scripts/check-vkr-template.sh
git commit -m "test: add vkr template verification"
```

## Task 9: Visual PDF Verification

**Files:**
- Read: `dissertation.pdf`
- Optional generated images: `/tmp/vkr-final-pages/*.png`

- [ ] **Step 1: Render the first four pages**

Run:

```bash
mkdir -p /tmp/vkr-final-pages
gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r160 -dFirstPage=1 -dLastPage=4 -sOutputFile=/tmp/vkr-final-pages/page-%02d.png dissertation.pdf
```

Expected: PASS and create `/tmp/vkr-final-pages/page-01.png` through `/tmp/vkr-final-pages/page-04.png`.

- [ ] **Step 2: Inspect the rendered pages**

Open the rendered images and verify:

- page 1 is the VKR title page and has no printed page number;
- pages 2 and 3 are the assignment sheet and have no printed page number;
- page 4 is `Содержание` and has bottom-center page number `4`;
- the title and assignment sheet follow the supplied PDF samples structurally.

- [ ] **Step 3: Record verification result**

Run:

```bash
git status --short
```

Expected: only intended source changes are present; rendered `/tmp` images are outside the repository.
