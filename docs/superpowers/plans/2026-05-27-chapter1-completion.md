# Дописывание главы 1 диссертации — план

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** добавить в `Dissertation/part1.tex` секции §1.3–§1.7 (представление текста, классификация, кластеризация, сравнение систем, постановка задачи разработки) в соответствии со спецификацией `docs/superpowers/specs/2026-05-27-chapter1-completion-design.md`.

**Architecture:** содержание добавляется поэтапно по секциям. Каждая секция: (1) расширение `biblio/external.bib` нужными записями, (2) при необходимости — новый TikZ-файл, (3) вставка LaTeX-текста секции, (4) `make dissertation` без `LaTeX Warning: Citation ... undefined` и `Reference ... undefined`, (5) коммит. После последней секции — удаление TODO-маркеров и финальная сборка.

**Tech Stack:** XeLaTeX + biber (по умолчанию), `biblatex-gost`, TikZ. Сборка через `make dissertation` из корня репозитория. Стиль и оформление — по образцу уже написанных §1.1–§1.2.

---

## Сквозные соглашения

Все вставляемые фрагменты соблюдают стиль §1.1–§1.2:

- кавычки «», тире `"---`;
- неразрывный пробел `~` в типичных конструкциях;
- ссылки только через `\autocite{...}`, `\ref{...}`, `\eqref{...}`;
- 4-пробельный отступ, LF, UTF-8, итоговая пустая строка — по `.editorconfig`.

В каждой секции §1.3–§1.5 — завершающий абзац, увязывающий изложенное с четырьмя свойствами задачи из §1.1. В §1.3, §1.4 и §1.7 — явная отсылка к главе 2 через `\ref{ch:ch2}`.

После каждой задачи запускается:

```bash
make dissertation
```

и в `dissertation.log` проверяется отсутствие новых строк `LaTeX Warning: Citation '...' on page ... undefined` и `LaTeX Warning: Reference '...' on page ... undefined`. PDF просматривается на корректность списков рисунков/таблиц и нумерацию.

---

## Task 1: расширение biblio для §1.3

**Files:**
- Modify: `biblio/external.bib` (добавление в конец файла)

- [ ] **Step 1: добавить блок-разделитель и 10 записей источников §1.3**

В конец `biblio/external.bib` вставить:

```bibtex

%%% Источники главы 1, §1.3 «Методы представления текста»

@ARTICLE{Salton1988TFIDF,
  author =  {Salton, Gerard and Buckley, Christopher},
  title =   {Term-weighting approaches in automatic text retrieval},
  journal = {Information Processing \& Management},
  volume =  {24},
  number =  {5},
  pages =   {513--523},
  year =    {1988},
  doi =     {10.1016/0306-4573(88)90021-0},
  language = {english},
}

@MISC{Mikolov2013word2vec,
  author =       {Mikolov, Tomas and Chen, Kai and Corrado, Greg and Dean, Jeffrey},
  title =        {Efficient Estimation of Word Representations in Vector Space},
  howpublished = {arXiv preprint arXiv:1301.3781},
  year =         {2013},
  url =          {https://arxiv.org/abs/1301.3781},
  language =     {english},
}

@InProceedings{Pennington2014GloVe,
  author =    {Pennington, Jeffrey and Socher, Richard and Manning, Christopher D.},
  title =     {{GloVe}: {Global} Vectors for Word Representation},
  booktitle = {Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  pages =     {1532--1543},
  year =      {2014},
  doi =       {10.3115/v1/D14-1162},
  publisher = {Association for Computational Linguistics},
  language =  {english},
}

@ARTICLE{Bojanowski2017fastText,
  author =  {Bojanowski, Piotr and Grave, Edouard and Joulin, Armand and Mikolov, Tomas},
  title =   {Enriching Word Vectors with Subword Information},
  journal = {Transactions of the Association for Computational Linguistics},
  volume =  {5},
  pages =   {135--146},
  year =    {2017},
  doi =     {10.1162/tacl_a_00051},
  language = {english},
}

@InProceedings{Devlin2019BERT,
  author =    {Devlin, Jacob and Chang, Ming-Wei and Lee, Kenton and Toutanova, Kristina},
  title =     {{BERT}: Pre-training of Deep Bidirectional Transformers for Language Understanding},
  booktitle = {Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT)},
  pages =     {4171--4186},
  year =      {2019},
  doi =       {10.18653/v1/N19-1423},
  publisher = {Association for Computational Linguistics},
  language =  {english},
}

@InProceedings{Conneau2020XLMR,
  author =    {Conneau, Alexis and Khandelwal, Kartikay and Goyal, Naman and Chaudhary, Vishrav and Wenzek, Guillaume and Guzm{\'a}n, Francisco and Grave, Edouard and Ott, Myle and Zettlemoyer, Luke and Stoyanov, Veselin},
  title =     {Unsupervised Cross-lingual Representation Learning at Scale},
  booktitle = {Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL)},
  pages =     {8440--8451},
  year =      {2020},
  doi =       {10.18653/v1/2020.acl-main.747},
  publisher = {Association for Computational Linguistics},
  language =  {english},
  options =   {maxnames=4},
}

@InProceedings{Reimers2019SBERT,
  author =    {Reimers, Nils and Gurevych, Iryna},
  title =     {Sentence-{BERT}: Sentence Embeddings using {Siamese BERT}-Networks},
  booktitle = {Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP-IJCNLP)},
  pages =     {3982--3992},
  year =      {2019},
  doi =       {10.18653/v1/D19-1410},
  publisher = {Association for Computational Linguistics},
  language =  {english},
}

@InProceedings{Reimers2020MultilingualSBERT,
  author =    {Reimers, Nils and Gurevych, Iryna},
  title =     {Making Monolingual Sentence Embeddings Multilingual using Knowledge Distillation},
  booktitle = {Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  pages =     {4512--4525},
  year =      {2020},
  doi =       {10.18653/v1/2020.emnlp-main.365},
  publisher = {Association for Computational Linguistics},
  language =  {english},
}

@InProceedings{Feng2022LaBSE,
  author =    {Feng, Fangxiaoyu and Yang, Yinfei and Cer, Daniel and Arivazhagan, Naveen and Wang, Wei},
  title =     {Language-agnostic {BERT} Sentence Embedding},
  booktitle = {Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (ACL)},
  pages =     {878--891},
  year =      {2022},
  doi =       {10.18653/v1/2022.acl-long.62},
  publisher = {Association for Computational Linguistics},
  language =  {english},
}

@InProceedings{Kutuzov2017RusVectores,
  author =    {Kutuzov, Andrey and Kuzmenko, Elizaveta},
  title =     {{WebVectores}: A Toolkit for Building Web Interfaces for Vector Semantic Models},
  booktitle = {Analysis of Images, Social Networks and Texts (AINL 2016)},
  series =    {Communications in Computer and Information Science},
  volume =    {661},
  pages =     {155--161},
  year =      {2017},
  doi =       {10.1007/978-3-319-52920-2_15},
  publisher = {Springer},
  language =  {english},
}
```

- [ ] **Step 2: проверка дубликатов и использования**

```bash
cd biblio && python3 check-bib-dupes-and-usage.py
```

