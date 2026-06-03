# Переработка главы 1 (математическое обоснование) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Перевести главу 1 диссертации из описательного обзора в главу с математическим обоснованием реально используемых методов и визуализацией кластеризации на синтетических данных, при нетто-сокращении объёма.

**Architecture:** Правится один файл `Dissertation/part1.tex`. Неиспользуемые семейства методов сворачиваются; для используемых (TF-IDF/косинус, контекстные эмбеддинги `bge-m3`, линейный+softmax классификатор, k-means/HDBSCAN/UMAP/DBCV) добавляются формулы с полной расшифровкой символов. Два новых рисунка генерируются matplotlib на синтетических данных и включаются как векторные PDF.

**Tech Stack:** LaTeX (XeLaTeX, шаблон Russian-LaTeX-Diplom), `make dissertation`; Python 3 + matplotlib/numpy/scipy/sklearn из `/home/dyingsleeper/PycharmProjects/diplom2.0/.venv`.

**Спецификация:** `docs/superpowers/specs/2026-06-02-chapter1-math-rework-design.md`.

**Сквозные требования (применять во всех задачах):**
- После каждой формулы — легенда «где …»: ни один символ не остаётся без расшифровки.
- Стиль .tex: UTF-8, LF, 4 пробела, без хвостовых пробелов, перевод строки в конце.
- Русский язык, кавычки «ёлочки», неразрывные пробелы `~` как в существующем тексте.
- Переиспользовать существующие ключи библиографии (новых не добавлять).
- Коммиты выполняются только с явного согласия автора (политика репозитория);
  в плане отмечены логические точки коммита.

---

## Базовые факты из кода `diplom2.0` (ground truth)

- Эмбеддинги: `BAAI/bge-m3`, многоязычная модель уровня предложения; косинус/евклид на нормированных.
- TF-IDF: только ключевые термины кластеров (`clustering/summaries.py`).
- Кластеризация: UMAP (вкл., cosine, n_components=15) → HDBSCAN (eom); k-means (8) — альтернатива.
- Подбор: Optuna+TPE; цель = DBCV + 0.1·persistence + 0.2·membership − 0.5·max(0, noise−0.35), ограничения: #кластеров∈[2,20], шум≤0.5, медианный размер≥5.
- Метрики кластеризации в коде: DBCV (`hdbscan.validity.validity_index`). Силуэт/DBI НЕ вычисляются.
- Классификатор (WIP): `nn.Embedding(vocab,128)`→mean-pool→`Linear`→логиты; инференс=`argmax` (порог τ/`other`/калибровка ещё не реализованы). Метрики: accuracy/macro-F1/weighted-F1.

---

## File Structure

- **Modify:** `Dissertation/part1.tex` — единственный правимый текстовый файл (главы 1).
- **Create:** `Dissertation/images/synthetic_plots.py` — генератор рисунков (воспроизводимость).
- **Create:** `Dissertation/images/hdbscan_mreach.pdf` — взаимная достижимость (артефакт генератора).
- **Create:** `Dissertation/images/dbcv_density_validity.pdf` — плотностная валидность DBCV (артефакт генератора).

Включение рисунков: `\includegraphics` (graphicspath уже содержит `Dissertation/images/`).

---

## Task 0: Базовая сборка и фиксация числа страниц

**Files:** нет правок; только измерение.

- [ ] **Step 1: Собрать текущую диссертацию (эталон до правок)**

Run:
```bash
cd /home/dyingsleeper/PycharmProjects/Russian-LaTeX-Diplom
make dissertation
```
Expected: сборка завершается, появляется `dissertation.pdf` в корне.

- [ ] **Step 2: Зафиксировать число страниц (базовая линия)**

Run:
```bash
pdfinfo dissertation.pdf | grep -i Pages || python3 -c "import sys;from pypdf import PdfReader;print('Pages:',len(PdfReader('dissertation.pdf').pages))"
```
Записать число `PAGES_BEFORE` (общее число страниц диссертации). Так как правим только главу 1, изменение общего числа страниц равно изменению объёма главы 1. Цель в конце: `PAGES_AFTER ≤ PAGES_BEFORE`.

- [ ] **Step 3: Зафиксировать число страниц именно главы 1 (точная проверка)**

Открыть `dissertation.pdf`, найти страницы от начала `\chapter{Анализ задачи…}` до начала главы 2; записать диапазон `CH1_PAGES_BEFORE`. (Можно по закладкам/оглавлению.)

---

## Task 1: Генератор синтетических рисунков (matplotlib → PDF)

**Files:**
- Create: `Dissertation/images/synthetic_plots.py`
- Create: `Dissertation/images/hdbscan_mreach.pdf`
- Create: `Dissertation/images/dbcv_density_validity.pdf`

