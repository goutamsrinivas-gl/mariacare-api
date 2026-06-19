from search import best_fuzzy_match, search_doctors

KNOWN_LOCATIONS = ["Bucharest", "Cluj-Napoca", "Timisoara", "Iasi"]
KNOWN_SPECIALTIES = ["Cardiology", "Dermatology", "Family Medicine", "Neurology"]

SAMPLE_DATA = [
    {
        "first_name": "Robert", "last_name": "Ionescu",
        "clinic_name": "Clinica Bucharest Care", "location": "Bucharest",
        "speciality": "Cardiology", "phone": "+40-21-000-0001",
        "email": "r.ionescu@test.ro", "postal_code": "010001",
        "county": "Ilfov", "years_experience": 10,
        "education": "Carol Davila", "languages": ["Romanian", "English"],
        "availability": "Mon-Fri 08:00-16:00", "rating": 4.5,
        "address": "Str. Test 1",
    },
    {
        "first_name": "Ana", "last_name": "Pop",
        "clinic_name": "Clinica Cluj Care", "location": "Cluj-Napoca",
        "speciality": "Dermatology", "phone": "+40-21-000-0002",
        "email": "a.pop@test.ro", "postal_code": "400001",
        "county": "Cluj", "years_experience": 5,
        "education": "UMF Cluj", "languages": ["Romanian"],
        "availability": "Mon-Sat 09:00-14:00", "rating": 3.8,
        "address": "Str. Test 2",
    },
]


def test_fuzzy_match_typo_bucharest():
    assert best_fuzzy_match("Bukalest", KNOWN_LOCATIONS, threshold=70) == "Bucharest"


def test_fuzzy_match_below_threshold_returns_none():
    assert best_fuzzy_match("ZZZZZ", KNOWN_LOCATIONS, threshold=70) is None


def test_search_by_location_normalizes_typo():
    results = search_doctors(SAMPLE_DATA, KNOWN_LOCATIONS, KNOWN_SPECIALTIES, location="Bukalest")
    assert len(results) == 1
    assert results[0][0]["location"] == "Bucharest"


def test_search_by_specialty_normalizes_typo():
    results = search_doctors(SAMPLE_DATA, KNOWN_LOCATIONS, KNOWN_SPECIALTIES, specialty="Cardiologgy")
    assert len(results) == 1
    assert results[0][0]["speciality"] == "Cardiology"


def test_language_filter_excludes_non_matching():
    results = search_doctors(SAMPLE_DATA, KNOWN_LOCATIONS, KNOWN_SPECIALTIES,
                             location="Bucharest", language="English")
    assert all("English" in r[0]["languages"] for r in results)


def test_availability_filter():
    results = search_doctors(SAMPLE_DATA, KNOWN_LOCATIONS, KNOWN_SPECIALTIES,
                             location="Bucharest", requested_time="Monday 10:00")
    assert len(results) == 1


def test_unrecognized_location_returns_empty():
    results = search_doctors(SAMPLE_DATA, KNOWN_LOCATIONS, KNOWN_SPECIALTIES, location="ZZZZZZZ")
    assert results == []


def test_doctor_name_fuzzy_match():
    results = search_doctors(SAMPLE_DATA, KNOWN_LOCATIONS, KNOWN_SPECIALTIES,
                             doctor_name="Dobert Ionescu")
    assert len(results) == 1
    assert results[0][0]["first_name"] == "Robert"