Ожидается: новые записи не помечены как дубликаты; могут быть помечены «unused» — нормально (используем в Task 3).

- [ ] **Step 3: пробная сборка биб-части без текста**

```bash
make dissertation
```

Ожидается: компиляция успешна; новые записи `.bib` не создают синтаксических ошибок biber.

- [ ] **Step 4: коммит**

```bash
git add biblio/external.bib
git commit -m "Добавил источники §1.3 главы 1 (представление текста)"
```

---

## Task 2: создание TikZ-схемы типологии эмбеддингов

**Files:**
- Create: `Dissertation/images/embedding_taxonomy.tikz`

- [ ] **Step 1: создать файл**

Содержимое `Dissertation/images/embedding_taxonomy.tikz`:

```latex
\begin{tikzpicture}[
        thick,
        >=stealth,
        node distance=10mm and 12mm,
        layer/.style={
                draw,
                rounded corners=2pt,
                align=center,
                minimum height=14mm,
                minimum width=44mm,
                inner sep=4pt,
                font=\small,
            },
        example/.style={
                draw=none,
                align=center,
                font=\scriptsize\itshape,
            },
    ]
    \node[layer]                                    (count)   {Счётные\\(BoW, TF-IDF)};
    \node[layer, right=of count]                    (static)  {Статичные\\(word2vec, GloVe, fastText)};
    \node[layer, right=of static]                   (context) {Контекстные\\(BERT, XLM-R)};
    \node[layer, right=of context]                  (multi)   {Multilingual\\(SBERT-multi, LaBSE)};

    \node[example, below=4mm of count]   (ex1) {интерпретируемость,\\один язык};
    \node[example, below=4mm of static]  (ex2) {семантика слова,\\subword $\to$ OOV};
    \node[example, below=4mm of context] (ex3) {контекст,\\fine-tuning};
    \node[example, below=4mm of multi]   (ex4) {общее пространство\\ru + en};

    \draw[->] (count)   -- (static);
    \draw[->] (static)  -- (context);
    \draw[->] (context) -- (multi);
\end{tikzpicture}
```

- [ ] **Step 2: коммит**

```bash
git add Dissertation/images/embedding_taxonomy.tikz
git commit -m "Добавил TikZ-схему типологии эмбеддингов для §1.3"
```

(Полная сборка с подключением — в Task 3.)

---

## Task 3: написание §1.3

**Files:**
- Modify: `Dissertation/part1.tex` (вставка перед строкой `% TODO: 3.3 …`)

- [ ] **Step 1: вставить секцию §1.3**

Удалить строку `% TODO: 3.3 Методы представления текста для классификации` и вставить вместо неё следующий блок (тот же отступ — без отступа, по структуре файла):

```latex
\section{Методы представления текста для классификации}\label{sec:ch1/repr}

Векторизатор \( \varphi \colon X \to \mathbb{R}^{d} \) из~постановки~\eqref{eq:classifier}
переводит нормализованное сообщение в~признаковое пространство, общее для последующих
кластеризации и~классификации. Выбор семейства \( \varphi \) определяет, какие из~свойств
задачи, перечисленных в~разделе~\ref{sec:ch1/domain}, могут быть выполнены принципиально,
а~какие требуют дополнительных усилий.

\subsection{Счётные представления}\label{subsec:ch1/repr/count}

Классическая отправная точка "--- модель «мешок слов» и~её взвешенный вариант
TF-IDF~\autocite{Manning2008IR, Salton1988TFIDF}: сообщению сопоставляется разреженный
вектор частот терминов, нормированных на~обратную документную частоту. Подход
интерпретируем, опирается на~устойчивые статистические оценки и~хорошо работает
на~узких темах с~устоявшейся лексикой, в~частности на~корпоративной переписке.
Существенным ограничением остаётся отсутствие учёта семантической близости слов и~почти
полное обнуление переноса между языками: русские и~английские формы одного понятия
оказываются ортогональными измерениями признакового вектора, что в~постановке настоящей
работы исключает использование TF-IDF как~единственного представления.

\subsection{Статичные дистрибутивные эмбеддинги}\label{subsec:ch1/repr/static}

Второй слой методов заменяет счётные признаки фиксированными низкоразмерными векторами,
обученными на~больших корпусах: word2vec~\autocite{Mikolov2013word2vec},
GloVe~\autocite{Pennington2014GloVe} и~fastText~\autocite{Bojanowski2017fastText}.
В~отличие от~счётных представлений, эти эмбеддинги фиксируют дистрибутивную семантику
и~поддерживают арифметику над~векторами; fastText дополнительно использует субсимвольные
$n$-граммы, что снимает проблему OOV-слов и~особенно полезно для морфологически богатого
русского языка. Для русского сегмента в~качестве ориентира выступают предобученные модели
RusVectores~\autocite{Kutuzov2017RusVectores}. Тем не~менее каждое слово отображается
в~единственный вектор вне зависимости от~контекста, поэтому многозначность и~специфика
почтового жанра учитываются ограниченно.

\subsection{Контекстные и multilingual представления}\label{subsec:ch1/repr/context}

Современный слой методов "--- контекстные представления на~основе трансформеров.
BERT~\autocite{Devlin2019BERT} обучается на~задачах маскированного языкового
моделирования и~следующего предложения и~отдаёт зависимый от~контекста вектор каждой
позиции; кросс-языковое расширение XLM-R~\autocite{Conneau2020XLMR} обучается совместно
на~ста языках, включая русский. Для классификации удобнее однородные представления уровня
предложения, поэтому используется Sentence-BERT~\autocite{Reimers2019SBERT}: на~базе
сиамской архитектуры дообученный энкодер отображает предложение в~фиксированный вектор,
сохраняющий близость по~смыслу. Multilingual-вариант получают дистилляцией знаний
из~монолингвального энкодера~\autocite{Reimers2020MultilingualSBERT}; альтернативный
сквозной подход реализует LaBSE~\autocite{Feng2022LaBSE}, обученный сопоставлять
параллельные предложения. Эти семейства одновременно покрывают многоязычность и~отдают
векторы, пригодные для нелинейной классификации и~плотностной кластеризации.

\subsection{Сводная типология}\label{subsec:ch1/repr/taxonomy}

Описанные семейства образуют последовательность с~монотонно растущей выразительной
способностью и~монотонно усложняющимися условиями обучения и~исполнения
(рисунок~\ref{fig:embedding-taxonomy}). Счётные и~статичные представления остаются
полезной базовой линией и~используются в~работе как~контрольная точка, однако только
последняя группа методов одновременно отвечает требованию multilingual и~не~требует
переобучения с~нуля на~локальном архиве писем. Вопросы локального исполнения, латентности
и~доступной размерности \(d\) рассматриваются в~главе~\ref{ch:ch2} при~описании компонента
\texttt{normalizer}--\texttt{embedder}.

\begin{figure}[h]
    \centering
    \input{Dissertation/images/embedding_taxonomy.tikz}
    \caption{Типология векторных представлений текста, рассматриваемых в~настоящей
        работе: счётные, статичные дистрибутивные, контекстные и~multilingual; в~каждой
        группе указаны характерные модели и~ключевые свойства}\label{fig:embedding-taxonomy}
\end{figure}

```

