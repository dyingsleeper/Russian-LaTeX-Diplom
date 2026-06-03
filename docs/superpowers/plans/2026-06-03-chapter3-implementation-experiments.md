# Глава 3 «Реализация и экспериментальное исследование» — План реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Заменить шаблонную главу 3 (`part3.tex`, «Вёрстка таблиц») на главу
«Реализация и экспериментальное исследование системы» с листингами кода и
результатами по этапам конвейера; добавить в `diplom2.0` оценочный слой,
порождающий требуемые артефакты.

**Architecture:** Две рабочие линии. **Фаза 1 (LaTeX, репозиторий
`Russian-LaTeX-Diplom`)** — глава 3 со структурой «по этапам конвейера»
(реализация + результат вместе), числа/рисунки на заметных плейсхолдерах
`\ph{...}`, листинги через `\lstinputlisting` из копий модулей в `listings/`,
полные модули в приложении. **Фаза 2 (Python, репозиторий
`/home/dyingsleeper/PycharmProjects/diplom2.0`)** — оценочный слой (вероятностный
инференс, метрики покрытия/`other`/поклассовые/матрица ошибок/τ-развёртка,
персист DBCV/силуэт/DBI, Optuna-артефакты, grouped-by-cluster split,
`experiments_ch3.py`). **Фаза 3 (интеграция)** — подстановка реальных артефактов
вместо плейсхолдеров (следующая итерация, на реальном ящике).

**Tech Stack:** XeLaTeX + `latexmk` + `make`; пакеты `listings`, `booktabs`;
Python ≥3.11, `pytest`, `scikit-learn`, `hdbscan`, `optuna`, `torch`,
`sentence-transformers`.

**Спека:** `docs/superpowers/specs/2026-06-03-chapter3-implementation-experiments-design.md`

---

## Структура файлов

**Фаза 1 — `Russian-LaTeX-Diplom`:**
- `Dissertation/part3.tex` — *замена целиком*: глава 3 (10 разделов).
- `Dissertation/userstyles.tex` — *дополнить*: макрос `\ph{...}` и `\phbox{...}`.
- `Dissertation/part1.tex` — *минимальная правка*: удалить критерий латентности
  в `subsec:ch1/dev/success`.
- `Dissertation/appendix.tex` — *дополнить*: листинги полных модулей.
- `biblio/external.bib` — *дополнить*: `Paszke2019PyTorch` (UMAP уже есть).
- `listings/*.py` — *создать*: копии модулей из `diplom2.0` для приложения и
  in-chapter фрагментов.
- `Dissertation/images/` — рамки-заглушки определяются через `\phbox` прямо в
  `part3.tex` (отдельные файлы не создаём до Фазы 3).

**Фаза 2 — `diplom2.0`:**
- `src/diplom_ai/evaluation/metrics.py` — *дополнить*: coverage, other-rate,
  per-class, confusion, threshold sweep.
- `src/diplom_ai/inference/predict.py` — *дополнить*: softmax, confidence,
  правило τ.
- `src/diplom_ai/clustering/pipeline.py` — *дополнить*: DBCV/силуэт/DBI в метрики
  запуска (через новую чистую функцию в `metrics`/`summaries`).
- `src/diplom_ai/clustering/tuner.py` — *дополнить*: сохранение Optuna-артефакта.
- `src/diplom_ai/training/train.py` (или новый `evaluation/splits.py`) —
  *дополнить*: grouped-by-cluster split.
- `scripts/experiments_ch3.py` — *создать*: драйвер экспериментов.
- `tests/...` — *создать*: модульные тесты по каждой новой функции.

---

# ФАЗА 1 — Глава 3 (LaTeX, плейсхолдеры)

Рабочая директория: `/home/dyingsleeper/PycharmProjects/Russian-LaTeX-Diplom`.
Проверка сборки во всех LaTeX-задачах: `make dissertation-draft` (быстрый режим).

## Task 1.0: Проверить внешние ссылки на метки шаблонной главы 3

**Files:**
- Read only.

- [ ] **Step 1: Найти ссылки на метки текущего `part3.tex`**

Run:
```bash
cd /home/dyingsleeper/PycharmProjects/Russian-LaTeX-Diplom
grep -rn "ch:ch3\|sec:ch3/\|tab:test\|tab:makecell\|tab:Ts0Sib\|tab:S:parse\|tab:S:align\|subsec:ch3/" \
  Dissertation common Synopsis Presentation 2>/dev/null | grep -v "part3.tex"
```

Expected: ссылки только из самого `part3.tex` (исключён). Если найдены внешние
ссылки на `tab:*`/`sec:ch3/*` — выписать их; метку главы `ch:ch3` сохраняем
(новая глава 3 её переиспользует), остальные шаблонные метки будут удалены.

- [ ] **Step 2: Зафиксировать результат**

Если внешних ссылок на удаляемые метки нет — продолжать. Если есть — отметить в
задаче, где их поправить (заменить на новые метки главы 3 из спеки).

## Task 1.1: Макросы плейсхолдеров `\ph` и `\phbox`

**Files:**
- Modify: `Dissertation/userstyles.tex` (в конец файла, до закрывающих определений)

- [ ] **Step 1: Добавить определения макросов**

Добавить в `Dissertation/userstyles.tex`:

```latex
% --- Черновые плейсхолдеры главы 3 (удалить при подстановке реальных данных) ---
% Заметный плейсхолдер значения: легко ищется по "\ph{" и виден красным.
\newcommand{\ph}[1]{\textcolor{red}{\textbf{\(\langle\)#1\(\rangle\)}}}
% Рамка-заглушка под будущий рисунок фиксированной высоты.
\newcommand{\phbox}[2][0.75\textwidth]{%
    \fbox{\parbox[c][5cm][c]{#1}{\centering\textcolor{red}{\textbf{[#2]}}}}}
```

- [ ] **Step 2: Проверить, что цвет `red` доступен**

Run:
```bash
grep -rn "usepackage.*xcolor\|usepackage.*\{color\}\|RequirePackage.*xcolor" \
  common Dissertation | head
```
Expected: `xcolor`/`color` подключён (его уже использует `\fixme` через
`\textcolor`). Дополнительно ничего не подключаем.

- [ ] **Step 3: Smoke-проверка макроса во временной вставке**

Временно добавить в начало `Dissertation/part3.tex` строку `\ph{тест}` после
существующего `\chapter{...}` (уберём в Task 1.3) и собрать.

Run: `make dissertation-draft`
Expected: сборка проходит, на странице главы 3 виден красный `⟨тест⟩`.

- [ ] **Step 4: Commit**

```bash
git add Dissertation/userstyles.tex
git commit -m "Глава 3: макросы плейсхолдеров \ph и \phbox"
```

## Task 1.2: Добавить `Paszke2019PyTorch` в библиографию и сверить ключи

**Files:**
- Modify: `biblio/external.bib`

- [ ] **Step 1: Сверить наличие ключей, используемых главой 3**

Run:
```bash
cd /home/dyingsleeper/PycharmProjects/Russian-LaTeX-Diplom
for k in Campello2013HDBSCAN McInnes2017HDBSCAN Akiba2019Optuna Moulavi2014DBCV \
  Rousseeuw1987Silhouette Davies1979DBI MacQueen1967KMeans Arthur2007KMeansPP \
  Chen2024BGEM3 Vila2023Argilla McInnes2018UMAP; do \
  printf "%-26s " "$k"; grep -q "{$k," biblio/*.bib && echo OK || echo MISSING; done
```
Expected: большинство `OK`. Любой `MISSING` (кроме PyTorch) — добавить запись по
образцу существующих в `biblio/external.bib`.

