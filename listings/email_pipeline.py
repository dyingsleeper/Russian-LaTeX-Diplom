from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

from app.queueing.contracts import (
    PipelineTaskRepository,
    TaskDraft,
)
from app.queueing.tasks import DrainSummary, HandlerContext
from app.storage.repositories import EmailRepository

ClusterMode = Literal["never", "auto", "always"]


@dataclass
class PipelineDependencies:
    email_repository: EmailRepository
    clustering_repository: Any
    task_repository: PipelineTaskRepository
    handler_context: HandlerContext
    drain: Callable[..., DrainSummary]
    max_attempts: int
    base_backoff_seconds: int
    ingest_imap: Callable[..., Any]
    eligible_embedding_count: Callable[..., int]
    latest_completed_cluster_coverage: Callable[..., int | None]
    embeddings_identity: Callable[[], tuple[str, str]]


def run_bootstrap_pipeline(
    *,
    config_path: str,
    mailbox_id: str,
    cluster_mode: ClusterMode,
    allow_partial: bool,
    deps: PipelineDependencies,
) -> dict[str, Any]:
    from loguru import logger

    logger.info(
        "email pipeline bootstrap started mailbox={} cluster_mode={} allow_partial={}",
        mailbox_id,
        cluster_mode,
        allow_partial,
    )
    summary: dict[str, Any] = {"mailbox": mailbox_id, "mode": "bootstrap"}

    deps.task_repository.reset_running_to_pending()

    summary["ingestion"] = _run_ingestion(deps=deps, mailbox_id=mailbox_id)

    normalization = _run_normalize_stage(deps=deps, mailbox_id=mailbox_id)
    summary["normalization"] = normalization
    if normalization["emails_failed"] > 0 and not allow_partial:
        summary["next_action"] = "fix_failed_tasks"
        logger.info(
            "email pipeline bootstrap stopped mailbox={} next_action={}",
            mailbox_id,
            summary["next_action"],
        )
        return summary

    embeddings = _run_embed_stage(deps=deps, mailbox_id=mailbox_id)
    summary["embeddings"] = embeddings
    if embeddings["tasks_failed"] > 0:
        summary["next_action"] = "fix_failed_tasks"
        logger.info(
            "email pipeline bootstrap stopped mailbox={} next_action={}",
            mailbox_id,
            summary["next_action"],
        )
        return summary

    summary["clustering"] = _decide_and_run_clustering(
        deps=deps, mailbox_id=mailbox_id, cluster_mode=cluster_mode
    )
    summary["next_action"] = _bootstrap_next_action(summary)
    logger.info(
        "email pipeline bootstrap completed mailbox={} next_action={}",
        mailbox_id,
        summary["next_action"],
    )
    return summary


def _run_ingestion(
    *,
    deps: PipelineDependencies,
    mailbox_id: str,
) -> dict[str, Any]:
    from loguru import logger

    logger.info("email pipeline ingestion started mailbox={}", mailbox_id)
    result = deps.ingest_imap(mailbox_id=mailbox_id)
    logger.info(
        "email pipeline ingestion completed mailbox={} imported={} skipped={} failed={}",
        mailbox_id,
        result.imported,
        result.skipped,
        result.failed,
    )
    return {
        "source": "imap",
        "imported": result.imported,
        "skipped": result.skipped,
        "failed": result.failed,
    }


