from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('track/', views.OrderTrackingView.as_view(), name='track'),
    path('order/<str:order_number>/', views.OrderDetailView.as_view(), name='detail'),
    path('enquiry/', views.EnquiryView.as_view(), name='enquiry'),
    path('quick-enquiry/', views.quick_enquiry, name='quick_enquiry'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
]
