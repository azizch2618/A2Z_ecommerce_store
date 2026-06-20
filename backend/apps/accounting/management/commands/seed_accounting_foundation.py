"""Seed chart of accounts, fiscal periods, and event mappings."""
from datetime import date

from django.core.management.base import BaseCommand

from apps.accounting.services import AccountingFoundationSeed, FiscalPeriodService
from apps.erp.models import Company
from apps.erp.services.document_sequence import DocumentSequenceService


class Command(BaseCommand):
    help = "Seed accounting foundation — COA, fiscal year, event mappings, JE sequence."

    def handle(self, *args, **options):
        company = Company.objects.filter(is_default=True, is_active=True).first()
        if not company:
            self.stderr.write("No default company — run seed_erp_foundation first.")
            return

        DocumentSequenceService.ensure_sequences(company=company)
        AccountingFoundationSeed.seed_company(company=company)
        AccountingFoundationSeed.seed_event_mappings()

        # AU fiscal year starting July if not exists
        if not company.fiscal_years.exists():
            start_month = company.fiscal_year_start_month or 7
            today = date.today()
            fy_start_year = today.year if today.month >= start_month else today.year - 1
            FiscalPeriodService.create_fiscal_year(
                company=company,
                year_label=f"FY{fy_start_year}-{str(fy_start_year + 1)[-2:]}",
                start_date=date(fy_start_year, start_month, 1),
            )

        self.stdout.write(self.style.SUCCESS("Accounting foundation seeded."))