- [ ] **Step 1: Написать скрипт-генератор**

Создать `Dissertation/images/synthetic_plots.py`:

```python
"""Synthetic-data figures for Chapter 1 (mutual reachability, DBCV density validity).

Run with the diplom2.0 venv:
    /home/dyingsleeper/PycharmProjects/diplom2.0/.venv/bin/python \
        Dissertation/images/synthetic_plots.py

Outputs (vector PDF, grayscale, print-friendly):
    Dissertation/images/hdbscan_mreach.pdf
    Dissertation/images/dbcv_density_validity.pdf
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial.distance import cdist

OUT = Path(__file__).resolve().parent
plt.rcParams.update({
    "font.size": 11,
    "font.family": "serif",
    "mathtext.fontset": "dejavuserif",
    "axes.linewidth": 0.8,
})
GREY = "0.45"
DARK = "0.10"


def core_distance(points: np.ndarray, m: int) -> np.ndarray:
    """Distance to the m-th nearest neighbour (1-indexed, excluding self)."""
    d = cdist(points, points)
    d.sort(axis=1)
    return d[:, m]  # column 0 is self (0.0)


def mutual_reachability(points: np.ndarray, m: int) -> np.ndarray:
    d = cdist(points, points)
    dc = core_distance(points, m)
    mreach = np.maximum(np.maximum(d, dc[:, None]), dc[None, :])
    np.fill_diagonal(mreach, 0.0)
    return mreach


def fig_mreach() -> None:
    rng = np.random.default_rng(7)
    dense = rng.normal(loc=[0.0, 0.0], scale=0.28, size=(9, 2))
    sparse = np.array([[2.4, 1.1]])  # isolated point => large core distance
    pts = np.vstack([dense, sparse])
    m = 3
    dc = core_distance(pts, m)

    a_idx = 0          # a point inside the dense group
    b_idx = len(pts) - 1  # the isolated point b
    a, b = pts[a_idx], pts[b_idx]
    d_ab = float(np.linalg.norm(a - b))
    dmreach = max(dc[a_idx], dc[b_idx], d_ab)

    fig, ax = plt.subplots(figsize=(5.4, 4.0))
    ax.scatter(pts[:, 0], pts[:, 1], s=26, c="white", edgecolors=DARK, zorder=3)
    for idx, lab in ((a_idx, "$a$"), (b_idx, "$b$")):
        ax.scatter(*pts[idx], s=46, c=DARK, zorder=4)
        ax.annotate(lab, pts[idx], textcoords="offset points",
                    xytext=(8, 6), fontsize=12)
    # core-distance circles around a and b (radius = distance to m-th neighbour)
    for idx in (a_idx, b_idx):
        ax.add_patch(Circle(pts[idx], dc[idx], fill=False, ls=":",
                            ec=GREY, lw=1.2, zorder=2))
    ax.annotate(r"$d_{\mathrm{core}}(a)$", a, textcoords="offset points",
                xytext=(-2, -dc[a_idx] * 42 - 6), ha="center", color=GREY)
    ax.annotate(r"$d_{\mathrm{core}}(b)$", b, textcoords="offset points",
                xytext=(dc[b_idx] * 30, 4), color=GREY)
    # base distance segment a-b
    ax.plot([a[0], b[0]], [a[1], b[1]], color=DARK, lw=1.4, zorder=2)
    mid = (a + b) / 2
    ax.annotate(r"$d(a,b)$", mid, textcoords="offset points",
                xytext=(0, 8), ha="center")
    ax.set_title(
        r"$d_{\mathrm{mreach}}(a,b)=\max\{d_{\mathrm{core}}(a),"
        r"d_{\mathrm{core}}(b),d(a,b)\}=" + f"{dmreach:.2f}$",
        fontsize=12)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "hdbscan_mreach.pdf")
    plt.close(fig)


def fig_dbcv() -> None:
    rng = np.random.default_rng(3)
    c1 = rng.normal(loc=[0.0, 0.0], scale=0.30, size=(14, 2))
    c2 = rng.normal(loc=[2.6, 0.3], scale=0.30, size=(14, 2))
    pts = np.vstack([c1, c2])
    labels = np.array([0] * len(c1) + [1] * len(c2))
    m = 3
    mreach = mutual_reachability(pts, m)

    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    markers = {0: "o", 1: "s"}
    for lab in (0, 1):
        mask = labels == lab
        ax.scatter(pts[mask, 0], pts[mask, 1], s=26, c="white",
                   edgecolors=DARK, marker=markers[lab], zorder=3)

    # DSC: longest edge of each cluster's internal MST (in mutual reachability)
    dsc_edges = []
    for lab in (0, 1):
        idx = np.where(labels == lab)[0]
        sub = mreach[np.ix_(idx, idx)]
        mst = minimum_spanning_tree(sub).toarray()
        for i in range(len(idx)):
            for j in range(len(idx)):
                if mst[i, j] > 0:
                    ax.plot(pts[[idx[i], idx[j]], 0], pts[[idx[i], idx[j]], 1],
                            color=GREY, lw=0.8, zorder=1)
        fi, fj = np.unravel_index(np.argmax(mst), mst.shape)
        dsc_edges.append((idx[fi], idx[fj], mst[fi, fj]))
    # highlight the larger DSC (density sparseness) edge
    dsc = max(dsc_edges, key=lambda e: e[2])
    ax.plot(pts[[dsc[0], dsc[1]], 0], pts[[dsc[0], dsc[1]], 1],
            color=DARK, lw=2.4, zorder=2)
    ax.annotate("DSC", (pts[dsc[0]] + pts[dsc[1]]) / 2,
                textcoords="offset points", xytext=(0, 8), ha="center")

    # DSPC: minimum mutual-reachability edge between the two clusters
    cross = mreach[np.ix_(np.where(labels == 0)[0], np.where(labels == 1)[0])]
    ci, cj = np.unravel_index(np.argmin(cross), cross.shape)
    p0 = pts[np.where(labels == 0)[0][ci]]
    p1 = pts[np.where(labels == 1)[0][cj]]
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=DARK, lw=2.0, ls="--", zorder=2)
    ax.annotate("DSPC", (p0 + p1) / 2, textcoords="offset points",
                xytext=(0, -14), ha="center")

    ax.set_title(r"$V(C_i)=\dfrac{\mathrm{DSPC}-\mathrm{DSC}}"
                 r"{\max\{\mathrm{DSPC},\mathrm{DSC}\}}$", fontsize=12)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "dbcv_density_validity.pdf")
    plt.close(fig)


if __name__ == "__main__":
    fig_mreach()
    fig_dbcv()
    print("wrote", OUT / "hdbscan_mreach.pdf")
    print("wrote", OUT / "dbcv_density_validity.pdf")
```