- [ ] **Step 2: Добавить запись PyTorch**

Добавить в конец `biblio/external.bib`:

```bibtex
@InProceedings{Paszke2019PyTorch,
  author    = {Paszke, Adam and Gross, Sam and Massa, Francisco and Lerer, Adam
               and Bradbury, James and Chanan, Gregory and Killeen, Trevor and others},
  title     = {{PyTorch}: An Imperative Style, High-Performance Deep Learning Library},
  booktitle = {Advances in Neural Information Processing Systems},
  volume    = {32},
  year      = {2019},
  pages     = {8024--8035},
}
```

- [ ] **Step 3: Сборка с обновлённой библиографией**

Run: `make dissertation-draft`
Expected: сборка проходит без ошибок BibTeX (запись не используется до Task 1.x —
это нормально, предупреждение об unused допустимо в draft).

- [ ] **Step 4: Commit**

```bash
git add biblio/external.bib
git commit -m "Глава 3: библиография — PyTorch"
```

## Task 1.3: Каркас главы 3 — заголовок и 10 пустых разделов

**Files:**
- Modify (замена целиком): `Dissertation/part3.tex`

- [ ] **Step 1: Заменить содержимое `part3.tex` на каркас**

Полностью заменить файл на:

```latex
\chapter{Реализация и экспериментальное исследование системы}\label{ch:ch3}

В главе описаны программная реализация спроектированной в
главе~\ref{ch:ch2} системы и результаты её экспериментального исследования на
реальной выборке электронной почты. Изложение ведётся по~этапам конвейера
обработки: для каждого этапа приводится ключевой фрагмент реализации и~получаемый
результат. \ph{черновая глава: числа и рисунки — плейсхолдеры}

\section{Среда реализации и организация кода}\label{sec:ch3/impl}

\section{Данные, экспериментальная установка и протокол оценки}\label{sec:ch3/setup}

\section{Синхронизация и нормализация писем}\label{sec:ch3/norm}

\section{Построение векторных представлений}\label{sec:ch3/embed}

\section{Кластеризация и подбор параметров}\label{sec:ch3/cluster}

\section{Ручная проверка и формирование классов}\label{sec:ch3/annot}

\section{Классификатор: обучение и оценка}\label{sec:ch3/clf}

\section{Применение классификатора и порог уверенности}\label{sec:ch3/infer}

\section{Демонстрация цикла переобучения}\label{sec:ch3/loop}

\section{Выводы по главе}\label{sec:ch3/concl}

\clearpage
```

- [ ] **Step 2: Сборка каркаса**

Run: `make dissertation-draft`
Expected: сборка проходит; в оглавлении глава 3 с новым названием и 10 разделами.

- [ ] **Step 3: Commit**

```bash
git add Dissertation/part3.tex
git commit -m "Глава 3: каркас (заголовок + 10 разделов)"
```

## Task 1.4: Скопировать модули `diplom2.0` в `listings/`

**Files:**
- Create: `listings/preprocessing.py`, `listings/normalization.py`,
  `listings/embeddings.py`, `listings/tuner.py`, `listings/import_labels.py`,
  `listings/text_classifier.py`, `listings/predict.py`, `listings/email_pipeline.py`,
  `listings/metrics.py`

- [ ] **Step 1: Скопировать файлы**

Run:
```bash
cd /home/dyingsleeper/PycharmProjects/Russian-LaTeX-Diplom
SRC=/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai
cp "$SRC/data/preprocessing.py"        listings/preprocessing.py
cp "$SRC/email/normalization.py"       listings/normalization.py
cp "$SRC/clustering/embeddings.py"     listings/embeddings.py
cp "$SRC/clustering/tuner.py"          listings/tuner.py
cp "$SRC/annotation/import_labels.py"  listings/import_labels.py
cp "$SRC/models/text_classifier.py"    listings/text_classifier.py
cp "$SRC/inference/predict.py"         listings/predict.py
cp "$SRC/orchestration/email_pipeline.py" listings/email_pipeline.py
cp "$SRC/evaluation/metrics.py"        listings/metrics.py
ls -1 listings/*.py
```
Expected: девять `.py` файлов в `listings/`.

> **Примечание.** `predict.py` и `metrics.py` сейчас — версии *до* Фазы 2.
> После реализации Фазы 2 их нужно перекопировать (Фаза 3), чтобы листинги Л3.7 и
> метрики соответствовали финальному коду.

- [ ] **Step 2: Определить точные диапазоны строк для in-chapter фрагментов**

Run (пример для одного файла; повторить для каждого):
```bash
grep -n "^def \|^    def \|^class " listings/tuner.py
```
Expected: список функций с номерами строк. Записать диапазоны для:
`listings/email_pipeline.py` — функция цикла дренажа очереди;
`listings/preprocessing.py` — `normalize_text` (≈12–24);
`listings/normalization.py` — `normalize_raw_email`;
`listings/embeddings.py` — функция батчевого построения с записью `.npz`;
`listings/tuner.py` — целевая функция Optuna (objective);
`listings/import_labels.py` — распространение метки + strict-режим;
`listings/text_classifier.py` — `forward`/конструктор модели.
Эти диапазоны используются в Task 1.7–1.13 в опции `linerange={A-B}`.

- [ ] **Step 3: Commit**

```bash
git add listings/*.py
git commit -m "Глава 3: копии модулей diplom2.0 для листингов"
```

## Task 1.5: Правка критериев успеха в главе 1 (удалить латентность CPU)

**Files:**
- Modify: `Dissertation/part1.tex` (`subsec:ch1/dev/success`, пункт про латентность)

- [ ] **Step 1: Удалить пункт критерия латентности**

В `Dissertation/part1.tex` в перечне критериев успеха удалить пункт:

```latex
    \item Среднее время инференса одного сообщения на~целевой конфигурации
        не~превышает \( \fixme{\tau_{\mathrm{lat}}} \)~мс на~CPU.
```

Остальные три критерия (качество+покрытие; изоляция данных; полный цикл) оставить.
Проверить, что нумерация/ссылки на критерии нигде не завязаны на номер удалённого
пункта (`grep -n "критери" Dissertation/*.tex`).

- [ ] **Step 2: Сборка**

Run: `make dissertation-draft`
Expected: сборка проходит; в §«Критерии успеха» три пункта.

- [ ] **Step 3: Commit**

```bash
git add Dissertation/part1.tex
git commit -m "Глава 1: убран критерий латентности на CPU (согласовано для главы 3)"
```

## Task 1.6: Раздел 3.1 — среда реализации и организация кода

**Files:**
- Modify: `Dissertation/part3.tex` (`sec:ch3/impl`)

- [ ] **Step 1: Наполнить раздел 3.1**

Под `\section{Среда реализации...}` добавить прозу + таблицу модулей + листинг
Л3.1. Концовка содержания (проза пишется по этим пунктам):
- стек: Python (\(\geqslant\)3.11), ключевые библиотеки (`sentence-transformers`,
  `hdbscan`, `optuna`, `scikit-learn`, `torch`, `psycopg`, `argilla`);
- организация `src/diplom_ai` по слоям (сослаться на главу 2, не дублировать);
- инструменты качества `ruff`/`mypy`/`pytest`, запуск инфраструктуры через
  Docker Compose;
- листинг Л3.1 — цикл дренажа очереди задач.

Вставить таблицу и листинг:

```latex
\begin{table}[htbp]
    \centering
    \caption{Пакеты приложения и их назначение}\label{tab:ch3/modules}
    \begin{tabular}{@{}ll@{}}
        \toprule
        Пакет & Назначение \\
        \midrule
        \texttt{email}         & синхронизация и нормализация писем \\
        \texttt{storage}       & доступ к PostgreSQL, схема, репозитории \\
        \texttt{queueing}      & очередь задач конвейера \\
        \texttt{orchestration} & диспетчеризация этапов \\
        \texttt{clustering}    & эмбеддинги, кластеризация, подбор параметров \\
        \texttt{annotation}    & экспорт/импорт разметки (Argilla) \\
        \texttt{training}      & обучение классификатора \\
        \texttt{inference}     & применение модели \\
        \texttt{evaluation}    & метрики качества \\
        \bottomrule
    \end{tabular}
\end{table}

\lstinputlisting[language={Python},linerange={\ph{A-B}},%
    caption={Цикл дренажа очереди задач},label={lst:ch3/drain}]%
    {listings/email_pipeline.py}
```

Заменить `\ph{A-B}` на диапазон из Task 1.4 Step 2.

- [ ] **Step 2: Сборка**

Run: `make dissertation-draft`
Expected: раздел 3.1 рендерится; таблица и листинг на месте; русские комментарии
в листинге читаемы (риск кириллицы под XeLaTeX — проверить визуально).

- [ ] **Step 3: Commit**

```bash
git add Dissertation/part3.tex
git commit -m "Глава 3: раздел 3.1 (среда и организация кода)"
```

## Task 1.7: Раздел 3.2 — данные, установка и протокол оценки

**Files:**
- Modify: `Dissertation/part3.tex` (`sec:ch3/setup`)

- [ ] **Step 1: Наполнить раздел 3.2**

Проза по пунктам:
- обезличенное описание корпуса (объём `\ph{N}`, доли ru/en `\ph{..}`, период
  `\ph{..}`, фильтр качества);
- конфигурация и версии (`BAAI/bge-m3` версия `\ph{..}`, seed `\ph{..}`);
- напоминание метрик со ссылками: `\ref{subsec:ch1/cluster/metrics}` (DBCV,
  силуэт, индекс Дэвиса–Боулдина), `\ref{subsec:ch1/task/metrics}` (accuracy,
  macro-F1, weighted-F1, покрытие, доля \texttt{other});
- протокол оценки классификатора: gold-тест из человеко-проверенных меток, сплит
  сгруппирован по кластеру (письма одного кластера не попадают в train и test
  одновременно), фиксированный seed, support на класс.

Вставить таблицу состава корпуса:

```latex
\begin{table}[htbp]
    \centering
    \caption{Состав исследуемой выборки писем}\label{tab:ch3/corpus}
    \begin{tabular}{@{}lr@{}}
        \toprule
        Характеристика & Значение \\
        \midrule
        Всего писем (после синхронизации) & \ph{N} \\
        Качество \texttt{ok} / \texttt{empty} / \texttt{too\_short} & \ph{..\,/\,..\,/\,..} \\
        Доля русскоязычных / англоязычных & \ph{0.NN} / \ph{0.NN} \\
        Период & \ph{ММ.ГГГГ--ММ.ГГГГ} \\
        \bottomrule
    \end{tabular}
\end{table}
```

- [ ] **Step 2: Сборка**

Run: `make dissertation-draft`
Expected: раздел 3.2 рендерится; ссылки `\ref` разрешаются (во втором проходе),
плейсхолдеры красные.

- [ ] **Step 3: Commit**

```bash
git add Dissertation/part3.tex
git commit -m "Глава 3: раздел 3.2 (данные, установка, протокол оценки)"
```

## Task 1.8: Раздел 3.3 — синхронизация и нормализация

**Files:**
- Modify: `Dissertation/part3.tex` (`sec:ch3/norm`)

- [ ] **Step 1: Наполнить раздел 3.3**

Проза: путь `IMAP -> raw MIME -> RawEmail -> NormalizedEmail`; токенизация
`LINK/EMAIL/DATE/TIME/NUM` реализована в `data/preprocessing.py`
(`normalize_text`), а `email/normalization.py` (`normalize_raw_email`)
**делегирует** ей и добавляет срез цитат/подписей/футеров, определение языка и
оценку качества. Привести два листинга (Л3.2a — токенизация, Л3.2b —
делегирование):

```latex
\lstinputlisting[language={Python},linerange={\ph{A-B}},%
    caption={Замена ссылок, адресов, дат и чисел токенами},label={lst:ch3/tokens}]%
    {listings/preprocessing.py}

\lstinputlisting[language={Python},linerange={\ph{C-D}},%
    caption={Нормализация письма: делегирование токенизации и срез цитат},%
    label={lst:ch3/normalize}]{listings/normalization.py}
```

Таблица распределения качества/языков (Т3.2) + анонимизированный пример
«до/после» (текст примера — `\ph{...}` либо обезличенный фрагмент):

```latex
\begin{table}[htbp]
    \centering
    \caption{Результат нормализации: качество и язык}\label{tab:ch3/norm-quality}
    \begin{tabular}{@{}lrr@{}}
        \toprule
        Категория & Русские & Английские \\
        \midrule
        \texttt{ok}        & \ph{..} & \ph{..} \\
        \texttt{empty}     & \ph{..} & \ph{..} \\
        \texttt{too\_short}& \ph{..} & \ph{..} \\
        \bottomrule
    \end{tabular}
\end{table}
```

- [ ] **Step 2: Сборка**

Run: `make dissertation-draft`
Expected: раздел 3.3 рендерится с двумя листингами и таблицей.

- [ ] **Step 3: Commit**

```bash
git add Dissertation/part3.tex
git commit -m "Глава 3: раздел 3.3 (нормализация)"
```

## Task 1.9: Раздел 3.4 — построение векторных представлений

**Files:**
- Modify: `Dissertation/part3.tex` (`sec:ch3/embed`)

- [ ] **Step 1: Наполнить раздел 3.4**

Проза: батчевое построение эмбеддингов `bge-m3`, атомарная запись `.npz`,
индексная запись в `email_embeddings`, версионирование, фильтр по языку/качеству.
Листинг Л3.3:

```latex
\lstinputlisting[language={Python},linerange={\ph{A-B}},%
    caption={Батчевое построение эмбеддингов и кеширование в \texttt{.npz}},%
    label={lst:ch3/embeddings}]{listings/embeddings.py}
```

Числа: размерность `\ph{d}`, число векторов после фильтра `\ph{N}`, размер кеша
`\ph{..МБ}`, время построения `\ph{..}` — в прозе или мини-таблице.

- [ ] **Step 2: Сборка**

Run: `make dissertation-draft`
Expected: раздел 3.4 рендерится.

- [ ] **Step 3: Commit**

```bash
git add Dissertation/part3.tex
git commit -m "Глава 3: раздел 3.4 (эмбеддинги)"
```

## Task 1.10: Раздел 3.5 — кластеризация и подбор параметров

**Files:**
- Modify: `Dissertation/part3.tex` (`sec:ch3/cluster`)

- [ ] **Step 1: Наполнить раздел 3.5**

Проза: HDBSCAN на нормированных векторах; подбор параметров Optuna (целевая —
DBCV + добавки − штраф за шум, при ограничениях допустимости); сравнение с
дефолтными параметрами и KMeans по протоколу (k = числу кластеров HDBSCAN либо по
максимуму силуэта; силуэт/индекс Дэвиса–Боулдина — на не-шумовых точках обоих
алгоритмов; DBCV — для HDBSCAN; доля покрытия — контекст). Листинг Л3.4:

```latex
\lstinputlisting[language={Python},linerange={\ph{A-B}},%
    caption={Целевая функция подбора параметров HDBSCAN (DBCV с добавками)},%
    label={lst:ch3/tuner}]{listings/tuner.py}
```

