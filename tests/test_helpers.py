import pytest
import pytz
from src.be_code_challenge.utils.helpers import parse_iso_datetime, is_time_within_range, get_day_of_week
from datetime import time, datetime
from src.be_code_challenge.utils.helpers import parse_time_range


def test_parse_iso_datetime_valid():
    date_str = "2024-08-13T15:30:00Z"
    expected = datetime(2024, 8, 13, 15, 30, tzinfo=pytz.UTC)
    result = parse_iso_datetime(date_str)
    assert result == expected


def test_parse_iso_datetime_with_timezone():
    date_str = "2024-08-13T15:30:00-05:00"
    expected = datetime(2024, 8, 13, 15, 30, tzinfo=pytz.FixedOffset(-300))
    result = parse_iso_datetime(date_str)
    assert result == expected


def test_parse_iso_datetime_invalid():
    with pytest.raises(ValueError):
        parse_iso_datetime("invalid-date")


def test_get_day_of_week_valid():
    dt = datetime(2024, 8, 13)  # A Tuesday
    assert get_day_of_week(dt) == "tue"


def test_get_day_of_week_edge_case():
    dt = datetime(2024, 8, 14)  # A Wednesday
    assert get_day_of_week(dt) == "wed"


def test_parse_time_range_valid():
    time_range_str = "0900-2100"
    start, end = parse_time_range(time_range_str)
    assert start == time(9, 0)
    assert end == time(21, 0)


def test_parse_time_range_invalid_format():
    with pytest.raises(ValueError):
        parse_time_range("0900-2500")


def test_parse_time_range_midnight():
    time_range_str = "2300-0100"
    start, end = parse_time_range(time_range_str)
    assert start == time(23, 0)
    assert end == time(1, 0)


def test_is_time_within_range_valid():
    t = time(10, 0)
    start_time = time(9, 0)
    end_time = time(17, 0)
    assert is_time_within_range(t, start_time, end_time) is True


def test_is_time_within_range_invalid():
    t = time(18, 0)
    start_time = time(9, 0)
    end_time = time(17, 0)
    assert is_time_within_range(t, start_time, end_time) is False


def test_is_time_within_range_midnight():
    t = time(23, 30)
    start_time = time(22, 0)
    end_time = time(2, 0)
    assert is_time_within_range(t, start_time, end_time) is True
