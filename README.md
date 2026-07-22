# EIS Marks Platform

Clean ERP marks data → relational SQLite schema → Django REST API → React UI.

Platform Engineer screening project for **Euro International School (Sikar)**. Focus: correct cleaning rules, live aggregates, and a maintainable small codebase.

| | |
|---|---|
| **GitHub Repository** | _[Add your public repo URL here]_ |
| **Demo Video (Loom)** | _[Add your 3–5 minute Loom URL here]_ |

---

## 1. Project Overview

School ERP exports are messy. This app takes:

- `data/students_marks.csv` — duplicates, inconsistent names, mixed date formats, blank absents  
- `data/corrections.json` — mark corrections (including intentional invalid rows)

Then it:

1. Cleans and imports the CSV into Django models  
2. Exposes list / detail / summary APIs  
3. Applies corrections through a validated write endpoint  
4. Shows results in a simple React front end  

Totals and averages are computed on read (never cached at import), so corrections stay consistent everywhere.

---

## 2. Features

- Idempotent CSV import (wipe + reload)
- Duplicate resolution (keep higher mark)
- Name and date normalization
- Absent marks as `NULL` in the DB / `"Absent"` in the UI
- Case-insensitive student search
- Class summary (subject averages + top student)
- Corrections API with strict validation
- HTTP script to apply `corrections.json`

---

## 3. System Architecture

One Django domain app (`academics`) with thin views, DRF serializers, and small service modules for import/cleaning/aggregations. React is a lightweight client over the same APIs.

---

## 4. ASCII Architecture Diagram

```text
┌─────────────────────┐     ┌─────────────────────┐
│ students_marks.csv  │     │  corrections.json   │
└─────────┬───────────┘     └──────────┬──────────┘
          │                            │
          ▼                            │
┌─────────────────────┐                │
│  import_marks       │                │
│  (management cmd)   │                │
└─────────┬───────────┘                │
          │                            │
          ▼                            │
┌─────────────────────┐                │
│  SQLite             │                │
│  Student / Mark     │◄───────────────┤
└─────────┬───────────┘                │
          │                            │
          ▼                            ▼
┌──────────────────────────────────────────────┐
│           Django REST Framework              │
│  GET  /api/students/                         │
│  GET  /api/students/<admission_no>/          │
│  GET  /api/summary/                          │
│  POST /api/marks/corrections/                │
└──────────────────────┬───────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐     ┌──────────────────────┐
│  React (Vite)    │     │ apply_corrections.py │
│  List / Detail / │     │ (HTTP POST loop)     │
│  Summary         │     └──────────────────────┘
└──────────────────┘
```

---

## 5. Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5, Django REST Framework |
| Database | SQLite (models are PostgreSQL-ready) |
| CORS | django-cors-headers |
| Frontend | React 18, Vite, React Router |
| Import | Python stdlib `csv` |
| Corrections client | `requests` |

---

## 6. Folder Structure

```text
.
├── README.md
├── ENGINEERING_BLUEPRINT.md
├── .gitignore
├── data/
│   ├── students_marks.csv
│   └── corrections.json
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   ├── academics/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tests.py
│   │   ├── services/
│   │   └── management/commands/import_marks.py
│   └── scripts/apply_corrections.py
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── api.js
        ├── App.jsx
        ├── components/Layout.jsx
        └── pages/
```

---

## 7. Database Design

### Student

| Field | Type | Notes |
|-------|------|-------|
| `admission_no` | CharField (PK) | e.g. `EIS-1012` |
| `name` | CharField | Title Case, trimmed |
| `student_class` | PositiveSmallInteger | JSON key: `"class"` |
| `section` | CharField | |
| `date_of_birth` | DateField | |

### Mark

| Field | Type | Notes |
|-------|------|-------|
| `id` | BigAutoField (PK) | |
| `student` | FK → Student | `CASCADE` |
| `subject` | CharField | English, Hindi, Maths, Science, Social Science |
| `marks_obtained` | IntegerField, nullable | `NULL` = Absent |

Unique constraint: `(student, subject)`.

---

## 8. Data Cleaning Rules

1. **Duplicates** — same `(admission_no, subject)` → keep the higher mark  
2. **Names** — trim, collapse spaces, Title Case  
3. **Absents** — blank marks → `NULL`; excluded from totals/averages  
4. **Dates** — normalize to `YYYY-MM-DD`  
5. **Subjects** — must be one of the five allowed values  
6. **Import** — transactional wipe + reload (safe to re-run)

---

## 9. API Endpoints

