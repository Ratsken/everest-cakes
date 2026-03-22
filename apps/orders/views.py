from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DetailView, TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import default_storage
import json
import logging
from datetime import datetime

from .models import Order, OrderTracking, PaymentTransaction, OrderAttachment, Enquiry
from apps.cart.views import get_or_create_cart
from .tasks import send_order_notifications, send_enquiry_notifications

logger = logging.getLogger(__name__)


class CheckoutView(View):
    """Checkout page"""
    template_name = 'orders/checkout.html'
    
    def get(self, request):
        cart = get_or_create_cart(request)
        if not cart or cart.total_items == 0:
            messages.error(request, 'Your cart is empty')
            return redirect('cart:view')
        
        from apps.core.models import SiteSetting
        site_settings = SiteSetting.get_settings()
        
        return render(request, self.template_name, {
            'cart': cart,
            'site_settings': site_settings,
        })
    
    def post(self, request):
        """Process checkout"""
        cart = get_or_create_cart(request)
        if not cart or cart.total_items == 0:
            return JsonResponse({'error': 'Cart is empty'}, status=400)
        
        # Get form data
        customer_name = request.POST.get('customer_name', '').strip()
        customer_email = request.POST.get('customer_email', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        delivery_address = request.POST.get('delivery_address', '').strip()
        delivery_city = request.POST.get('delivery_city', '').strip()
        delivery_date = request.POST.get('delivery_date', '').strip()
        delivery_time_slot = request.POST.get('delivery_time_slot', '').strip()
        delivery_instructions = request.POST.get('delivery_instructions', '').strip()
        payment_method = request.POST.get('payment_method', 'cod')
        
        # Gift options
        is_gift = request.POST.get('is_gift') == 'true'
        recipient_name = request.POST.get('recipient_name', '').strip()
        recipient_phone = request.POST.get('recipient_phone', '').strip()
        gift_message = request.POST.get('gift_message', '').strip()
        
        # Customer notes
        notes = request.POST.get('notes', '').strip()
        
        # Validate required fields
        if not all([customer_name, customer_email, customer_phone, delivery_address, delivery_date]):
            return JsonResponse({'error': 'Please fill all required fields'}, status=400)
        
        # Validate phone number format
        if not customer_phone.startswith('+'):
            if customer_phone.startswith('0'):
                customer_phone = '+254' + customer_phone[1:]
            elif customer_phone.startswith('254'):
                customer_phone = '+' + customer_phone
            else:
                customer_phone = '+254' + customer_phone
        
        # Prepare order items
        items = []
        for cart_item in cart.items.all():
            # Get attributes display
            attributes = []
            for attr_id, opt_id in cart_item.selected_attributes.items():
                try:
                    from apps.products.models import ProductAttribute, ProductAttributeOption
                    attr = ProductAttribute.objects.get(id=attr_id)
                    opt = ProductAttributeOption.objects.get(id=opt_id)
                    attributes.append({
                        'attribute_id': str(attr.id),
                        'attribute': attr.name,
                        'option_id': str(opt.id),
                        'option': opt.name,
                        'price_adjustment': str(opt.price_adjustment)
                    })
                except:
                    pass
            
            # Get addons display
            addons = []
            for addon_item in cart_item.selected_addons:
                try:
                    from apps.products.models import ProductAddon
                    addon = ProductAddon.objects.get(id=addon_item.get('addon_id'))
                    qty = addon_item.get('quantity', 1)
                    addons.append({
                        'addon_id': str(addon.id),
                        'name': addon.name,
                        'price': str(addon.price),
                        'quantity': qty,
                        'total': str(addon.price * qty)
                    })
                except:
                    pass
            
            items.append({
                'product_id': str(cart_item.product.id),
                'name': cart_item.product.name,
                'variant_id': str(cart_item.variant.id) if cart_item.variant else None,
                'variant_name': cart_item.variant.name if cart_item.variant else None,
                'quantity': cart_item.quantity,
                'base_price': str(cart_item.base_price),
                'attributes_price': str(cart_item.attributes_price),
                'addons_price': str(cart_item.addons_price),
                'unit_price': str(cart_item.unit_price),
                'total_price': str(cart_item.total_price),
                'attributes': attributes,
                'addons': addons,
                'custom_message': cart_item.custom_message,
                'special_instructions': cart_item.special_instructions,
                'image': cart_item.product.featured_image.url if cart_item.product.featured_image else None,
            })
        
        # Parse delivery date
        try:
            delivery_date_parsed = datetime.strptime(delivery_date, '%Y-%m-%d').date()
        except:
            try:
                delivery_date_parsed = datetime.strptime(delivery_date, '%d/%m/%Y').date()
            except:
                return JsonResponse({'error': 'Invalid delivery date format'}, status=400)
        
        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            delivery_address=delivery_address,
            delivery_city=delivery_city,
            delivery_date=delivery_date_parsed,
            delivery_time_slot=delivery_time_slot,
            delivery_instructions=delivery_instructions,
            payment_method=payment_method,
            items=items,
            subtotal=cart.subtotal,
            delivery_fee=cart.delivery_fee,
            total=cart.total,
            is_gift=is_gift,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            gift_message=gift_message,
            notes=notes,
        )
        
        # Handle file attachments
        attachments = request.FILES.getlist('attachments')
        for attachment in attachments:
            if attachment:
                attachment_type = 'video' if attachment.content_type.startswith('video') else 'image'
                OrderAttachment.objects.create(
                    order=order,
                    attachment_type=attachment_type,
                    file=attachment
                )
        
        # Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status='Order Placed',
            description='Your order has been successfully placed'
        )
        
        # Clear cart
        cart.items.all().delete()
        
        # Update status based on payment
        if payment_method in ['cash', 'cod']:
            order.status = 'confirmed'
            order.save()
            order.deduct_stock_once()
        
        # Send notifications (async)
        send_order_notifications.delay(str(order.id))
        
        if request.htmx:
            return render(request, 'orders/partials/order_success.html', {'order': order})
        
        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'redirect_url': order.get_absolute_url()
        })


