from pydantic import BaseModel, model_validator
from typing import Optional, List


class SearchRequest(BaseModel):
    location: Optional[str] = None
    specialty: Optional[str] = None
    doctor_name: Optional[str] = None
    clinic_name: Optional[str] = None
    language: Optional[str] = None
    requested_time: Optional[str] = None  # e.g. "Monday 10:00"

    @model_validator(mode="after")
    def at_least_one_search_field(self):
        if not any([self.location, self.specialty, self.doctor_name, self.clinic_name]):
            raise ValueError("Provide at least one of: location, specialty, doctor_name, clinic_name")
        return self


class DoctorResult(BaseModel):
    doctor: str
    clinic: str
    speciality: str
    location: str
    availability: str
    languages: List[str]
    rating: float
    phone: str
    email: str
    match_score: int


class SearchResponse(BaseModel):
    results: List[DoctorResult]
    total: int
