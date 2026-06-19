DAY_ABBREV = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
DAY_FULL = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6,
}


def _to_minutes(t: str) -> int:
    h, m = map(int, t.split(":"))
    return h * 60 + m


def _parse_window(availability: str) -> tuple[set[int], int, int]:
    day_part, time_part = availability.split(" ")
    start_day, end_day = day_part.split("-")
    days = set(range(DAY_ABBREV[start_day], DAY_ABBREV[end_day] + 1))
    start_time, end_time = time_part.split("-")
    return days, _to_minutes(start_time), _to_minutes(end_time)


def is_available(availability: str, requested_time: str) -> bool:
    parts = requested_time.strip().split(" ")
    if len(parts) != 2:
        return False
    day_str, time_str = parts
    day_idx = DAY_FULL.get(day_str)
    if day_idx is None:
        return False
    requested_min = _to_minutes(time_str)
    days, start_min, end_min = _parse_window(availability)
    return day_idx in days and start_min <= requested_min <= end_min
