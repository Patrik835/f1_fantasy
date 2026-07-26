from datetime import datetime, timedelta, timezone


def utc_now():
    return datetime.now(timezone.utc)


def to_utc_aware(value):
    if value is None:
        return None
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def to_utc_naive(value):
    aware_value = to_utc_aware(value)
    if aware_value is None:
        return None
    return aware_value.replace(tzinfo=None)


def parse_api_datetime(value):
    if not value:
        return None
    return to_utc_aware(datetime.fromisoformat(value.replace("Z", "+00:00")))


def prediction_deadline(race_date):
    return to_utc_aware(race_date) - timedelta(hours=1)