- [ ] **Step 2: сборка**

```bash
make dissertation
```

Ожидается: успех. В `dissertation.log` отсутствуют строки `Citation 'Salton1988TFIDF' undefined`, `Citation 'Mikolov2013word2vec' undefined`, ..., `Reference 'fig:embedding-taxonomy' undefined`.

Проверка одной командой:

```bash
grep -E "(Citation|Reference) '(Salton1988TFIDF|Mikolov2013word2vec|Pennington2014GloVe|Bojanowski2017fastText|Devlin2019BERT|Conneau2020XLMR|Reimers2019SBERT|Reimers2020MultilingualSBERT|Feng2022LaBSE|Kutuzov2017RusVectores|fig:embedding-taxonomy)' .* undefined" dissertation.log
```

Ожидается: пустой вывод.

- [ ] **Step 3: визуальная проверка PDF**

Открыть `dissertation.pdf`, найти §1.3, убедиться: четыре подраздела на месте, рисунок 1.2 (или соответствующий номер) отрисовался, ссылка на главу 2 кликабельна.

- [ ] **Step 4: коммит**

```bash
git add Dissertation/part1.tex
git commit -m "Написал §1.3 главы 1: методы представления текста"
```

---

## Task 4: расширение biblio для §1.4

**Files:**
- Modify: `biblio/external.bib`

- [ ] **Step 1: добавить 11 записей источников §1.4**

В конец `biblio/external.bib` вставить:

```bibtex

%%% Источники главы 1, §1.4 «Методы классификации»

@InProceedings{McCallum1998NaiveBayes,
  author =    {McCallum, Andrew and Nigam, Kamal},
  title =     {A Comparison of Event Models for Naive {Bayes} Text Classification},
  booktitle = {AAAI-98 Workshop on Learning for Text Categorization},
  pages =     {41--48},
  year =      {1998},
  language =  {english},
}

@InProceedings{Joachims1998SVMTextCat,
  author =    {Joachims, Thorsten},
  title =     {Text categorization with Support Vector Machines: Learning with many relevant features},
  booktitle = {Machine Learning: ECML-98},
  series =    {Lecture Notes in Computer Science},
  volume =    {1398},
  pages =     {137--142},
  year =      {1998},
  doi =       {10.1007/BFb0026683},
  publisher = {Springer},
  language =  {english},
}

@ARTICLE{Fan2008LIBLINEAR,
  author =  {Fan, Rong-En and Chang, Kai-Wei and Hsieh, Cho-Jui and Wang, Xiang-Rui and Lin, Chih-Jen},
  title =   {{LIBLINEAR}: A library for large linear classification},
  journal = {Journal of Machine Learning Research},
  volume =  {9},
  pages =   {1871--1874},
  year =    {2008},
  language = {english},
}

@ARTICLE{Pedregosa2011sklearn,
  author =  {Pedregosa, Fabian and Varoquaux, Ga{\"e}l and Gramfort, Alexandre and Michel, Vincent and Thirion, Bertrand and Grisel, Olivier and Blondel, Mathieu and Prettenhofer, Peter and Weiss, Ron and Dubourg, Vincent and Vanderplas, Jake and Passos, Alexandre and Cournapeau, David and Brucher, Matthieu and Perrot, Matthieu and Duchesnay, {\'E}douard},
  title =   {Scikit-learn: Machine Learning in {Python}},
  journal = {Journal of Machine Learning Research},
  volume =  {12},
  pages =   {2825--2830},
  year =    {2011},
  options = {maxnames=4},
  language = {english},
}

@ARTICLE{Crammer2006PA,
  author =  {Crammer, Koby and Dekel, Ofer and Keshet, Joseph and Shalev-Shwartz, Shai and Singer, Yoram},
  title =   {Online Passive-Aggressive Algorithms},
  journal = {Journal of Machine Learning Research},
  volume =  {7},
  pages =   {551--585},
  year =    {2006},
  options = {maxnames=4},
  language = {english},
}

@InProceedings{Dredze2008CW,
  author =    {Dredze, Mark and Crammer, Koby and Pereira, Fernando},
  title =     {Confidence-Weighted Linear Classification},
  booktitle = {Proceedings of the 25th International Conference on Machine Learning (ICML)},
  pages =     {264--271},
  year =      {2008},
  doi =       {10.1145/1390156.1390190},
  publisher = {Association for Computing Machinery},
  language =  {english},
}

@ARTICLE{Breiman2001RF,
  author =  {Breiman, Leo},
  title =   {Random Forests},
  journal = {Machine Learning},
  volume =  {45},
  number =  {1},
  pages =   {5--32},
  year =    {2001},
  doi =     {10.1023/A:1010933404324},
  language = {english},
}

@InProceedings{Chen2016XGBoost,
  author =    {Chen, Tianqi and Guestrin, Carlos},
  title =     {{XGBoost}: A Scalable Tree Boosting System},
  booktitle = {Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining},
  pages =     {785--794},
  year =      {2016},
  doi =       {10.1145/2939672.2939785},
  publisher = {Association for Computing Machinery},
  language =  {english},
}

@InProceedings{Ke2017LightGBM,
  author =    {Ke, Guolin and Meng, Qi and Finley, Thomas and Wang, Taifeng and Chen, Wei and Ma, Weidong and Ye, Qiwei and Liu, Tie-Yan},
  title =     {{LightGBM}: A Highly Efficient Gradient Boosting Decision Tree},
  booktitle = {Advances in Neural Information Processing Systems 30 (NeurIPS)},
  pages =     {3146--3154},
  year =      {2017},
  options =   {maxnames=4},
  language =  {english},
}

@InProceedings{Guo2017Calibration,
  author =    {Guo, Chuan and Pleiss, Geoff and Sun, Yu and Weinberger, Kilian Q.},
  title =     {On Calibration of Modern Neural Networks},
  booktitle = {Proceedings of the 34th International Conference on Machine Learning (ICML)},
  pages =     {1321--1330},
  year =      {2017},
  language =  {english},
}

@InProceedings{Hendrycks2017Baseline,
  author =    {Hendrycks, Dan and Gimpel, Kevin},
  title =     {A Baseline for Detecting Misclassified and Out-of-Distribution Examples in Neural Networks},
  booktitle = {Proceedings of the 5th International Conference on Learning Representations (ICLR)},
  year =      {2017},
  url =       {https://arxiv.org/abs/1610.02136},
  language =  {english},
}
```

- [ ] **Step 2: проверка**

```bash
cd biblio && python3 check-bib-dupes-and-usage.py
make dissertation
```

Ожидается: дубликатов нет, сборка успешна.

- [ ] **Step 3: коммит**

```bash
git add biblio/external.bib
git commit -m "Добавил источники §1.4 главы 1 (классификация)"
```

---

## Task 5: написание §1.4

**Files:**
- Modify: `Dissertation/part1.tex` (вставка перед строкой `% TODO: 3.4 …`)

- [ ] **Step 1: вставить секцию §1.4**

Удалить строку `% TODO: 3.4 Методы классификации` и вставить вместо неё следующий блок:

```latex
\section{Методы классификации текстов}\label{sec:ch1/clf}

Классификатор \( f_\theta \) в~постановке~\eqref{eq:decision-rule} обязан возвращать
оценки правдоподобия \( p_k(x) \) для каждого пользовательского класса. Этот раздел
рассматривает семейства классификаторов, востребованные в~прикладных работах по~почте,
с~акцентом на~три практически значимых критерия: совместимость с~ограниченной размеченной
выборкой, поддержку инкрементного обучения как~ответ на~concept drift и~калибровку
вероятностей, без~которой правило с~порогом~\(\tau\) теряет смысл.

\subsection{Вероятностные и линейные методы}\label{subsec:ch1/clf/linear}

Базовая линия для классификации текста "--- мультиномиальный наивный байесовский
классификатор~\autocite{McCallum1998NaiveBayes}, линейные SVM и~логистическая регрессия
поверх TF-IDF~\autocite{Joachims1998SVMTextCat}. Эффективные реализации линейных моделей
для разреженных признаков предоставляют LIBLINEAR~\autocite{Fan2008LIBLINEAR}
и~scikit-learn~\autocite{Pedregosa2011sklearn}; обучение остаётся линейным по~числу
примеров, а~предсказание сводится к~одному скалярному произведению. Линейные модели
хорошо ведут себя при~ограниченной разметке и~при~стационарном распределении, однако
сама по~себе модель не~даёт калиброванной вероятности и~требует дополнительной
постобработки.

\subsection{Онлайн-классификаторы}\label{subsec:ch1/clf/online}

Для задачи с~явным concept drift естественны алгоритмы инкрементного обучения, обновляющие
веса по~каждому новому примеру: Passive-Aggressive~\autocite{Crammer2006PA}
и~Confidence-Weighted Linear Classification~\autocite{Dredze2008CW}. Именно эти семейства
рассматриваются в~прикладной работе TaskTracer~\autocite{Keiser2009TaskTracer} для
предсказания проектной принадлежности писем. Онлайн-классификаторы дешевы в~обновлении
и~устойчивы к~постепенному изменению распределения, но~уверенность модели в~них
относительная (margin), а~не~калиброванная вероятность; для согласования с~решающим
правилом~\eqref{eq:decision-rule} требуется отдельный шаг калибровки.

\subsection{Деревья и бустинг}\label{subsec:ch1/clf/trees}

Семейство ансамблей решающих деревьев "--- Random Forest~\autocite{Breiman2001RF}
и~бустинговые реализации XGBoost~\autocite{Chen2016XGBoost}
и~LightGBM~\autocite{Ke2017LightGBM} "--- де-факто стандарт для табличных задач
и~признаков невысокой размерности. На~больших разреженных TF-IDF-векторах эти методы
проигрывают линейным как~по~времени обучения, так~и~по~качеству, однако при~работе поверх
плотных эмбеддингов и~небольшого числа обучающих примеров они дают конкурентные
результаты и~отдают встроенные оценки важности признаков, полезные для анализа ошибок.

\subsection{Нейронные классификаторы поверх эмбеддингов}\label{subsec:ch1/clf/neural}

Линейная или мелкая полносвязная голова поверх предобученных эмбеддингов (в~частности,
SBERT-векторов из~раздела~\ref{subsec:ch1/repr/context}) "--- наиболее частая базовая
архитектура для нейронной классификации текста при~ограниченной разметке. Дополнительный
выигрыш даёт частичный fine-tuning энкодера на~целевом домене, но~ценой большего объёма
данных и~вычислений. Для постановки с~явной категорией \texttt{other} критична калибровка
выходных вероятностей: классический Platt-scaling и~temperature scaling описаны
в~работе~\autocite{Guo2017Calibration}, а~базовая эвристика максимальной softmax-уверенности
для отделения out-of-distribution-примеров рассмотрена в~работе~\autocite{Hendrycks2017Baseline}.
Без~этих механизмов правило~\eqref{eq:decision-rule} оказывается чувствительным к~общему
уровню уверенности модели и~не~отделяет «незнакомое» от~«неоднозначного».

\medskip

Совместно перечисленные методы покрывают спектр от~интерпретируемых линейных моделей
до~гибких нейронных архитектур с~калибровкой; критерии выбора конкретной модели
\(f_\theta\) для настоящей работы "--- объём доступной разметки, время инференса
на~CPU и~совместимость с~инкрементным обновлением "--- рассматриваются
в~главе~\ref{ch:ch2} вместе с~решением для постобработки уверенности.

```

- [ ] **Step 2: сборка**

```bash
make dissertation
```

- [ ] **Step 3: проверка ссылок**

```bash
grep -E "(Citation|Reference) '(McCallum1998NaiveBayes|Joachims1998SVMTextCat|Fan2008LIBLINEAR|Pedregosa2011sklearn|Crammer2006PA|Dredze2008CW|Breiman2001RF|Chen2016XGBoost|Ke2017LightGBM|Guo2017Calibration|Hendrycks2017Baseline|subsec:ch1/repr/context)' .* undefined" dissertation.log
```

Ожидается: пустой вывод.

- [ ] **Step 4: коммит**

```bash
git add Dissertation/part1.tex
git commit -m "Написал §1.4 главы 1: методы классификации"
```

---

## Task 6: расширение biblio для §1.5

**Files:**
- Modify: `biblio/external.bib`

- [ ] **Step 1: добавить 9 записей источников §1.5**

В конец `biblio/external.bib` вставить:

```bibtex

%%% Источники главы 1, §1.5 «Методы кластеризации»

@InProceedings{MacQueen1967KMeans,
  author =    {MacQueen, James},
  title =     {Some methods for classification and analysis of multivariate observations},
  booktitle = {Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability},
  volume =    {1},
  pages =     {281--297},
  year =      {1967},
  publisher = {University of California Press},
  language =  {english},
}

@InProceedings{Arthur2007KMeansPP,
  author =    {Arthur, David and Vassilvitskii, Sergei},
  title =     {$k$-means++: The Advantages of Careful Seeding},
  booktitle = {Proceedings of the Eighteenth Annual ACM-SIAM Symposium on Discrete Algorithms (SODA)},
  pages =     {1027--1035},
  year =      {2007},
  publisher = {Society for Industrial and Applied Mathematics},
  language =  {english},
}

@InProceedings{Ester1996DBSCAN,
  author =    {Ester, Martin and Kriegel, Hans-Peter and Sander, J{\"o}rg and Xu, Xiaowei},
  title =     {A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise},
  booktitle = {Proceedings of the Second International Conference on Knowledge Discovery and Data Mining (KDD)},
  pages =     {226--231},
  year =      {1996},
  publisher = {AAAI Press},
  language =  {english},
}

@InProceedings{Campello2013HDBSCAN,
  author =    {Campello, Ricardo J. G. B. and Moulavi, Davoud and Sander, J{\"o}rg},
  title =     {Density-Based Clustering Based on Hierarchical Density Estimates},
  booktitle = {Advances in Knowledge Discovery and Data Mining (PAKDD)},
  series =    {Lecture Notes in Computer Science},
  volume =    {7819},
  pages =     {160--172},
  year =      {2013},
  doi =       {10.1007/978-3-642-37456-2_14},
  publisher = {Springer},
  language =  {english},
}

@ARTICLE{McInnes2017HDBSCAN,
  author =  {McInnes, Leland and Healy, John and Astels, Steve},
  title =   {hdbscan: Hierarchical density based clustering},
  journal = {Journal of Open Source Software},
  volume =  {2},
  number =  {11},
  pages =   {205},
  year =    {2017},
  doi =     {10.21105/joss.00205},
  language = {english},
}

@MISC{McInnes2018UMAP,
  author =       {McInnes, Leland and Healy, John and Melville, James},
  title =        {{UMAP}: Uniform Manifold Approximation and Projection for Dimension Reduction},
  howpublished = {arXiv preprint arXiv:1802.03426},
  year =         {2018},
  url =          {https://arxiv.org/abs/1802.03426},
  language =     {english},
}

@ARTICLE{Blei2003LDA,
  author =  {Blei, David M. and Ng, Andrew Y. and Jordan, Michael I.},
  title =   {Latent {Dirichlet} Allocation},
  journal = {Journal of Machine Learning Research},
  volume =  {3},
  pages =   {993--1022},
  year =    {2003},
  language = {english},
}

@ARTICLE{Rousseeuw1987Silhouette,
  author =  {Rousseeuw, Peter J.},
  title =   {Silhouettes: A graphical aid to the interpretation and validation of cluster analysis},
  journal = {Journal of Computational and Applied Mathematics},
  volume =  {20},
  pages =   {53--65},
  year =    {1987},
  doi =     {10.1016/0377-0427(87)90125-7},
  language = {english},
}

@ARTICLE{Davies1979DBI,
  author =  {Davies, David L. and Bouldin, Donald W.},
  title =   {A Cluster Separation Measure},
  journal = {IEEE Transactions on Pattern Analysis and Machine Intelligence},
  volume =  {PAMI-1},
  number =  {2},
  pages =   {224--227},
  year =    {1979},
  doi =     {10.1109/TPAMI.1979.4766909},
  language = {english},
}
```

- [ ] **Step 2: проверка**

```bash
cd biblio && python3 check-bib-dupes-and-usage.py
make dissertation
```

- [ ] **Step 3: коммит**

```bash
git add biblio/external.bib
git commit -m "Добавил источники §1.5 главы 1 (кластеризация)"
```

---

## Task 7: создание TikZ-схемы кластеризации с выбросами

**Files:**
- Create: `Dissertation/images/clustering_outliers.tikz`

- [ ] **Step 1: создать файл**

Содержимое `Dissertation/images/clustering_outliers.tikz`:

```latex
\begin{tikzpicture}[
        thick,
        >=stealth,
        every node/.style={font=\scriptsize},
        cluster1/.style={circle, draw=black, fill=black!10, inner sep=1pt, minimum size=2.6mm},
        cluster2/.style={circle, draw=black, fill=black!30, inner sep=1pt, minimum size=2.6mm},
        cluster3/.style={circle, draw=black, fill=black!60, text=white, inner sep=1pt, minimum size=2.6mm},
        noise/.style={circle, draw=black, fill=white, inner sep=1pt, minimum size=2.4mm, dashed},
        panel/.style={draw, rounded corners=2pt, minimum width=56mm, minimum height=42mm},
    ]

    \begin{scope}[local bounding box=left]
        \node[panel] (Lframe) at (0,0) {};
        \node[anchor=north, font=\small] at (Lframe.north) {а) k-means: все точки приписаны};
        % три кластера + «выбросы», но все покрашены
        \foreach \x/\y in {-1.6/0.7, -1.2/1.1, -1.8/0.4, -1.4/0.2, -1.1/0.9}
            \node[cluster1] at (\x,\y) {};
        \foreach \x/\y in {0.6/0.5, 1.0/0.9, 0.4/1.0, 0.9/0.3, 1.2/0.6}
            \node[cluster2] at (\x,\y) {};
        \foreach \x/\y in {-0.4/-1.0, -0.1/-1.4, 0.2/-1.1, -0.3/-0.7}
            \node[cluster3] at (\x,\y) {};
        % «истинные выбросы», тоже покрашенные (искусственно отнесённые)
        \foreach \x/\y/\c in {1.7/-1.3/cluster3, -1.8/-1.2/cluster1, 1.8/1.4/cluster2}
            \node[\c] at (\x,\y) {};
    \end{scope}

    \begin{scope}[xshift=72mm, local bounding box=right]
        \node[panel] (Rframe) at (0,0) {};
        \node[anchor=north, font=\small] at (Rframe.north) {б) HDBSCAN: часть точек "--- шум};
        % те же три кластера
        \foreach \x/\y in {-1.6/0.7, -1.2/1.1, -1.8/0.4, -1.4/0.2, -1.1/0.9}
            \node[cluster1] at (\x,\y) {};
        \foreach \x/\y in {0.6/0.5, 1.0/0.9, 0.4/1.0, 0.9/0.3, 1.2/0.6}
            \node[cluster2] at (\x,\y) {};
        \foreach \x/\y in {-0.4/-1.0, -0.1/-1.4, 0.2/-1.1, -0.3/-0.7}
            \node[cluster3] at (\x,\y) {};
        % выбросы — отдельный стиль (шум)
        \foreach \x/\y in {1.7/-1.3, -1.8/-1.2, 1.8/1.4}
            \node[noise] at (\x,\y) {};
    \end{scope}
\end{tikzpicture}
```

- [ ] **Step 2: коммит**

```bash
git add Dissertation/images/clustering_outliers.tikz
git commit -m "Добавил TikZ-иллюстрацию кластеризации с выбросами для §1.5"
```

---

## Task 8: написание §1.5

**Files:**
- Modify: `Dissertation/part1.tex` (вставка перед строкой `% TODO: 3.5 …`)

- [ ] **Step 1: вставить секцию §1.5**

Удалить строку `% TODO: 3.5 Методы кластеризации для bootstrap классов` и вставить вместо неё:

