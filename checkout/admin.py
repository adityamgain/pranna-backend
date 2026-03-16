from django.contrib import admin
from .models import Order, OrderItem, Coupon, ShippingRate, OrderHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_id', 'product_name', 'product_price', 'quantity', 'subtotal']
    can_delete = False


class OrderHistoryInline(admin.TabularInline):
    model = OrderHistory
    extra = 0
    readonly_fields = ['status', 'notes', 'created_by', 'created_at']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id', 'full_name', 'email', 'phone',
        'total', 'status', 'payment_status', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at', 'country']
    search_fields = ['order_id', 'order_number', 'full_name', 'email', 'phone']
    readonly_fields = [
        'order_id', 'order_number', 'created_at', 'updated_at',
        'subtotal', 'shipping_cost', 'tax', 'discount', 'total',
        'ip_address', 'coupon_details'
    ]
    inlines = [OrderItemInline, OrderHistoryInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'order_number', 'created_at', 'updated_at')
        }),
        ('Customer Details', {
            'fields': ('full_name', 'email', 'phone', 'sms_opt_in', 'email_opt_in')
        }),
        ('Shipping Address', {
            'fields': ('address', 'apartment', 'city', 'state', 'postal_code', 'country')
        }),
        ('Order Summary', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'discount', 'total')
        }),
        ('Coupon', {
            'fields': ('coupon_code', 'coupon_discount', 'coupon_details'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'payment_status', 'notes', 'admin_notes')
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'tracking_url', 'estimated_delivery', 'delivered_at')
        }),
        ('Additional Info', {
            'fields': ('ip_address', 'user_agent', 'cart_items'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    def mark_as_confirmed(self, request, queryset):
        for order in queryset:
            order.status = 'confirmed'
            order.save()
            OrderHistory.objects.create(
                order=order,
                status='confirmed',
                created_by=request.user.email or 'admin'
            )
        self.message_user(request, f"{queryset.count()} orders marked as confirmed")

    mark_as_confirmed.short_description = "Mark selected orders as Confirmed"

    def mark_as_shipped(self, request, queryset):
        for order in queryset:
            order.status = 'shipped'
            order.save()
            OrderHistory.objects.create(
                order=order,
                status='shipped',
                created_by=request.user.email or 'admin'
            )
        self.message_user(request, f"{queryset.count()} orders marked as shipped")

    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def mark_as_delivered(self, request, queryset):
        for order in queryset:
            order.mark_as_delivered()
            OrderHistory.objects.create(
                order=order,
                status='delivered',
                notes='Payment collected via COD',
                created_by=request.user.email or 'admin'
            )
        self.message_user(request, f"{queryset.count()} orders marked as delivered")

    mark_as_delivered.short_description = "Mark selected orders as Delivered"

    def mark_as_cancelled(self, request, queryset):
        for order in queryset:
            order.cancel_order("Cancelled by admin")
            OrderHistory.objects.create(
                order=order,
                status='cancelled',
                created_by=request.user.email or 'admin'
            )
        self.message_user(request, f"{queryset.count()} orders marked as cancelled")

    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'type', 'value', 'min_order_amount',
        'valid_from', 'valid_to', 'used_count', 'max_uses', 'is_active'
    ]
    list_filter = ['type', 'is_active', 'applicable_to']
    search_fields = ['code']
    readonly_fields = ['created_at', 'updated_at', 'used_count']

    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'type', 'value', 'description')
        }),
        ('Applicability', {
            'fields': ('applicable_to', 'applicable_categories', 'applicable_products')
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'used_count', 'per_user_limit')
        }),
        ('Requirements', {
            'fields': ('min_order_amount', 'min_quantity', 'max_discount_amount')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to', 'is_active', 'first_time_only')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'countries', 'rate_type', 'base_rate',
        'free_shipping_threshold', 'estimated_delivery', 'is_default'
    ]
    list_filter = ['rate_type', 'is_active', 'is_default']
    search_fields = ['name', 'countries']

    def estimated_delivery(self, obj):
        return f"{obj.estimated_days_min}-{obj.estimated_days_max} days"

    estimated_delivery.short_description = 'Estimated Delivery'


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'created_at', 'created_by']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_id', 'order__email']
    readonly_fields = ['created_at']