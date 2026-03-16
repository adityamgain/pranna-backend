from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid


class Coupon(models.Model):
    """Enhanced coupon model with more features"""

    COUPON_TYPES = [
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
    ]

    APPLICABLE_TO = [
        ('all', 'All Products'),
        ('category', 'Specific Category'),
        ('products', 'Specific Products'),
    ]

    code = models.CharField(max_length=50, unique=True, db_index=True)
    type = models.CharField(max_length=20, choices=COUPON_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2,
                                help_text="Discount value (percentage or fixed amount)")

    # Applicability
    applicable_to = models.CharField(max_length=20, choices=APPLICABLE_TO, default='all')
    applicable_categories = models.JSONField(default=list, blank=True, help_text="List of category IDs")
    applicable_products = models.JSONField(default=list, blank=True, help_text="List of product IDs")

    # Usage limits
    max_uses = models.PositiveIntegerField(default=1, help_text="Maximum number of times this coupon can be used")
    used_count = models.PositiveIntegerField(default=0, editable=False)
    per_user_limit = models.PositiveIntegerField(default=1, help_text="Maximum uses per customer (by email)")

    # Minimum requirements
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_quantity = models.PositiveIntegerField(default=1, help_text="Minimum quantity required")

    # Maximum discount (for percentage coupons)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Validity
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    # First time customer only
    first_time_only = models.BooleanField(default=False)

    # Description
    description = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['valid_from', 'valid_to']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.code} - {self.get_type_display()}"

    @property
    def is_valid(self):
        now = timezone.now()
        return (
                self.is_active and
                self.valid_from <= now <= self.valid_to and
                self.used_count < self.max_uses
        )

    def calculate_discount(self, subtotal, items=None, email=None):
        """Calculate discount amount with all conditions"""
        if not self.is_valid:
            return 0

        if subtotal < self.min_order_amount:
            return 0

        # Check first time customer
        if self.first_time_only and email:
            if Order.objects.filter(email=email).exists():
                return 0

        # Check per user limit
        if email and self.per_user_limit:
            user_usage = Order.objects.filter(
                email=email,
                coupon_code=self.code,
                status__in=['confirmed', 'processing', 'shipped', 'delivered']
            ).count()
            if user_usage >= self.per_user_limit:
                return 0

        # Check applicable products/categories
        if self.applicable_to != 'all' and items:
            applicable_total = 0
            total_items = 0

            for item in items:
                item_applicable = False

                if self.applicable_to == 'category':
                    item_category = item.get('category_id')
                    if item_category and item_category in self.applicable_categories:
                        item_applicable = True

                elif self.applicable_to == 'products':
                    if item.get('id') in self.applicable_products:
                        item_applicable = True

                if item_applicable:
                    applicable_total += item['price'] * item['quantity']
                    total_items += item['quantity']

            if total_items < self.min_quantity:
                return 0

            subtotal = applicable_total

        # Calculate discount
        if self.type == 'percentage':
            discount = (subtotal * self.value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
        elif self.type == 'fixed':
            discount = min(self.value, subtotal)
        else:  # free_shipping
            discount = 0  # Shipping discount handled separately

        return discount

    def increment_usage(self):
        self.used_count += 1
        self.save(update_fields=['used_count'])


class Order(models.Model):
    """Enhanced Order model with all requested fields - COD Only"""

    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed Delivery'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),  # Waiting for delivery
        ('paid', 'Paid'),  # Paid upon delivery
        ('failed', 'Failed'),  # Payment failed at delivery
    ]

    # Order identification
    order_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order_id = models.CharField(max_length=20, unique=True, editable=False, db_index=True)

    # Customer information
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=20)
    full_name = models.CharField(max_length=200)

    # Shipping address
    address = models.TextField()
    apartment = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Nepal')

    # Contact preferences
    sms_opt_in = models.BooleanField(default=False)
    email_opt_in = models.BooleanField(default=False)

    # Order details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    # Coupon
    coupon_code = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_details = models.JSONField(default=dict, blank=True, help_text="Snapshot of coupon details at time of order")

    # Cart data (store as JSON)
    cart_items = models.JSONField(default=list, help_text="List of ordered items")

    # Status
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending', db_index=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending', db_index=True)

    # Additional info
    notes = models.TextField(blank=True, help_text="Customer notes or special instructions")
    admin_notes = models.TextField(blank=True, help_text="Internal notes for staff")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)

    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    tracking_url = models.URLField(blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Audit
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['order_id']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['coupon_code']),
        ]

    def __str__(self):
        return f"Order {self.order_id}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_order_id()

        # Ensure total matches calculations
        calculated_total = self.subtotal + self.shipping_cost + self.tax - self.discount
        if abs(calculated_total - self.total) > 0.01:
            self.total = calculated_total

        super().save(*args, **kwargs)

    def generate_order_id(self):
        """Generate unique order ID"""
        date_prefix = timezone.now().strftime('%Y%m%d')
        last_order = Order.objects.filter(
            order_id__startswith=f"ORD-{date_prefix}"
        ).order_by('-order_id').first()

        if last_order:
            last_number = int(last_order.order_id.split('-')[-1])
            new_number = str(last_number + 1).zfill(5)
        else:
            new_number = '00001'

        return f"ORD-{date_prefix}-{new_number}"

    @property
    def item_count(self):
        return sum(item.get('quantity', 0) for item in self.cart_items)

    def mark_as_delivered(self):
        self.status = 'delivered'
        self.payment_status = 'paid'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'payment_status', 'delivered_at'])

    def cancel_order(self, reason=""):
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.cancelled_reason = reason
        self.save(update_fields=['status', 'cancelled_at', 'cancelled_reason'])


class OrderItem(models.Model):
    """Individual items within an order"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField(db_index=True)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    # Product snapshot at time of order
    product_snapshot = models.JSONField(default=dict)

    # Applied discount for this item (if any)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'product_id']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    def save(self, *args, **kwargs):
        self.subtotal = (self.product_price * self.quantity) - self.discount_amount
        super().save(*args, **kwargs)


class ShippingRate(models.Model):
    """Shipping rates with advanced options"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Applicable countries (comma-separated or 'all')
    countries = models.TextField(default='all', help_text="Comma-separated list of country codes or 'all'")

    RATE_TYPES = [
        ('fixed', 'Fixed Rate'),
        ('price_based', 'Based on Order Amount'),
    ]

    rate_type = models.CharField(max_length=20, choices=RATE_TYPES, default='fixed')

    # Rate values
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Free shipping threshold
    free_shipping_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Order amount for free shipping"
    )

    # Estimated delivery
    estimated_days_min = models.PositiveIntegerField(default=3)
    estimated_days_max = models.PositiveIntegerField(default=7)

    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def calculate_rate(self, order_amount=0):
        """Calculate shipping rate based on order amount"""

        # Check free shipping
        if self.free_shipping_threshold and order_amount >= self.free_shipping_threshold:
            return 0

        if self.rate_type == 'fixed':
            return self.base_rate
        else:
            return self.base_rate


class OrderHistory(models.Model):
    """Track order status changes"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=20, choices=Order.ORDER_STATUS)
    notes = models.TextField(blank=True)
    created_by = models.CharField(max_length=100, blank=True, help_text="User or system that made the change")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', '-created_at']),
        ]

    def __str__(self):
        return f"{self.order.order_id} - {self.get_status_display()} at {self.created_at}"