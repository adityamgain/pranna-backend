from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    # Checkout endpoints
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('apply-coupon/', views.ApplyCouponView.as_view(), name='apply-coupon'),
    path('shipping-rates/', views.ShippingRateView.as_view(), name='shipping-rates'),

    # Verification endpoints
    path('send-verification/', views.SendVerificationView.as_view(), name='send-verification'),
    path('verify-code/', views.VerifyCodeView.as_view(), name='verify-code'),

    # Newsletter endpoint
    path('newsletter-subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),

    # Order endpoints
    path('track-order/', views.TrackOrderView.as_view(), name='track-order'),
    path('order/<str:order_id>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('order/<str:order_id>/cancel/', views.CancelOrderView.as_view(), name='cancel-order'),
]