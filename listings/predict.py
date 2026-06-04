from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from diplom_ai.training.text_vectorizer import attention_mask, encode_text


def top_label(logits: Sequence[float], labels: Sequence[str]) -> str:
    if len(logits) != len(labels):
        raise ValueError("logits and labels must have the same length")
    index = max(range(len(logits)), key=lambda item: logits[item])
    return labels[index]


@dataclass
class SavedTextClassifier:
    model: Any
    vocabulary: dict[str, int]
    labels: list[str]
    max_length: int
    device: str

    def predict(self, texts: Sequence[str]) -> list[str]:
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
            predictions = logits.argmax(dim=1).cpu().tolist()

        return [self.labels[int(index)] for index in predictions]


def load_saved_classifier(artifact_dir: str | Path, device: str = "cpu") -> SavedTextClassifier:
    import torch

    from diplom_ai.models.text_classifier import MeanPoolingTextClassifier, TextClassifierConfig

    run_dir = Path(artifact_dir)
    training_config = _read_json(run_dir / "training_config.json")
    vocabulary_payload = _read_json(run_dir / "vocab.json")
    label_payload = _read_json(run_dir / "label_mapping.json")

    classification = training_config.get("classification")
    if not isinstance(classification, dict):
        raise ValueError(f"Invalid training_config.json in {run_dir}")
    token_to_id = vocabulary_payload.get("token_to_id")
    labels = label_payload.get("labels")
    if (
        not isinstance(token_to_id, dict)
        or not all(isinstance(key, str) for key in token_to_id)
        or not all(isinstance(value, int) for value in token_to_id.values())
    ):
        raise ValueError(f"Invalid vocab.json in {run_dir}")
    if not isinstance(labels, list) or not all(isinstance(label, str) for label in labels):
        raise ValueError(f"Invalid label_mapping.json in {run_dir}")
    token_to_id_map = cast(dict[str, int], token_to_id)
    label_list = cast(list[str], labels)

    torch_device = torch.device(device)
    model = MeanPoolingTextClassifier(
        TextClassifierConfig(
            vocab_size=int(classification["vocab_size"]),
            embedding_dim=int(classification["embedding_dim"]),
            num_labels=int(classification["num_labels"]),
            padding_idx=int(classification.get("padding_idx", 0)),
            dropout=float(classification.get("dropout", 0.1)),
        )
    ).to(torch_device)
    state_dict = torch.load(run_dir / "model.pt", map_location=torch_device)
    model.load_state_dict(state_dict)

    return SavedTextClassifier(
        model=model,
        vocabulary=dict(token_to_id_map),
        labels=label_list,
        max_length=int(classification["max_length"]),
        device=device,
    )


def _read_json(path: Path) -> dict[str, object]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return loaded