- [ ] **Step 2: Запустить генератор**

Run:
```bash
cd /home/dyingsleeper/PycharmProjects/Russian-LaTeX-Diplom
/home/dyingsleeper/PycharmProjects/diplom2.0/.venv/bin/python Dissertation/images/synthetic_plots.py
```
Expected: печатает два `wrote …`; созданы `hdbscan_mreach.pdf` и `dbcv_density_validity.pdf`.

- [ ] **Step 3: Проверить, что PDF валидны и не пустые**

Run:
```bash
ls -l Dissertation/images/hdbscan_mreach.pdf Dissertation/images/dbcv_density_validity.pdf
pdfinfo Dissertation/images/hdbscan_mreach.pdf | grep -i "Page size"
```
Expected: оба файла существуют, размер > 3 КБ, корректный page size.

- [ ] **Step 4: Визуально просмотреть рисунки**

Открыть оба PDF (Read tool на PDF или просмотрщик). Убедиться: точки, окружности core-distance и ребро d_mreach видны (рис. 1); MST, выделенные DSC и DSPC видны (рис. 2). Если подписи налезают — поправить смещения `xytext` и перезапустить.

- [ ] **Step 5 (commit point):** при согласии автора — `git add Dissertation/images/synthetic_plots.py Dissertation/images/hdbscan_mreach.pdf Dissertation/images/dbcv_density_validity.pdf`.

---

## Task 2: §1.3 — представление текста (математика + свёртка статичных)

**Files:** Modify `Dissertation/part1.tex` (раздел `sec:ch1/repr`, строки ~236–306).

- [ ] **Step 1: §1.3.1 Счётные — добавить TF-IDF и косинус**

Заменить тело подпункта `subsec:ch1/repr/count` так, чтобы после описательного абзаца шли формулы. Вставить:

```latex
Формально терму \( t \) в~сообщении \( x \) сопоставляется вес
\begin{equation}
    \label{eq:tfidf}
    w_{t,x} = \mathrm{tf}(t, x)\cdot \log\frac{N}{n_t},
\end{equation}
где \( w_{t,x} \) "--- вес терма \( t \) в~сообщении \( x \); \( \mathrm{tf}(t,x) \) "---
частота терма \( t \) в~\( x \); \( N \) "--- число сообщений в~корпусе;
\( n_t \) "--- число сообщений, содержащих \( t \). Сообщение представляется
разреженным вектором \( \varphi_{\text{tfidf}}(x) \in \mathbb{R}^{|V|} \), где
\( V \) "--- словарь корпуса. Близость двух представлений измеряется косинусной мерой
\begin{equation}
    \label{eq:cosine}
    \cos\bigl(\varphi(x), \varphi(x')\bigr) =
    \frac{\langle \varphi(x), \varphi(x') \rangle}{\lVert \varphi(x) \rVert \, \lVert \varphi(x') \rVert},
\end{equation}
где \( \langle \cdot, \cdot \rangle \) "--- скалярное произведение, а~\( \lVert \cdot \rVert \) "---
евклидова норма; для единично нормированных векторов косинус совпадает со~скалярным
произведением и~монотонно связан с~евклидовым расстоянием.
```
Сохранить ключи `Manning2008IR`, `Salton1988TFIDF`. Описательный текст про ограничения TF-IDF сжать до 1–2 строк.

- [ ] **Step 2: §1.3.2 Статичные — свернуть до 2–3 строк**

Тело `subsec:ch1/repr/static` заменить кратким абзацем (методы не используются):

```latex
Статичные дистрибутивные эмбеддинги "--- word2vec~\autocite{Mikolov2013word2vec},
GloVe~\autocite{Pennington2014GloVe}, fastText~\autocite{Bojanowski2017fastText}
(для русского "--- RusVectores~\autocite{Kutuzov2017RusVectores}) "--- фиксируют
дистрибутивную семантику отдельных слов, но~отображают слово в~единственный вектор
вне контекста. В~настоящей работе они не~используются и~приводятся как~историческая
ступень между счётными и~контекстными представлениями.
```

- [ ] **Step 3: §1.3.3 Контекстные — добавить математику предложенческого вектора**

В конце `subsec:ch1/repr/context` добавить формулу пулинга и нормировки:

```latex
Контекстный энкодер отображает сообщение в~единый вектор усреднением представлений
токенов с~последующей единичной нормировкой:
\begin{equation}
    \label{eq:sentence-embedding}
    \varphi(x) = \frac{1}{\lvert T(x) \rvert} \sum_{t \in T(x)} \mathbf{e}_t,
    \qquad \widehat{\varphi}(x) = \frac{\varphi(x)}{\lVert \varphi(x) \rVert},
\end{equation}
где \( T(x) \) "--- множество (непустых) позиций токенов сообщения \( x \);
\( \lvert T(x) \rvert \) "--- их число; \( \mathbf{e}_t \in \mathbb{R}^{d} \) "---
контекстный вектор токена \( t \), выдаваемый трансформерным энкодером;
\( \widehat{\varphi}(x) \) "--- нормированное представление, для которого косинусная
близость~\eqref{eq:cosine} сводится к~скалярному произведению. Именно такое
многоязычное представление уровня предложения используется в~работе для~кластеризации
исторической выборки.
```
Оставить ключи `Devlin2019BERT`, `Conneau2020XLMR`, `Reimers2019SBERT`, `Reimers2020MultilingualSBERT`, `Feng2022LaBSE`. Описательную часть сократить.

- [ ] **Step 4: §1.3.4 Типология — сократить текст, рисунок оставить.**

Убрать дублирующие формулировки, оставить 2–3 строки вывода и `figure` с `embedding_taxonomy.tikz`.

- [ ] **Step 5: Сборка-проверка**

Run:
```bash
make dissertation-draft
```
Expected: компиляция без ошибок; в `.log` нет `Undefined control sequence`, нет нерешённых ссылок на новые `eq:tfidf/eq:cosine/eq:sentence-embedding`.

- [ ] **Step 6 (commit point):** при согласии автора закоммитить §1.3.

---

## Task 3: §1.4 — классификация (свёртка трёх семейств + абстрактный WIP-классификатор)

**Files:** Modify `Dissertation/part1.tex` (раздел `sec:ch1/clf`, строки ~308–373).

- [ ] **Step 1: Свернуть §1.4.1–1.4.3 в один абзац «Базовые семейства»**

Удалить подпункты `subsec:ch1/clf/linear`, `subsec:ch1/clf/online`, `subsec:ch1/clf/trees` и заменить одним подпунктом:

```latex
\subsection{Базовые семейства}\label{subsec:ch1/clf/baselines}

В~качестве контрольных моделей рассматриваются классические семейства, не~выбранные
как~целевое решение. Вероятностные и~линейные модели поверх
TF-IDF "--- мультиномиальный наивный Байес~\autocite{McCallum1998NaiveBayes}, линейные
SVM и~логистическая регрессия~\autocite{Joachims1998SVMTextCat,Fan2008LIBLINEAR,Pedregosa2011sklearn} "---
дёшевы и~устойчивы при~ограниченной разметке, но~не~дают калиброванной вероятности.
Онлайн-классификаторы "--- Passive-Aggressive~\autocite{Crammer2006PA} и~Confidence-Weighted~\autocite{Dredze2008CW},
применённые в~TaskTracer~\autocite{Keiser2009TaskTracer} "--- инкрементно обновляются
при~дрейфе, но~их уверенность относительна (margin), а~не~вероятность. Ансамбли деревьев "---
Random Forest~\autocite{Breiman2001RF}, XGBoost~\autocite{Chen2016XGBoost},
LightGBM~\autocite{Ke2017LightGBM} "--- сильны на~плотных признаках невысокой
размерности, но~проигрывают на~разреженных TF-IDF-векторах. Эти семейства служат
ориентиром сравнения, тогда как~целевая архитектура строится поверх многоязычных
эмбеддингов (раздел~\ref{subsec:ch1/repr/context}).
```

- [ ] **Step 2: §1.4.2 Нейроклассификатор — пометить WIP и дать абстрактную математику**

Заменить тело `subsec:ch1/clf/neural` (переименовать метку оставить прежней для совместимости ссылок, либо обновить — проверить, что на неё нет внешних ссылок) на:

```latex
\subsection{Нейронный классификатор поверх эмбеддингов}\label{subsec:ch1/clf/neural}

\footnote{Компонент классификатора находится в~активной доработке; ниже приводится
его математическая постановка в~текущем, обобщённом виде.}%
Целевая архитектура "--- линейный классификатор поверх векторного представления
\( h = \varphi(x) \in \mathbb{R}^{d} \). Логиты и~апостериорные оценки классов
вычисляются как
\begin{align}
    z(x) &= W h(x) + b, \qquad W \in \mathbb{R}^{K \times d},\ b \in \mathbb{R}^{K}, \label{eq:logits} \\
    p_k(x) &= \frac{\exp\bigl(z_k(x)\bigr)}{\sum_{j=1}^{K} \exp\bigl(z_j(x)\bigr)}, \qquad k = 1, \dots, K, \label{eq:softmax}
\end{align}
где \( h(x) \) "--- представление сообщения \( x \) размерности \( d \);
\( W \) и~\( b \) "--- матрица весов и~вектор смещений линейного слоя; \( K \) "---
число пользовательских классов; \( z_k(x) \) "--- \( k \)-й логит; \( p_k(x) \in (0,1) \) "---
апостериорная оценка класса \( k \), \( \sum_k p_k(x) = 1 \). Параметры
\( \theta = \{W, b, \dots\} \) настраиваются минимизацией эмпирического
кросс-энтропийного риска
\begin{equation}
    \label{eq:cross-entropy}
    \mathcal{L}(\theta) = -\frac{1}{N} \sum_{i=1}^{N} \sum_{k=1}^{K}
        \mathbb{1}\bigl[\,y_i = k\,\bigr] \log p_k(x_i),
\end{equation}
где \( N \) "--- размер обучающей выборки; \( (x_i, y_i) \) "--- размеченные пары;
\( \mathbb{1}[\cdot] \) "--- индикатор. Оценки \( p_k(x) \) подаются в~решающее
правило с~порогом~\( \tau \) \eqref{eq:decision-rule}: при~\( \max_k p_k(x) < \tau \)
сообщение получает исход \texttt{other}. Калибровка вероятностей (temperature/Platt
scaling~\autocite{Guo2017Calibration}) и~softmax-эвристика выделения
out-of-distribution~\autocite{Hendrycks2017Baseline}, согласующие уровень уверенности
с~порогом, относятся к~направлению дальнейшей доработки компонента.
```
Удалить завершающий `\medskip`-абзац-резюме раздела или сократить его до 2 строк.

- [ ] **Step 3: Проверить ссылки на удалённые метки**

Run:
```bash
grep -rn "ch1/clf/linear\|ch1/clf/online\|ch1/clf/trees" Dissertation/ Synopsis/ common/
```
Expected: пусто (на эти метки нигде не ссылаются). Если есть ссылки — обновить на `subsec:ch1/clf/baselines`.

- [ ] **Step 4: Сборка-проверка**

Run: `make dissertation-draft`
Expected: без ошибок; новые метки `eq:logits/eq:softmax/eq:cross-entropy` разрешаются; сноска WIP отображается.

- [ ] **Step 5 (commit point):** при согласии автора закоммитить §1.4.

---

## Task 4: §1.5 — кластеризация (математика + два рисунка)

**Files:** Modify `Dissertation/part1.tex` (раздел `sec:ch1/cluster`, строки ~375–449).

- [ ] **Step 1: §1.5.1 Партиционные — добавить целевую функцию k-means**

В `subsec:ch1/cluster/partition` добавить:

```latex
Алгоритм минимизирует суммарную внутрикластерную дисперсию
\begin{equation}
    \label{eq:kmeans}
    \min_{\{C_1, \dots, C_k\}} \sum_{j=1}^{k} \sum_{x \in C_j}
        \bigl\lVert \varphi(x) - \mu_j \bigr\rVert^2,
    \qquad \mu_j = \frac{1}{\lvert C_j \rvert} \sum_{x \in C_j} \varphi(x),
\end{equation}
где \( C_j \) "--- \( j \)-й кластер (подмножество сообщений); \( \mu_j \) "--- его
центроид; \( k \) "--- фиксированное число кластеров; \( \lvert C_j \rvert \) "---
размер кластера; \( \lVert \cdot \rVert \) "--- евклидова норма. Фиксированность~\( k \)
и~приписывание каждой точки к~ближайшему центру (без~выделения шума) ограничивают
применимость метода в~постановке настоящей работы.
```

- [ ] **Step 2: §1.5.2 Плотностные — DBSCAN/HDBSCAN core+mreach+стабильность + рисунок**

В `subsec:ch1/cluster/density` добавить определения и формулу:

```latex
DBSCAN~\autocite{Ester1996DBSCAN} задаёт ядровую точку условием
\( \lvert N_\varepsilon(x) \rvert \geqslant \mathit{minPts} \), где
\( N_\varepsilon(x) \) "--- множество точек в~радиусе~\( \varepsilon \) от~\( x \),
\( \mathit{minPts} \) "--- минимальное число соседей; не~прошедшие порог точки
помечаются как~шум. HDBSCAN~\autocite{Campello2013HDBSCAN,McInnes2017HDBSCAN}
устраняет зависимость от~единого~\( \varepsilon \), вводя ядровое расстояние
\( d_{\mathrm{core}}(x) \) "--- расстояние от~\( x \) до~его \( m \)-го ближайшего
соседа (\( m = \mathit{min\_samples} \)) "--- и~взаимную достижимость
\begin{equation}
    \label{eq:mreach}
    d_{\mathrm{mreach}}(a, b) = \max\bigl\{ d_{\mathrm{core}}(a),\,
        d_{\mathrm{core}}(b),\, d(a, b) \bigr\},
\end{equation}
где \( d(a,b) \) "--- базовое (евклидово) расстояние между точками \( a \) и~\( b \).
Кластеры строятся как~устойчивые поддеревья минимального остова в~метрике
\( d_{\mathrm{mreach}} \); устойчивость (persistence) кластера~\( C \) измеряется как
\begin{equation}
    \label{eq:stability}
    S(C) = \sum_{x \in C} \bigl( \lambda_{\max}(x, C) - \lambda_{\mathrm{birth}}(C) \bigr),
    \qquad \lambda = \frac{1}{d_{\mathrm{mreach}}},
\end{equation}
где \( \lambda \) "--- уровень плотности (обратное расстояние);
\( \lambda_{\mathrm{birth}}(C) \) "--- уровень появления кластера;
\( \lambda_{\max}(x, C) \) "--- уровень, на~котором точка \( x \) покидает \( C \);
\( S(C) \) "--- суммарная устойчивость (чем больше, тем стабильнее кластер).
Геометрия взаимной достижимости показана на~рисунке~\ref{fig:hdbscan-mreach}.
```

Добавить рисунок:
```latex
\begin{figure}[h]
    \centering
    \includegraphics[width=0.72\textwidth]{hdbscan_mreach}
    \caption{Взаимная достижимость HDBSCAN на~синтетических точках: вокруг
        \( a \) и~\( b \) показаны окружности ядрового расстояния \( d_{\mathrm{core}} \)
        (радиус "--- до~\( m \)-го соседа); для разреженной точки~\( b \) ядровое
        расстояние велико, поэтому \( d_{\mathrm{mreach}}(a,b) \) определяется им,
        а~не~прямым расстоянием \( d(a,b) \)}\label{fig:hdbscan-mreach}
\end{figure}
```

- [ ] **Step 3: §1.5.3 Снижение размерности — UMAP оставить, LDA убрать**

Тело `subsec:ch1/cluster/dimred` переписать без LDA:

```latex
Контекстные эмбеддинги размещают сообщения в~пространстве сотен измерений, где
плотностные алгоритмы теряют устойчивость. Поэтому перед HDBSCAN применяется
нелинейное снижение размерности UMAP~\autocite{McInnes2018UMAP}: метод строит
взвешенный граф \( k \)-ближайших соседей в~исходном пространстве и~ищет
низкоразмерное вложение, сохраняющее его локальную структуру. В~настоящей работе
UMAP включён как~подготовительный шаг кластеризации, после которого HDBSCAN
работает в~пространстве небольшой размерности.
```
(Ключ `Blei2003LDA` удаляется из главы — проверить, что он не нужен в других местах главы 1.)