Рисунки и таблицы:

```latex
\begin{figure}[htbp]
    \centering
    \phbox{рис.: история оптимизации Optuna --- заменить на \texttt{optuna\_history.pdf}}
    \caption{История оптимизации DBCV (Optuna, TPE)}\label{fig:ch3/optuna}
\end{figure}

\begin{table}[htbp]
    \centering
    \caption{Лучшие гиперпараметры HDBSCAN и важность параметров}\label{tab:ch3/optuna-best}
    \begin{tabular}{@{}lr@{}}
        \toprule
        Параметр & Значение / важность \\
        \midrule
        \texttt{min\_cluster\_size} & \ph{..} \\
        \texttt{min\_samples}       & \ph{..} \\
        Значение целевой функции     & \ph{0.NN} \\
        Важность \texttt{min\_cluster\_size} / \texttt{min\_samples} & \ph{0.NN} / \ph{0.NN} \\
        \bottomrule
    \end{tabular}
\end{table}

\begin{table}[htbp]
    \centering
    \caption{Сравнение алгоритмов кластеризации (внутренние метрики)}\label{tab:ch3/cluster-compare}
    \begin{tabular}{@{}lrrr@{}}
        \toprule
        Метрика & HDBSCAN+тюнер & HDBSCAN (дефолт) & KMeans \\
        \midrule
        Число кластеров            & \ph{..} & \ph{..} & \ph{..} \\
        Силуэт (без шума)          & \ph{0.NN} & \ph{0.NN} & \ph{0.NN} \\
        Индекс Дэвиса--Боулдина    & \ph{0.NN} & \ph{0.NN} & \ph{0.NN} \\
        DBCV                       & \ph{0.NN} & \ph{0.NN} & --- \\
        Доля покрытия (1 -- шум)   & \ph{0.NN} & \ph{0.NN} & 1.00 \\
        \bottomrule
    \end{tabular}
\end{table}

\begin{table}[htbp]
    \centering
    \caption{Метрики итогового запуска кластеризации}\label{tab:ch3/cluster-metrics}
    \begin{tabular}{@{}lr@{}}
        \toprule
        Показатель & Значение \\
        \midrule
        Число кластеров          & \ph{K} \\
        Доля шума                & \ph{0.NN} \\
        DBCV                     & \ph{0.NN} \\
        Силуэт                   & \ph{0.NN} \\
        Индекс Дэвиса--Боулдина  & \ph{0.NN} \\
        \bottomrule
    \end{tabular}
\end{table}

\begin{figure}[htbp]
    \centering
    \phbox{рис.: 2D-проекция кластеров (UMAP) --- заменить на \texttt{cluster\_projection.pdf}}
    \caption{Двумерная проекция кластеров (UMAP)}\label{fig:ch3/projection}
\end{figure}

\begin{table}[htbp]
    \centering
    \caption{Ключевые термины кластеров (TF-IDF)}\label{tab:ch3/topterms}
    \begin{tabular}{@{}llr@{}}
        \toprule
        Кластер & Топ-термины & Размер \\
        \midrule
        1 & \ph{термины} & \ph{..} \\
        2 & \ph{термины} & \ph{..} \\
        \multicolumn{3}{@{}l}{\ph{... остальные кластеры}} \\
        \bottomrule
    \end{tabular}
\end{table}
```

- [ ] **Step 2: Сборка**

Run: `make dissertation-draft`
Expected: раздел 3.5 рендерится; четыре таблицы, две рамки-заглушки, листинг.

- [ ] **Step 3: Commit**

```bash
git add Dissertation/part3.tex
git commit -m "Глава 3: раздел 3.5 (кластеризация и подбор параметров)"
```

## Task 1.11: Раздел 3.6 — ручная проверка и формирование классов

**Files:**
- Modify: `Dissertation/part3.tex` (`sec:ch3/annot`)

- [ ] **Step 1: Наполнить раздел 3.6**

Проза: ревью представителей в Argilla; распространение метки на кластер;
strict-режим (разногласие → `other`). Листинг Л3.5:

```latex
\lstinputlisting[language={Python},linerange={\ph{A-B}},%
    caption={Распространение метки на кластер и обработка разногласия},%
    label={lst:ch3/propagate}]{listings/import_labels.py}
```

Таблица итоговых классов:

```latex
\begin{table}[htbp]
    \centering
    \caption{Сформированные классы и их размеры}\label{tab:ch3/classes}
    \begin{tabular}{@{}lr@{}}
        \toprule
        Класс & Число писем \\
        \midrule
        \ph{класс 1} & \ph{..} \\
        \ph{класс 2} & \ph{..} \\
        \texttt{other} & \ph{..} \\
        \bottomrule
    \end{tabular}
\end{table}
```

Числа объёма ручного труда: представителей `\ph{..}` из `\ph{N}` писем (доля
`\ph{0.NN}`).

- [ ] **Step 2: Сборка**

Run: `make dissertation-draft`
Expected: раздел 3.6 рендерится.

- [ ] **Step 3: Commit**

```bash
git add Dissertation/part3.tex
git commit -m "Глава 3: раздел 3.6 (ручная проверка и классы)"
```

## Task 1.12: Раздел 3.7 — классификатор: обучение и оценка

**Files:**
- Modify: `Dissertation/part3.tex` (`sec:ch3/clf`)

- [ ] **Step 1: Наполнить раздел 3.7**

Проза: архитектура классификатора (словарь + обучаемые эмбеддинги, mean-pooling,
линейная голова); оценка на gold-тесте (grouped по кластеру, seed). Листинг Л3.6:

```latex
\lstinputlisting[language={Python},linerange={\ph{A-B}},%
    caption={Классификатор: эмбеддинги, mean-pooling и линейная голова},%
    label={lst:ch3/model}]{listings/text_classifier.py}
```

Метрики и матрица ошибок:

```latex
\begin{table}[htbp]
    \centering
    \caption{Качество классификатора на gold-тесте}\label{tab:ch3/clf-overall}
    \begin{tabular}{@{}lr@{}}
        \toprule
        Метрика & Значение \\
        \midrule
        Accuracy     & \ph{0.NN} \\
        macro-F1     & \ph{0.NN} \\
        weighted-F1  & \ph{0.NN} \\
        Покрытие     & \ph{0.NN} \\
        Доля \texttt{other} & \ph{0.NN} \\
        \bottomrule
    \end{tabular}
\end{table}

\begin{table}[htbp]
    \centering
    \caption{Поклассовые показатели качества}\label{tab:ch3/clf-perclass}
    \begin{tabular}{@{}lrrrr@{}}
        \toprule
        Класс & Precision & Recall & F1 & Support \\
        \midrule
        \ph{класс 1} & \ph{0.NN} & \ph{0.NN} & \ph{0.NN} & \ph{..} \\
        \ph{класс 2} & \ph{0.NN} & \ph{0.NN} & \ph{0.NN} & \ph{..} \\
        \bottomrule
    \end{tabular}
\end{table}

\begin{figure}[htbp]
    \centering
    \phbox{рис.: матрица ошибок --- заменить на \texttt{confusion\_matrix.pdf}}
    \caption{Матрица ошибок классификатора}\label{fig:ch3/confusion}
\end{figure}
```

- [ ] **Step 2: Сборка**

Run: `make dissertation-draft`
Expected: раздел 3.7 рендерится.

- [ ] **Step 3: Commit**

```bash
git add Dissertation/part3.tex
git commit -m "Глава 3: раздел 3.7 (классификатор)"
```

## Task 1.13: Раздел 3.8 — применение и порог уверенности τ

