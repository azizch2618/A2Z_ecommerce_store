"""Order transactional emails."""
from django.conf import settings
from django.core.mail import send_mail

from apps.orders.models import Order


def _order_recipient(order: Order) -> str:
    if order.customer.user_id and order.customer.user.email:
        return order.customer.user.email
    return order.guest_email


def send_order_confirmation_email(order: Order) -> None:
    recipient = _order_recipient(order)
    if not recipient:
        return

    total_aud = order.total_inc_gst_cents / 100
    subject = f"Order confirmed — {order.order_number}"
    message = (
        f"Thank you for your order with A2Z Tools.\n\n"
        f"Order number: {order.order_number}\n"
        f"Total (inc GST): ${total_aud:,.2f} {order.currency_code}\n"
        f"Status: Paid\n\n"
        f"You can view your order in your account at {settings.FRONTEND_URL.rstrip('/')}/account/orders/{order.public_id}\n\n"
        "— A2Z Tools"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=False,
    )
