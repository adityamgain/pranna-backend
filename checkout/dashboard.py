from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta, date

from jet.dashboard.dashboard import Dashboard
from jet.dashboard import modules

from .models import Order, OrderItem, Coupon
from merchandise.models import Merchandise




class ProductStockModule(modules.DashboardModule):
    """Displays product inventory with stock alerts"""
    title = _('Product Stock Status')
    template = 'jet.dashboard/modules/product_stock.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all active products, ordered by stock (lowest first)
        products = Merchandise.objects.filter(is_active=True).order_by('stock')

        # Separate low stock products (e.g., stock <= 5)
        low_stock_threshold = 5
        low_stock_products = products.filter(stock__lte=low_stock_threshold)
        other_products = products.filter(stock__gt=low_stock_threshold)

        context.update({
            'low_stock_products': low_stock_products,
            'other_products': other_products,
            'total_products': products.count(),
            'out_of_stock': products.filter(stock=0).count(),
            'low_stock_count': low_stock_products.count(),
        })
        return context


class OrdersSummaryModule(modules.DashboardModule):
    """Enhanced summary with metric cards"""
    title = _('Order Summary')
    template = 'jet.dashboard/modules/orders_summary.html'

    class Media:
        css = {
            'all': ('jet.dashboard/css/orders_summary.css',)
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)

        delivered_orders = Order.objects.filter(status='delivered')

        # Calculate total revenue (delivered orders only)
        total_revenue = delivered_orders.aggregate(Sum('total'))['total__sum'] or 0

        context.update({
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'confirmed_orders': Order.objects.filter(status='confirmed').count(),
            'shipped_orders': Order.objects.filter(status='shipped').count(),
            'delivered_orders': delivered_orders.count(),
            'cancelled_orders': Order.objects.filter(status='cancelled').count(),

            'revenue_today': delivered_orders.filter(
                created_at__date=today
            ).aggregate(Sum('total'))['total__sum'] or 0,

            'revenue_7days': delivered_orders.filter(
                created_at__date__gte=last_7_days
            ).aggregate(Sum('total'))['total__sum'] or 0,

            'revenue_30days': delivered_orders.filter(
                created_at__date__gte=last_30_days
            ).aggregate(Sum('total'))['total__sum'] or 0,

            'total_revenue': total_revenue,

            'orders_today': Order.objects.filter(created_at__date=today).count(),
            'orders_7days': Order.objects.filter(created_at__date__gte=last_7_days).count(),
            'avg_order_value': delivered_orders.aggregate(
                avg=Sum('total') / Count('id')
            )['avg'] or 0,

            'active_coupons': Coupon.objects.filter(
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            ).count(),
        })
        return context


class RevenueChartModule(modules.DashboardModule):
    """Revenue trend for last 7 days"""
    title = _('Revenue Trend (Last 7 Days)')
    template = 'jet.dashboard/modules/revenue_chart.html'

    class Media:
        js = ('https://cdn.jsdelivr.net/npm/chart.js',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.now().date()
        dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
        labels = [d.strftime('%a %d') for d in dates]
        revenue_data = []

        for d in dates:
            revenue = Order.objects.filter(
                status='delivered',
                created_at__date=d
            ).aggregate(Sum('total'))['total__sum'] or 0
            revenue_data.append(float(revenue))

        context['labels'] = labels
        context['revenue_data'] = revenue_data
        return context


class RecentOrdersTableModule(modules.DashboardModule):
    """Recent orders displayed as a table with status badges"""
    title = _('Recent Orders')
    template = 'jet.dashboard/modules/recent_orders_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recent_orders = Order.objects.order_by('-created_at')[:10]
        context['recent_orders'] = recent_orders
        return context


class TopProductsTableModule(modules.DashboardModule):
    """Top products as a styled table"""
    title = _('Top Selling Products')
    template = 'jet.dashboard/modules/top_products_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        top_products = OrderItem.objects.values(
            'product_name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('product_price') * Sum('quantity')
        ).order_by('-total_quantity')[:10]

        context['top_products'] = top_products
        return context


class QuickActionButtons(modules.LinkList):
    """Quick actions styled as buttons"""
    title = _('Quick Actions')

    def init_with_context(self, context):
        self.children = [
            {
                'title': _('➕ New Order'),
                'url': '/admin/checkout/order/add/',
                'external': False,
                'attrs': {'class': 'button default'}
            },
            {
                'title': _('🎟️ Coupons'),
                'url': '/admin/checkout/coupon/',
                'external': False,
                'attrs': {'class': 'button'}
            },
            {
                'title': _('🚚 Shipping Rates'),
                'url': '/admin/checkout/shippingrate/',
                'external': False,
                'attrs': {'class': 'button'}
            },
            {
                'title': _('📦 All Orders'),
                'url': '/admin/checkout/order/',
                'external': False,
                'attrs': {'class': 'button'}
            },
        ]


class CustomIndexDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        # Row 1: Summary + Chart
        self.children.append(OrdersSummaryModule(
            _('Order Summary'),
            column=0,
            order=0
        ))
        self.children.append(RevenueChartModule(
            _('Revenue Trend'),
            column=1,
            order=0
        ))
        self.children.append(QuickActionButtons(
            _('Quick Actions'),
            column=2,
            order=0
        ))

        # Row 2: Recent Orders and Top Products
        self.children.append(RecentOrdersTableModule(
            _('Recent Orders'),
            column=0,
            order=1,
            colspan=2  # spans two columns
        ))
        self.children.append(TopProductsTableModule(
            _('Top Products'),
            column=2,
            order=1
        ))

        # Row 3: App list and recent actions (optional)
        self.children.append(modules.AppList(
            _('Applications'),
            exclude=('django.contrib.*',),
            column=0,
            order=2
        ))
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=10,
            column=1,
            order=2,
            colspan=2
        ))


class CustomIndexDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        # Row 1: Summary + Chart + Quick Actions
        self.children.append(OrdersSummaryModule(column=0, order=0))
        self.children.append(RevenueChartModule(column=1, order=0))
        self.children.append(QuickActionButtons(column=2, order=0))

        # Row 2: Recent Orders (spans 2 columns) and Product Stock (1 column)
        self.children.append(RecentOrdersTableModule(column=0, order=1, colspan=2))
        self.children.append(ProductStockModule(column=2, order=1))   # <--- new module

        # Row 3: Top Products and Applications/Recent Actions
        self.children.append(TopProductsTableModule(column=0, order=2))
        self.children.append(modules.AppList(
            _('Applications'),
            exclude=('django.contrib.*',),
            column=1,
            order=2
        ))
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=10,
            column=2,
            order=2
        ))


class PlotlyRevenueModule(modules.DashboardModule):
    """Embed Plotly Dash app in JET dashboard"""
    title = _('Advanced Revenue Analytics')
    template = 'jet.dashboard/modules/plotly_revenue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dash_url'] = '/dash/revenue/'
        return context