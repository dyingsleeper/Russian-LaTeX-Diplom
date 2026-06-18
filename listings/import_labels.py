from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from diplom_ai.annotation.contracts import (
    NEW_CLASS_SENTINEL,
    AnnotationBatchStatus,
    AnnotationError,
    AnnotationResponse,
    ClassLabelDraft,
    ClassLabelRecord,
    EmailLabelDraft,
    ImportSummary,
)
from diplom_ai.storage.repositories import AnnotationRepository

if TYPE_CHECKING:
    from diplom_ai.annotation.argilla_client import ArgillaClient

_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_label_name(raw: str) -> str:
    return _WHITESPACE_RE.sub(" ", raw.strip().lower())


def _member_source(member_id: int, rep_ids: set[int]) -> str:
    return "rep_direct" if member_id in rep_ids else "cluster_propagation"


@dataclass(frozen=True)
class ResolutionOutcome:
    class_label_id: int | None
    created_new: bool
    warning: str | None


def resolve_class_label(
    *,
    response: AnnotationResponse,
    mailbox_id: str,
    repository: AnnotationRepository,
    labels_by_name: dict[str, ClassLabelRecord],
) -> ResolutionOutcome:
    proposed = response.proposed_new_class.strip()
    if proposed:
        normalized = _normalize_label_name(proposed)
        cached = labels_by_name.get(normalized)
        if cached is not None:
            return ResolutionOutcome(
                class_label_id=cached.id, created_new=False, warning=None
            )
        record = repository.upsert_class_label(
            ClassLabelDraft(
                mailbox_id=mailbox_id,
                name=normalized,
                display_name=proposed,
                origin="argilla_proposed",
            )
        )
        labels_by_name[normalized] = record
        return ResolutionOutcome(
            class_label_id=record.id, created_new=True, warning=None
        )

    if response.label == NEW_CLASS_SENTINEL:
        return ResolutionOutcome(
            class_label_id=None,
            created_new=False,
            warning=(
                f"email={response.normalized_email_id}: "
                "new class selected without name"
            ),
        )

    normalized = _normalize_label_name(response.label)
    cached = labels_by_name.get(normalized)
    if cached is not None:
        return ResolutionOutcome(
            class_label_id=cached.id, created_new=False, warning=None
        )
    return ResolutionOutcome(
        class_label_id=None,
        created_new=False,
        warning=(
            f"email={response.normalized_email_id}: "
            f"unknown label {response.label!r}"
        ),
    )


@dataclass(frozen=True)
class ClusterAggregation:
    cluster_id: int
    disagreement: bool
    drafts: list[EmailLabelDraft]


def aggregate_cluster_labels(
    *,
    mailbox_id: str,
    annotation_batch_id: int,
    cluster_run_id: int,
    cluster_id: int,
    other_label_id: int,
    rep_class_label_by_id: dict[int, int],
    cluster_member_ids: list[int],
) -> ClusterAggregation:
    if not rep_class_label_by_id:
        return ClusterAggregation(
            cluster_id=cluster_id, disagreement=False, drafts=[]
        )

    distinct_labels = set(rep_class_label_by_id.values())
    if len(distinct_labels) > 1:
        drafts = [
            EmailLabelDraft(
                normalized_email_id=member_id,
                mailbox_id=mailbox_id,
                class_label_id=other_label_id,
                annotation_batch_id=annotation_batch_id,
                source="disagreement_other",
                cluster_run_id=cluster_run_id,
                cluster_id=cluster_id,
            )
            for member_id in cluster_member_ids
        ]
        return ClusterAggregation(
            cluster_id=cluster_id, disagreement=True, drafts=drafts
        )

    (consensus_label_id,) = distinct_labels
    rep_ids = set(rep_class_label_by_id)
    drafts = [
            EmailLabelDraft(
                normalized_email_id=member_id,
                mailbox_id=mailbox_id,
                class_label_id=consensus_label_id,
                annotation_batch_id=annotation_batch_id,
                source=_member_source(member_id, rep_ids),
                cluster_run_id=cluster_run_id,
                cluster_id=cluster_id,
            )
        for member_id in cluster_member_ids
    ]
    return ClusterAggregation(
        cluster_id=cluster_id, disagreement=False, drafts=drafts
    )