**Files:**
- Modify: `Dissertation/part3.tex` (`sec:ch3/infer`)

- [ ] **Step 1: Наполнить раздел 3.8**

Проза: вероятностный инференс (softmax, confidence = max prob), решающее правило —
низкоуверенные (по порогу τ) → `other`; компромисс покрытие/точность; выбор
рабочего τ. Листинг Л3.7 (после Фазы 2; до неё — каркас с `% TODO`):

```latex
\lstinputlisting[language={Python},linerange={\ph{A-B}},%
    caption={Решающее правило с порогом уверенности \(\tau\)},%
    label={lst:ch3/threshold}]{listings/predict.py}
```

Развёртка по τ:

```latex
\begin{figure}[htbp]
    \centering
    \phbox{рис.: развёртка метрик по \(\tau\) --- заменить на \texttt{tau\_sweep.pdf}}
    \caption{Зависимость покрытия и macro-F1 от порога \(\tau\)}\label{fig:ch3/tau}
\end{figure}

\begin{table}[htbp]
    \centering
    \caption{Метрики при различных порогах \(\tau\)}\label{tab:ch3/tau}
    \begin{tabular}{@{}rrrr@{}}
        \toprule
        \(\tau\) & Покрытие & macro-F1 & Доля \texttt{other} \\
        \midrule
        \ph{0.5} & \ph{0.NN} & \ph{0.NN} & \ph{0.NN} \\
        \ph{0.7} & \ph{0.NN} & \ph{0.NN} & \ph{0.NN} \\
        \ph{0.9} & \ph{0.NN} & \ph{0.NN} & \ph{0.NN} \\
        \bottomrule
    \end{tabular}
\end{table}
```

- [ ] **Step 2: Сборка**

Run: `make dissertation-draft`
Expected: раздел 3.8 рендерится.

- [ ] **Step 3: Commit**

```bash
git add Dissertation/part3.tex
git commit -m "Глава 3: раздел 3.8 (порог уверенности)"
```

## Task 1.14: Раздел 3.9 — демонстрация цикла переобучения

**Files:**
- Modify: `Dissertation/part3.tex` (`sec:ch3/loop`)

- [ ] **Step 1: Наполнить раздел 3.9**

Проза-сценарий: накопление буфера `other` до порога N → перекластеризация буфера →
ручная проверка → обучение новой версии → активация по quality gates. Зафиксировать
версии модели до/после и факт активации. Таблица версий:

```latex
\begin{table}[htbp]
    \centering
    \caption{Версии модели в сценарии цикла переобучения}\label{tab:ch3/versions}
    \begin{tabular}{@{}llrr@{}}
        \toprule
        Версия & Статус & macro-F1 & Покрытие \\
        \midrule
        \ph{v1} & archived & \ph{0.NN} & \ph{0.NN} \\
        \ph{v2} & active   & \ph{0.NN} & \ph{0.NN} \\
        \bottomrule
    \end{tabular}
\end{table}
```

Текст явно отмечает, что это подтверждение работоспособности цикла (критерий
успеха №4 из `\ref{subsec:ch1/dev/success}`), а не исследование дрейфа.

- [ ] **Step 2: Сборка**

Run: `make dissertation-draft`
Expected: раздел 3.9 рендерится.

- [ ] **Step 3: Commit**

```bash
git add Dissertation/part3.tex
git commit -m "Глава 3: раздел 3.9 (цикл переобучения)"
```

## Task 1.15: Раздел 3.10 — выводы и сводная таблица критериев

**Files:**
- Modify: `Dissertation/part3.tex` (`sec:ch3/concl`)

- [ ] **Step 1: Наполнить раздел 3.10**

Проза: краткое резюме реализации и результатов; обсуждение ограничений. Сводная
таблица (критерии 1, 3, 4; критерий латентности удалён):

```latex
\begin{table}[htbp]
    \centering
    \caption{Достигнутые показатели против критериев успеха}\label{tab:ch3/criteria}
    \begin{tabular}{@{}p{0.55\textwidth}ll@{}}
        \toprule
        Критерий (\ref{subsec:ch1/dev/success}) & Цель & Достигнуто \\
        \midrule
        Качество классификации (macro-F1) при покрытии & \(\geqslant\)\ph{..} & \ph{0.NN} \\
        Изоляция данных (нет передачи во вне)           & да    & да (архит.) \\
        Полный цикл \texttt{other}$\to$проверка$\to$переобучение$\to$активация & реализован & §\ref{sec:ch3/loop} \\
        \bottomrule
    \end{tabular}
\end{table}
```

- [ ] **Step 2: Сборка**

Run: `make dissertation-draft`
Expected: раздел 3.10 рендерится; ссылки разрешаются.

- [ ] **Step 3: Commit**

```bash
git add Dissertation/part3.tex
git commit -m "Глава 3: раздел 3.10 (выводы и сводная таблица)"
```

## Task 1.16: Листинги полных модулей в приложении

**Files:**
- Modify: `Dissertation/appendix.tex` (раздел в приложении A)

- [ ] **Step 1: Добавить листинги полных модулей**

В `Dissertation/appendix.tex` (приложение `app:A`) добавить раздел с полными
модулями по образцу существующего `\lstinputlisting` (строка 116). Для каждого
файла:

```latex
\begingroup
\captiondelim{ }
\lstinputlisting[language={Python},%
    caption={Модуль нормализации писем},label={lst:app/normalization}]%
    {listings/normalization.py}
\endgroup
```

Повторить для: `preprocessing.py`, `tuner.py`, `text_classifier.py`,
`predict.py`, `metrics.py`. Длинные файлы при необходимости разбить опциями
`firstline`/`lastline`.

- [ ] **Step 2: Сборка**

Run: `make dissertation-draft`
Expected: приложение собирается; листинги переносятся по страницам.

- [ ] **Step 3: Commit**

```bash
git add Dissertation/appendix.tex
git commit -m "Глава 3: листинги полных модулей в приложении"
```

## Task 1.17: Полная сборка диссертации (не-draft) и финальная проверка Фазы 1

**Files:**
- Read only (сборка).

- [ ] **Step 1: Полная сборка**

Run: `make dissertation`
Expected: сборка проходит; глава 3, листинги и таблицы на месте; ссылки `\ref`
разрешены; библиография собралась. Если ссылки `?` — повторить сборку (двойной
проход) либо см. процедуру в `Readme/Installation.md`.

- [ ] **Step 2: Визуальная проверка плейсхолдеров**

Run:
```bash
grep -c "\\\\ph{" Dissertation/part3.tex
```
Expected: ненулевое число — все незаполненные значения помечены и видны красным в
PDF (их заменит Фаза 3).

- [ ] **Step 3: Commit (если были правки сборки)**

```bash
git add -A && git commit -m "Глава 3: полная сборка диссертации проходит" || echo "нет изменений"
```

---

# ФАЗА 2 — Оценочный слой в `diplom2.0` (TDD)

Рабочая директория: `/home/dyingsleeper/PycharmProjects/diplom2.0`.
Активировать окружение и запускать тесты: `pytest` (см. `Makefile`/`pyproject.toml`).
Все функции — чистые, тестируются модульно. Коммиты — в репозитории `diplom2.0`.

## Task 2.1: Метрики покрытия, доли `other`, поклассовые и матрица ошибок

**Files:**
- Modify: `src/diplom_ai/evaluation/metrics.py`
- Test: `tests/evaluation/test_metrics_ch3.py`

- [ ] **Step 1: Написать падающие тесты**

Create `tests/evaluation/test_metrics_ch3.py`:

