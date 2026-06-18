from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np

from diplom_ai.clustering.contracts import (
    EmailEmbeddingDraft,
    SourceFilter,
)
from diplom_ai.email.contracts import NormalizedEmailRecord
from diplom_ai.storage.repositories import ClusteringRepository


@dataclass(frozen=True)
class EmbeddingsConfig:
    model: str
    version: str
    batch_size: int
    artifacts_dir: str


@dataclass(frozen=True)
class EmbeddingResult:
    computed: int
    skipped: int
    vector_path: str
    total_rows: int


class EmbeddingEncoder(Protocol):
    def encode_batch(self, texts: list[str]) -> np.ndarray: ...


_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9_]")


def model_safe_filename(model_name: str) -> str:
    name = model_name.replace("/", "__")
    return _UNSAFE_CHARS.sub("_", name)


def vector_path_for(config: EmbeddingsConfig, mailbox_id: str) -> Path:
    return (
        Path(config.artifacts_dir)
        / mailbox_id
        / model_safe_filename(config.model)
        / f"{config.version}.npz"
    )


def write_vectors(vector_path: Path, vectors: np.ndarray) -> None:
    vector_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_stem = vector_path.parent / (vector_path.stem + ".tmp")
    np.savez(tmp_stem, vectors=vectors)
    os.replace(str(tmp_stem) + ".npz", vector_path)


def load_sentence_transformer_encoder(
    model: str, device: str
) -> EmbeddingEncoder:
    from sentence_transformers import SentenceTransformer

    model_obj = SentenceTransformer(model, device=device)

    class _Encoder:
        def encode_batch(self, texts: list[str]) -> np.ndarray:
            arr = model_obj.encode(
                texts,
                batch_size=len(texts),
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            return np.asarray(arr, dtype=np.float32)

    return _Encoder()


def compute_pending_embeddings(
    *,
    clustering_repository: ClusteringRepository,
    config: EmbeddingsConfig,
    mailbox_id: str,
    source_filter: SourceFilter,
    encoder: EmbeddingEncoder,
    limit: int | None,
) -> EmbeddingResult:
    list_pending = (
        clustering_repository.list_pending_normalized_emails_for_embedding
    )
    pending = list_pending(
        mailbox_id=mailbox_id,
        embedding_model=config.model,
        embedding_version=config.version,
        source_filter=source_filter,
        limit=limit,
    )
    vector_path = vector_path_for(config, mailbox_id)
    existing_count = _count_existing_embeddings(
        clustering_repository=clustering_repository,
        mailbox_id=mailbox_id,
        config=config,
        source_filter=source_filter,
    )
    if not pending:
        total_rows = _row_count(vector_path)
        return EmbeddingResult(
            computed=0,
            skipped=existing_count,
            vector_path=str(vector_path),
            total_rows=total_rows,
        )

    batches: list[np.ndarray] = []
    chunks = _chunk(pending, config.batch_size)
    for batch in chunks:
        texts = [record.normalized_text for record in batch]
        batches.append(encoder.encode_batch(texts))
    new_matrix = np.vstack(batches)
    start_row = _merge_and_write(vector_path, new_matrix)

    for offset, record in enumerate(pending):
        clustering_repository.save_email_embedding(
            EmailEmbeddingDraft(
                normalized_email_id=record.id,
                mailbox_id=mailbox_id,
                embedding_model=config.model,
                embedding_version=config.version,
                vector_dim=int(new_matrix.shape[1]),
                vector_path=str(vector_path),
                vector_row=start_row + offset,
            )
        )

    return EmbeddingResult(
        computed=len(pending),
        skipped=existing_count,
        vector_path=str(vector_path),
        total_rows=start_row + len(pending),
    )


def _merge_and_write(vector_path: Path, new_vectors: np.ndarray) -> int:
    if vector_path.exists():
        existing = np.load(vector_path)["vectors"]
        final = np.vstack([existing, new_vectors])
        start_row = int(existing.shape[0])
    else:
        final = new_vectors
        start_row = 0
    write_vectors(vector_path, final)
    return start_row


def _chunk(
    records: list[NormalizedEmailRecord], size: int
) -> list[list[NormalizedEmailRecord]]:
    return [records[i : i + size] for i in range(0, len(records), size)]


def _row_count(vector_path: Path) -> int:
    if not vector_path.exists():
        return 0
    return int(np.load(vector_path)["vectors"].shape[0])


def _count_existing_embeddings(
    *,
    clustering_repository: ClusteringRepository,
    mailbox_id: str,
    config: EmbeddingsConfig,
    source_filter: SourceFilter,
) -> int:
    return len(
        clustering_repository.list_email_embeddings(
            mailbox_id=mailbox_id,
            embedding_model=config.model,
            embedding_version=config.version,
            source_filter=source_filter,
        )
    )
