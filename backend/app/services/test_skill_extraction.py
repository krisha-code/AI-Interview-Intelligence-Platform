
from backend.app.services.skill_extraction import extract_skills


sample_text = """
Python SQL TensorFlow Python Docker SQL
"""

print(extract_skills(sample_text))