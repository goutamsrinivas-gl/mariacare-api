import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import SearchRequest, SearchResponse, DoctorResult
from search import search_doctors

_data_path = Path(__file__).parent / "data" / "healthcare_data.json"
with open(_data_path) as f:
    DATA = json.load(f)
KNOWN_LOCATIONS = sorted(set(r["location"] for r in DATA))
KNOWN_SPECIALTIES = sorted(set(r["speciality"] for r in DATA))

app = FastAPI(title="MariaCare Doctor Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/search/doctors", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    matches = search_doctors(
        data=DATA,
        known_locations=KNOWN_LOCATIONS,
        known_specialties=KNOWN_SPECIALTIES,
        location=request.location,
        specialty=request.specialty,
        doctor_name=request.doctor_name,
        clinic_name=request.clinic_name,
        language=request.language,
        requested_time=request.requested_time,
    )
    results = [
        DoctorResult(
            doctor=f"{r['first_name']} {r['last_name']}",
            clinic=r["clinic_name"],
            speciality=r["speciality"],
            location=r["location"],
            availability=r["availability"],
            languages=r["languages"],
            rating=r["rating"],
            phone=r["phone"],
            email=r["email"],
            match_score=score,
        )
        for r, score in matches
    ]
    return SearchResponse(results=results, total=len(results))
