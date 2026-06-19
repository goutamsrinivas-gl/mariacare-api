import pytest
from models import SearchRequest


def test_valid_request_with_location():
    req = SearchRequest(location="Bucharest")
    assert req.location == "Bucharest"


def test_valid_request_with_specialty():
    req = SearchRequest(specialty="Cardiology")
    assert req.specialty == "Cardiology"


def test_invalid_request_no_search_fields():
    with pytest.raises(Exception):
        SearchRequest(language="English")


def test_all_optional_fields_with_doctor_name():
    req = SearchRequest(doctor_name="Ion Popescu", language="Romanian", requested_time="Monday 10:00")
    assert req.doctor_name == "Ion Popescu"
    assert req.language == "Romanian"
