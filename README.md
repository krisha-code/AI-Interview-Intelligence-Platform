# AI Interview Intelligence Platform

An AI-powered recruitment platform that automates resume screening, interview analysis, answer evaluation, candidate ranking, and final hiring decision generation.

The system has two main sides:

* **Recruiter Side**: Add job description, upload resumes, view candidate rankings, detailed reports, and final hiring decision.
* **Candidate Side**: Upload resume, give interview, record/capture media, answer interview questions, and view AI-generated feedback.

---

## Features

### Recruiter Side

* Recruiter dashboard
* Add job role and job description
* Upload candidate resume
* Resume skill extraction
* Resume-job semantic matching
* Candidate ranking
* Detailed candidate report
* Final hiring decision

### Candidate Side

* Candidate resume upload
* Interview audio analysis
* Interview image analysis
* Live image capture
* Live video recorder
* Uploaded video analysis
* Answer quality evaluation
* Candidate feedback view

---

## Tech Stack

### Backend

* FastAPI
* SQLAlchemy
* PostgreSQL
* Pydantic

### Frontend

* Streamlit
* Streamlit WebRTC

### Machine Learning / AI

* Sentence Transformers
* Whisper
* DeepFace
* Transformers
* Scikit-learn
* OpenCV

### Database

* PostgreSQL

---

## System Architecture

```text
Recruiter Side
    ↓
Add Job Role + Job Description
    ↓
Upload Candidate Resume
    ↓
Resume Analysis + Skill Matching
    ↓
Candidate Ranking + Report
    ↓
Final Hiring Decision
```

```text
Candidate Side
    ↓
Upload Resume
    ↓
Give Interview
    ↓
Audio / Image / Video Analysis
    ↓
Answer Quality Evaluation
    ↓
View Feedback
```

---

## Project Workflow

1. Recruiter enters job title and job description.
2. Recruiter or candidate uploads resume.
3. System extracts resume text and skills.
4. System compares resume with job description.
5. Candidate gives interview using audio, image, and video.
6. System analyzes:

   * Speech transcript
   * Sentiment
   * Filler words
   * Facial emotion
   * Confidence
   * Video behavior
7. Candidate answers interview questions.
8. System evaluates answer quality using relevance, STAR method, and clarity.
9. Recruiter views ranking, report, and final hiring decision.
10. Candidate can view feedback.

---

## Project Structure

```text
AI-Interview-Intelligence-Platform/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── database/
│       ├── services/
│       └── interview/
│
├── frontend/
│   └── app.py
│
├── datasets/
├── docs/
├── models/
├── notebooks/
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Database Tables

The system uses PostgreSQL with the following tables:

```text
candidates
jobs
matches
interview_analysis
answer_quality
image_analysis
video_analysis
```

---

## How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/krisha-code/AI-Interview-Intelligence-Platform.git
cd AI-Interview-Intelligence-Platform
```

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

## PostgreSQL Setup

Install PostgreSQL and create database:

```sql
CREATE DATABASE ai_interview_db;
CREATE USER ai_user WITH PASSWORD 'ai_password';
GRANT ALL PRIVILEGES ON DATABASE ai_interview_db TO ai_user;
ALTER DATABASE ai_interview_db OWNER TO ai_user;
```

Database URL used in the project:

```python
postgresql+psycopg2://ai_user:ai_password@localhost:5432/ai_interview_db
```

Create tables:

```bash
python -c "from backend.app.database.db import Base, engine; from backend.app.database.models import Candidate, Job, Match, InterviewAnalysis, AnswerQuality, VideoAnalysis, ImageAnalysis; Base.metadata.create_all(bind=engine); print('PostgreSQL tables created successfully')"
```

---

## Run Backend

```bash
uvicorn backend.app.main:app --reload
```

Backend will run on:

```text
http://localhost:8000
```

---

## Run Frontend

Open another terminal:

```bash
source venv/bin/activate
streamlit run frontend/app.py
```

Frontend will run on:

```text
http://localhost:8501
```

---

## Main API Endpoints

```text
POST /upload_resume_and_analyze
POST /upload_interview_analysis
POST /upload_image_analysis
POST /upload_video_analysis
POST /analyze_answer_quality
GET  /rank_candidates
GET  /candidate_report/{candidate_id}
GET  /final_candidate_score/{candidate_id}
```

---

## Screenshots

Add screenshots inside the `screenshots/` folder.

Recommended screenshots:

```text
Recruiter Dashboard
Add Job & Upload Resume
Candidate Interview Analysis
Live Video Recorder
Candidate Rankings
Candidate Report
Final Hiring Decision
Candidate Feedback
```

---

## Future Scope

* Recruiter and candidate login system
* Job-wise candidate tracking
* LLM-based AI interviewer
* Adaptive follow-up questions
* Email notification system
* Cloud deployment
* Docker-based production setup
* Advanced analytics dashboard

---

## Project Status

```text
Backend: Completed
Frontend: Completed
PostgreSQL Migration: Completed
Recruiter Side: Completed
Candidate Side: Completed
Live Video Recorder: Completed
AI Scoring System: Completed
```

---

## Author

**Krisha Gandhi**

B.Tech Information Technology
K.J. Somaiya Institute of Technology
