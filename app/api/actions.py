"""
Actions API Routes
------------------
POST endpoints for triggering operations.
"""

import logging
from functools import partial
from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.models import (
    ScanRequest,
    MarkReadRequest,
    DeleteScanRequest,
    UnsubscribeRequest,
    DeleteEmailsRequest,
    DeleteBulkRequest,
    DownloadEmailsRequest,
    CreateLabelRequest,
    ApplyLabelRequest,
    RemoveLabelRequest,
    ArchiveRequest,
    MarkImportantRequest,
    PreviewEmailsRequest,
)
from app.services import (
    scan_emails,
    get_gmail_service,
    sign_out,
    unsubscribe_single,
    mark_emails_as_read,
    scan_senders_for_delete,
    delete_emails_by_sender,
    delete_emails_bulk_background,
    download_emails_background,
    create_label,
    delete_label,
    apply_label_to_senders_background,
    remove_label_from_senders_background,
    archive_emails_background,
    mark_important_background,
    preview_emails_background,
)

router = APIRouter(prefix="/api", tags=["Actions"])
logger = logging.getLogger(__name__)


@router.post("/scan")
async def api_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """Start email scan for unsubscribe links."""
    filters_dict = (
        request.filters.model_dump(exclude_none=True) if request.filters else None
    )
    background_tasks.add_task(scan_emails, request.limit, filters_dict)
    return {"status": "started"}


@router.post("/sign-in")
async def api_sign_in(background_tasks: BackgroundTasks):
    """Trigger OAuth sign-in flow."""
    background_tasks.add_task(get_gmail_service)
    return {"status": "signing_in"}


@router.post("/sign-out")
async def api_sign_out():
    """Sign out and clear credentials."""
    try:
        return sign_out()
    except Exception as e:
        logger.exception("Error during sign-out")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sign out",
        ) from e


@router.post("/unsubscribe")
async def api_unsubscribe(request: UnsubscribeRequest):
    """Unsubscribe from a single sender."""
    try:
        return unsubscribe_single(request.domain, request.link)
    except Exception as e:
        logger.exception("Error during unsubscribe")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unsubscribe",
        ) from e


@router.post("/mark-read")
async def api_mark_read(request: MarkReadRequest, background_tasks: BackgroundTasks):
    """Mark emails as read."""
    filters_dict = (
        request.filters.model_dump(exclude_none=True) if request.filters else None
    )
    background_tasks.add_task(mark_emails_as_read, request.count, filters_dict)
    return {"status": "started"}


@router.post("/delete-scan")
async def api_delete_scan(
    request: DeleteScanRequest, background_tasks: BackgroundTasks
):
    """Scan senders for bulk delete."""
    filters_dict = (
        request.filters.model_dump(exclude_none=True) if request.filters else None
    )
    background_tasks.add_task(scan_senders_for_delete, request.limit, filters_dict)
    return {"status": "started"}


@router.post("/delete-emails")
async def api_delete_emails(request: DeleteEmailsRequest):
    """Delete emails from a specific sender."""
    if not request.sender or not request.sender.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sender email is required",
        )
    try:
        return delete_emails_by_sender(request.sender)
    except Exception as e:
        logger.exception("Error deleting emails")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete emails",
        ) from e


@router.post("/delete-emails-bulk")
async def api_delete_emails_bulk(
    request: DeleteBulkRequest, background_tasks: BackgroundTasks
):
    """Delete emails from multiple senders (background task with progress)."""
    background_tasks.add_task(delete_emails_bulk_background, request.senders)
    return {"status": "started"}


@router.post("/download-emails")
async def api_download_emails(
    request: DownloadEmailsRequest, background_tasks: BackgroundTasks
):
    """Start downloading email metadata for selected senders."""
    # Note: Empty list is allowed - service function will handle it gracefully
    background_tasks.add_task(download_emails_background, request.senders)
    return {"status": "started"}


# ----- Label Management Endpoints -----


@router.post("/labels")
async def api_create_label(request: CreateLabelRequest):
    """Create a new Gmail label."""
    try:
        return create_label(request.name)
    except Exception as e:
        logger.exception("Error creating label")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create label",
        ) from e


@router.delete("/labels/{label_id}")
async def api_delete_label(label_id: str):
    """Delete a Gmail label."""
    if not label_id or not label_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Label ID is required",
        )
    try:
        return delete_label(label_id)
    except Exception as e:
        logger.exception("Error deleting label")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete label",
        ) from e


@router.post("/apply-label")
async def api_apply_label(
    request: ApplyLabelRequest, background_tasks: BackgroundTasks
):
    """Apply a label to emails from selected senders."""
    if not request.label_id or not request.label_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Label ID is required",
        )
    if not request.senders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one sender is required",
        )
    background_tasks.add_task(
        apply_label_to_senders_background, request.label_id, request.senders
    )
    return {"status": "started"}


@router.post("/remove-label")
async def api_remove_label(
    request: RemoveLabelRequest, background_tasks: BackgroundTasks
):
    """Remove a label from emails from selected senders."""
    if not request.label_id or not request.label_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Label ID is required",
        )
    if not request.senders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one sender is required",
        )
    background_tasks.add_task(
        remove_label_from_senders_background, request.label_id, request.senders
    )
    return {"status": "started"}


@router.post("/archive")
async def api_archive(request: ArchiveRequest, background_tasks: BackgroundTasks):
    """Archive emails from selected senders (remove from inbox)."""
    if not request.senders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one sender is required",
        )
    background_tasks.add_task(archive_emails_background, request.senders)
    return {"status": "started"}


@router.post("/mark-important")
async def api_mark_important(
    request: MarkImportantRequest, background_tasks: BackgroundTasks
):
    """Mark/unmark emails from selected senders as important."""
    if not request.senders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one sender is required",
        )
    background_tasks.add_task(
        partial(mark_important_background, request.senders, important=request.important)
    )
    return {"status": "started"}


@router.post("/preview-emails")
async def api_preview_emails(request: PreviewEmailsRequest, background_tasks: BackgroundTasks):
    """Preview emails from a sender before deleting."""
    background_tasks.add_task(preview_emails_background, request.sender, request.limit)
    return {"status": "started"}


# ----- Cleanup Rules Endpoints -----


@router.get("/cleanup-rules")
async def api_get_cleanup_rules():
    """Get all cleanup rules."""
    from app.services.gmail.cleanup_rules import get_rules
    return get_rules()


@router.post("/cleanup-rules")
async def api_add_cleanup_rule(request: dict):
    """Add a new cleanup rule."""
    from app.services.gmail.cleanup_rules import add_rule
    return add_rule(
        sender=request.get("sender", ""),
        action=request.get("action", "delete"),
        schedule=request.get("schedule", "manual"),
        label_id=request.get("label_id")
    )


@router.delete("/cleanup-rules/{rule_id}")
async def api_delete_cleanup_rule(rule_id: str):
    """Delete a cleanup rule."""
    from app.services.gmail.cleanup_rules import delete_rule
    delete_rule(rule_id)
    return {"success": True}


@router.post("/cleanup-rules/{rule_id}/toggle")
async def api_toggle_cleanup_rule(rule_id: str):
    """Toggle a cleanup rule on/off."""
    from app.services.gmail.cleanup_rules import toggle_rule
    result = toggle_rule(rule_id)
    if not result:
        raise HTTPException(status_code=404, detail="Rule not found")
    return result


@router.post("/cleanup-rules/{rule_id}/run")
async def api_run_cleanup_rule(rule_id: str):
    """Run a cleanup rule immediately."""
    from app.services.gmail.cleanup_rules import run_rule
    return run_rule(rule_id)