```python
from diplom_ai.evaluation.metrics import (
    coverage,
    other_rate,
    per_class_metrics,
    confusion_matrix_labeled,
)


def test_coverage_and_other_rate():
    preds = ["a", "other", "b", "other"]
    assert coverage(preds, other_label="other") == 0.5
    assert other_rate(preds, other_label="other") == 0.5


def test_per_class_metrics_keys_and_support():
    y_true = ["a", "a", "b", "b"]
    y_pred = ["a", "b", "b", "b"]
    result = per_class_metrics(y_true, y_pred, labels=["a", "b"])
    assert set(result["a"]) == {"precision", "recall", "f1", "support"}
    assert result["a"]["support"] == 2
    assert result["b"]["support"] == 2
    assert result["a"]["recall"] == 0.5


def test_confusion_matrix_labeled_shape():
    y_true = ["a", "b", "a"]
    y_pred = ["a", "a", "a"]
    labels = ["a", "b"]
    matrix = confusion_matrix_labeled(y_true, y_pred, labels)
    assert matrix == [[2, 0], [1, 0]]
```

- [ ] **Step 2: Запустить тесты — убедиться, что падают**

Run: `pytest tests/evaluation/test_metrics_ch3.py -v`
Expected: FAIL (`ImportError`/`cannot import name`).

- [ ] **Step 3: Реализовать функции**

Добавить в `src/diplom_ai/evaluation/metrics.py`:

```python
def coverage(predictions: Sequence[str], *, other_label: str = "other") -> float:
    if not predictions:
        return 0.0
    accepted = sum(1 for p in predictions if p != other_label)
    return accepted / len(predictions)


def other_rate(predictions: Sequence[str], *, other_label: str = "other") -> float:
    if not predictions:
        return 0.0
    return sum(1 for p in predictions if p == other_label) / len(predictions)


def per_class_metrics(
    y_true: Sequence[str], y_pred: Sequence[str], labels: Sequence[str]
) -> dict[str, dict[str, float]]:
    from sklearn.metrics import precision_recall_fscore_support  # type: ignore[import-untyped]

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=list(labels), zero_division=0
    )
    return {
        label: {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
        }
        for i, label in enumerate(labels)
    }


def confusion_matrix_labeled(
    y_true: Sequence[str], y_pred: Sequence[str], labels: Sequence[str]
) -> list[list[int]]:
    from sklearn.metrics import confusion_matrix  # type: ignore[import-untyped]

    matrix = confusion_matrix(y_true, y_pred, labels=list(labels))
    return matrix.tolist()
```

- [ ] **Step 4: Запустить тесты — убедиться, что проходят**

Run: `pytest tests/evaluation/test_metrics_ch3.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/diplom_ai/evaluation/metrics.py tests/evaluation/test_metrics_ch3.py
git commit -m "evaluation: coverage, other-rate, per-class, confusion"
```

## Task 2.2: Развёртка метрик по порогу τ

**Files:**
- Modify: `src/diplom_ai/evaluation/metrics.py`
- Test: `tests/evaluation/test_threshold_sweep.py`

- [ ] **Step 1: Написать падающий тест**

Create `tests/evaluation/test_threshold_sweep.py`:

```python
from diplom_ai.evaluation.metrics import threshold_sweep


def test_threshold_sweep_rows_and_other_rate():
    # два класса, вероятности по классам [a, b]
    y_true = ["a", "b", "a"]
    probs = [[0.9, 0.1], [0.4, 0.6], [0.55, 0.45]]
    labels = ["a", "b"]
    rows = threshold_sweep(
        y_true, probs, labels, thresholds=[0.5, 0.8], other_label="other"
    )
    assert [r["tau"] for r in rows] == [0.5, 0.8]
    # при tau=0.8 второй и третий примеры уходят в other (max prob < 0.8)
    row_high = rows[1]
    assert row_high["other_rate"] == 2 / 3
    assert {"tau", "coverage", "macro_f1", "other_rate"} <= set(row_high)
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `pytest tests/evaluation/test_threshold_sweep.py -v`
Expected: FAIL (`cannot import name 'threshold_sweep'`).

- [ ] **Step 3: Реализовать**

Добавить в `src/diplom_ai/evaluation/metrics.py`:

```python
def threshold_sweep(
    y_true: Sequence[str],
    probabilities: Sequence[Sequence[float]],
    labels: Sequence[str],
    *,
    thresholds: Sequence[float],
    other_label: str = "other",
) -> list[dict[str, Any]]:
    from sklearn.metrics import f1_score  # type: ignore[import-untyped]

    rows: list[dict[str, Any]] = []
    for tau in thresholds:
        predictions: list[str] = []
        for probs in probabilities:
            best_index = max(range(len(probs)), key=lambda i: probs[i])
            predictions.append(
                labels[best_index] if probs[best_index] >= tau else other_label
            )
        rows.append(
            {
                "tau": tau,
                "coverage": coverage(predictions, other_label=other_label),
                "other_rate": other_rate(predictions, other_label=other_label),
                "macro_f1": float(
                    f1_score(y_true, predictions, average="macro", zero_division=0)
                ),
            }
        )
    return rows
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `pytest tests/evaluation/test_threshold_sweep.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/diplom_ai/evaluation/metrics.py tests/evaluation/test_threshold_sweep.py
git commit -m "evaluation: развёртка метрик по порогу tau"
```

## Task 2.3: Вероятностный инференс и правило τ

**Files:**
- Modify: `src/diplom_ai/inference/predict.py`
- Test: `tests/inference/test_predict_threshold.py`

- [ ] **Step 1: Написать падающие тесты для чистых помощников**

Create `tests/inference/test_predict_threshold.py`:

```python
from diplom_ai.inference.predict import softmax, apply_threshold


def test_softmax_sums_to_one():
    probs = softmax([2.0, 1.0, 0.1])
    assert abs(sum(probs) - 1.0) < 1e-9
    assert probs[0] > probs[1] > probs[2]


def test_apply_threshold_routes_low_confidence_to_other():
    labels = ["a", "b"]
    # уверенный → класс; неуверенный → other
    assert apply_threshold([0.95, 0.05], labels, tau=0.8) == ("a", 0.95)
    assert apply_threshold([0.55, 0.45], labels, tau=0.8) == ("other", 0.55)
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `pytest tests/inference/test_predict_threshold.py -v`
Expected: FAIL (`cannot import name`).

- [ ] **Step 3: Реализовать чистые помощники + метод вероятностей**

Добавить в `src/diplom_ai/inference/predict.py`:

```python
def softmax(logits: Sequence[float]) -> list[float]:
    import math

    maximum = max(logits)
    exps = [math.exp(value - maximum) for value in logits]
    total = sum(exps)
    return [value / total for value in exps]


def apply_threshold(
    probabilities: Sequence[float],
    labels: Sequence[str],
    *,
    tau: float,
    other_label: str = "other",
) -> tuple[str, float]:
    best_index = max(range(len(probabilities)), key=lambda i: probabilities[i])
    confidence = probabilities[best_index]
    label = labels[best_index] if confidence >= tau else other_label
    return label, confidence
```

И метод в `SavedTextClassifier` (рядом с `predict`):

```python
    def predict_proba(self, texts: Sequence[str]) -> list[list[float]]:
        import torch

        self.model.eval()
        encoded = [encode_text(text, self.vocabulary, self.max_length) for text in texts]
        masks = [attention_mask(input_ids) for input_ids in encoded]
        if not encoded:
            return []
        torch_device = torch.device(self.device)
        with torch.no_grad():
            input_ids = torch.tensor(encoded, dtype=torch.long).to(torch_device)
            attention_masks = torch.tensor(masks, dtype=torch.long).to(torch_device)
            logits = self.model(input_ids, attention_masks)
            probabilities = torch.softmax(logits, dim=1).cpu().tolist()
        return [list(map(float, row)) for row in probabilities]

    def predict_with_threshold(
        self, texts: Sequence[str], *, tau: float, other_label: str = "other"
    ) -> list[tuple[str, float]]:
        return [
            apply_threshold(row, self.labels, tau=tau, other_label=other_label)
            for row in self.predict_proba(texts)
        ]
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `pytest tests/inference/test_predict_threshold.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/diplom_ai/inference/predict.py tests/inference/test_predict_threshold.py
git commit -m "inference: вероятности, softmax и правило порога tau"
```

