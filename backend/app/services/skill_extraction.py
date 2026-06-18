from backend.app.utils.skills import SKILLS

def extract_skills(text, skills=SKILLS):

    text = text.lower()

    checked_skills = []

    for skill in skills:
        if skill.lower() in text:
            checked_skills.append(skill)

    checked_skills = sorted(set(checked_skills))

    return checked_skills

