from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


@dataclass(frozen=True)
class TextClassifierConfig:
    vocab_size: int
    embedding_dim: int
    num_labels: int
    padding_idx: int = 0
    dropout: float = 0.1


class MeanPoolingTextClassifier(nn.Module):
    """Small baseline classifier for token id tensors."""

    def __init__(self, config: TextClassifierConfig) -> None:
        super().__init__()
        self.embedding = nn.Embedding(
            num_embeddings=config.vocab_size,
            embedding_dim=config.embedding_dim,
            padding_idx=config.padding_idx,
        )
        self.dropout = nn.Dropout(config.dropout)
        self.classifier = nn.Linear(config.embedding_dim, config.num_labels)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        embeddings = self.embedding(input_ids)
        mask = attention_mask.unsqueeze(-1).type_as(embeddings)
        summed = (embeddings * mask).sum(dim=1)
        counts = mask.sum(dim=1).clamp_min(1.0)
        pooled = summed / counts
        logits: torch.Tensor = self.classifier(self.dropout(pooled))
        return logits