```latex
\section{Методы кластеризации для bootstrap классов}\label{sec:ch1/cluster}

В~постановке~\eqref{eq:label-set} множество пользовательских классов \(Y_{\text{user}}\)
не~задано заранее. Первичный набор классов формируется по~исторической выборке писем
кластеризацией в~признаковом пространстве \(\mathbb{R}^{d}\), задаваемом векторизатором
из~раздела~\ref{sec:ch1/repr}. Этот раздел рассматривает семейства методов кластеризации
с~точки зрения двух требований: способности работать без~априорного числа классов и~явного
выделения сообщений, не~попадающих ни~в~один из~устойчивых кластеров "--- естественного
прообраза категории \texttt{other}.

\subsection{Партиционные методы}\label{subsec:ch1/cluster/partition}

Базовая партиционная схема "--- алгоритм \(k\)-means~\autocite{MacQueen1967KMeans}
и~его инициализация \(k\)-means++~\autocite{Arthur2007KMeansPP}: точки делятся
на~\(k\) непересекающихся групп с~минимизацией суммы квадратов расстояний до~центроидов.
Метод прост, быстр и~используется как~базовая линия, но~требует фиксированного \(k\),
не~выделяет выбросы (каждая точка приписывается к~ближайшему центру) и~предполагает
сферические по~форме кластеры в~используемой метрике. В~постановке с~неизвестным числом
проектных категорий и~разнородной массой шумовых сообщений эти ограничения существенны.

\subsection{Плотностные методы}\label{subsec:ch1/cluster/density}

Плотностные алгоритмы трактуют кластер как~область высокой плотности точек, разделённую
областями низкой плотности. DBSCAN~\autocite{Ester1996DBSCAN} задаёт кластер минимальным
числом соседей в~радиусе~\(\varepsilon\) и~явно помечает точки, не~прошедшие порог,
как~шум. Иерархическое обобщение HDBSCAN~\autocite{Campello2013HDBSCAN} устраняет
зависимость от~единого радиуса \(\varepsilon\) и~определяет устойчивые кластеры
переменной плотности; популярная программная реализация описана
в~работе~\autocite{McInnes2017HDBSCAN}. Для постановки настоящей работы плотностные
методы важны тем, что отдельный класс «шум» структурно сопоставим с~категорией
\texttt{other} из~правила~\eqref{eq:decision-rule}: сообщения, не~попавшие ни~в~один
устойчивый кластер на~этапе bootstrap, естественно отнести в~буфер обратной связи,
а~не~принудительно распределить по~пользовательским классам
(рисунок~\ref{fig:clustering-outliers}).

\subsection{Снижение размерности и тематические модели}\label{subsec:ch1/cluster/dimred}

Контекстные эмбеддинги, рассматриваемые в~разделе~\ref{subsec:ch1/repr/context},
размещают сообщения в~пространстве сотен измерений, где плотностные алгоритмы теряют
устойчивость. Один из~распространённых способов компенсировать «проклятие
размерности» "--- предварительное снижение размерности нелинейным методом, в~частности
UMAP~\autocite{McInnes2018UMAP}, после чего HDBSCAN применяется уже к~векторам
небольшой размерности. Альтернативная линия "--- тематическое моделирование, например
LDA~\autocite{Blei2003LDA}: модель интерпретируема и~даёт мягкие распределения тем,
однако ориентирована на~представления уровня слов и~хуже сочетается с~многоязычным
семантическим пространством.

\subsection{Метрики качества кластеризации}\label{subsec:ch1/cluster/metrics}

Для внутренней оценки качества кластеризации в~настоящей работе рассматриваются
коэффициент силуэта~\autocite{Rousseeuw1987Silhouette} и~индекс
Дэвиса-Боулдина~\autocite{Davies1979DBI}. Эти метрики измеряют компактность кластеров
и~их разделимость в~используемой метрике, но~напрямую не~отражают пригодности
результатов для последующей ручной аннотации: устойчивые с~точки зрения метрики
кластеры могут быть слишком крупными для содержательной разметки, и~наоборот. Поэтому
численные показатели в~работе используются как~ориентир, а~окончательное решение
о~принятии кластеров принимается в~процедуре review с~привлечением пользователя,
описанной в~главе~\ref{ch:ch2}.

\begin{figure}[h]
    \centering
    \input{Dissertation/images/clustering_outliers.tikz}
    \caption{Сравнение партиционной и~плотностной кластеризации: \emph{а)}~\(k\)-means
        приписывает каждую точку к~ближайшему центру, не~различая шум; \emph{б)}~HDBSCAN
        выделяет три плотных кластера и~помечает оставшиеся точки как~шум (пунктирные
        обводки), что естественно сопоставимо с~категорией~\texttt{other}}\label{fig:clustering-outliers}
\end{figure}

```

- [ ] **Step 2: сборка**

```bash
make dissertation
```

- [ ] **Step 3: проверка**

```bash
grep -E "(Citation|Reference) '(MacQueen1967KMeans|Arthur2007KMeansPP|Ester1996DBSCAN|Campello2013HDBSCAN|McInnes2017HDBSCAN|McInnes2018UMAP|Blei2003LDA|Rousseeuw1987Silhouette|Davies1979DBI|fig:clustering-outliers|sec:ch1/repr|subsec:ch1/repr/context)' .* undefined" dissertation.log
```

Ожидается: пустой вывод. Открыть PDF, проверить рисунок 1.3 (или соответствующий номер).

- [ ] **Step 4: коммит**

```bash
git add Dissertation/part1.tex
git commit -m "Написал §1.5 главы 1: методы кластеризации"
```

---

## Task 9: написание §1.6 (сравнение систем)

**Files:**
- Modify: `Dissertation/part1.tex` (вставка перед строкой `% TODO: 3.6 …`)

Новые источники не требуются — все четыре системы уже в `biblio/external.bib`.

- [ ] **Step 1: вставить секцию §1.6 с таблицей**

Удалить строку `% TODO: 3.6 Сравнительный анализ существующих систем` и вставить вместо неё:

```latex
\section{Сравнительный анализ существующих систем}\label{sec:ch1/systems}

В~разделе~\ref{sec:ch1/domain} перечислены четыре свойства задачи "--- персонализированные
классы, multilingual, locality и~явный учёт concept drift. Дополнительно
правило~\eqref{eq:decision-rule} требует категории \texttt{other} и~обратной связи
с~пользователем. Этот раздел сопоставляет с~этими осями четыре системы организации
входящей корреспонденции, отражающие основные практические подходы.

\subsection{Outlook Focused Inbox}\label{subsec:ch1/systems/outlook}

Focused~Inbox в~Microsoft Outlook~\autocite{Microsoft2024FocusedInbox} делит входящие
письма на~две папки "--- Focused и~Other "--- на~основе персонализированной модели
важности. Модель обновляется по~неявным сигналам пользователя (чтение, перенос
сообщений) и~формально учитывает индивидуальные предпочтения. Целевая шкала бинарна:
система не~поддерживает произвольный набор тематических классов. Обучение и~ранжирование
выполняются на~стороне серверов сервиса, что не~совместимо с~требованием locality
из~раздела~\ref{sec:ch1/domain}.

\subsection{Gmail Priority Inbox}\label{subsec:ch1/systems/gmail}

Priority~Inbox в~Gmail~\autocite{Aberdeen2010PriorityInbox} использует персонализированный
логистический классификатор поверх большого набора признаков отправителя, темы и~истории
взаимодействия для предсказания важности сообщения. Модель адаптируется к~конкретному
пользователю и~поддерживает онлайн-дообучение, однако итоговая шкала, как~и~в~Outlook,
сводится к~бинарному «importance / not important»; собственные тематические классы
не~предусмотрены. Серверное исполнение и~использование внешней инфраструктуры также
исключают применение системы в~постановке настоящей работы.

\subsection{TaskTracer}\label{subsec:ch1/systems/tasktracer}

TaskTracer~\autocite{Keiser2009TaskTracer} оценивает несколько онлайн-классификаторов
"--- наивный байесовский, Passive-Aggressive и~Confidence-Weighted "--- для предсказания
проектной принадлежности входящих писем по~истории работы пользователя. В~отличие
от~Focused~Inbox и~Priority~Inbox, система оперирует пользовательскими проектами
и~приближается к~многоклассовой постановке~\eqref{eq:classifier}. Из~совместимости
с~настоящей задачей выпадают две оси: специальная категория \texttt{other} в~исходной
постановке отсутствует, а~работа ведётся только с~англоязычной перепиской, что не~даёт
ответа на~требование multilingual.

\subsection{EmFORE}\label{subsec:ch1/systems/emfore}

EmFORE~\autocite{Singh2023EmFORE} индуктивно выводит символьные правила распределения
писем по~существующим папкам и~явно адаптирует их к~изменению признаков и~состава
категорий, реализуя один из~рабочих сценариев учёта concept drift. Подход опирается
на~стабильные структурные признаки (отправитель, шаблон темы, шаблоны заголовков)
и~не~использует кластеризацию для формирования начальных классов; категория
\texttt{other} как~активный буфер обратной связи также не~предусмотрена.
Multilingual-применение в~работе явно не~декларируется.

\subsection{Сводное сравнение}\label{subsec:ch1/systems/summary}

Сопоставление перечисленных систем по~осям, существенным для постановки настоящей
работы, приведено в~таблице~\ref{tab:systems-compare}. Ручные правила почтового
клиента и~пользовательские фильтры Sieve рассматриваются в~разделе~\ref{sec:ch1/domain}
и~в~таблице отдельной строкой не~представлены.

\begin{table}[h]
    \centering
    \begin{threeparttable}
        \caption{Сравнение существующих систем организации входящей почты с~целевыми
            требованиями настоящей работы}\label{tab:systems-compare}
        \begin{tabular}{| p{30mm} | c | c | c | c | c | p{22mm} |}
            \hline
            Система                      & Перс. классы\tnote{1}        & Multilingual & Locality     & \texttt{other}\tnote{2} & Concept drift & Источник классов \\
            \hline
            Focused Inbox~\autocite{Microsoft2024FocusedInbox}
                                         & \(-\)\tnote{3}               & \(\pm\)      & \(-\)        & \(-\)                   & \(+\)         & встроенная бинарная \\
            \hline
            Priority Inbox~\autocite{Aberdeen2010PriorityInbox}
                                         & \(-\)\tnote{3}               & \(\pm\)      & \(-\)        & \(-\)                   & \(+\)         & встроенная бинарная \\
            \hline
            TaskTracer~\autocite{Keiser2009TaskTracer}
                                         & \(+\)                        & \(-\)        & \(+\)        & \(-\)                   & \(+\)         & пользовательские проекты \\
            \hline
            EmFORE~\autocite{Singh2023EmFORE}
                                         & \(+\)                        & \(-\)        & \(\pm\)      & \(-\)                   & \(+\)         & папки + индуктивные правила \\
            \hline
            \textbf{Настоящая работа}    & \(+\)                        & \(+\)        & \(+\)        & \(+\)                   & \(+\)         & bootstrap кластеризацией \\
            \hline
        \end{tabular}
        \begin{tablenotes}\footnotesize
            \item[1] Произвольный набор тематических классов, заданный пользователем.
            \item[2] Явная категория для сообщений вне устойчивых классов с~накоплением для переобучения.
            \item[3] Поддерживается только бинарное разделение important/other.
        \end{tablenotes}
    \end{threeparttable}
\end{table}

Из~таблицы~\ref{tab:systems-compare} следует, что ни~одна из~рассмотренных систем
не~закрывает все оси одновременно: системы крупных почтовых сервисов поддерживают
concept drift, но~не~дают произвольных классов и~требуют передачи данных вовне; работы
TaskTracer и~EmFORE дают персонализированные классы, но~не~рассчитаны на~multilingual
и~явное обращение с~категорией \texttt{other}. Целевая строка таблицы фиксирует
требования, которым должна удовлетворять система настоящей работы.

```

- [ ] **Step 2: сборка**

```bash
make dissertation
```

- [ ] **Step 3: проверка**

```bash
grep -E "(Citation|Reference) '(tab:systems-compare|Microsoft2024FocusedInbox|Aberdeen2010PriorityInbox|Keiser2009TaskTracer|Singh2023EmFORE)' .* undefined" dissertation.log
```

Открыть PDF: убедиться, что таблица 1.1 попала в `\listoftables`, нумерация колонок и сносок корректна, перенос строк в ячейках допустим.

- [ ] **Step 4: коммит**

```bash
git add Dissertation/part1.tex
git commit -m "Написал §1.6 главы 1: сравнение существующих систем"
```

---

## Task 10: написание §1.7 и удаление TODO

**Files:**
- Modify: `Dissertation/part1.tex` (вставка вместо TODO §1.7 + удаление всех оставшихся TODO-строк)

- [ ] **Step 1: вставить §1.7 и убрать все TODO-маркеры**

Удалить оставшиеся строки:

```
% TODO: 3.7 Постановка задачи разработки
```

(а также, если после Task 1–Task 9 какие-то `% TODO:` остались по другим причинам — снять их при условии, что соответствующая секция уже написана).

На место `% TODO: 3.7 …` вставить:

```latex
\section{Постановка задачи разработки}\label{sec:ch1/dev}

\subsection{Резюме предметной области}\label{subsec:ch1/dev/summary}

Постановка~\eqref{eq:classifier}--\eqref{eq:decision-rule} вместе со~свойствами
из~раздела~\ref{sec:ch1/domain} и~метриками раздела~\ref{subsec:ch1/task/metrics}
формирует следующую совокупность требований к~системе: персонализированные
тематические классы, формируемые по~исторической выборке; единое признаковое
пространство для русско-английской переписки; локальное исполнение всех компонентов;
учёт concept drift с~явной категорией~\texttt{other} как~буфером обратной связи.
Сопоставление с~существующими системами из~таблицы~\ref{tab:systems-compare}
показывает, что ни~одно из~готовых решений не~удовлетворяет всем требованиям
одновременно, что и~определяет содержание дальнейшей работы.

\subsection{Список задач разработки}\label{subsec:ch1/dev/tasks}

В~рамках работы решаются следующие задачи разработки.

\begin{enumerate}
    \item Нормализация входящих сообщений: построение конвейера, переводящего MIME-сообщение
        в~канонический контракт \texttt{normalized\_text}, включающий поля заголовка,
        очищенный основной текст и~идентификатор языка.
    \item Векторизация: реализация локального multilingual-векторизатора~\(\varphi\)
        для русско-английской переписки, не~требующего передачи текста писем во~внешние
        сервисы; конкретный выбор семейства методов "--- глава~\ref{ch:ch2}.
    \item Bootstrap пользовательских классов: процедура кластеризации архива писем
        в~пространстве \(\varphi\) с~явным выделением шумовых сообщений и~подготовкой
        кандидатов для ручного review.
    \item Обучение классификатора: реализация классификатора \(f_\theta\), отдающего
        калиброванные оценки \(p_k(x)\), и~интеграция решающего правила~\eqref{eq:decision-rule}
        с~порогами по~уверенности и~отнесением низкоуверенных сообщений в~\texttt{other}.
    \item Цикл обратной связи: накопление сообщений категории \texttt{other},
        периодический review и~пороговый триггер переобучения как~механизм
        реакции на~concept drift~\autocite{Gama2014ConceptDrift}.
    \item Инкрементное обновление и~версионирование: хранение версий модели вместе
        с~метриками macro-F1, weighted-F1 и~coverage, активация новой версии
        по~quality gates.
    \item Эмпирическая оценка: проведение экспериментов на~архиве писем,
        репрезентативном для целевого пользователя, с~отчётом по~метрикам
        раздела~\ref{subsec:ch1/task/metrics}.
\end{enumerate}

\subsection{Критерии успеха}\label{subsec:ch1/dev/success}

Система считается решающей поставленную задачу при~одновременном выполнении следующих
критериев.

\begin{enumerate}
    \item Качество классификации на~тестовом срезе достигает значения
        \( \mathrm{macro\text{-}F_1} \geqslant \fixme{\tau_{\mathrm{F1}}} \) при~coverage
        не~ниже \( \fixme{c_{0}} \) от~общего объёма входящих писем; конкретные
        числовые пороги фиксируются по~результатам экспериментов в~главе~\ref{ch:ch3}.
    \item Среднее время инференса одного сообщения на~целевой конфигурации
        не~превышает \( \fixme{\tau_{\mathrm{lat}}} \)~мс на~CPU.
    \item Архитектура и~процедуры эксплуатации формально гарантируют отсутствие
        передачи текста писем во~внешние сервисы (locality).
    \item Реализован полный цикл «\texttt{other}~$\to$~review~$\to$~переобучение
        $\to$~активация», подтверждённый сценариями использования в~главе~\ref{ch:ch3}.
\end{enumerate}

Архитектурная реализация перечисленных задач разработки, выбор конкретных моделей
и~алгоритмов, а~также организация цикла обратной связи рассматриваются
в~главе~\ref{ch:ch2}.

```

