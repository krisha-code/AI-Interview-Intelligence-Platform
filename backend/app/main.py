
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os
import json
import pickle
from backend.app.database.db import Base
from backend.app.database.db import engine
from backend.app.database.db import DB_BACKEND, DB_HOST
from backend.app.database.models import Candidate, Job, Match, InterviewAnalysis, AnswerQuality, VideoAnalysis, ImageAnalysis, InterviewQuestion
from backend.app.database.models import Match
from backend.app.database.db import SessionLocal
from backend.app.interview.answer_quality import evaluate_answer
from backend.app.database.db import get_db
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.services.skill_extraction import extract_skills
from backend.app.services.suggestions import generate_suggestions
from backend.app.services.pdf_parser import extract_text_from_pdf
from fastapi import UploadFile, File, Form, Depends, HTTPException
from backend.app.interview.speech_to_text import transcribe_audio
from backend.app.interview.answer_quality import evaluate_answer
from backend.app.interview.interview_pipeline import analyze_interview
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.app.interview.emotion_detection import detect_emotion
from backend.app.interview.confidence_detection import face_visibility_score
from backend.app.utils import skills
from backend.app.interview.video_analysis import analyze_interview_video
from backend.app.services.pdf_parser import extract_text_from_pdf
from backend.app.services.resume_pipeline import analyze_resume as analyze_resume_pipeline
app = FastAPI()
Base.metadata.create_all(bind=engine)
# Load data
RESUME_DATASET_PATH = "datasets/raw/resumes/Resume.csv"

if os.path.exists(RESUME_DATASET_PATH):
    resume_df = pd.read_csv(RESUME_DATASET_PATH)
else:
    resume_df = pd.DataFrame()
# Load embeddings
EMBEDDINGS_PATH = "models/resume_embeddings.npy"

if os.path.exists(EMBEDDINGS_PATH):
    resume_embeddings = np.load(EMBEDDINGS_PATH)
else:
    resume_embeddings = None

# Load model
# Load model
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)
CATEGORY_CLASSIFIER_PATH = "models/category_classifier.pkl"

if os.path.exists(CATEGORY_CLASSIFIER_PATH):
    with open(CATEGORY_CLASSIFIER_PATH, "rb") as f:
        category_classifier = pickle.load(f)
else:
    category_classifier = None

CATEGORY_ENCODER_PATH = "models/category_encoder.pkl"

if os.path.exists(CATEGORY_ENCODER_PATH):
    with open(CATEGORY_ENCODER_PATH, "rb") as f:
        category_encoder = pickle.load(f)
else:
    category_encoder = None

class JobRequest(BaseModel):
    job_text: str

class JobCreateRequest(BaseModel):
    job_title: str
    job_description: str


class QuestionCreateRequest(BaseModel):
    question: str


class ResumeAnalysisRequest(BaseModel):
    job_text: str
    resume_text: str

print("Category Classifier Loaded:", category_classifier is not None)
print("Category Encoder Loaded:", category_encoder is not None)

class AnswerQualityRequest(BaseModel):
    candidate_id: int
    question: str
    answer: str



@app.get("/")
def home():
    return {
        "message": "AI Interview Intelligence Platform Running"
    }
@app.get("/candidates")
def get_candidates(
    db: Session = Depends(get_db)
):
    candidates = db.query(Candidate).order_by(
        Candidate.id.desc()
    ).all()

    return [
        {
            "candidate_id": candidate.id,
            "filename": candidate.filename,
            "skills": candidate.skills,
            "final_score": candidate.final_score
        }
        for candidate in candidates
    ]
@app.post("/jobs")
def create_job(
    request: JobCreateRequest,
    db: Session = Depends(get_db)
):
    job = Job(
        job_title=request.job_title,
        job_description=request.job_description
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "job_title": job.job_title,
        "job_description": job.job_description
    }


@app.get("/jobs")
def get_jobs(
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).order_by(Job.id.desc()).all()

    return [
        {
            "job_id": job.id,
            "job_title": job.job_title,
            "job_description": job.job_description
        }
        for job in jobs
    ]