- [ ] **Step 4: §1.5.4 Метрики — DBCV/стабильность на первый план + рисунок; силуэт/DBI как ориентир**

Тело `subsec:ch1/cluster/metrics` заменить на:

```latex
Основной внутренней мерой качества в~работе служит плотностной индекс валидности
DBCV~\autocite{Moulavi2014DBCV}, согласованный с~метрикой взаимной достижимости
HDBSCAN. Для кластера~\( C_i \) вводятся внутрикластерная разреженность
\( \mathrm{DSC}(C_i) \) "--- наибольшее ребро минимального остова \( C_i \)
в~метрике \( d_{\mathrm{mreach}} \) "--- и~межкластерная разделимость
\( \mathrm{DSPC}(C_i, C_j) \) "--- наименьшая взаимная достижимость между точками
\( C_i \) и~\( C_j \); валидность кластера
\begin{equation}
    \label{eq:dbcv-cluster}
    V(C_i) = \frac{\min_{j \neq i} \mathrm{DSPC}(C_i, C_j) - \mathrm{DSC}(C_i)}
        {\max\bigl\{ \min_{j \neq i} \mathrm{DSPC}(C_i, C_j),\ \mathrm{DSC}(C_i) \bigr\}},
\end{equation}
а~итоговый индекс "--- средневзвешенное по~размерам кластеров
\begin{equation}
    \label{eq:dbcv}
    \mathrm{DBCV} = \sum_{i} \frac{\lvert C_i \rvert}{N}\, V(C_i) \in [-1, 1],
\end{equation}
где \( \mathrm{DSC} \) "--- плотностная разреженность (внутри кластера);
\( \mathrm{DSPC} \) "--- плотностная разделимость (между кластерами);
\( \lvert C_i \rvert \) "--- размер кластера~\( C_i \); \( N \) "--- общее число
точек; большие значения \( \mathrm{DBCV} \) отвечают плотным и~хорошо разделённым
кластерам (рисунок~\ref{fig:dbcv-validity}). При~автоматическом подборе параметров
HDBSCAN целевая функция объединяет DBCV с~устойчивостью~\eqref{eq:stability}
и~средней уверенностью принадлежности при~штрафе за~долю шума, а~поиск ведётся
в~области допустимых решений (число кластеров, доля шума, медианный размер).
Классические индексы "--- коэффициент силуэта~\autocite{Rousseeuw1987Silhouette}
и~индекс Дэвиса-Боулдина~\autocite{Davies1979DBI} "--- предполагают выпуклые
кластеры и~используются лишь как~вспомогательный ориентир. Окончательное решение
о~принятии кластеров требует ручной проверки кандидатов.
```

Добавить рисунок:
```latex
\begin{figure}[h]
    \centering
    \includegraphics[width=0.72\textwidth]{dbcv_density_validity}
    \caption{Плотностная валидность DBCV на~синтетических данных: рёбра показывают
        минимальные остовы кластеров в~метрике взаимной достижимости; выделены
        внутрикластерная разреженность \( \mathrm{DSC} \) (наибольшее внутреннее
        ребро) и~межкластерная разделимость \( \mathrm{DSPC} \) (наименьшее ребро
        между кластерами), из~которых складывается индекс}\label{fig:dbcv-validity}
\end{figure}
```

- [ ] **Step 5: Согласовать существующий рисунок `clustering_outliers` и итоговый абзац**

Оставить рисунок `fig:clustering-outliers` и завершающий абзац раздела; убедиться, что метки и ссылки (`Akiba2019Optuna` упоминается в §1.5.4 опционально) корректны. Убрать дублирование с новым текстом.

- [ ] **Step 6: Сборка-проверка**

Run: `make dissertation`
Expected: без ошибок; рисунки `hdbscan_mreach`, `dbcv_density_validity` вставлены и видны; все `eq:kmeans/eq:mreach/eq:stability/eq:dbcv-cluster/eq:dbcv` и `\ref` на рисунки разрешаются.

- [ ] **Step 7 (commit point):** при согласии автора закоммитить §1.5 + рисунки.

---

## Task 5: §1.6 — свёртка описаний систем вокруг таблицы

**Files:** Modify `Dissertation/part1.tex` (раздел `sec:ch1/systems`, строки ~451–554).

- [ ] **Step 1: Свернуть 4 подпункта в компактный текст**

Удалить подпункты `subsec:ch1/systems/outlook`, `…/gmail`, `…/tasktracer`, `…/emfore` (их описательные абзацы) и заменить одним вводным абзацем перед таблицей, сохранив таблицу `tab:systems-compare` и итоговый абзац после неё:

```latex
Рассматриваются четыре характерные системы организации входящей корреспонденции.
Focused~Inbox (Outlook)~\autocite{Microsoft2024FocusedInbox} и~Priority~Inbox
(Gmail)~\autocite{Aberdeen2010PriorityInbox} персонализируют важность письма, но~сводят
результат к~бинарной шкале «важное/прочее», исполняются на~серверах сервиса
и~не~допускают произвольных тематических классов. TaskTracer~\autocite{Keiser2009TaskTracer}
предсказывает проектную принадлежность письма онлайн-классификаторами и~приближается
к~многоклассовой постановке~\eqref{eq:classifier}, но~работает только с~англоязычной
перепиской и~без~категории \texttt{other}. EmFORE~\autocite{Singh2023EmFORE} индуктивно
выводит символьные правила распределения по~папкам с~явной адаптацией к~дрейфу
признаков, опираясь на~структурные признаки, но~без~кластеризации для формирования
классов и~без~активного буфера \texttt{other}. Сопоставление по~осям, существенным
для настоящей работы, приведено в~таблице~\ref{tab:systems-compare}.
```
Подпункт `subsec:ch1/systems/summary` (вокруг таблицы) сохранить; убрать ссылки на удалённые метки подпунктов, если они есть.

- [ ] **Step 2: Проверить ссылки на удалённые метки**

Run:
```bash
grep -rn "ch1/systems/outlook\|ch1/systems/gmail\|ch1/systems/tasktracer\|ch1/systems/emfore" Dissertation/ Synopsis/ common/
```
Expected: пусто. Иначе обновить ссылки.

- [ ] **Step 3: Сборка-проверка**

Run: `make dissertation-draft`
Expected: без ошибок; таблица на месте; ссылки разрешаются.

- [ ] **Step 4 (commit point):** при согласии автора закоммитить §1.6.

---

## Task 6: Итоговая верификация и сравнение объёма

**Files:** нет правок; проверка.

- [ ] **Step 1: Полная сборка**

Run: `make dissertation`
Expected: успешная сборка `dissertation.pdf`, без новых warning по ссылкам/цитатам (проверить `grep -i "undefined\|rerun\|warning: citation" Dissertation/part1.log`).

- [ ] **Step 2: Сравнить число страниц**

Run:
```bash
pdfinfo dissertation.pdf | grep -i Pages
```
Сравнить `PAGES_AFTER` с `PAGES_BEFORE` из Task 0. Критерий: `PAGES_AFTER ≤ PAGES_BEFORE` (нетто-сокращение). Также сверить диапазон страниц главы 1 (`CH1_PAGES_AFTER ≤ CH1_PAGES_BEFORE`).

- [ ] **Step 3: Проверить расшифровку всех символов**

Просмотреть итоговый `part1.tex`: каждая формула (`eq:tfidf, eq:cosine, eq:sentence-embedding, eq:logits, eq:softmax, eq:cross-entropy, eq:kmeans, eq:mreach, eq:stability, eq:dbcv-cluster, eq:dbcv`) сопровождается легендой «где …», в которой определён каждый символ. Зафиксировать в отчёте.

- [ ] **Step 4: Проверить отметку WIP §1.4.2 и визуальную корректность рисунков** в собранном PDF.

- [ ] **Step 5: Отчёт автору**

Сообщить: число страниц до/после, перечень свёрнутых подпунктов, перечень добавленных формул и двух рисунков, оставшиеся открытые вопросы (если есть).

- [ ] **Step 6 (commit point):** при согласии автора — финальный коммит / либо единый коммит всех изменений главы 1.

---

## Self-Review (выполнено при написании плана)

**Spec coverage:** все пункты спецификации покрыты — §1.3 (Task 2), §1.4 свёртка+WIP (Task 3), §1.5 математика+2 рисунка (Task 4), §1.6 свёртка (Task 5), генерация рисунков (Task 1), нетто-сокращение и проверка (Task 0/6), расшифровка символов (сквозное + Task 6 Step 3), классификатор абстрактный+WIP (Task 3 Step 2).

**Placeholder scan:** в шагах приведён реальный LaTeX/Python-код и точные команды; «TODO/TBD» отсутствуют.

**Type/label consistency:** метки уравнений и рисунков уникальны и согласованы между задачами (`fig:hdbscan-mreach`, `fig:dbcv-validity`, `eq:mreach`↔`eq:stability`↔`eq:dbcv-*`; ссылка на `eq:decision-rule`/`eq:classifier` — существующие). Удаляемые метки подпунктов проверяются grep-шагами (Task 3 Step 3, Task 5 Step 2).