## Task 2.4: Внутренние метрики кластеризации (DBCV/силуэт/DBI) и их персист

**Files:**
- Create: `src/diplom_ai/clustering/internal_metrics.py`
- Modify: `src/diplom_ai/clustering/pipeline.py` (метрики запуска)
- Test: `tests/clustering/test_internal_metrics.py`

- [ ] **Step 1: Написать падающий тест**

Create `tests/clustering/test_internal_metrics.py`:

```python
import numpy as np

from diplom_ai.clustering.internal_metrics import internal_cluster_metrics


def test_internal_metrics_on_two_clusters():
    rng = np.random.default_rng(0)
    cluster_a = rng.normal(loc=0.0, scale=0.05, size=(20, 2))
    cluster_b = rng.normal(loc=5.0, scale=0.05, size=(20, 2))
    embeddings = np.vstack([cluster_a, cluster_b])
    labels = np.array([0] * 20 + [1] * 20)
    metrics = internal_cluster_metrics(embeddings, labels, noise_label=-1)
    assert {"silhouette", "davies_bouldin", "dbcv"} <= set(metrics)
    assert metrics["silhouette"] > 0.5      # явно разделимые кластеры
    assert metrics["davies_bouldin"] >= 0.0


def test_internal_metrics_excludes_noise_for_silhouette():
    rng = np.random.default_rng(1)
    embeddings = np.vstack(
        [rng.normal(0.0, 0.05, (10, 2)), rng.normal(5.0, 0.05, (10, 2)), [[2.5, 2.5]]]
    )
    labels = np.array([0] * 10 + [1] * 10 + [-1])  # последняя точка — шум
    metrics = internal_cluster_metrics(embeddings, labels, noise_label=-1)
    assert metrics["silhouette"] > 0.5  # шумовая точка не ломает силуэт
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `pytest tests/clustering/test_internal_metrics.py -v`
Expected: FAIL (модуль не существует).

- [ ] **Step 3: Реализовать чистую функцию**

Create `src/diplom_ai/clustering/internal_metrics.py`:

```python
from __future__ import annotations

from typing import Any

import numpy as np


def internal_cluster_metrics(
    embeddings: np.ndarray, labels: np.ndarray, *, noise_label: int = -1
) -> dict[str, Any]:
    """Силуэт и индекс Дэвиса–Боулдина считаются на не-шумовых точках;
    DBCV — на всех точках (учитывает шум по построению)."""
    from sklearn.metrics import davies_bouldin_score, silhouette_score  # type: ignore[import-untyped]

    mask = labels != noise_label
    result: dict[str, Any] = {"silhouette": None, "davies_bouldin": None, "dbcv": None}
    non_noise_labels = labels[mask]
    if len(set(non_noise_labels.tolist())) >= 2:
        result["silhouette"] = float(silhouette_score(embeddings[mask], non_noise_labels))
        result["davies_bouldin"] = float(
            davies_bouldin_score(embeddings[mask], non_noise_labels)
        )
    try:
        from hdbscan.validity import validity_index  # type: ignore[import-untyped]

        result["dbcv"] = float(
            validity_index(embeddings.astype(np.float64), labels.astype(np.intp))
        )
    except Exception:  # noqa: BLE001 — DBCV необязателен, метрика-ориентир
        result["dbcv"] = None
    return result
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `pytest tests/clustering/test_internal_metrics.py -v`
Expected: PASS.

- [ ] **Step 5: Подключить в pipeline**

В `src/diplom_ai/clustering/pipeline.py` в формирование `metrics` (где сейчас
`n_clusters`/`n_outliers`/...) добавить вызов `internal_cluster_metrics(...)` по
матрице эмбеддингов и массиву меток запуска и слить результат в `metrics`.

- [ ] **Step 6: Прогнать тесты пакета clustering**

Run: `pytest tests/clustering -v`
Expected: PASS (существующие тесты не сломаны).

- [ ] **Step 7: Commit**

```bash
git add src/diplom_ai/clustering/internal_metrics.py \
        src/diplom_ai/clustering/pipeline.py \
        tests/clustering/test_internal_metrics.py
git commit -m "clustering: внутренние метрики DBCV/силуэт/DBI и их сохранение"
```

## Task 2.5: Сохранение Optuna-артефакта (история, лучшие, важность)

**Files:**
- Modify: `src/diplom_ai/clustering/tuner.py`
- Test: `tests/clustering/test_optuna_artifact.py`

- [ ] **Step 1: Написать падающий тест**

Create `tests/clustering/test_optuna_artifact.py`:

```python
import optuna

from diplom_ai.clustering.tuner import study_artifact


def test_study_artifact_contains_history_and_best():
    study = optuna.create_study(direction="maximize")

    def objective(trial):
        x = trial.suggest_float("x", 0.0, 1.0)
        return -((x - 0.3) ** 2)

    study.optimize(objective, n_trials=8)
    artifact = study_artifact(study)
    assert len(artifact["history"]) == 8
    assert "best_params" in artifact and "x" in artifact["best_params"]
    assert "best_value" in artifact
    assert "importances" in artifact  # может быть пустым при одном параметре
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `pytest tests/clustering/test_optuna_artifact.py -v`
Expected: FAIL (`cannot import name 'study_artifact'`).

- [ ] **Step 3: Реализовать**

Добавить в `src/diplom_ai/clustering/tuner.py`:

```python
def study_artifact(study: "optuna.Study") -> dict[str, Any]:
    import optuna

    try:
        importances = optuna.importance.get_param_importances(study)
        importances = {k: float(v) for k, v in importances.items()}
    except Exception:  # noqa: BLE001 — важность недоступна при <2 параметрах/триалов
        importances = {}
    return {
        "history": [
            {"number": t.number, "value": t.value, "params": dict(t.params)}
            for t in study.trials
            if t.value is not None
        ],
        "best_params": dict(study.best_params),
        "best_value": float(study.best_value),
        "importances": importances,
    }
```

Импорт `Any` и `optuna` обеспечить в шапке модуля (optuna уже используется).
В функции тюнинга после оптимизации сохранять артефакт в JSON рядом с прочими
артефактами запуска (путь — по конфигу/`run_id`).

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `pytest tests/clustering/test_optuna_artifact.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/diplom_ai/clustering/tuner.py tests/clustering/test_optuna_artifact.py
git commit -m "clustering: сохранение Optuna-артефакта (история, лучшие, важность)"
```

## Task 2.6: Grouped-by-cluster split (gold-тест без утечки)

**Files:**
- Create: `src/diplom_ai/evaluation/splits.py`
- Test: `tests/evaluation/test_splits.py`

- [ ] **Step 1: Написать падающие тесты**

Create `tests/evaluation/test_splits.py`:

```python
from diplom_ai.evaluation.splits import grouped_train_test_split


