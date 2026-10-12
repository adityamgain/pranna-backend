import calendar as pycalendar
from datetime import date, datetime, time, timedelta

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .ics import build_calendar
from .models import Event
from .serializers import CalendarEventSerializer, EventSerializer


def _parse_bound(value, name, is_end=False):
    """Parse YYYY-MM-DD or ISO datetime. A date-only end bound is inclusive of that whole day."""
    if not value:
        return None
    dt = parse_datetime(value)
    if dt is None:
        d = parse_date(value)
        if d is None:
            raise ValidationError({name: 'Use YYYY-MM-DD or an ISO 8601 datetime.'})
        if is_end:
            d += timedelta(days=1)
        dt = datetime.combine(d, time.min)
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    return dt


def _local_day_start(d):
    return timezone.make_aware(datetime.combine(d, time.min))


def filter_events(queryset, params):
    range_start = _parse_bound(params.get('start'), 'start')
    range_end = _parse_bound(params.get('end'), 'end', is_end=True)
    if range_start and range_end and range_end <= range_start:
        raise ValidationError({'end': 'end must be after start.'})
    if range_start or range_end:
        queryset = queryset.overlapping(
            range_start or timezone.make_aware(datetime.min + timedelta(days=1)),
            range_end or timezone.make_aware(datetime.max - timedelta(days=1)),
        )

    event_type = params.get('type')
    if event_type:
        queryset = queryset.filter(event_type__in=event_type.split(','))

    featured = params.get('featured')
    if featured and featured.lower() == 'true':
        queryset = queryset.filter(is_featured=True)

    for field in ('destination', 'journey', 'package'):
        value = params.get(field)
        if value:
            lookup = f'{field}_id' if value.isdigit() else f'{field}__slug'
            queryset = queryset.filter(**{lookup: value})

    search = params.get('search')
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(short_description__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )
    return queryset


def _public_queryset():
    return Event.objects.published().select_related('destination', 'journey', 'package')


# ---------- Public Endpoints ----------

class EventListView(generics.ListAPIView):
    """
    GET /api/events/
    Query params: start, end (YYYY-MM-DD or ISO datetime; returns events overlapping the range),
    type (comma separated), featured=true, destination, journey, package (id or slug), search.
    """
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = []

    def get_queryset(self):
        return filter_events(_public_queryset(), self.request.query_params).order_by('start', 'title')


class UpcomingEventListView(generics.ListAPIView):
    """
    GET /api/events/upcoming/?limit=6
    Published events that have not finished yet, soonest first.
    """
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = []
    pagination_class = None

    def get_queryset(self):
        queryset = filter_events(_public_queryset().upcoming(), self.request.query_params).order_by('start')
        try:
            limit = int(self.request.query_params.get('limit', 10))
        except ValueError:
            raise ValidationError({'limit': 'Must be an integer.'})
        return queryset[:max(1, min(limit, 100))]


class EventDetailView(generics.RetrieveAPIView):
    """GET /api/events/<slug>/"""
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return _public_queryset()


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def event_calendar(request):
    """
    GET /api/events/calendar/?year=2026&month=10
    Returns the month's events plus a `days` map of YYYY-MM-DD -> event ids
    (multi-day events appear on every day they cover). Accepts the same filters as the list.
    """
    today = timezone.localdate()
    try:
        year = int(request.query_params.get('year', today.year))
        month = int(request.query_params.get('month', today.month))
        first = date(year, month, 1)
    except ValueError:
        raise ValidationError({'detail': 'year and month must be valid integers (month 1-12).'})

    last = date(year, month, pycalendar.monthrange(year, month)[1])
    params = request.query_params.copy()
    params.pop('start', None)
    params.pop('end', None)
    events = list(
        filter_events(_public_queryset(), params)
        .overlapping(_local_day_start(first), _local_day_start(last + timedelta(days=1)))
        .order_by('start', 'title')
    )

    days = {}
    for event in events:
        for d in event.local_dates():
            if first <= d <= last:
                days.setdefault(d.isoformat(), []).append(event.id)

    return Response({
        'year': year,
        'month': month,
        'start': first.isoformat(),
        'end': last.isoformat(),
        'events': CalendarEventSerializer(events, many=True).data,
        'days': dict(sorted(days.items())),
    })


def _ics_response(events, request, filename):
    response = HttpResponse(build_calendar(events, request), content_type='text/calendar; charset=utf-8')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


def event_calendar_feed(request):
    """GET /api/events/calendar.ics - subscribable iCalendar feed of upcoming published events."""
    events = filter_events(_public_queryset().upcoming(), request.GET).order_by('start')
    return _ics_response(events, request, 'pranna-events.ics')


def event_ics(request, slug):
    """GET /api/events/<slug>/ics/ - single event as an .ics file."""
    event = get_object_or_404(_public_queryset(), slug=slug)
    return _ics_response([event], request, f'{event.slug}.ics')


# ---------- Admin Endpoints ----------

class EventAdminListView(generics.ListAPIView):
    """GET /api/events/admin/ - all events including unpublished (admin only)."""
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = []

    def get_queryset(self):
        queryset = Event.objects.select_related('destination', 'journey', 'package')
        return filter_events(queryset, self.request.query_params).order_by('start', 'title')


class EventCreateView(generics.CreateAPIView):
    """POST /api/events/admin/create/"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAdminUser]


class EventUpdateView(generics.UpdateAPIView):
    """PUT/PATCH /api/events/admin/update/<slug>/"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'


class EventDeleteView(generics.DestroyAPIView):
    """DELETE /api/events/admin/delete/<slug>/"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'
