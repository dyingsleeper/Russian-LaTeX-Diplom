# План второй главы дипломной работы

> **Статус:** WIP.
>
> **Ревью:** план ещё не прошёл ревью и не утверждён. Перед переносом в
> `Dissertation/part2.tex` его нужно проверить по структуре диплома, фактическому
> состоянию проекта `diplom2.0` и требованиям научного руководителя.

## Назначение главы

Глава 2 должна описывать проектирование модульной локальной системы классификации
электронной почты на основе проекта `diplom-ai`. Основной акцент делается на
архитектуру приложения, поток данных, модель хранения, нормализацию писем,
построение эмбеддингов, кластеризацию, ручную проверку результатов и подготовку
данных для классификатора.

Глава не должна позиционировать проект как CLI-only систему. Командная строка
может упоминаться только как один из способов запуска пайплайна и проверки
работоспособности. Проект описывается как единое модульное приложение без
планируемого разбиения на отдельные сервисы.

Категория `other` не должна быть смысловым центром главы. Её можно упоминать
только как один из технических механизмов обработки спорных, шумовых или
неуверенно размеченных сообщений.

## Предлагаемое название

```tex
\chapter{Проектирование модульной системы классификации электронной почты}\label{ch:ch2}
```

## 2.1 Требования к системе

Раздел переводит постановку из главы 1 в инженерные требования к системе.

Раскрыть:

- локальную обработку содержимого писем;
- read-only синхронизацию с почтовым ящиком;
- поддержку русско-английских текстов;
- воспроизводимость обработки;
- хранение промежуточных состояний;
- модульную архитектуру без разбиения на отдельные сервисы;
- возможность ручной проверки кластеров перед обучением классификатора.

Опорные материалы:

- `/home/dyingsleeper/PycharmProjects/diplom2.0/docs/ROADMAP.md`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/README.md`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/configs/default.yaml`.

## 2.2 Общая архитектура приложения

Раздел описывает `diplom-ai` как единое Python-приложение с внутренними модулями,
разделёнными по ответственности.

Описать модули:

- `email` -- синхронизация, MIME-парсинг, нормализация;
- `storage` -- PostgreSQL-схема и репозитории;
- `queueing` -- таблица задач и последовательное выполнение этапов;
- `orchestration` -- управление пайплайном обработки писем;
- `clustering` -- эмбеддинги, HDBSCAN/KMeans, summaries, visualization;
- `annotation` -- экспорт и импорт ручной разметки через Argilla;
- `training` -- подготовка и обучение базового классификатора;
- `inference` -- загрузка сохранённых артефактов и получение предсказаний.

Иллюстрация: модульная архитектура приложения. На схеме нужно показать не
сервисы, а внутренние пакеты и направление потока данных между ними.

Опорные материалы:

- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/cli.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/orchestration/email_pipeline.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/CLAUDE.md`.

## 2.3 Модель данных

Раздел описывает структуру хранения и объясняет, как обеспечивается
трассируемость обработки: от исходного письма до эмбеддингов, кластеров,
разметки и обучающих данных.

Описать группы таблиц:

- исходные письма: `raw_emails`;
- нормализованные письма: `normalized_emails`;
- векторные представления: `email_embeddings`;
- результаты кластеризации: `cluster_runs`, `cluster_assignments`,
  `cluster_summaries`;
- задачи пайплайна: `pipeline_tasks`;
- ручная разметка: `class_labels`, `annotation_batches`, `email_labels`.

Рекомендуемая таблица в дипломе: сущность, назначение, ключевые поля, роль в
пайплайне.

Опорные материалы:

- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/storage/schema.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/storage/repositories.py`.

## 2.4 Синхронизация и нормализация писем

Раздел описывает путь письма от почтового ящика до канонического текстового
представления.

Основной поток:

```text
IMAP -> raw MIME -> RawEmail -> NormalizedEmail -> normalized_text
```

Раскрыть:

- read-only IMAP-доступ;
- дедупликацию по `content_hash` и IMAP UID;
- сохранение исходного MIME;
- извлечение текста из MIME и HTML;
- удаление CSS, подписей, цитированных ответов и типовых футеров;
- замену ссылок, адресов, дат, времени и чисел на служебные токены;
- определение языка;
- оценку качества текста.

Опорные материалы:

- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/email/imap_sync.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/email/parsing.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/email/normalization.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/data/preprocessing.py`.

## 2.5 Построение эмбеддингов

Раздел связывает теоретический обзор multilingual-представлений из главы 1 с
конкретной реализацией в проекте.

Описать:

- локальную загрузку модели из конфигурации;
- текущую модель `BAAI/bge-m3`;
- батчевое построение эмбеддингов;
- кеширование в `.npz`;
- запись индекса в таблицу `email_embeddings`;
- версионирование через `clustering.embeddings.version`;
- фильтрацию исходных сообщений по языку и качеству текста.

Опорные материалы:

- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/clustering/embeddings.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/clustering/config.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/configs/default.yaml`.

