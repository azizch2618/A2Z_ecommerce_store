from django.apps import AppConfig


class PayrollConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.payroll"
    verbose_name = "Payroll"

    def ready(self) -> None:
        from apps.payroll import event_handlers  # noqa: F401