- [ ] **Step 2: подтвердить, что в `part1.tex` не остаётся ни одного `% TODO:`**

```bash
grep -n "% TODO" Dissertation/part1.tex
```

Ожидается: пустой вывод.

- [ ] **Step 3: полная сборка**

```bash
make distclean
make dissertation
```

`distclean` нужен, чтобы перестроить `.aux` с нуля и убедиться, что все перекрёстные ссылки разрешаются за два прохода biber/biblatex.

- [ ] **Step 4: финальная проверка ссылок и общих предупреждений**

```bash
grep -E "(Citation|Reference) '.*' .* undefined" dissertation.log | sort -u
```

Ожидается: пустой вывод.

```bash
grep -E "(Overfull|Underfull) (\\\\hbox|\\\\vbox)" dissertation.log | wc -l
```

Если число badboxes сильно больше, чем до Task 1, просмотреть их (особенно в таблице §1.6) и поправить вручную форматирование.

- [ ] **Step 5: визуальный обзор PDF**

Открыть `dissertation.pdf` и пройти по списку:

1. оглавление содержит §1.3–§1.7 с корректными номерами страниц;
2. список рисунков содержит «Типология векторных представлений…» и «Сравнение партиционной и~плотностной кластеризации…»;
3. список таблиц содержит «Сравнение существующих систем…»;
4. внутри текста: ссылки `\eqref{eq:classifier}`, `\eqref{eq:decision-rule}`, `\ref{ch:ch2}`, `\ref{ch:ch3}`, `\ref{tab:systems-compare}` отображаются как номера, а не `??`;
5. цитаты в `\autocite{...}` отображаются номерами/ссылками согласно `biblatex-gost`.

- [ ] **Step 6: финальный коммит**

```bash
git add Dissertation/part1.tex
git commit -m "Дописал §1.7 главы 1 и убрал TODO-маркеры"
```

---

## Self-Review

Пробежал план против спека `docs/superpowers/specs/2026-05-27-chapter1-completion-design.md`:

**1. Spec coverage:**

| Спек | Реализация |
| --- | --- |
| §1.3 представление текста (4 подраздела + связка) | Task 1 (биб) + Task 2 (tikz) + Task 3 (текст). Четыре `\subsection` с метками `subsec:ch1/repr/{count,static,context,taxonomy}`. |
| §1.4 классификация (4 подраздела + связка) | Task 4 + Task 5. Четыре `\subsection` с метками `subsec:ch1/clf/{linear,online,trees,neural}` + завершающий `\medskip`-абзац со ссылкой на главу 2. |
| §1.5 кластеризация (3 + метрики + связка) | Task 6 + Task 7 (tikz) + Task 8. Подразделы `subsec:ch1/cluster/{partition,density,dimred,metrics}`. |
| §1.6 сравнение систем + таблица 1.1 | Task 9. Метка `tab:systems-compare`, ссылки `subsec:ch1/systems/{outlook,gmail,tasktracer,emfore,summary}`. |
| §1.7 список задач + критерии успеха + мостик | Task 10. Подразделы `subsec:ch1/dev/{summary,tasks,success}`. Пороги обозначены `\fixme{}`. |
| TikZ-схема типологии эмбеддингов | Task 2. Стиль воспроизводит `classification_scheme.tikz`. |
| TikZ-иллюстрация кластеризации | Task 7. Две панели (k-means vs HDBSCAN). |
| Таблица сравнения систем | Task 9 (внутри секции §1.6). |
| ~25 новых биб-записей с DOI/URL где применимо | Task 1 (10), Task 4 (11), Task 6 (9) = 30 — соответствует спеку «~25». |
| Удаление TODO-маркеров и сохранение `\FloatBarrier` | Task 10 (steps 1–2). |
| Проверка сборки `make dissertation` | После каждой задачи. |
| Стилевые требования (`«»`, `"---`, `~`, 4 пробела, LF, UTF-8) | Все вставляемые блоки соблюдают; явно зафиксировано в «Сквозных соглашениях». |
| `make examples` не запускать | План явно ссылается на `make dissertation` и не требует `make examples`. |

**2. Placeholder scan:** в плане нет «TODO», «TBD», «implement later», нет ссылок на не определённые в плане ключи. Внутри `Dissertation/part1.tex` появляются `\fixme{...}` только в §1.7 для трёх числовых порогов — это намеренно и согласовано со спеком (раздел 5).

**3. Type consistency:** все ключи цитирования, используемые в текстах задач 3/5/8/9/10, заведены в соответствующих биб-задачах 1/4/6 либо уже присутствуют в `biblio/external.bib`. Все `\ref{}` и `\eqref{}` указывают на метки, заведённые в `part1.tex` (уже существующие в §1.1–§1.2 или вводимые в §1.3–§1.7 настоящим планом). Имена меток выбраны единообразно: `sec:ch1/<name>`, `subsec:ch1/<section>/<sub>`, `fig:<name>`, `tab:<name>`.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-27-chapter1-completion.md`.**

Two execution options:

1. **Subagent-Driven (recommended)** — диспатчу свежего сабагента под каждую задачу, ревью между задачами, быстрая итерация.
2. **Inline Execution** — выполняем задачи в этой же сессии через `superpowers:executing-plans`, батчевое исполнение с чекпоинтами.

Какой вариант?
