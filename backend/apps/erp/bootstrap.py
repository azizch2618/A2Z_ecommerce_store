"""Idempotent ERP foundation bootstrap for runtime and tests."""
from __future__ import annotations

from apps.erp.models import Company, WorkflowDefinition


def ensure_foundation() -> None:
    """Ensure default company, sequences, and workflow definitions exist."""
    if Company.objects.filter(is_default=True).exists() and WorkflowDefinition.objects.exists():
        return

    from django.core.management import call_command

    call_command("seed_erp_foundation", verbosity=0)
