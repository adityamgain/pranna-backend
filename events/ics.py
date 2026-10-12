from datetime import timedelta

from django.utils import timezone

PRODID = '-//Pranna Wellness//Events//EN'


def _escape(text):
    return (
        (text or '')
        .replace('\\', '\\\\')
        .replace(';', '\\;')
        .replace(',', '\\,')
        .replace('\r\n', '\\n')
        .replace('\n', '\\n')
    )


def _fold(line):
    """Fold lines longer than 75 octets per RFC 5545."""
    encoded = line.encode('utf-8')
    if len(encoded) <= 75:
        return line
    parts, current = [], b''
    for char in line:
        b = char.encode('utf-8')
        if len(current) + len(b) > (75 if not parts else 74):
            parts.append(current.decode('utf-8'))
            current = b''
        current += b
    parts.append(current.decode('utf-8'))
    return '\r\n '.join(parts)


def _utc(dt):
    return dt.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def _event_lines(event, request):
    lines = [
        'BEGIN:VEVENT',
        f'UID:event-{event.pk}@pranna',
        f'DTSTAMP:{_utc(event.updated_at or timezone.now())}',
        f'SUMMARY:{_escape(event.title)}',
    ]
    if event.all_day:
        first = timezone.localtime(event.start).date()
        last = timezone.localtime(event.effective_end).date()
        lines.append(f'DTSTART;VALUE=DATE:{first:%Y%m%d}')
        lines.append(f'DTEND;VALUE=DATE:{last + timedelta(days=1):%Y%m%d}')
    else:
        lines.append(f'DTSTART:{_utc(event.start)}')
        if event.end:
            lines.append(f'DTEND:{_utc(event.end)}')
    description = event.short_description or event.description
    if description:
        lines.append(f'DESCRIPTION:{_escape(description)}')
    location = event.location or (event.destination.name if event.destination else '')
    if location:
        lines.append(f'LOCATION:{_escape(location)}')
    url = event.registration_url or request.build_absolute_uri(f'/api/events/{event.slug}/')
    lines.append(f'URL:{url}')
    lines.append(f'CATEGORIES:{_escape(event.get_event_type_display())}')
    lines.append('END:VEVENT')
    return lines


def build_calendar(events, request):
    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        f'PRODID:{PRODID}',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'X-WR-CALNAME:Pranna Events',
    ]
    for event in events:
        lines.extend(_event_lines(event, request))
    lines.append('END:VCALENDAR')
    return '\r\n'.join(_fold(line) for line in lines) + '\r\n'