def _run_normalize_stage(
    *, deps: PipelineDependencies, mailbox_id: str
) -> dict[str, int]:
    from loguru import logger

    logger.info("email pipeline normalization started mailbox={}", mailbox_id)
    pending = deps.email_repository.list_raw_emails(
        mailbox_id=mailbox_id, status="pending"
    )
    logger.info(
        "email pipeline normalization pending mailbox={} count={}",
        mailbox_id,
        len(pending),
    )
    enqueued = 0
    for raw in pending:
        deps.task_repository.enqueue(
            TaskDraft(
                task_name="normalize_email",
                dedupe_key=f"raw_email:{raw.id}",
                payload={"raw_email_id": raw.id},
            )
        )
        enqueued += 1
    drain_summary = deps.drain(
        task_repository=deps.task_repository,
        handler_context=deps.handler_context,
        max_attempts=deps.max_attempts,
        base_backoff_seconds=deps.base_backoff_seconds,
    )
    by = drain_summary.by_task.get("normalize_email", {})
    result = {
        "tasks_enqueued": enqueued,
        "tasks_failed": by.get("failed", 0),
        "emails_completed": by.get("completed", 0),
        "emails_failed": by.get("failed", 0),
    }
    logger.info(
        "email pipeline normalization completed mailbox={} enqueued={} completed={} failed={}",
        mailbox_id,
        result["tasks_enqueued"],
        result["emails_completed"],
        result["emails_failed"],
    )
    return result


def _run_embed_stage(
    *, deps: PipelineDependencies, mailbox_id: str
) -> dict[str, int]:
    from loguru import logger

    logger.info("email pipeline embeddings started mailbox={}", mailbox_id)
    model, version = deps.embeddings_identity()
    deps.task_repository.enqueue(
        TaskDraft(
            task_name="embed_pending_emails",
            dedupe_key=f"embed:{mailbox_id}:{model}:{version}",
            payload={
                "mailbox_id": mailbox_id,
                "embedding_model": model,
                "embedding_version": version,
            },
        )
    )
    before = deps.eligible_embedding_count(mailbox_id=mailbox_id)
    logger.info(
        "email pipeline embeddings before mailbox={} existing={}",
        mailbox_id,
        before,
    )
    drain_summary = deps.drain(
        task_repository=deps.task_repository,
        handler_context=deps.handler_context,
        max_attempts=deps.max_attempts,
        base_backoff_seconds=deps.base_backoff_seconds,
    )
    after = deps.eligible_embedding_count(mailbox_id=mailbox_id)
    by = drain_summary.by_task.get("embed_pending_emails", {})
    result = {
        "tasks_enqueued": 1,
        "tasks_failed": by.get("failed", 0),
        "emails_computed": max(after - before, 0),
        "emails_skipped": before,
    }
    logger.info(
        "email pipeline embeddings completed mailbox={} computed={} skipped={} failed={}",
        mailbox_id,
        result["emails_computed"],
        result["emails_skipped"],
        result["tasks_failed"],
    )
    return result


def _decide_and_run_clustering(
    *,
    deps: PipelineDependencies,
    mailbox_id: str,
    cluster_mode: ClusterMode,
) -> dict[str, Any]:
    from loguru import logger

    logger.info(
        "email pipeline clustering started mailbox={} mode={}",
        mailbox_id,
        cluster_mode,
    )
    if cluster_mode == "never":
        logger.info(
            "email pipeline clustering completed mailbox={} decision=skipped_by_mode",
            mailbox_id,
        )
        return {"decision": "skipped_by_mode"}
    eligible = deps.eligible_embedding_count(mailbox_id=mailbox_id)
    logger.info(
        "email pipeline clustering eligible mailbox={} count={}",
        mailbox_id,
        eligible,
    )
    if cluster_mode == "auto":
        coverage = deps.latest_completed_cluster_coverage(mailbox_id=mailbox_id)
        if coverage is not None and coverage >= eligible:
            logger.info(
                "email pipeline clustering completed mailbox={} decision=skipped_up_to_date",
                mailbox_id,
            )
            return {"decision": "skipped_up_to_date"}
    config_hash = _build_config_hash(deps)
    deps.task_repository.enqueue(
        TaskDraft(
            task_name="run_clustering",
            dedupe_key=f"cluster:{mailbox_id}:{config_hash}",
            payload={"mailbox_id": mailbox_id},
        )
    )
    drain_summary = deps.drain(
        task_repository=deps.task_repository,
        handler_context=deps.handler_context,
        max_attempts=deps.max_attempts,
        base_backoff_seconds=deps.base_backoff_seconds,
    )
    by = drain_summary.by_task.get("run_clustering", {})
    if by.get("failed"):
        logger.info(
            "email pipeline clustering completed mailbox={} decision=failed failed={}",
            mailbox_id,
            by["failed"],
        )
        return {"decision": "failed", "tasks_failed": by["failed"]}
    logger.info("email pipeline clustering completed mailbox={} decision=ran", mailbox_id)
    return {"decision": "ran"}


