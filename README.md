# MariaCare Doctor Search API

A lightweight doctor and clinic search API built on top of MariaCare's raw database export. Handles fuzzy matching for typos and speech-to-text transcription errors — "Bukalest" resolves to Bucharest, "Cardiologgy" to Cardiology, "Dobert Ionescu" to Robert Ionescu.

**Live demo:** https://mariacare-api.vercel.app  
**API endpoint:** `POST https://mariacare-api.vercel.app/search/doctors`

---

## The Problem

MariaCare's database has no search, filter, or query API — only a raw JSON dump endpoint. Building on top of that directly means:

- No fuzzy matching for misspelled names or locations
- No filtering by specialty, language, or availability
- No ranking or relevance scoring

This project adds that layer without touching MariaCare's infrastructure.

---

## Architecture

```
MariaCare JSON dump
        │
        ▼
┌───────────────────┐
│   Data Load       │  Reads JSON at startup (~7,000 records, ~3MB)
│   (in-memory)     │  Derives known locations + specialties from data
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   Search Layer    │  rapidfuzz: normalizes typos in location & specialty
│   (search.py)     │  WRatio scoring for doctor/clinic name matching
│                   │  Exact filter on language enum
│                   │  Availability window parser (Mon-Fri 08:00-16:00)
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   FastAPI         │  Single POST /search/doctors endpoint
│   (main.py)       │  Pydantic request/response validation
│                   │  Returns top 10 results ranked by composite score
└────────┬──────────┘
         │
         ▼
    Vercel (serverless)
```

### Why in-memory?

At ~7,000 records and 3MB, the dataset fits comfortably in memory. Loading it at module startup means:
- Zero database infrastructure to maintain
- Sub-millisecond filtering once loaded
- Simple daily refresh: redeploy or restart to pick up new data

### Why rapidfuzz?

Purpose-built fuzzy string matching with no external dependencies. Used in two modes:

- **Location & specialty** — matched against the known value sets derived from the data (42 cities, 20 specialties). Input is normalized to the best matching canonical value before filtering, so results are always exact matches against clean data.
- **Doctor & clinic names** — scored directly against each record using `WRatio` (which tries multiple strategies and picks the best score). Records below a 65% similarity threshold are excluded.

### Composite ranking

```
composite_score = fuzzy_score × 0.6 + (rating / 5 × 100) × 0.4
```

Fuzzy relevance weighs more than rating, but highly rated doctors surface ahead of equally relevant lower-rated ones.

---

## API

### `POST /search/doctors`

**Request body** (all fields optional, but at least one search field required):

```json
{
  "location": "Bukalest",
  "specialty": "Cardiologgy",
  "doctor_name": "Dobert Ionescu",
  "clinic_name": "Clinica Cluj",
  "language": "English",
  "requested_time": "Monday 10:00"
}
```

| Field | Type | Notes |
|---|---|---|
| `location` | string | Fuzzy matched against 42 known Romanian cities |
| `specialty` | string | Fuzzy matched against 20 known specialties |
| `doctor_name` | string | Optional. Fuzzy matched against first + last name |
| `clinic_name` | string | Optional. Fuzzy matched against clinic name |
| `language` | string | Exact match. One of: Romanian, English, French, German, Hungarian, Italian, Spanish |
| `requested_time` | string | Format: `"Monday 10:00"`. Checked against doctor's availability window |

**Response:**

```json
{
  "results": [
    {
      "doctor": "Robert Ionescu",
      "clinic": "Clinica Bucharest Care",
      "speciality": "Cardiology",
      "location": "Bucharest",
      "availability": "Mon-Fri 08:00-16:00",
      "languages": ["Romanian", "English"],
      "rating": 4.7,
      "phone": "+40-...",
      "email": "r.ionescu@...",
      "match_score": 91
    }
  ],
  "total": 5
}
```

Returns up to 10 results, sorted by composite score descending.

---

## Project Structure

```
mariacare-api/
├── main.py              # FastAPI app, data load at startup
├── search.py            # Fuzzy matching: best_fuzzy_match(), search_doctors()
├── availability.py      # Parses "Mon-Fri 08:00-16:00" windows, is_available()
├── models.py            # Pydantic: SearchRequest, DoctorResult, SearchResponse
├── data/
│   └── healthcare_data.json   # 7,029 records (~3MB)
├── index.html           # Frontend demo (served by Vercel CDN)
├── tests/
│   ├── test_models.py
│   ├── test_availability.py
│   ├── test_search.py
│   └── test_api.py
├── requirements.txt
├── vercel.json
└── Dockerfile
```

---

## Running Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

API at `http://localhost:8000` — interactive docs at `http://localhost:8000/docs`.

### Run tests

```bash
pytest -v
```

26 tests covering models, availability parsing, fuzzy search logic, and API integration.

---

## Deployment

### Vercel (current)

```bash
vercel --prod
```

Routing in `vercel.json`: `/search/doctors` hits the Python serverless function; everything else is served as static files from Vercel's CDN.

### Docker

```bash
docker build -t mariacare-api .
docker run -p 8000:8000 mariacare-api
```

### Daily data refresh

For production, point a daily cron job at MariaCare's JSON endpoint, replace `data/healthcare_data.json`, and redeploy. On Vercel this takes ~20 seconds and requires no downtime.

---

## Data Schema

Each record in the JSON dump:

```json
{
  "first_name": "Ionut",
  "last_name": "Dumitrescu",
  "clinic_name": "Clinica Cluj-Napoca Care",
  "location": "Cluj-Napoca",
  "speciality": "Psychiatry",
  "address": "Strada Victoriei 29",
  "phone": "+40-279-189-704",
  "email": "ionut.dumitrescu@clinica-cluj-napoca-care.ro",
  "postal_code": "542417",
  "county": "Cluj",
  "years_experience": 3,
  "education": "Carol Davila University of Medicine and Pharmacy",
  "languages": ["Italian"],
  "availability": "Mon-Fri 08:00-16:00",
  "rating": 3.2
}
```
