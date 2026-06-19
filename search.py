from typing import Optional
from rapidfuzz import fuzz
from availability import is_available


def best_fuzzy_match(query: str, candidates: list[str], threshold: int) -> Optional[str]:
    best_score, best_match = 0, None
    for candidate in candidates:
        score = fuzz.token_sort_ratio(query.lower(), candidate.lower())
        if score > best_score:
            best_score, best_match = score, candidate
    return best_match if best_score >= threshold else None


def search_doctors(
    data: list[dict],
    known_locations: list[str],
    known_specialties: list[str],
    location: Optional[str] = None,
    specialty: Optional[str] = None,
    doctor_name: Optional[str] = None,
    clinic_name: Optional[str] = None,
    language: Optional[str] = None,
    requested_time: Optional[str] = None,
    top_n: int = 10,
) -> list[tuple[dict, int]]:
    normalized_location = best_fuzzy_match(location, known_locations, 70) if location else None
    normalized_specialty = best_fuzzy_match(specialty, known_specialties, 70) if specialty else None

    if location and normalized_location is None:
        return []
    if specialty and normalized_specialty is None:
        return []

    scored = []
    for record in data:
        if normalized_location and record["location"] != normalized_location:
            continue
        if normalized_specialty and record["speciality"] != normalized_specialty:
            continue
        if language and language not in record["languages"]:
            continue
        if requested_time and not is_available(record["availability"], requested_time):
            continue

        name_score = 100
        clinic_score = 100

        if doctor_name:
            full_name = f"{record['first_name']} {record['last_name']}"
            name_score = fuzz.WRatio(doctor_name.lower(), full_name.lower())
            if name_score < 65:
                continue

        if clinic_name:
            clinic_score = fuzz.WRatio(clinic_name.lower(), record["clinic_name"].lower())
            if clinic_score < 65:
                continue

        active = [s for f, s in [(doctor_name, name_score), (clinic_name, clinic_score)] if f]
        fuzzy_score = sum(active) / len(active) if active else 100.0
        composite = fuzzy_score * 0.6 + (record["rating"] / 5.0 * 100) * 0.4
        scored.append((composite, record, int(fuzzy_score)))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [(record, score) for _, record, score in scored[:top_n]]
