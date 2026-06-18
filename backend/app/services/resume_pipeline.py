from backend.app.services.pdf_parser import extract_text_from_pdf
from backend.app.services.skill_extraction import extract_skills
from backend.app.services.resume_matcher import calculate_match_score


def analyze_resume(pdf_path, job_description):

    resume_text = extract_text_from_pdf(
        pdf_path
    )

    resume_skills = extract_skills(
        resume_text
    )

    job_skills = extract_skills(
        job_description
    )

    matched_skills = list(
        set(resume_skills)
        &
        set(job_skills)
    )

    missing_skills = list(
        set(job_skills)
        -
        set(resume_skills)
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

    semantic_match_score = calculate_match_score(
        resume_text,
        job_description
    )

    final_match_score = round(
    (
        semantic_match_score * 0.7
    )
    +
    (
        skill_match_percentage * 0.3
    ),
    2
)

    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_match_percentage": float(skill_match_percentage),
        "semantic_match_score": float(semantic_match_score),
        "final_match_score": float(final_match_score)
    }