def test_clusters_disjoint_between_train_and_test():
    items = list(range(20))
    cluster_ids = [i // 2 for i in items]  # 10 кластеров по 2 элемента
    train, test = grouped_train_test_split(
        items, cluster_ids, test_fraction=0.3, seed=42
    )
    train_clusters = {cluster_ids[i] for i in train}
    test_clusters = {cluster_ids[i] for i in test}
    assert train_clusters.isdisjoint(test_clusters)
    assert len(train) + len(test) == len(items)


def test_split_is_deterministic_with_seed():
    items = list(range(20))
    cluster_ids = [i // 2 for i in items]
    a = grouped_train_test_split(items, cluster_ids, test_fraction=0.3, seed=7)
    b = grouped_train_test_split(items, cluster_ids, test_fraction=0.3, seed=7)
    assert a == b
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `pytest tests/evaluation/test_splits.py -v`
Expected: FAIL (модуль не существует).

- [ ] **Step 3: Реализовать**

Create `src/diplom_ai/evaluation/splits.py`:

```python
from __future__ import annotations

import random
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def grouped_train_test_split(
    items: Sequence[T],
    cluster_ids: Sequence[int],
    *,
    test_fraction: float,
    seed: int,
) -> tuple[list[int], list[int]]:
    """Делит индексы items на train/test так, что один кластер целиком попадает
    либо в train, либо в test (исключает утечку от распространения меток)."""
    if len(items) != len(cluster_ids):
        raise ValueError("items and cluster_ids must be the same length")
    clusters = sorted(set(cluster_ids))
    random.Random(seed).shuffle(clusters)
    test_cluster_count = max(1, round(len(clusters) * test_fraction))
    test_clusters = set(clusters[:test_cluster_count])
    train_indices: list[int] = []
    test_indices: list[int] = []
    for index, cluster in enumerate(cluster_ids):
        (test_indices if cluster in test_clusters else train_indices).append(index)
    return train_indices, test_indices
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `pytest tests/evaluation/test_splits.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/diplom_ai/evaluation/splits.py tests/evaluation/test_splits.py
git commit -m "evaluation: grouped-by-cluster split для gold-теста"
```

## Task 2.7: Драйвер экспериментов `experiments_ch3.py`

**Files:**
- Create: `scripts/experiments_ch3.py`
- Test: `tests/scripts/test_experiments_ch3_cli.py`

- [ ] **Step 1: Написать smoke-тест CLI**

Create `tests/scripts/test_experiments_ch3_cli.py`:

```python
import subprocess
import sys


def test_experiments_ch3_help_runs():
    result = subprocess.run(
        [sys.executable, "scripts/experiments_ch3.py", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--out" in result.stdout
```

- [ ] **Step 2: Запустить — убедиться, что падает**

Run: `pytest tests/scripts/test_experiments_ch3_cli.py -v`
Expected: FAIL (скрипт не существует).

- [ ] **Step 3: Реализовать скелет драйвера**

Create `scripts/experiments_ch3.py`:

```python
"""Драйвер экспериментов главы 3: выгружает таблицы (CSV) и рисунки (PDF) для
кластеризации, подбора параметров, классификатора и развёртки по tau."""
from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Эксперименты главы 3")
    parser.add_argument("--out", type=Path, default=Path("artifacts/ch3"),
                        help="каталог для CSV/PDF артефактов")
    parser.add_argument("--mailbox-id", type=int, default=None,
                        help="идентификатор ящика; по умолчанию активный")
    parser.add_argument("--tau-grid", type=str, default="0.5,0.7,0.9",
                        help="сетка порогов уверенности через запятую")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    # TODO(Фаза 3): прогон на реальном ящике —
    #   1) кластеризация + internal_cluster_metrics -> cluster_metrics.csv
    #   2) study_artifact -> optuna.json + optuna_history.pdf
    #   3) grouped_train_test_split + обучение + per_class_metrics + confusion -> CSV/PDF
    #   4) threshold_sweep по --tau-grid -> tau_sweep.csv + tau_sweep.pdf
    print(f"experiments_ch3: артефакты будут записаны в {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Запустить — убедиться, что проходит**

Run: `pytest tests/scripts/test_experiments_ch3_cli.py -v`
Expected: PASS.

- [ ] **Step 5: Полный прогон тестов и линтеров**

Run: `pytest && ruff check . && mypy src`
Expected: всё зелёное (или согласованные исключения проекта).

- [ ] **Step 6: Commit**

```bash
git add scripts/experiments_ch3.py tests/scripts/test_experiments_ch3_cli.py
git commit -m "scripts: драйвер экспериментов главы 3 (скелет + CLI)"
```

---

# ФАЗА 3 — Интеграция (следующая итерация, на реальном ящике)

> Выполняется после прогона `scripts/experiments_ch3.py` на реальном ящике.

## Task 3.1: Подстановка реальных артефактов

**Files:**
- Modify: `Dissertation/part3.tex`; `Dissertation/images/*.pdf`; `listings/*.py`

- [ ] **Step 1: Перекопировать обновлённые модули в `listings/`**

`predict.py` и `metrics.py` после Фазы 2 изменились — повторить копирование
(Task 1.4 Step 1) и уточнить `linerange` листингов Л3.7 и связанных.

- [ ] **Step 2: Заменить рамки-заглушки на рисунки**

Положить `cluster_projection.pdf`, `optuna_history.pdf`, `confusion_matrix.pdf`,
`tau_sweep.pdf` в `Dissertation/images/`; заменить каждый `\phbox{...}` на
`\includegraphics[width=...]{Dissertation/images/<файл>.pdf}`.

- [ ] **Step 3: Заменить все `\ph{...}` реальными числами**

Run: `grep -n "\\\\ph{" Dissertation/part3.tex`
Заменить каждое значение из CSV-артефактов. Цель — ноль вхождений `\ph{`.

- [ ] **Step 4: Полная сборка**

Run: `make dissertation`
Expected: глава 3 без красных плейсхолдеров; рисунки и числа реальные.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "Глава 3: подстановка реальных результатов и рисунков"
```

---

## Зависимости и порядок

- **Фаза 1** исполняется первой и независима (даёт компилируемую главу с
  плейсхолдерами — немедленный результат).
- **Фаза 2** независима от Фазы 1 (другой репозиторий); может идти параллельно.
- **Фаза 3** зависит от Фаз 1 и 2 + реального прогона на ящике.

## Self-review (выполнено автором плана)

- **Покрытие спеки:** разделы 3.1–3.10 → Tasks 1.6–1.15; листинги Л3.1–Л3.7 →
  Tasks 1.6–1.13 + приложение Task 1.16; рисунки F3.1–F3.4 → `\phbox` в Tasks
  1.10/1.12/1.13; таблицы Т3.1–Т3.10 → соответствующие задачи; оценочный слой
  (решение 6) → Tasks 2.1–2.7; протокол gold-теста (решение 8) → Task 2.6;
  KMeans-протокол (решение 9) → проза Task 1.10; удаление критерия латентности
  (решение 10) → Task 1.5; макрос `\ph` (решение 7) → Task 1.1; делегирование
  нормализации (Low #1) → Task 1.8; Python ≥3.11 (Low #2) → Task 1.6;
  PyTorch-библиография → Task 1.2.
- **Типы/имена:** функции Фазы 2 (`coverage`, `other_rate`, `per_class_metrics`,
  `confusion_matrix_labeled`, `threshold_sweep`, `softmax`, `apply_threshold`,
  `predict_proba`, `predict_with_threshold`, `internal_cluster_metrics`,
  `study_artifact`, `grouped_train_test_split`) согласованы между тестами и
  реализацией.
- **Метки LaTeX:** `ch:ch3`, `sec:ch3/*`, `tab:ch3/*`, `fig:ch3/*`,
  `lst:ch3/*` — согласованы; внешние ссылки проверяются в Task 1.0.
