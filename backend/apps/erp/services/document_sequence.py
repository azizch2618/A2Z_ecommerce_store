"""Configurable atomic document numbering."""
from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.erp.models import Company, DocumentSequence


class DocumentSequenceService:
    DEFAULT_PATTERNS: dict[str, dict] = {
        "SO": {"prefix": "SO-", "name": "Sales Order", "pattern": "{prefix}{year}-{seq}"},
        "PO": {"prefix": "PO-", "name": "Purchase Order", "pattern": "{prefix}{year}-{seq}"},
        "PR": {"prefix": "PR-", "name": "Purchase Request", "pattern": "{prefix}{year}-{seq}"},
        "INV": {"prefix": "INV-", "name": "Invoice", "pattern": "{prefix}{year}-{seq}"},
        "QT": {"prefix": "QT-", "name": "Quote", "pattern": "{prefix}{year}-{seq}"},
        "GRN": {"prefix": "GRN-", "name": "Goods Receipt", "pattern": "{prefix}{year}-{seq}"},
        "ST": {"prefix": "ST-", "name": "Stock Transfer", "pattern": "{prefix}{year}-{seq}"},
        "PK": {"prefix": "PK-", "name": "Pick List", "pattern": "{prefix}{year}-{seq}"},
        "PT": {"prefix": "PT-", "name": "Putaway Task", "pattern": "{prefix}{year}-{seq}"},
        "CC": {"prefix": "CC-", "name": "Cycle Count", "pattern": "{prefix}{year}-{seq}"},
        "ADJ": {"prefix": "ADJ-", "name": "Inventory Adjustment", "pattern": "{prefix}{year}-{seq}"},
        "TA": {"prefix": "TA-", "name": "Trade Account", "pattern": "{prefix}{seq}"},
        "JE": {"prefix": "JE-", "name": "Journal Entry", "pattern": "{prefix}{year}-{seq}"},
        "AP": {"prefix": "AP-", "name": "AP Invoice", "pattern": "{prefix}{year}-{seq}"},
        "RP": {"prefix": "RP-", "name": "AR Payment", "pattern": "{prefix}{year}-{seq}"},
        "PP": {"prefix": "PP-", "name": "AP Payment", "pattern": "{prefix}{year}-{seq}"},
        "CN": {"prefix": "CN-", "name": "Credit Note", "pattern": "{prefix}{year}-{seq}"},
        "DN": {"prefix": "DN-", "name": "Debit Note", "pattern": "{prefix}{year}-{seq}"},
        "EMP": {"prefix": "EMP-", "name": "Employee", "pattern": "{prefix}{year}-{seq}"},
        "LR": {"prefix": "LR-", "name": "Leave Request", "pattern": "{prefix}{year}-{seq}"},
        "HA": {"prefix": "HA-", "name": "HRM Asset", "pattern": "{prefix}{year}-{seq}"},
    }

    @staticmethod
    def get_default_company() -> Company | None:
        return Company.objects.filter(is_default=True, is_active=True).first()

    @classmethod
    def ensure_sequences(cls, *, company: Company | None = None) -> None:
        company = company or cls.get_default_company()
        for code, spec in cls.DEFAULT_PATTERNS.items():
            DocumentSequence.objects.get_or_create(
                company=company,
                code=code,
                defaults={
                    "name": spec["name"],
                    "prefix": spec["prefix"],
                    "pattern": spec["pattern"],
                    "reset_period": DocumentSequence.ResetPeriod.YEARLY
                    if "{year}" in spec["pattern"]
                    else DocumentSequence.ResetPeriod.NEVER,
                    "padding": 6 if "{year}" in spec["pattern"] else 8,
                },
            )

    @classmethod
    @transaction.atomic
    def next_number(cls, code: str, *, company: Company | None = None) -> str:
        from apps.erp.bootstrap import ensure_foundation

        ensure_foundation()
        company = company or cls.get_default_company()
        sequence = (
            DocumentSequence.objects.select_for_update()
            .filter(code=code, company=company, is_active=True)
            .first()
        )
        if sequence is None:
            cls.ensure_sequences(company=company)
            sequence = DocumentSequence.objects.select_for_update().get(
                code=code,
                company=company,
            )

        now = timezone.localdate()
        reset_key = ""
        if sequence.reset_period == DocumentSequence.ResetPeriod.YEARLY:
            reset_key = str(now.year)
        elif sequence.reset_period == DocumentSequence.ResetPeriod.MONTHLY:
            reset_key = now.strftime("%Y%m")

        if reset_key and sequence.last_reset_key != reset_key:
            sequence.next_value = 1
            sequence.last_reset_key = reset_key

        seq_value = sequence.next_value
        sequence.next_value += 1
        sequence.save(update_fields=["next_value", "last_reset_key", "updated_at"])

        return cls._format_number(sequence, seq_value, now)

    @staticmethod
    def _format_number(sequence: DocumentSequence, seq_value: int, today) -> str:
        formatted_seq = str(seq_value).zfill(sequence.padding)
        return sequence.pattern.format(
            prefix=sequence.prefix,
            year=str(today.year),
            month=f"{today.month:02d}",
            seq=formatted_seq,
        )

    @classmethod
    def preview_next(cls, code: str, *, company: Company | None = None) -> str:
        """Non-mutating preview of the next number."""
        company = company or cls.get_default_company()
        sequence = DocumentSequence.objects.filter(code=code, company=company).first()
        if sequence is None:
            spec = cls.DEFAULT_PATTERNS.get(code, {"prefix": f"{code}-", "pattern": "{prefix}{seq}"})
            return spec["pattern"].format(
                prefix=spec.get("prefix", f"{code}-"),
                year=str(timezone.localdate().year),
                month=f"{timezone.localdate().month:02d}",
                seq=str(1).zfill(6),
            )
        return cls._format_number(sequence, sequence.next_value, timezone.localdate())