Base URL: `http://127.0.0.1:8000/api/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/students/?search=` | List students; optional name search |
| GET | `/students/<admission_no>/` | Detail with marks, total, average |
| GET | `/summary/` | Subject averages + top student |
| POST | `/marks/corrections/` | Update a mark (`200` / `400`) |

### Sample: list students

```bash
curl "http://127.0.0.1:8000/api/students/?search=aditya"
```

```json
[
  {
    "admission_no": "EIS-1009",
    "name": "Aditya Gupta",
    "class": 6,
    "section": "A",
    "dob": "2014-07-22",
    "average": 95.4
  }
]
```

### Sample: student detail

```bash
curl "http://127.0.0.1:8000/api/students/EIS-1034/"
```

```json
{
  "admission_no": "EIS-1034",
  "name": "Lakshita Joshi",
  "class": 6,
  "section": "B",
  "dob": "2014-11-27",
  "marks": [
    { "subject": "Social Science", "marks": null },
    { "subject": "Science", "marks": 85 }
  ],
  "total": 347,
  "average": 86.8
}
```

### Sample: summary

```bash
curl "http://127.0.0.1:8000/api/summary/"
```

```json
{
  "subject_averages": {
    "English": 73.9,
    "Hindi": 72.2,
    "Maths": 63.9,
    "Science": 68.2,
    "Social Science": 70.4
  },
  "top_student": {
    "admission_no": "EIS-1009",
    "name": "Aditya Gupta",
    "total": 477
  }
}
```

### Sample: correction

```bash
curl -X POST "http://127.0.0.1:8000/api/marks/corrections/" \
  -H "Content-Type: application/json" \
  -d "{\"admission_no\":\"EIS-1034\",\"subject\":\"Social Science\",\"marks\":62}"
```

**200**

```json
{
  "admission_no": "EIS-1034",
  "subject": "Social Science",
  "marks": 62
}
```

**400** (example: marks out of range)

```json
{
  "detail": "Ensure this value is less than or equal to 100."
}
```

---

## 10. Backend Setup

Prerequisites: Python 3.11+, Git.

From the repository root:

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Migrate
python backend/manage.py migrate

# 5. Import CSV
python backend/manage.py import_marks

# 6. Start API server
python backend/manage.py runserver 127.0.0.1:8000
```

API: `http://127.0.0.1:8000/api/`

---

## 11. Frontend Setup

Prerequisites: Node.js 18+ and npm.

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173`  
CORS allowlist includes the Vite origin on port `5173`.

---

## 12. Import Process

```bash
python backend/manage.py import_marks

# optional custom path
python backend/manage.py import_marks --csv data/students_marks.csv
```

Expected output for the provided CSV:

```text
rows_read=253, students=47, marks=235, absents=9
```

Re-run to reset the database to a clean pre-correction state.

---

## 13. Corrections Process

With the Django server running:

```bash
python backend/scripts/apply_corrections.py
```

Posts every object in `data/corrections.json` to `POST /api/marks/corrections/`.  
Continues after failures. Typical result: `ok=6 fail=3`.

---

## 14. Project Workflow

```text
migrate
  → import_marks
  → answer pre-correction questions
  → apply_corrections.py   (server must be running)
  → answer post-correction questions
  → import_marks again to reset
```

---

## 15. Testing

```bash
python backend/manage.py test academics
```

Focused unit tests:

1. Duplicate rows keep the higher mark  
2. Absent (`NULL`) marks are excluded from averages  
3. Corrections API rejects invalid corrections  

---

## 16. Demo Video

**Loom / screen recording:** _[Add your 3–5 minute demo URL here]_

Suggested walkthrough:

1. Search on the students list  
2. Open a student detail page (show an Absent badge)  
3. Open Summary  
4. Apply one valid correction via API/script  
5. Refresh detail to show the update  

### Screenshots

Add screenshots after recording (optional but recommended):

| Screen | File (example) |
|--------|----------------|
| Students list | `docs/screenshots/students.png` |
| Student detail | `docs/screenshots/detail.png` |
| Summary | `docs/screenshots/summary.png` |

```markdown
![Students list](docs/screenshots/students.png)
![Student detail](docs/screenshots/detail.png)
![Summary](docs/screenshots/summary.png)
```

---

## 17. Future Improvements

1. PostgreSQL + Docker Compose for shared environments  
2. Correction audit log (who / when / old → new)  
3. Authentication for exam-office vs read-only access  

---

## 18. Author

Built for the Euro International School **Platform Engineer** screening assignment.

| | |
|---|---|
| **GitHub Repository** | _[Add your public repo URL here]_ |
| **Demo Video (Loom)** | _[Add your Loom URL here]_ |
