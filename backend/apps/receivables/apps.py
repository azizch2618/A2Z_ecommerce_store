from django.apps import AppConfig


class ReceivablesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.receivables"
    verbose_name = "Accounts Receivable"

    def ready(self) -> None:
        from apps.receivables import event_handlers  # noqa: F401