class OrderDetailView(DetailView):
    """Order detail/tracking page"""
    model = Order
    template_name = 'orders/detail.html'
    context_object_name = 'order'
    slug_url_kwarg = 'order_number'
    slug_field = 'order_number'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracking'] = self.object.tracking.all()[:10]
        context['attachments'] = self.object.attachments.all()
        return context


class OrderTrackingView(View):
    """Order tracking by order number"""
    template_name = 'orders/track.html'
    
    def get(self, request):
        order_number = request.GET.get('order_number', '')
        order = None
        if order_number:
            try:
                order = Order.objects.get(order_number=order_number.upper())
            except Order.DoesNotExist:
                messages.error(request, 'Order not found')
        
        return render(request, self.template_name, {'order': order})
    
    def post(self, request):
        order_number = request.POST.get('order_number', '').strip().upper()
        try:
            order = Order.objects.get(order_number=order_number)
            return redirect('orders:detail', order_number=order.order_number)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found. Please check your order number.')
            return render(request, self.template_name, {})


def mpesa_callback(request):
    """M-Pesa payment callback"""
    from .models import PaymentTransaction
    
    try:
        data = json.loads(request.body)
        logger.info(f"M-Pesa callback: {data}")
        
        result = data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = result.get('CheckoutRequestID')
        result_code = result.get('ResultCode')
        
        try:
            transaction = PaymentTransaction.objects.get(checkout_request_id=checkout_request_id)
            order = transaction.order
            
            if result_code == 0:
                # Payment successful
                callback_metadata = result.get('CallbackMetadata', {}).get('Item', [])
                mpesa_receipt = None
                for item in callback_metadata:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        mpesa_receipt = item.get('Value')
                
                transaction.status = 'success'
                transaction.transaction_id = mpesa_receipt
                transaction.response_data = data
                transaction.save()
                
                order.mark_paid(mpesa_receipt)
                order.status = 'confirmed'
                order.save()
                order.deduct_stock_once()
                
                OrderTracking.objects.create(
                    order=order,
                    status='Payment Confirmed',
                    description=f'Payment of KES {order.total} received via M-Pesa'
                )
                
                # Send confirmation
                send_order_notifications.delay(str(order.id))
                
            else:
                # Payment failed
                transaction.status = 'failed'
                transaction.response_data = data
                transaction.save()
                
                order.payment_status = 'failed'
                order.save()
                
        except PaymentTransaction.DoesNotExist:
            logger.error(f"Transaction not found: {checkout_request_id}")
            
    except Exception as e:
        logger.error(f"M-Pesa callback error: {e}")
    
    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})


@require_POST
def verify_payment(request):
    """Check payment status"""
    order_number = request.POST.get('order_number')
    
    try:
        order = Order.objects.get(order_number=order_number)
        return JsonResponse({
            'payment_status': order.payment_status,
            'order_status': order.status,
            'is_paid': order.payment_status == 'completed'
        })
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)


# Enquiry Views
class EnquiryView(View):
    """Contact/Enquiry form"""
    template_name = 'orders/enquiry.html'
    
    def get(self, request):
        product_id = request.GET.get('product')
        product = None
        if product_id:
            from apps.products.models import Product
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                pass
        
        return render(request, self.template_name, {'product': product})
    
    def post(self, request):
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        product_id = request.POST.get('product_id')
        
        if not all([name, email, subject, message]):
            return JsonResponse({'error': 'Please fill all required fields'}, status=400)
        
        product = None
        if product_id:
            from apps.products.models import Product
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                pass
        
        enquiry = Enquiry.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            product=product
        )
        
        # Handle image attachment
        if request.FILES.get('image'):
            enquiry.image = request.FILES['image']
            enquiry.save()
        
        # Send notifications
        send_enquiry_notifications.delay(str(enquiry.id))
        
        if request.htmx:
            return render(request, 'orders/partials/enquiry_success.html', {'enquiry': enquiry})
        
        messages.success(request, 'Thank you! We have received your enquiry and will get back to you soon.')
        return redirect('orders:enquiry')


@require_POST
def quick_enquiry(request):
    """Quick enquiry form (AJAX/HTMX)"""
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    message = request.POST.get('message', '').strip()
    product_id = request.POST.get('product_id')
    
    if not all([name, email or phone, message]):
        return JsonResponse({'error': 'Please fill all required fields'}, status=400)
    
    product = None
    if product_id:
        from apps.products.models import Product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            pass
    
    enquiry = Enquiry.objects.create(
        name=name,
        email=email,
        phone=phone,
        subject=f"Enquiry about {product.name}" if product else "General Enquiry",
        message=message,
        product=product
    )
    
    send_enquiry_notifications.delay(str(enquiry.id))
    
    return JsonResponse({'success': True, 'message': 'Enquiry sent! We will contact you soon.'})
