import datetime
from datetime import timedelta, timezone


def has_expired(expiry: int):
    return expiry <= get_current_timestamp()


def get_current_timestamp():
    # Get the current timezone-aware datetime object in UTC
    current_time = datetime.datetime.now(timezone.utc)

    # Get the Unix epoch timestamp in seconds
    timestamp_seconds = current_time.timestamp()

    return int(timestamp_seconds * 1000)


def get_timestamp(expires_delta: timedelta = timedelta(hours=1)) -> int:
    # Get the current timezone-aware datetime object in UTC
    current_time = datetime.datetime.now(timezone.utc)
    current_time = current_time + expires_delta

    # Get the Unix epoch timestamp in seconds
    timestamp_seconds = current_time.timestamp()

    return int(timestamp_seconds * 1000)


def get_current_datetime() -> datetime:
    return datetime.datetime.now(timezone.utc)


def get_n_previous_day_timestamp(days):
    prev_time = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=days)
    midnight_prev_time = datetime.datetime.combine(prev_time, datetime.time.min)
    return midnight_prev_time.timestamp() * 1000


def get_today_midnight_time():
    now = datetime.datetime.now(tz=timezone.utc)
    midnight_date = datetime.datetime(now.year, now.month, now.day, tzinfo=timezone.utc)  # Midnight
    return midnight_date.timestamp() * 1000


def get_formatted_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    time_str = ''
    if days > 0:
        time_str += f'{int(days)} days '
    if hours > 0:
        time_str += f'{int(hours)} hours '
    if minutes > 0:
        time_str += f'{int(minutes)} minutes '
    if seconds > 0 or time_str == '':
        time_str += f'{int(seconds)} seconds'

    return time_str
