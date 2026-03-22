from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import timedelta
import logging
import requests

logger = logging.getLogger(__name__)


@shared_task
def send_order_notifications(order_id):
    """Send order notifications via email and WhatsApp"""
    from .models import Order
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Send email notifications
        send_order_email_customer.delay(order_id)
        send_order_email_admin.delay(order_id)
        
        # Send WhatsApp notifications
        send_order_whatsapp_admin.delay(order_id)
        send_order_whatsapp_customer.delay(order_id)
        
        return {'status': 'success', 'order_id': str(order.id)}
        
    except Exception as e:
        logger.error(f"Order notification failed for {order_id}: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def send_order_email_customer(order_id):
    """Send order confirmation email to customer"""
    from .models import Order
    
    try:
        order = Order.objects.get(id=order_id)
        
        subject = f"Order Confirmation - #{order.order_number}"
        
        # Plain text version
        plain_message = f"""
Order Confirmation - #{order.order_number}

Dear {order.customer_name},

Thank you for your order! Here are the details:

ORDER ITEMS:
{order.items_summary}

DELIVERY DETAILS:
Date: {order.delivery_date.strftime('%A, %B %d, %Y')}
Time: {order.delivery_time_slot or 'Any time'}
Address: {order.delivery_address}, {order.delivery_city}

PAYMENT:
Method: {order.get_payment_method_display()}
Status: {order.get_payment_status_display()}
Total: KSh {order.total}

Thank you for choosing Everest Cakes!

Best regards,
Everest Cakes Team
{settings.SITE_URL}
        """
        
        # HTML version
        html_message = render_to_string('emails/order_confirmation.html', {'order': order})
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_message,
            fail_silently=True,
        )
        
        # Mark as sent
        Order.objects.filter(id=order_id).update(email_sent=True)
        
        logger.info(f"Order email sent to customer: {order.customer_email}")
        return f"Email sent to {order.customer_email}"
        
    except Exception as e:
        logger.error(f"Failed to send customer email for {order_id}: {e}")
        return None


@shared_task
def send_order_email_admin(order_id):
    """Send order notification to admin"""
    from .models import Order
    
    try:
        order = Order.objects.get(id=order_id)
        
        subject = f"🛒 New Order - #{order.order_number}"
        
        message = f"""
NEW ORDER RECEIVED

Order Number: {order.order_number}
Customer: {order.customer_name}
Phone: {order.customer_phone}
Email: {order.customer_email}

ITEMS:
{order.items_summary}

DELIVERY:
Date: {order.delivery_date.strftime('%A, %B %d, %Y')}
Time: {order.delivery_time_slot or 'Any time'}
Address: {order.delivery_address}, {order.delivery_city}
Instructions: {order.delivery_instructions or 'None'}

PAYMENT:
Method: {order.get_payment_method_display()}
Status: {order.get_payment_status_display()}
Total: KSh {order.total}

{f'GIFT ORDER - Recipient: {order.recipient_name} ({order.recipient_phone})' if order.is_gift else ''}

{f'Customer Notes: {order.notes}' if order.notes else ''}

View in Admin: {settings.SITE_URL}/admin/orders/order/{order.id}/
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )
        
        logger.info(f"Order email sent to admin: {settings.ADMIN_EMAIL}")
        return f"Admin email sent"
        
    except Exception as e:
        logger.error(f"Failed to send admin email for {order_id}: {e}")
        return None


@shared_task
def send_order_whatsapp_admin(order_id):
    """Send WhatsApp notification to admin about new order"""
    from .models import Order
    
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.ADMIN_WHATSAPP_NUMBER:
        logger.warning("WhatsApp credentials not configured")
        return None
    
    try:
        order = Order.objects.get(id=order_id)
        
        # WhatsApp Business API
        url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        message = f"""🛒 *NEW ORDER*

📦 Order: #{order.order_number}
👤 Customer: {order.customer_name}
📞 Phone: {order.customer_phone}

📅 Delivery: {order.delivery_date.strftime('%d/%m/%Y')}
📍 Location: {order.delivery_city}

💰 Total: KSh {order.total}
💳 Payment: {order.get_payment_method_display()}

{f'🎁 GIFT for {order.recipient_name}' if order.is_gift else ''}

View: {settings.SITE_URL}/admin/orders/order/{order.id}/
        """
        
        payload = {
            "messaging_product": "whatsapp",
            "to": settings.ADMIN_WHATSAPP_NUMBER,
            "type": "text",
            "text": {"body": message}
        }
        
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            Order.objects.filter(id=order_id).update(whatsapp_sent=True)
            logger.info(f"WhatsApp notification sent for order {order.order_number}")
        
        return response.json()
        
    except Exception as e:
        logger.error(f"WhatsApp admin notification failed: {e}")
        return None


@shared_task
def send_order_whatsapp_customer(order_id):
    """Send WhatsApp confirmation to customer"""
    from .models import Order
    
    if not settings.WHATSAPP_ACCESS_TOKEN:
        return None
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Format phone number
        phone = order.customer_phone.replace('+', '')
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        
        url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        message = f"""🎂 *Everest Cakes*

Dear {order.customer_name},

Your order has been confirmed!

