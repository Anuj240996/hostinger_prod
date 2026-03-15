import datetime
import pytz
from dateutil.parser import parse as dateutil_parser
from datetime import timedelta

IST_TIMEZONE_STRING = 'Asia/Kolkata'
IST_TIMEZONE = pytz.timezone(IST_TIMEZONE_STRING)
UTC_TIMEZONE = pytz.timezone("UTC")
DEFAULT_DATE_TIME_STRING_FORMAT = "%d %b, %Y %I:%M %p"


def convert_seconds_to_duration_string(data):
    return str(datetime.timedelta(seconds=data))


def now_ist():
    return datetime.datetime.now(IST_TIMEZONE)


def now_utc():
    return datetime.datetime.now(UTC_TIMEZONE)


def very_old_date_time():
    dt = datetime.datetime.now(IST_TIMEZONE)
    dt = dt.replace(year=1901, month=1, day=1)

    return dt


def today():
    return now_ist().date()


def add_time_zone(datetime_obj):
    return IST_TIMEZONE.localize(datetime_obj)


def convert_to_ist_timezone(datetime_obj):
    if not datetime_obj.tzinfo:
        # No timezone present add IST
        datetime_obj = datetime_obj.replace(tzinfo=IST_TIMEZONE)
    else:
        datetime_obj = datetime_obj.astimezone(IST_TIMEZONE)
    return datetime_obj


def parse_date_time_from_amazon_sheet(date_str):
    if not date_str:
        return None
    try:
        parsed_date_time = convert_to_ist_timezone(dateutil_parser(date_str))
    except Exception as e:
        parsed_date_time = None

    return parsed_date_time


def parse_date(data, should_add_time_zone=True, ignore_exception=False, date_time_format=""):
    if isinstance(data, datetime.datetime) or isinstance(data, datetime.date):
        if should_add_time_zone and isinstance(data, datetime.datetime):
            return convert_to_ist_timezone(data)
        else:
            return data
    else:
        try:
            if date_time_format:
                parsed_data = datetime.datetime.strptime(data, date_time_format)
            else:
                parsed_data = dateutil_parser(data)
            if should_add_time_zone:
                return convert_to_ist_timezone(parsed_data)
            else:
                return parsed_data
        except Exception as e:
            if ignore_exception:
                capture_exception(e)
                return None
            else:
                raise e


def convert_datetime_to_string(data, format=DEFAULT_DATE_TIME_STRING_FORMAT, should_add_time_zone=False):
    parsed_data = parse_date(data, should_add_time_zone=should_add_time_zone, ignore_exception=True)
    if parsed_data:
        return parsed_data.strftime(format)
    else:
        return ""