@app.post("/jobs/{job_id}/questions")
def add_interview_question(
    job_id: int,
    request: QuestionCreateRequest,
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    question = InterviewQuestion(
        job_id=job_id,
        question=request.question
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return {
        "question_id": question.id,
        "job_id": job_id,
        "question": question.question
    }


@app.get("/jobs/{job_id}/questions")
def get_interview_questions(
    job_id: int,
    db: Session = Depends(get_db)
):
    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.job_id == job_id
    ).order_by(InterviewQuestion.id.asc()).all()

    return [
        {
            "question_id": q.id,
            "job_id": q.job_id,
            "question": q.question
        }
        for q in questions
    ]

@app.get("/db_status")
def db_status():
    return {
        "database_backend": DB_BACKEND,
        "database_host": DB_HOST
    }
@app.post("/upload_resume_and_analyze")
async def upload_resume_and_analyze(

    resume: UploadFile = File(...),
    job_text: str = Form(...),
    job_title: str = Form("Not Provided"),
    db: Session = Depends(get_db)

):

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    file_path = f"uploads/{resume.filename}"

    with open(
        file_path,
        "wb"
    ) as buffer:

        buffer.write(
            await resume.read()
        )

    result = analyze_resume_pipeline(
        file_path,
        job_text
    )

    suggestions = generate_suggestions(
        result["missing_skills"]
    )

    candidate = Candidate(

        filename=resume.filename,

        skills=", ".join(
            result["resume_skills"]
        ),

        matched_skills=", ".join(
            result["matched_skills"]
        ),

        missing_skills=", ".join(
            result["missing_skills"]
        ),

        semantic_score=float(
            result["semantic_match_score"]
        ),

        skill_match_percentage=float(
            result["skill_match_percentage"]
        ),

        final_score=float(
            result["final_match_score"]
        )
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    job = Job(

        job_title=job_title,

        job_description=job_text
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    match = Match(

        candidate_id=candidate.id,

        job_id=job.id,

        semantic_score=float(
            result["semantic_match_score"]
        ),

        skill_match_percentage=float(
            result["skill_match_percentage"]
        ),

        final_score=float(
            result["final_match_score"]
        )
    )

    db.add(match)
    db.commit()
    db.refresh(match)

    return {

        "candidate_id":
        candidate.id,

        "job_id":
        job.id,

        "match_id":
        match.id,

        "filename":
        resume.filename,

        "job_title":
        job_title,

        "resume_skills":
        result["resume_skills"],

        "job_skills":
        result["job_skills"],

        "matched_skills":
        result["matched_skills"],

        "missing_skills":
        result["missing_skills"],

        "suggestions":
        suggestions,

        "skill_match_percentage":
        result["skill_match_percentage"],

        "semantic_match_score":
        result["semantic_match_score"],

        "final_match_score":
        result["final_match_score"]
    }
@app.post("/upload_resume_for_job")
async def upload_resume_for_job(
    resume: UploadFile = File(...),
    job_id: int = Form(...),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    file_path = f"uploads/{resume.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(await resume.read())

    result = analyze_resume_pipeline(
        file_path,
        job.job_description
    )

    suggestions = generate_suggestions(
        result["missing_skills"]
    )

    candidate = Candidate(
        filename=resume.filename,
        skills=", ".join(result["resume_skills"]),
        matched_skills=", ".join(result["matched_skills"]),
        missing_skills=", ".join(result["missing_skills"]),
        semantic_score=float(result["semantic_match_score"]),
        skill_match_percentage=float(result["skill_match_percentage"]),
        final_score=float(result["final_match_score"])
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    match = Match(
        candidate_id=candidate.id,
        job_id=job.id,
        semantic_score=float(result["semantic_match_score"]),
        skill_match_percentage=float(result["skill_match_percentage"]),
        final_score=float(result["final_match_score"])
    )

    db.add(match)
    db.commit()
    db.refresh(match)

    return {
        "candidate_id": candidate.id,
        "job_id": job.id,
        "match_id": match.id,
        "filename": resume.filename,
        "job_title": job.job_title,
        "resume_skills": result["resume_skills"],
        "job_skills": result["job_skills"],
        "matched_skills": result["matched_skills"],
        "missing_skills": result["missing_skills"],
        "suggestions": suggestions,
        "skill_match_percentage": result["skill_match_percentage"],
        "semantic_match_score": result["semantic_match_score"],
        "final_match_score": result["final_match_score"]
    }
@app.post("/upload_resume")
async def upload_resume(
    resume: UploadFile = File(...)
):

    file_path = f"uploads/{resume.filename}"

    with open(file_path, "wb") as f:

        content = await resume.read()

        f.write(content)

    resume_text = extract_text_from_pdf(
        file_path
    )
    resume_skills = extract_skills(resume_text)
    resume_embedding = model.encode(
    [resume_text]
)

    prediction_category = "Not available"
    if category_classifier is not None and category_encoder is not None:
        prediction_label = category_classifier.predict(resume_embedding)
        prediction_category = category_encoder.inverse_transform(prediction_label)[0]
        print("Final Category:")
        print(prediction_category)
    else:
        print("Category model not available. Skipping category prediction.")

    return {
        "filename": resume.filename,
        "skills": resume_skills,
        "predicted_category": prediction_category,
    }

@app.post("/analyze_resume")
def analyze_resume(request: ResumeAnalysisRequest):
    
    # Extract skills from Job Description
    job_skills = extract_skills(
        request.job_text
    )

    # Extract skills from Resume
    resume_skills = extract_skills(
        request.resume_text
    )

    # Common skills
    matched_skills = list(
        set(job_skills) &
        set(resume_skills)
    )
    
    missing_skills = list(
        set(job_skills) -
        set(resume_skills)
    )

    suggestions = generate_suggestions(
        missing_skills
    )
    
    if len(job_skills) > 0:
        skill_match_percentage = round(
            (
                len(matched_skills)
                /
                len(job_skills)
            ) * 100,
            2
        )
    else:
        skill_match_percentage = 0

    # Calculate semantic score
    resume_embedding = model.encode([request.resume_text])
    job_embedding = model.encode([request.job_text])
    semantic_score = float(
        cosine_similarity(
            job_embedding,
            resume_embedding
        )[0][0]
    )
    skill_score = skill_match_percentage / 100

    # Calculate final score
    final_score = float(
        round(
            (semantic_score * 0.7)
            +
            (skill_score * 0.3),
            4
        )
    )
    return {

    "skill_match_percentage":
    skill_match_percentage,

    "matched_skills":
    matched_skills,

    "missing_skills":
    missing_skills,

    "suggestions":
    suggestions,

    "semantic_score":
    round(
        semantic_score,
        4
    ),

    "final_score":
    final_score
}

@app.post("/match")
def match_resumes(request: JobRequest):
    if resume_df.empty or resume_embeddings is None:
        raise HTTPException(
            status_code=503,
            detail="Bulk resume dataset is not available in deployed app. Use /upload_resume_and_analyze instead."
        )

    # Extract skills from Job Description
    job_skills = extract_skills(
        request.job_text
    )

    # Create Job Embedding
    job_embedding = model.encode(
        [request.job_text]
    )

    # Semantic Similarity Scores
    scores = cosine_similarity(
        job_embedding,
        resume_embeddings
    )[0]

    all_results = []

    # Check EVERY resume
    for idx in range(len(resume_df)):
        
        resume_text = resume_df.iloc[idx]["Resume_str"]

        # Extract skills from resume
        resume_skills = extract_skills(
            resume_text
        )

        # Common skills
        matched_skills = list(
            set(job_skills) &
            set(resume_skills)
        )
        
        missing_skills = list(
            set(job_skills) -
            set(resume_skills)
        )

        suggestions = generate_suggestions(
            missing_skills
        )
        # Skill Match Percentage
        if len(job_skills) > 0:

            skill_match_percentage = round(
                (
                    len(matched_skills)
                    / len(job_skills)
                ) * 100,
                2
            )

        else:

            skill_match_percentage = 0

        # Semantic Score
        semantic_score = float(
            scores[idx]
        )

        # Convert skill percentage to 0-1 scale
        skill_score = (
            skill_match_percentage
            / 100
        )

        # Hybrid Score
        final_score = round(
            (
                semantic_score * 0.7
            )
            +
            (
                skill_score * 0.3
            ),
            4
        )

        # Get current resume embedding
        resume_embedding = resume_embeddings[idx]

        # Convert shape from (384,) to (1,384)
        resume_embedding = resume_embedding.reshape(1, -1)

        # Predict category using SVM
        predicted_category_encoded = category_classifier.predict(
            resume_embedding
        )

        # Convert encoded label back to text
        predicted_category = category_encoder.inverse_transform(
            predicted_category_encoded
        )[0]

        all_results.append({

            "resume_index":
            int(idx),

            "semantic_score":
            round(
                semantic_score,
                4
            ),

            "skills":
            resume_skills,

            "resume_text":
            resume_text[:800],

            "skill_match_percentage":
            skill_match_percentage,

            "matched_skills":
            matched_skills,

            "final_score":
            final_score,

            "missing_skills":
            missing_skills,

            "suggestions":
            suggestions
        })

    # Sort by Final Score
    all_results = sorted(
        all_results,
        key=lambda x: x["final_score"],
        reverse=True
    )

    # Top 5 Resumes
    results = all_results[:5]

    # Add Rank
    for i, item in enumerate(
        results,
        start=1
    ):
        item["rank"] = i

    # Save Best Resume
    os.makedirs(
        "outputs",
        exist_ok=True
    )

    best_resume_index = results[0][
        "resume_index"
    ]

    best_resume = resume_df.iloc[
        best_resume_index
    ]

    with open(
        "outputs/best_resume.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            best_resume["Resume_str"]
        )

    return results



@app.post("/transcribe_audio")
async def transcribe_interview_audio(
    audio: UploadFile = File(...)
):

    audio_path = f"interview_audio/{audio.filename}"

    with open(audio_path, "wb") as buffer:
        buffer.write(await audio.read())

    transcript = transcribe_audio(audio_path)

    return JSONResponse(
        content={
            "filename": audio.filename,
            "transcript": transcript
        }
    )
    
@app.post("/upload_interview_analysis")
async def upload_interview_analysis(

    candidate_id: int = Form(...),
    audio: UploadFile = File(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)

):

    os.makedirs(
        "interview_audio",
        exist_ok=True
    )

    os.makedirs(
        "interview_images",
        exist_ok=True
    )

    audio_path = f"interview_audio/{audio.filename}"

    image_path = f"interview_images/{image.filename}"

    with open(audio_path, "wb") as audio_file:

        audio_file.write(
            await audio.read()
        )

    with open(image_path, "wb") as image_file:

        image_file.write(
            await image.read()
        )

    result = analyze_interview(
        audio_path,
        image_path
    )

    interview_record = InterviewAnalysis(

        candidate_id=candidate_id,

        transcript=result["transcript"],

        sentiment=result["sentiment"]["sentiment"],

        sentiment_score=float(
            result["sentiment_score"]
        ),

        filler_count=int(
            result["filler_count"]
        ),

        filler_score=float(
            result["filler_score"]
        ),

        dominant_emotion=result["dominant_emotion"],

        emotion_score=float(
            result["emotion_score"]
        ),

        confidence_score=float(
            result["confidence_score"]
        ),

        overall_interview_score=float(
            result["overall_interview_score"]
        )
    )

    db.add(interview_record)

    db.commit()

    db.refresh(interview_record)

    return {

        "interview_analysis_id":
        interview_record.id,

        "candidate_id":
        candidate_id,

        "transcript":
        result["transcript"],

        "sentiment":
        result["sentiment"],

        "sentiment_score":
        result["sentiment_score"],

        "filler_count":
        result["filler_count"],

        "filler_score":
        result["filler_score"],

        "dominant_emotion":
        result["dominant_emotion"],

        "emotion_score":
        result["emotion_score"],

        "confidence_score":
        result["confidence_score"],

        "overall_interview_score":
        result["overall_interview_score"]
    }
    
@app.get("/final_candidate_score/{candidate_id}")
def final_candidate_score(

    candidate_id: int,
    db: Session = Depends(get_db)

):

    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id
    ).first()

    if candidate is None:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    interview = db.query(InterviewAnalysis).filter(
        InterviewAnalysis.candidate_id == candidate_id
    ).order_by(
        InterviewAnalysis.id.desc()
    ).first()

    if interview is None:

        raise HTTPException(
            status_code=404,
            detail="Interview analysis not found for this candidate"
        )

    answer_quality = db.query(AnswerQuality).filter(
        AnswerQuality.candidate_id == candidate_id
    ).order_by(
        AnswerQuality.id.desc()
    ).first()

    if answer_quality is None:

        raise HTTPException(
            status_code=404,
            detail="Answer quality analysis not found for this candidate"
        )

    resume_score = float(
        candidate.final_score
    )

    interview_score = float(
        interview.overall_interview_score
    )

    answer_quality_score = float(
        answer_quality.answer_quality_score
    )

    final_candidate_score = round(
        (
            resume_score * 0.40
        )
        +
        (
            interview_score * 0.30
        )
        +
        (
            answer_quality_score * 0.30
        ),
        2
    )

    if final_candidate_score >= 85:
        decision = "Strong Candidate"

    elif final_candidate_score >= 70:
        decision = "Good Candidate"

    else:
        decision = "Needs Improvement"

    return {

        "candidate_id":
        candidate.id,

        "resume_score":
        resume_score,

        "interview_delivery_score":
        interview_score,

        "answer_quality_score":
        answer_quality_score,

        "final_candidate_score":
        final_candidate_score,

        "decision":
        decision
    }

@app.get("/rank_candidates")
def rank_candidates(
    db: Session = Depends(get_db)
):

    candidates = db.query(Candidate).all()

    rankings = []

    for candidate in candidates:

        interview = db.query(InterviewAnalysis).filter(
            InterviewAnalysis.candidate_id == candidate.id
        ).order_by(
            InterviewAnalysis.id.desc()
        ).first()

        answer_quality = db.query(AnswerQuality).filter(
            AnswerQuality.candidate_id == candidate.id
        ).order_by(
            AnswerQuality.id.desc()
        ).first()

        if interview is None or answer_quality is None:
            continue

        resume_score = float(
            candidate.final_score
        )

        interview_score = float(
            interview.overall_interview_score
        )

        answer_quality_score = float(
            answer_quality.answer_quality_score
        )

        final_score = round(
            (
                resume_score * 0.40
            )
            +
            (
                interview_score * 0.30
            )
            +
            (
                answer_quality_score * 0.30
            ),
            2
        )

        if final_score >= 85:
            decision = "Strong Candidate"

        elif final_score >= 70:
            decision = "Good Candidate"

        else:
            decision = "Needs Improvement"

        rankings.append({

            "candidate_id":
            candidate.id,

            "filename":
            candidate.filename,

            "resume_score":
            resume_score,

            "interview_delivery_score":
            interview_score,

            "answer_quality_score":
            answer_quality_score,

            "final_candidate_score":
            final_score,

            "decision":
            decision
        })

    rankings = sorted(
        rankings,
        key=lambda x: x["final_candidate_score"],
        reverse=True
    )

    for index, candidate in enumerate(
        rankings,
        start=1
    ):
        candidate["rank"] = index

    return rankings


@app.post("/analyze_answer_quality")
def analyze_answer_quality(
    request: AnswerQualityRequest,
    db: Session = Depends(get_db)
):

    result = evaluate_answer(
        request.question,
        request.answer
    )

    answer_record = AnswerQuality(

        candidate_id=request.candidate_id,

        question=request.question,

        answer=request.answer,

        relevance_score=float(
            result["relevance_score"]
        ),

        star_score=float(
            result["star_score"]
        ),

        clarity_score=float(
            result["clarity_score"]
        ),

        answer_quality_score=float(
            result["answer_quality_score"]
        ),

        feedback=" | ".join(
            result["feedback"]
        )
    )

    db.add(answer_record)

    db.commit()

    db.refresh(answer_record)

    return {

        "answer_quality_id":
        answer_record.id,

        "candidate_id":
        request.candidate_id,

        "question":
        result["question"],

        "answer":
        result["answer"],

        "relevance_score":
        result["relevance_score"],

        "star_score":
        result["star_score"],

        "star_parts":
        result["star_parts"],

        "missing_star_parts":
        result["missing_star_parts"],

        "clarity_score":
        result["clarity_score"],

        "word_count":
        result["word_count"],

        "filler_count":
        result["filler_count"],

        "answer_quality_score":
        result["answer_quality_score"],

        "feedback":
        result["feedback"]
    }
@app.post("/upload_video_analysis")
async def upload_video_analysis(

    candidate_id: int = Form(...),
    video: UploadFile = File(...),
    db: Session = Depends(get_db)

):

    os.makedirs(
        "interview_videos",
        exist_ok=True
    )

    video_path = f"interview_videos/{video.filename}"

    with open(video_path, "wb") as video_file:

        video_file.write(
            await video.read()
        )

    result = analyze_interview_video(
        video_path
    )

    if result["status"] != "success":

        return result

    video_record = VideoAnalysis(

        candidate_id=candidate_id,

        video_path=result["video_path"],

        total_frames_read=int(
            result["total_frames_read"]
        ),

        analyzed_frames=int(
            result["analyzed_frames"]
        ),

        emotion_distribution=json.dumps(
            result["emotion_distribution"]
        ),

        overall_dominant_emotion=result[
            "overall_dominant_emotion"
        ],

        average_confidence_score=float(
            result["average_confidence_score"]
        )
    )

    db.add(video_record)

    db.commit()

    db.refresh(video_record)

    result["video_analysis_id"] = video_record.id
    result["candidate_id"] = candidate_id

    return result

@app.post("/upload_image_analysis")
async def upload_image_analysis(

    candidate_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)

):

    os.makedirs(
        "interview_images",
        exist_ok=True
    )

    image_path = f"interview_images/{image.filename}"

    with open(image_path, "wb") as image_file:

        image_file.write(
            await image.read()
        )

    emotion_result = detect_emotion(
    image_path
)

    confidence_score = face_visibility_score(
    image_path
)

    emotion_scores = {
    emotion: float(score)
    for emotion, score in emotion_result["emotions"].items()
}

    image_record = ImageAnalysis(

    candidate_id=candidate_id,

    image_path=image_path,

    dominant_emotion=emotion_result[
        "dominant_emotion"
    ],

    emotion_scores=json.dumps(
        emotion_scores
    ),

    confidence_score=float(
        confidence_score
    )
)

    db.add(image_record)

    db.commit()

    db.refresh(image_record)

    return {

    "image_analysis_id":
    image_record.id,

    "candidate_id":
    candidate_id,

    "image_path":
    image_path,

    "dominant_emotion":
    emotion_result["dominant_emotion"],

    "emotion_scores":
    emotion_scores,

    "confidence_score":
    confidence_score
}



@app.get("/candidate_report/{candidate_id}")
def candidate_report(
    candidate_id: int,
    db: Session = Depends(get_db)
):

    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id
    ).first()

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    interview = db.query(InterviewAnalysis).filter(
        InterviewAnalysis.candidate_id == candidate_id
    ).order_by(
        InterviewAnalysis.id.desc()
    ).first()

    answer_quality = db.query(AnswerQuality).filter(
        AnswerQuality.candidate_id == candidate_id
    ).order_by(
        AnswerQuality.id.desc()
    ).first()

    image_analysis = db.query(ImageAnalysis).filter(
        ImageAnalysis.candidate_id == candidate_id
    ).order_by(
        ImageAnalysis.id.desc()
    ).first()

    video_analysis = db.query(VideoAnalysis).filter(
        VideoAnalysis.candidate_id == candidate_id
    ).order_by(
        VideoAnalysis.id.desc()
    ).first()

    resume_score = float(candidate.final_score)

    interview_score = (
        float(interview.overall_interview_score)
        if interview
        else 0
    )

    answer_quality_score = (
        float(answer_quality.answer_quality_score)
        if answer_quality
        else 0
    )

    final_score = round(
        (
            resume_score * 0.40
        )
        +
        (
            interview_score * 0.30
        )
        +
        (
            answer_quality_score * 0.30
        ),
        2
    )

    if final_score >= 85:
        decision = "Strong Candidate"

    elif final_score >= 70:
        decision = "Good Candidate"

    else:
        decision = "Needs Improvement"

    return {

        "candidate": {
            "candidate_id": candidate.id,
            "filename": candidate.filename,
            "skills": candidate.skills
        },

        "resume_analysis": {
            "resume_score": resume_score,
            "matched_skills": candidate.matched_skills,
            "missing_skills": candidate.missing_skills,
            "skill_match_percentage": candidate.skill_match_percentage,
            "semantic_score": candidate.semantic_score
        },

        "interview_delivery_analysis": {
            "available": interview is not None,
            "transcript": interview.transcript if interview else None,
            "sentiment": interview.sentiment if interview else None,
            "sentiment_score": interview.sentiment_score if interview else None,
            "filler_count": interview.filler_count if interview else None,
            "filler_score": interview.filler_score if interview else None,
            "dominant_emotion": interview.dominant_emotion if interview else None,
            "emotion_score": interview.emotion_score if interview else None,
            "confidence_score": interview.confidence_score if interview else None,
            "interview_score": interview_score
      },

        "answer_quality_analysis": {
            "available": answer_quality is not None,
            "relevance_score": answer_quality.relevance_score if answer_quality else None,
            "star_score": answer_quality.star_score if answer_quality else None,
            "clarity_score": answer_quality.clarity_score if answer_quality else None,
            "answer_quality_score": answer_quality_score,
            "feedback": answer_quality.feedback if answer_quality else None
        },

        "image_analysis": {
            "available": image_analysis is not None,
            "dominant_emotion": image_analysis.dominant_emotion if image_analysis else None,
            "confidence_score": image_analysis.confidence_score if image_analysis else None
        },

        "video_analysis": {
            "available": video_analysis is not None,
            "overall_dominant_emotion": video_analysis.overall_dominant_emotion if video_analysis else None,
            "average_confidence_score": video_analysis.average_confidence_score if video_analysis else None,
            "analyzed_frames": video_analysis.analyzed_frames if video_analysis else None
        },

        "final_result": {
            "final_candidate_score": final_score,
            "decision": decision
        }
    }
