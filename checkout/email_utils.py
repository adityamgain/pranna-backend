from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_verification_email(email, code):
    """Send verification code via email"""
    try:
        subject = 'Verify Your Email - Pranna Wellness'
        html_content = render_to_string('emails/verification_email.html', {
            'code': code,
            'email': email
        })
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Verification email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        raise


def send_verification_sms(phone, code):
    """Send verification code via SMS"""
    # Integrate with SMS provider like Twilio, Nexmo, etc.
    # Example with Twilio:
    """
    from twilio.rest import Client

    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f'Your Pranna Wellness verification code is: {code}',
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone
    )
    """

    # For development, just log it
    logger.info(f"SMS verification code {code} sent to {phone}")
    print(f"📱 SMS to {phone}: Your verification code is {code}")


def send_order_confirmation_email(order):
    """Send order confirmation to customer"""
    try:
        subject = f'Order Confirmation #{order.order_id} - Pranna Wellness'

        # Calculate totals
        subtotal = float(order.subtotal)
        shipping = float(order.shipping_cost)
        tax = float(order.tax)
        discount = float(order.discount)
        total = float(order.total)

        html_content = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'customer_name': order.full_name,
            'order_id': order.order_id,
            'items': order.cart_items,
            'subtotal': f"{subtotal:.2f}",
            'shipping': f"{shipping:.2f}",
            'tax': f"{tax:.2f}",
            'discount': f"{discount:.2f}",
            'total': f"{total:.2f}",
            'payment_method': 'Cash on Delivery'
        })
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [order.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Order confirmation email sent to {order.email}")
    except Exception as e:
        logger.error(f"Failed to send order confirmation to {order.email}: {str(e)}")
        raise


def send_admin_notification_email(order):
    """Send notification to admin about new order"""
    try:
        admin_email = 'amgainaditya@gmail.com'
        subject = f'🚨 New Order Received #{order.order_id} - Pranna Wellness'

        # Calculate total
        total = float(order.total)

        html_content = render_to_string('emails/admin_notification.html', {
            'order': order,
            'customer_name': order.full_name,
            'customer_email': order.email,
            'customer_phone': order.phone,
            'order_id': order.order_id,
            'items': order.cart_items,
            'total': f"{total:.2f}",
            'shipping_address': f"{order.address}, {order.city}, {order.state} {order.postal_code}, {order.country}",
            'admin_url': f"{settings.SITE_URL}/admin/checkout/order/{order.id}/"
        })
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [admin_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Admin notification sent to {admin_email}")
    except Exception as e:
        logger.error(f"Failed to send admin notification: {str(e)}")
        raise