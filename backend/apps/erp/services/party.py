"""Party master data service."""
from __future__ import annotations

from apps.customers.models import Customer
from apps.erp.constants import PartyType
from apps.erp.models import Contact, Party
from apps.suppliers.models import Supplier


class PartyService:
    @staticmethod
    def create_party(
        *,
        party_type: str,
        display_name: str,
        legal_name: str = "",
        tax_id: str = "",
        email: str = "",
        phone: str = "",
        company=None,
        metadata: dict | None = None,
    ) -> Party:
        return Party.objects.create(
            party_type=party_type,
            display_name=display_name,
            legal_name=legal_name or display_name,
            tax_id=tax_id,
            email=email,
            phone=phone,
            company=company,
            metadata=metadata or {},
        )

    @classmethod
    def ensure_for_customer(cls, customer: Customer) -> Party:
        existing = Party.objects.filter(customer=customer).first()
        if existing:
            return existing

        display = str(customer.user.email) if customer.user_id else str(customer.public_id)
        org = customer.organization
        party_type = PartyType.ORGANIZATION if org else PartyType.PERSON
        legal_name = org.legal_name if org else display

        party = cls.create_party(
            party_type=party_type,
            display_name=org.trading_name if org and org.trading_name else legal_name,
            legal_name=legal_name,
            tax_id=org.abn if org and org.abn else "",
            email=org.email if org else (customer.user.email if customer.user_id else ""),
            phone=org.phone if org else "",
        )
        party.customer = customer
        party.save(update_fields=["customer", "updated_at"])
        return party

    @classmethod
    def ensure_for_supplier(cls, supplier: Supplier) -> Party:
        existing = Party.objects.filter(supplier=supplier).first()
        if existing:
            return existing

        party = cls.create_party(
            party_type=PartyType.ORGANIZATION,
            display_name=supplier.name,
            legal_name=supplier.name,
            tax_id=supplier.abn,
            email=supplier.email,
            phone=supplier.phone,
        )
        party.supplier = supplier
        party.save(update_fields=["supplier", "updated_at"])
        return party

    @staticmethod
    def add_contact(
        *,
        party: Party,
        first_name: str,
        last_name: str = "",
        email: str = "",
        phone: str = "",
        position: str = "",
        notes: str = "",
        is_primary: bool = False,
    ) -> Contact:
        if is_primary:
            Contact.objects.filter(party=party, is_primary=True).update(is_primary=False)
        return Contact.objects.create(
            party=party,
            first_name=first_name,
            last_name=last_name,
            email=email or party.email,
            phone=phone or party.phone,
            position=position,
            notes=notes,
            is_primary=is_primary,
        )
