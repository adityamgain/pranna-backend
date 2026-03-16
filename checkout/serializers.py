from rest_framework import serializers
from django.utils import timezone
from .models import Order, OrderItem, Coupon, ShippingRate, OrderHistory


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_id', 'product_name', 'product_price',
            'quantity', 'subtotal', 'product_snapshot', 'discount_amount'
        ]
        read_only_fields = ['id', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_id',
            'email', 'phone', 'full_name',
            'address', 'apartment', 'city', 'state', 'postal_code', 'country',
            'sms_opt_in', 'email_opt_in',
            'subtotal', 'shipping_cost', 'tax', 'discount', 'total',
            'coupon_code', 'coupon_discount', 'coupon_details',
            'cart_items', 'status', 'payment_status',
            'notes', 'admin_notes', 'ip_address',
            'tracking_number', 'tracking_url', 'estimated_delivery',
            'created_at', 'updated_at', 'delivered_at',
            'items', 'item_count'
        ]
        read_only_fields = [
            'id', 'order_number', 'order_id', 'created_at',
            'updated_at', 'delivered_at', 'item_count'
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders - COD Only"""

    # Customer info
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    full_name = serializers.CharField(max_length=200)

    # Shipping address
    address = serializers.CharField()
    apartment = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField()
    state = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField()
    country = serializers.CharField(default='Nepal')

    # Preferences
    sms_opt_in = serializers.BooleanField(default=False)
    email_opt_in = serializers.BooleanField(default=False)

    # Order details
    cart_items = serializers.JSONField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    tax = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)

    # Coupon
    coupon_code = serializers.CharField(required=False, allow_blank=True, max_length=50)

    # Additional
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_cart_items(self, value):
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("Cart cannot be empty")

        for item in value:
            required_fields = ['id', 'name', 'price', 'quantity']
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(f"Missing {field} in cart item")

            if item['quantity'] < 1:
                raise serializers.ValidationError("Quantity must be at least 1")

        return value

    def validate(self, data):
        # Validate total
        subtotal = data['subtotal']
        shipping = data['shipping_cost']
        tax = data['tax']
        discount = data.get('discount', 0)
        total = data['total']

        calculated_total = subtotal + shipping + tax - discount
        if abs(calculated_total - total) > 1:  # Allow small rounding differences
            raise serializers.ValidationError("Total amount does not match order calculations")

        return data


class ApplyCouponSerializer(serializers.Serializer):
    """Serializer for applying coupon"""
    coupon_code = serializers.CharField(max_length=50)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    cart_items = serializers.JSONField(required=False, default=list)
    email = serializers.EmailField(required=False, allow_null=True)


class TrackOrderSerializer(serializers.Serializer):
    """Serializer for tracking order"""
    order_id = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)


class ShippingRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingRate
        fields = ['id', 'name', 'description', 'base_rate', 'estimated_days_min', 'estimated_days_max']