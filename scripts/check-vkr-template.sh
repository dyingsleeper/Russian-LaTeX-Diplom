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