## 2.6 Кластеризация исторической почты

Раздел описывает bootstrap пользовательских классов через кластеризацию
исторической выборки писем.

Раскрыть:

- HDBSCAN как основной алгоритм;
- KMeans как альтернативный режим;
- подбор параметров HDBSCAN через Optuna;
- сохраняемые метрики запуска: число кластеров, число выбросов, объём выборки,
  доля выбросов;
- выбор представителей кластеров;
- TF-IDF top terms для интерпретации;
- PNG-визуализацию кластеров как диагностический артефакт.

Иллюстрация: поток от `email_embeddings` к `cluster_runs`,
`cluster_assignments` и `cluster_summaries`.

Опорные материалы:

- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/clustering/pipeline.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/clustering/summaries.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/clustering/tuner.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/clustering/visualization.py`.

## 2.7 Ручная проверка и консолидация классов

Раздел описывает Argilla как локальный инструмент ревью результатов
кластеризации. Акцент делается на снижении объёма ручной работы: пользователь
проверяет представителей кластеров, а не каждое письмо.

Основной поток:

```text
ClusterRun -> representatives -> Argilla dataset -> user labels -> email_labels
```

Раскрыть:

- формирование набора записей для проверки;
- отображение темы, тела письма, отправителя и ключевых терминов кластера;
- создание новых классов при импорте ответов;
- распространение согласованной метки представителей на сообщения кластера;
- сохранение результата в `email_labels`;
- сохранение истории пакетов разметки в `annotation_batches`.

Опорные материалы:

- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/annotation/export.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/annotation/import_labels.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/annotation/contracts.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/docker-compose.yml`.

## 2.8 Обучение и инференс

Раздел должен честно разделять уже реализованные компоненты и следующий
интеграционный шаг.

Описать реализованное:

- базовый `MeanPoolingTextClassifier`;
- обучение по стабильному CSV-контракту `oid,text,label`;
- сохранение артефактов `model.pt`, `vocab.json`, `label_mapping.json`,
  `metrics.json`, `training_config.json`;
- загрузку сохранённого классификатора;
- получение предсказаний для новых текстов.

Отдельно зафиксировать архитектурное продолжение:

- данные из `email_labels` должны быть преобразованы в training snapshot;
- training snapshot должен стать входом для email-классификатора;
- этот переход не требует изменения модульной архитектуры, так как storage,
  training и inference уже разделены по ответственности.

Опорные материалы:

- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/training/train.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/models/text_classifier.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/inference/predict.py`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/src/diplom_ai/evaluation/metrics.py`.

## 2.9 Конфигурация, окружение и проверка

Раздел описывает воспроизводимость и инженерную проверяемость проекта.

Раскрыть:

- `configs/default.yaml` как основной контракт параметров;
- `.env` для секретов и локальных подключений;
- PostgreSQL и Argilla через Docker Compose;
- `.venv` для локального Python-окружения;
- команды проверки: `make test`, `make pytest`, `make lint`,
  `make typecheck`, `make check`;
- тесты по слоям: нормализация, IMAP, схема БД, репозитории, кластеризация,
  Argilla, пайплайн.

Опорные материалы:

- `/home/dyingsleeper/PycharmProjects/diplom2.0/Makefile`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/pyproject.toml`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/docs/local-venv-make.md`;
- `/home/dyingsleeper/PycharmProjects/diplom2.0/tests/`.

## 2.10 Выводы по главе

В выводах нужно кратко зафиксировать, что разработана модульная локальная
архитектура, закрывающая путь от получения писем до подготовленной разметки и
базового классификатора. Экспериментальные результаты, подбор параметров,
сравнение алгоритмов и оценку качества следует перенести в главу 3.

## Рекомендуемые иллюстрации и таблицы

- Рисунок 2.1: модульная архитектура приложения.
- Рисунок 2.2: поток данных от IMAP до разметки.
- Рисунок 2.3: схема кластеризации и выбора представителей.
- Таблица 2.1: модули проекта и их ответственность.
- Таблица 2.2: основные таблицы PostgreSQL и их назначение.
- Таблица 2.3: ключевые параметры `configs/default.yaml`.

## Ограничения текущей версии плана

- План не прошёл ревью.
- План не перенесён в `Dissertation/part2.tex`.
- План не содержит готового текста главы, а задаёт структуру и источники.
- Перед написанием главы нужно повторно сверить фактическое состояние
  `diplom2.0`, особенно блоки обучения и интеграции разметки в training snapshot.
