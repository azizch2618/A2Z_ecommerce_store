from django.apps import AppConfig


class PayablesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.payables"
    verbose_name = "Accounts Payable"

    def ready(self) -> None:
        from apps.payables import event_handlers  # noqa: F401
