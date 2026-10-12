from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Event


def aware(*args):
    return timezone.make_aware(datetime(*args))


class EventModelTests(TestCase):
    def test_slug_is_generated_and_unique(self):
        a = Event.objects.create(title='Sound Healing', start=aware(2026, 11, 1, 10))
        b = Event.objects.create(title='Sound Healing', start=aware(2026, 11, 1, 18))
        self.assertEqual(a.slug, 'sound-healing-2026-11-01')
        self.assertEqual(b.slug, 'sound-healing-2026-11-01-2')

    def test_end_before_start_is_invalid(self):
        event = Event(title='Bad', start=aware(2026, 11, 2), end=aware(2026, 11, 1))
        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_local_dates_spans_multi_day_event(self):
        event = Event(title='Retreat', start=aware(2026, 10, 30, 9), end=aware(2026, 11, 2, 12))
        self.assertEqual(
            [d.isoformat() for d in event.local_dates()],
            ['2026-10-30', '2026-10-31', '2026-11-01', '2026-11-02'],
        )


class EventApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.retreat = Event.objects.create(
            title='Mustang Retreat', event_type='retreat',
            start=aware(2026, 10, 30, 9), end=aware(2026, 11, 2, 17), is_featured=True,
        )
        self.workshop = Event.objects.create(
            title='Yoga Workshop', event_type='workshop',
            start=aware(2026, 11, 15, 8), end=aware(2026, 11, 15, 10), location='Kathmandu',
        )
        self.hidden = Event.objects.create(
            title='Draft Event', start=aware(2026, 11, 20, 8), is_published=False,
        )

    def test_list_excludes_unpublished(self):
        res = self.client.get('/api/events/')
        self.assertEqual(res.status_code, 200)
        slugs = [e['slug'] for e in res.data['results']]
        self.assertEqual(slugs, [self.retreat.slug, self.workshop.slug])

    def test_list_date_range_returns_overlapping_events(self):
        res = self.client.get('/api/events/', {'start': '2026-11-01', 'end': '2026-11-10'})
        self.assertEqual([e['slug'] for e in res.data['results']], [self.retreat.slug])

    def test_list_filters(self):
        res = self.client.get('/api/events/', {'type': 'workshop'})
        self.assertEqual([e['slug'] for e in res.data['results']], [self.workshop.slug])
        res = self.client.get('/api/events/', {'featured': 'true'})
        self.assertEqual([e['slug'] for e in res.data['results']], [self.retreat.slug])
        res = self.client.get('/api/events/', {'search': 'kathmandu'})
        self.assertEqual([e['slug'] for e in res.data['results']], [self.workshop.slug])

    def test_invalid_date_returns_400(self):
        res = self.client.get('/api/events/', {'start': 'not-a-date'})
        self.assertEqual(res.status_code, 400)

    def test_calendar_groups_by_day(self):
        res = self.client.get('/api/events/calendar/', {'year': 2026, 'month': 11})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['start'], '2026-11-01')
        self.assertEqual(res.data['end'], '2026-11-30')
        self.assertEqual(len(res.data['events']), 2)
        self.assertEqual(res.data['days']['2026-11-01'], [self.retreat.id])
        self.assertEqual(res.data['days']['2026-11-02'], [self.retreat.id])
        self.assertEqual(res.data['days']['2026-11-15'], [self.workshop.id])
        self.assertNotIn('2026-10-31', res.data['days'])
        self.assertNotIn('2026-11-20', res.data['days'])

    def test_calendar_invalid_month(self):
        res = self.client.get('/api/events/calendar/', {'year': 2026, 'month': 13})
        self.assertEqual(res.status_code, 400)

    def test_upcoming(self):
        past = Event.objects.create(title='Past', start=timezone.now() - timedelta(days=3),
                                    end=timezone.now() - timedelta(days=2))
        ongoing = Event.objects.create(title='Ongoing', start=timezone.now() - timedelta(days=1),
                                       end=timezone.now() + timedelta(days=1))
        res = self.client.get('/api/events/upcoming/', {'limit': 50})
        slugs = [e['slug'] for e in res.data]
        self.assertNotIn(past.slug, slugs)
        self.assertIn(ongoing.slug, slugs)
        self.assertNotIn(self.hidden.slug, slugs)

    def test_detail_and_unpublished_404(self):
        self.assertEqual(self.client.get(f'/api/events/{self.retreat.slug}/').status_code, 200)
        self.assertEqual(self.client.get(f'/api/events/{self.hidden.slug}/').status_code, 404)

    def test_ics_exports(self):
        res = self.client.get(f'/api/events/{self.workshop.slug}/ics/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'text/calendar; charset=utf-8')
        body = res.content.decode()
        self.assertIn('BEGIN:VCALENDAR', body)
        self.assertIn('SUMMARY:Yoga Workshop', body)
        self.assertIn('DTSTART:20261115T080000Z', body)
        self.assertIn('LOCATION:Kathmandu', body)

    def test_all_day_ics_uses_exclusive_date_end(self):
        event = Event.objects.create(title='Festival', start=aware(2027, 1, 5), end=aware(2027, 1, 6, 23),
                                     all_day=True)
        body = self.client.get(f'/api/events/{event.slug}/ics/').content.decode()
        self.assertIn('DTSTART;VALUE=DATE:20270105', body)
        self.assertIn('DTEND;VALUE=DATE:20270107', body)

    def test_admin_endpoints_require_staff(self):
        payload = {'title': 'New Class', 'event_type': 'class', 'start': '2026-12-01T09:00:00Z'}
        self.assertIn(self.client.post('/api/events/admin/create/', payload).status_code, (401, 403))

        admin = get_user_model().objects.create_user('admin', password='pw', is_staff=True)
        self.client.force_authenticate(admin)
        res = self.client.post('/api/events/admin/create/', payload, format='json')
        self.assertEqual(res.status_code, 201, res.data)
        slug = res.data['slug']

        res = self.client.patch(f'/api/events/admin/update/{slug}/', {'end': '2026-11-30T09:00:00Z'},
                                format='json')
        self.assertEqual(res.status_code, 400)

        res = self.client.get('/api/events/admin/')
        self.assertIn(self.hidden.slug, [e['slug'] for e in res.data['results']])

        self.assertEqual(self.client.delete(f'/api/events/admin/delete/{slug}/').status_code, 204)
