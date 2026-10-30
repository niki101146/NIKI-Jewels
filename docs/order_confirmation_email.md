# Order confirmation email (Django)

The zip only contains templates/static files, so the order view is not included.
Add this to your project's backend.

## 1. settings.py
```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your-store@gmail.com"          # store sender account
EMAIL_HOST_PASSWORD = "gmail-app-password"        # Gmail App Password (not normal password)
DEFAULT_FROM_EMAIL = "NIKI Jewels <your-store@gmail.com>"
```
(Keep the password in an environment variable, not in the code.)

## 2. In the view that saves the order (right after the order is created)
```python
from django.core.mail import send_mail

def send_order_confirmation(order, customer_email, customer_name):
    body = (
        f"Hi {customer_name},\n\n"
        f"Thank you for shopping with NIKI Jewels! Your order #{order.id} has been received.\n"
        f"Our team will contact you shortly to confirm it.\n\n"
        f"With love,\nNIKI Jewels - Timeless Beauty, Lasting You"
    )
    send_mail(
        subject=f"Order #{order.id} received - NIKI Jewels",
        message=body,
        from_email=None,                 # uses DEFAULT_FROM_EMAIL
        recipient_list=[customer_email],
        fail_silently=True,              # never block the order if mail fails
    )
```
Call `send_order_confirmation(order, form.cleaned_data["email"], form.cleaned_data["name"])`
after the order is saved.