📦 Order: #{order.order_number}
📅 Delivery: {order.delivery_date.strftime('%A, %d %B %Y')}
💰 Total: KSh {order.total}
💳 Payment: {order.get_payment_method_display()}

Thank you for choosing us! 🙏

Track your order: {settings.SITE_URL}/orders/track/?order_number={order.order_number}
        """
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": message}
        }
        
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        return response.json()
        
    except Exception as e:
        logger.error(f"WhatsApp customer notification failed: {e}")
        return None


@shared_task
def send_enquiry_notifications(enquiry_id):
    """Send enquiry notifications via email and WhatsApp"""
    from .models import Enquiry
    
    try:
        enquiry = Enquiry.objects.get(id=enquiry_id)
        
        # Send email to admin
        send_enquiry_email_admin.delay(enquiry_id)
        
        # Send WhatsApp to admin
        send_enquiry_whatsapp_admin.delay(enquiry_id)
        
        return {'status': 'success', 'enquiry_id': str(enquiry.id)}
        
    except Exception as e:
        logger.error(f"Enquiry notification failed for {enquiry_id}: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def send_enquiry_email_admin(enquiry_id):
    """Send enquiry email to admin"""
    from .models import Enquiry
    
    try:
        enquiry = Enquiry.objects.get(id=enquiry_id)
        
        subject = f"📧 New Enquiry - {enquiry.subject}"
        
        message = f"""
NEW ENQUIRY RECEIVED

From: {enquiry.name}
Email: {enquiry.email}
Phone: {enquiry.phone or 'Not provided'}

Subject: {enquiry.subject}

Message:
{enquiry.message}

{f'Product: {enquiry.product.name}' if enquiry.product else ''}

Reply to: {enquiry.email}
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )
        
        Enquiry.objects.filter(id=enquiry_id).update(email_sent=True)
        logger.info(f"Enquiry email sent for {enquiry_id}")
        return "Email sent"
        
    except Exception as e:
        logger.error(f"Failed to send enquiry email: {e}")
        return None


@shared_task
def send_enquiry_whatsapp_admin(enquiry_id):
    """Send WhatsApp notification about enquiry"""
    from .models import Enquiry
    
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.ADMIN_WHATSAPP_NUMBER:
        return None
    
    try:
        enquiry = Enquiry.objects.get(id=enquiry_id)
        
        url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        message = f"""📧 *NEW ENQUIRY*

👤 {enquiry.name}
📞 {enquiry.phone or 'No phone'}
📧 {enquiry.email}

📌 {enquiry.subject}

💬 {enquiry.message[:200]}{'...' if len(enquiry.message) > 200 else ''}

{f'🎂 Product: {enquiry.product.name}' if enquiry.product else ''}
        """
        
        payload = {
            "messaging_product": "whatsapp",
            "to": settings.ADMIN_WHATSAPP_NUMBER,
            "type": "text",
            "text": {"body": message}
        }
        
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            Enquiry.objects.filter(id=enquiry_id).update(whatsapp_sent=True)
        
        return response.json()
        
    except Exception as e:
        logger.error(f"WhatsApp enquiry notification failed: {e}")
        return None


@shared_task
def send_payment_reminder(order_id):
    """Send payment reminder"""
    from .models import Order
    
    try:
        order = Order.objects.get(id=order_id)
        
        # For M-Pesa pending payments
        if order.payment_method == 'mpesa' and order.payment_status == 'pending':
            # Initiate STK Push again
            from .views import initiate_mpesa_payment
            initiate_mpesa_payment(order)
        
        # Send reminder message
        if settings.WHATSAPP_ACCESS_TOKEN:
            phone = order.customer_phone.replace('+', '')
            if phone.startswith('0'):
                phone = '254' + phone[1:]
            
            url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
            
            message = f"""🎂 *Payment Reminder*

Dear {order.customer_name},

Your order #{order.order_number} is pending payment of KSh {order.total}.

Please complete payment to confirm your order.

Thank you! 🙏
            """
            
            payload = {
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "text",
                "text": {"body": message}
            }
            
            headers = {
                "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            
            requests.post(url, json=payload, headers=headers, timeout=30)
        
        return f"Reminder sent for order {order.order_number}"
        
    except Exception as e:
        logger.error(f"Payment reminder failed: {e}")
        return None


@shared_task
def generate_daily_report():
    """Generate daily order report"""
    from .models import Order
    from django.db.models import Sum, Count
    
    today = timezone.now().date()
    
    stats = Order.objects.filter(
        created_at__date=today
    ).aggregate(
        total_orders=Count('id'),
        total_revenue=Sum('total'),
        pending_orders=Count('id', filter=models.Q(status='pending')),
        completed_orders=Count('id', filter=models.Q(status='delivered'))
    )
    
    subject = f"📊 Daily Report - {today}"
    message = f"""
Daily Order Report - {today}

📈 Summary:
- Total Orders: {stats['total_orders']}
- Total Revenue: KES {stats['total_revenue'] or 0}
- Pending: {stats['pending_orders']}
- Completed: {stats['completed_orders']}

---
Everest Cakes
    """
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        fail_silently=True,
    )
    
    return f"Report sent for {today}"
