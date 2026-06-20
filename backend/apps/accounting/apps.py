from django.apps import AppConfig


class AccountingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounting"
    verbose_name = "Accounting"

    def ready(self) -> None:
        from apps.accounting import event_handlers  # noqa: F401