def _build_config_hash(deps: PipelineDependencies) -> str:
    model, version = deps.embeddings_identity()
    return f"{model}:{version}"


def _bootstrap_next_action(summary: dict[str, Any]) -> str:
    clustering = summary.get("clustering", {})
    decision = clustering.get("decision")
    if decision == "ran":
        return "review_clusters"
    if decision == "failed":
        return "fix_failed_tasks"
    if decision in ("skipped_by_mode", "skipped_up_to_date"):
        return "ready_for_annotation_phase"
    return "nothing_to_do"


def run_run_pipeline(
    *,
    config_path: str,
    mailbox_id: str,
    cluster_mode: ClusterMode,
    allow_partial: bool,
    deps: PipelineDependencies,
) -> dict[str, Any]:
    from loguru import logger

    logger.info(
        "email pipeline run started mailbox={} cluster_mode={} allow_partial={}",
        mailbox_id,
        cluster_mode,
        allow_partial,
    )
    summary: dict[str, Any] = {"mailbox": mailbox_id, "mode": "run"}
    deps.task_repository.reset_running_to_pending()
    summary["ingestion"] = _run_ingestion(deps=deps, mailbox_id=mailbox_id)
    normalization = _run_normalize_stage(deps=deps, mailbox_id=mailbox_id)
    summary["normalization"] = normalization
    if normalization["emails_failed"] > 0 and not allow_partial:
        summary["next_action"] = "fix_failed_tasks"
        logger.info(
            "email pipeline run stopped mailbox={} next_action={}",
            mailbox_id,
            summary["next_action"],
        )
        return summary
    embeddings = _run_embed_stage(deps=deps, mailbox_id=mailbox_id)
    summary["embeddings"] = embeddings
    if embeddings["tasks_failed"] > 0:
        summary["next_action"] = "fix_failed_tasks"
        logger.info(
            "email pipeline run stopped mailbox={} next_action={}",
            mailbox_id,
            summary["next_action"],
        )
        return summary
    summary["clustering"] = _decide_and_run_clustering(
        deps=deps, mailbox_id=mailbox_id, cluster_mode=cluster_mode
    )
    summary["next_action"] = _bootstrap_next_action(summary)
    logger.info(
        "email pipeline run completed mailbox={} next_action={}",
        mailbox_id,
        summary["next_action"],
    )
    return summary


def build_status_report(
    *,
    mailbox_id: str,
    email_repository: EmailRepository,
    clustering_repository: Any,  # noqa: ARG001
    task_repository: PipelineTaskRepository,
    embeddings_identity: Callable[[], tuple[str, str]],
) -> dict[str, Any]:
    model, version = embeddings_identity()
    pending_raw = email_repository.list_raw_emails(
        mailbox_id=mailbox_id, status="pending"
    )
    failed_raw = email_repository.list_raw_emails(
        mailbox_id=mailbox_id, status="failed"
    )
    return {
        "mailbox": mailbox_id,
        "tasks": task_repository.status_counts(),
        "failed_tasks": [
            {
                "id": t.id,
                "task_name": t.task_name,
                "attempts": t.attempts,
                "error_code": t.error_code,
            }
            for t in task_repository.list_failed()
        ],
        "raw_emails": {
            "pending": len(pending_raw),
            "failed": len(failed_raw),
        },
        "embeddings": {
            "model": model,
            "version": version,
        },
    }
