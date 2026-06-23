from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Text

from backend.app.database.db import Base


class Candidate(Base):

    __tablename__ = "candidates"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(String)

    skills = Column(String)

    matched_skills = Column(String)

    missing_skills = Column(String)

    semantic_score = Column(Float)

    skill_match_percentage = Column(Float)

    final_score = Column(Float)


class Job(Base):

    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    job_title = Column(String)

    job_description = Column(String)


class Match(Base):

    __tablename__ = "matches"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id")
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id")
    )

    semantic_score = Column(Float)

    skill_match_percentage = Column(Float)

    final_score = Column(Float)


class InterviewAnalysis(Base):

    __tablename__ = "interview_analysis"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id")
    )

    transcript = Column(Text)

    sentiment = Column(String)

    sentiment_score = Column(Float)

    filler_count = Column(Integer)

    filler_score = Column(Float)

    dominant_emotion = Column(String)

    emotion_score = Column(Float)

    confidence_score = Column(Float)

    overall_interview_score = Column(Float)


class AnswerQuality(Base):

    __tablename__ = "answer_quality"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id")
    )

    question = Column(Text)

    answer = Column(Text)

    relevance_score = Column(Float)

    star_score = Column(Float)

    clarity_score = Column(Float)

    answer_quality_score = Column(Float)

    feedback = Column(Text)

class VideoAnalysis(Base):

    __tablename__ = "video_analysis"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id")
    )

    video_path = Column(String)

    total_frames_read = Column(Integer)

    analyzed_frames = Column(Integer)

    emotion_distribution = Column(Text)

    overall_dominant_emotion = Column(String)

    average_confidence_score = Column(Float)

class ImageAnalysis(Base):

    __tablename__ = "image_analysis"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id")
    )

    image_path = Column(String)

    dominant_emotion = Column(String)

    emotion_scores = Column(Text)

    confidence_score = Column(Float)

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    question = Column(Text)