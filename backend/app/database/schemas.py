from pydantic import BaseModel

class CandidateResponse(BaseModel):
    id: int
    filename: str
    matched_skills: str
    missing_skills: str
    semantic_score: float
    skills_matching_percentage: float
    final_score: float

    class Config:
        from_attributes = True