def import_annotations(
    *,
    annotation_repository: AnnotationRepository,
    client: ArgillaClient,
    batch_id: int,
) -> ImportSummary:
    batch = annotation_repository.get_annotation_batch(batch_id)
    if batch is None:
        raise AnnotationError(
            "db_write_failed",
            f"annotation_batch {batch_id} not found",
        )
    already_imported = (
        batch.status == "imported"
        and batch.responses_imported >= batch.records_exported
    )
    if already_imported:
        return ImportSummary(
            responses_total=batch.responses_imported,
            responses_skipped=0,
            classes_new=0,
            clusters_propagated=0,
            clusters_disagreement=0,
            outliers_labeled=0,
            email_labels_written=batch.labels_propagated,
            warnings=[f"batch {batch_id} already imported"],
        )

    try:
        raw_responses = client.fetch_submitted_responses(
            dataset_name=batch.argilla_dataset,
            workspace_name=batch.argilla_workspace,
        )
    except Exception as exc:
        annotation_repository.mark_batch_status(
            batch_id,
            status="failed",
            error_code="argilla_unreachable",
            error_message=str(exc),
        )
        raise AnnotationError("argilla_unreachable", str(exc)) from exc

    other_label = annotation_repository.ensure_system_other_label(
        mailbox_id=batch.mailbox_id
    )
    list_labels = annotation_repository.list_class_labels
    labels_by_name = {
        r.name: r for r in list_labels(mailbox_id=batch.mailbox_id)
    }
    warnings: list[str] = []
    classes_new = 0
    resolved: dict[int, int] = {}

    for raw in raw_responses:
        try:
            normalized_email_id = int(raw["record_id"])
        except (TypeError, ValueError):
            warnings.append(
                f"skip record_id={raw.get('record_id')!r}: not int"
            )
            continue
        response = AnnotationResponse(
            normalized_email_id=normalized_email_id,
            label=raw.get("label") or "",
            proposed_new_class=raw.get("proposed_new_class") or "",
        )
        outcome = resolve_class_label(
            response=response,
            mailbox_id=batch.mailbox_id,
            repository=annotation_repository,
            labels_by_name=labels_by_name,
        )
        if outcome.warning is not None:
            warnings.append(outcome.warning)
        if outcome.created_new:
            classes_new += 1
        proposed_name = response.proposed_new_class.strip()
        if proposed_name and outcome.class_label_id is not None:
            label_name = _normalize_label_name(proposed_name)
            try:
                client.add_label_options(
                    dataset_name=batch.argilla_dataset,
                    workspace_name=batch.argilla_workspace,
                    label_names=[label_name],
                )
            except Exception as exc:
                annotation_repository.mark_batch_status(
                    batch_id,
                    status="failed",
                    error_code="argilla_unreachable",
                    error_message=str(exc),
                )
                raise AnnotationError(
                    "argilla_unreachable", str(exc)
                ) from exc
        if outcome.class_label_id is None:
            continue
        resolved[normalized_email_id] = outcome.class_label_id

    responses_total = len(raw_responses)
    responses_skipped = responses_total - len(resolved)

    list_assignments = (
        annotation_repository.list_cluster_assignments_for_export
    )
    rep_candidates = list_assignments(cluster_run_id=batch.cluster_run_id)
    rep_clusters: dict[int, list[int]] = {}
    outlier_ids: set[int] = set()
    for candidate in rep_candidates:
        if candidate.is_outlier:
            outlier_ids.add(candidate.normalized_email_id)
        elif candidate.is_representative:
            rep_clusters.setdefault(candidate.cluster_id, []).append(
                candidate.normalized_email_id
            )

    clusters_propagated = 0
    clusters_disagreement = 0
    outliers_labeled = 0
    all_drafts: list[EmailLabelDraft] = []

    for cluster_id, rep_ids in rep_clusters.items():
        if any(rep_id not in resolved for rep_id in rep_ids):
            continue
        rep_class_label_by_id = {
            rep_id: resolved[rep_id] for rep_id in rep_ids
        }
        list_members = (
            annotation_repository.list_normalized_email_ids_in_cluster
        )
        member_ids = list_members(
            cluster_run_id=batch.cluster_run_id, cluster_id=cluster_id
        )
        aggregation = aggregate_cluster_labels(
            mailbox_id=batch.mailbox_id,
            annotation_batch_id=batch_id,
            cluster_run_id=batch.cluster_run_id,
            cluster_id=cluster_id,
            other_label_id=other_label.id,
            rep_class_label_by_id=rep_class_label_by_id,
            cluster_member_ids=member_ids,
        )
        all_drafts.extend(aggregation.drafts)
        if aggregation.disagreement:
            clusters_disagreement += 1
        else:
            clusters_propagated += 1

    for outlier_id in outlier_ids:
        if outlier_id not in resolved:
            continue
        all_drafts.append(
            EmailLabelDraft(
                normalized_email_id=outlier_id,
                mailbox_id=batch.mailbox_id,
                class_label_id=resolved[outlier_id],
                annotation_batch_id=batch_id,
                source="outlier_direct",
                cluster_run_id=batch.cluster_run_id,
                cluster_id=None,
            )
        )
        outliers_labeled += 1

    try:
        written = annotation_repository.save_email_labels(all_drafts)
    except Exception as exc:
        annotation_repository.mark_batch_status(
            batch_id,
            status="failed",
            error_code="db_write_failed",
            error_message=str(exc),
        )
        raise AnnotationError("db_write_failed", str(exc)) from exc

    batch_complete = responses_total >= batch.records_exported
    final_status: AnnotationBatchStatus = (
        "imported" if batch_complete else "exported"
    )
    annotation_repository.mark_batch_status(
        batch_id,
        status=final_status,
        error_code="",
        error_message="",
        responses_imported=len(resolved),
        labels_propagated=batch.labels_propagated + written,
    )

    return ImportSummary(
        responses_total=responses_total,
        responses_skipped=responses_skipped,
        classes_new=classes_new,
        clusters_propagated=clusters_propagated,
        clusters_disagreement=clusters_disagreement,
        outliers_labeled=outliers_labeled,
        email_labels_written=written,
        warnings=warnings,
    )
