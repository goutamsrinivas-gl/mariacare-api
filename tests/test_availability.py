from availability import is_available


def test_monday_within_mon_fri_window():
    assert is_available("Mon-Fri 08:00-16:00", "Monday 10:00") is True


def test_saturday_outside_mon_fri_window():
    assert is_available("Mon-Fri 08:00-16:00", "Saturday 10:00") is False


def test_time_before_window_start():
    assert is_available("Mon-Fri 08:00-16:00", "Monday 07:00") is False


def test_time_after_window_end():
    assert is_available("Mon-Fri 08:00-16:00", "Monday 17:00") is False


def test_saturday_within_mon_sat_window():
    assert is_available("Mon-Sat 09:00-14:00", "Saturday 12:00") is True


def test_boundary_times_are_inclusive():
    assert is_available("Mon-Fri 08:00-16:00", "Monday 08:00") is True
    assert is_available("Mon-Fri 08:00-16:00", "Monday 16:00") is True


def test_tue_sat_window():
    assert is_available("Tue-Sat 08:30-16:30", "Wednesday 09:00") is True
    assert is_available("Tue-Sat 08:30-16:30", "Monday 09:00") is False
