from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from django.conf import settings
import logging
import random
import string

from .models import Order, OrderItem, Coupon, ShippingRate, OrderHistory
from .serializers import (
    OrderSerializer, OrderCreateSerializer, ApplyCouponSerializer,
    TrackOrderSerializer, ShippingRateSerializer
)
from .email_utils import (
    send_verification_email,
    send_order_confirmation_email,
    send_admin_notification_email,
    send_verification_sms
)

logger = logging.getLogger(__name__)


class SendVerificationView(APIView):
    """Send verification code to email and phone"""

    def post(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')

        if not email or not phone:
            return Response({
                'success': False,
                'message': 'Email and phone are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generate 6-digit verification code
        code = ''.join(random.choices(string.digits, k=6))

        # Store in cache with 10 minute expiry
        cache_key = f"verification_{email}_{phone}"
        cache.set(cache_key, code, timeout=600)  # 10 minutes

        try:
            # Send email
            send_verification_email(email, code)

            # Send SMS (implement with your SMS provider)
            send_verification_sms(phone, code)

            # In development, return the code for testing
            if settings.DEBUG:
                return Response({
                    'success': True,
                    'message': 'Verification code sent',
                    'code': code  # Only in development!
                })

            return Response({
                'success': True,
                'message': 'Verification code sent to your email and phone'
            })

        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to send verification code. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyCodeView(APIView):
    """Verify the entered code"""

    def post(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')
        entered_code = request.data.get('code')

        if not email or not phone or not entered_code:
            return Response({
                'success': False,
                'message': 'Email, phone and code are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"verification_{email}_{phone}"
        stored_code = cache.get(cache_key)

        if stored_code and stored_code == entered_code:
            # Delete used code
            cache.delete(cache_key)

            return Response({
                'success': True,
                'message': 'Verification successful'
            })
        else:
            return Response({
                'success': False,
                'message': 'Invalid or expired verification code'
            }, status=status.HTTP_400_BAD_REQUEST)


class CheckoutView(APIView):
    """Process checkout and create order - COD Only"""

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            with transaction.atomic():
                # Get client IP
                ip_address = request.META.get('REMOTE_ADDR')
                user_agent = request.META.get('HTTP_USER_AGENT', '')

                # Create order
                order = Order.objects.create(
                    email=data['email'],
                    phone=data['phone'],
                    full_name=data['full_name'],
                    address=data['address'],
                    apartment=data.get('apartment', ''),
                    city=data['city'],
                    state=data.get('state', ''),
                    postal_code=data['postal_code'],
                    country=data['country'],
                    sms_opt_in=data.get('sms_opt_in', False),
                    email_opt_in=data.get('email_opt_in', False),
                    subtotal=data['subtotal'],
                    shipping_cost=data['shipping_cost'],
                    tax=data['tax'],
                    discount=data.get('discount', 0),
                    total=data['total'],
                    coupon_code=data.get('coupon_code', ''),
                    cart_items=data['cart_items'],
                    notes=data.get('notes', ''),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    status='pending',
                    payment_status='pending'
                )

                # Create order items
                for item in data['cart_items']:
                    OrderItem.objects.create(
                        order=order,
                        product_id=item['id'],
                        product_name=item['name'],
                        product_price=item['price'],
                        quantity=item['quantity'],
                        product_snapshot=item
                    )

                # Update coupon usage if applied
                if data.get('coupon_code'):
                    try:
                        coupon = Coupon.objects.get(
                            code=data['coupon_code'],
                            is_active=True,
                            valid_from__lte=timezone.now(),
                            valid_to__gte=timezone.now()
                        )
                        coupon.increment_usage()

                        # Store coupon details
                        order.coupon_details = {
                            'code': coupon.code,
                            'type': coupon.type,
                            'value': float(coupon.value),
                            'discount': float(data.get('discount', 0))
                        }
                        order.save(update_fields=['coupon_details'])

                    except Coupon.DoesNotExist:
                        pass

                # Create order history
                OrderHistory.objects.create(
                    order=order,
                    status='pending',
                    notes='Order placed via Cash on Delivery',
                    created_by='customer'
                )

                # Send order confirmation email to customer
                try:
                    send_order_confirmation_email(order)
                except Exception as e:
                    logger.error(f"Failed to send order confirmation email: {str(e)}")

                # Send notification to admin
                try:
                    send_admin_notification_email(order)
                except Exception as e:
                    logger.error(f"Failed to send admin notification: {str(e)}")

                return Response({
                    'success': True,
                    'message': 'Order placed successfully',
                    'order_id': order.order_id,
                    'order_number': str(order.order_number),
                    'total': float(order.total),
                    'estimated_delivery': order.estimated_delivery
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Checkout error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to process order. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApplyCouponView(APIView):
    """Apply coupon code and get discount"""

    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        coupon_code = serializer.validated_data['coupon_code']
        subtotal = serializer.validated_data['subtotal']
        cart_items = serializer.validated_data.get('cart_items', [])
        email = serializer.validated_data.get('email')

        try:
            coupon = Coupon.objects.get(
                code=coupon_code,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            )

            # Calculate discount
            discount = coupon.calculate_discount(
                subtotal=subtotal,
                items=cart_items,
                email=email
            )

            if discount > 0:
                return Response({
                    'success': True,
                    'message': 'Coupon applied successfully',
                    'discount': float(discount),
                    'coupon_code': coupon.code,
                    'coupon_type': coupon.type,
                    'free_shipping': coupon.type == 'free_shipping'
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Coupon cannot be applied to this order'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Coupon.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid or expired coupon code'
            }, status=status.HTTP_400_BAD_REQUEST)


class TrackOrderView(APIView):
    """Track order by order_id or email"""

    def post(self, request):
        serializer = TrackOrderSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        order_id = serializer.validated_data.get('order_id')
        email = serializer.validated_data.get('email')

        try:
            if order_id:
                order = Order.objects.get(order_id=order_id)
            elif email:
                order = Order.objects.filter(email=email).latest('created_at')
            else:
                return Response({
                    'success': False,
                    'message': 'Please provide order_id or email'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get order history
            history = order.history.values('status', 'notes', 'created_at').order_by('-created_at')

            return Response({
                'success': True,
                'order': {
                    'order_id': order.order_id,
                    'status': order.status,
                    'payment_status': order.payment_status,
                    'estimated_delivery': order.estimated_delivery,
                    'tracking_number': order.tracking_number,
                    'tracking_url': order.tracking_url,
                    'created_at': order.created_at,
                    'total': float(order.total),
                    'items_count': order.item_count
                },
                'history': list(history)
            })

        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ShippingRateView(APIView):
    """Get shipping rates for a country"""

    def get(self, request):
        country = request.query_params.get('country', 'Nepal')
        order_amount = request.query_params.get('amount', 0)

        try:
            order_amount = float(order_amount)
        except ValueError:
            order_amount = 0

        # Find applicable shipping rates
        rates = ShippingRate.objects.filter(is_active=True)
        applicable_rates = []

        for rate in rates:
            countries = [c.strip() for c in rate.countries.split(',')]
            if 'all' in countries or country in countries:
                shipping_cost = rate.calculate_rate(order_amount)

                applicable_rates.append({
                    'id': rate.id,
                    'name': rate.name,
                    'description': rate.description,
                    'cost': float(shipping_cost),
                    'estimated_days': f"{rate.estimated_days_min}-{rate.estimated_days_max} days"
                })

        # Default rate if none found
        if not applicable_rates:
            # Get default shipping rate or create one
            default_rate = ShippingRate.objects.filter(is_default=True).first()
            if default_rate:
                shipping_cost = default_rate.calculate_rate(order_amount)
                applicable_rates.append({
                    'id': default_rate.id,
                    'name': default_rate.name,
                    'description': default_rate.description,
                    'cost': float(shipping_cost),
                    'estimated_days': f"{default_rate.estimated_days_min}-{default_rate.estimated_days_max} days"
                })
            else:
                # Fallback default
                applicable_rates.append({
                    'id': 0,
                    'name': 'Standard Shipping',
                    'description': 'Standard shipping',
                    'cost': 10.00 if country != 'Nepal' else 5.00,
                    'estimated_days': '5-10 days'
                })

        return Response(applicable_rates)


class OrderDetailView(APIView):
    """Get order details by order_id"""

    def get(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
            serializer = OrderSerializer(order)
            return Response({
                'success': True,
                'order': serializer.data
            })
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)


class CancelOrderView(APIView):
    """Cancel an order (if within cancellation window)"""

    def post(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)

            # Check if order can be cancelled (only pending orders)
            if order.status not in ['pending', 'confirmed']:
                return Response({
                    'success': False,
                    'message': 'Order cannot be cancelled at this stage'
                }, status=status.HTTP_400_BAD_REQUEST)

            reason = request.data.get('reason', 'Cancelled by customer')
            order.cancel_order(reason)

            # Create history entry
            OrderHistory.objects.create(
                order=order,
                status='cancelled',
                notes=f"Order cancelled. Reason: {reason}",
                created_by='customer'
            )

            return Response({
                'success': True,
                'message': 'Order cancelled successfully'
            })

        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)


class NewsletterSubscribeView(APIView):
    """Subscribe to newsletter"""

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({
                'success': False,
                'message': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Here you would integrate with your newsletter service
        # For now, just return success
        return Response({
            'success': True,
            'message': 'Successfully subscribed to newsletter!'
        })