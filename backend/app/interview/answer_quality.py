from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from backend.app.interview.filler_word_detection import detect_filler_words


model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_relevance_score(question, answer):

    question_embedding = model.encode([question])
    answer_embedding = model.encode([answer])

    similarity = cosine_similarity(
        question_embedding,
        answer_embedding
    )[0][0]

    semantic_score = float(similarity) * 100

    question_words = set(
        question.lower()
        .replace(".", "")
        .replace(",", "")
        .split()
    )

    answer_words = set(
        answer.lower()
        .replace(".", "")
        .replace(",", "")
        .split()
    )

    stopwords = {
        "tell", "me", "about", "a", "an", "the",
        "you", "your", "on", "in", "of", "and",
        "to", "for", "worked"
    }

    important_question_words = question_words - stopwords

    if len(important_question_words) > 0:

        keyword_score = (
            len(
                important_question_words
                &
                answer_words
            )
            /
            len(important_question_words)
        ) * 100

    else:

        keyword_score = 0

    domain_bonus = 0

    ml_keywords = [
        "machine learning",
        "nlp",
        "tf-idf",
        "tensorflow",
        "model",
        "recommendation",
        "cosine similarity",
        "fastapi",
        "streamlit"
    ]

    if "machine learning" in question.lower():

        for keyword in ml_keywords:

            if keyword in answer.lower():

                domain_bonus += 5

    domain_bonus = min(domain_bonus, 20)

    final_relevance_score = round(
        (
            semantic_score * 0.50
        )
        +
        (
            keyword_score * 0.30
        )
        +
        domain_bonus,
        2
    )

    return min(final_relevance_score, 100)


def analyze_star_method(answer):

    answer_lower = answer.lower()

    situation_keywords = [
        "project",
        "problem",
        "challenge",
        "situation",
        "worked on",
        "during"
    ]

    task_keywords = [
        "responsible",
        "task",
        "goal",
        "needed to",
        "my role",
        "objective"
    ]

    action_keywords = [
        "implemented",
        "built",
        "created",
        "developed",
        "used",
        "trained",
        "solved",
        "improved",
        "designed"
    ]

    result_keywords = [
        "result",
        "achieved",
        "improved",
        "accuracy",
        "performance",
        "reduced",
        "increased",
        "successfully",
        "outcome"
    ]

    star_parts = {
        "situation": any(word in answer_lower for word in situation_keywords),
        "task": any(word in answer_lower for word in task_keywords),
        "action": any(word in answer_lower for word in action_keywords),
        "result": any(word in answer_lower for word in result_keywords)
    }

    score = round(
        (
            sum(star_parts.values())
            /
            4
        ) * 100,
        2
    )

    missing_parts = [
        part
        for part, present in star_parts.items()
        if not present
    ]

    return {
        "star_score": score,
        "star_parts": star_parts,
        "missing_star_parts": missing_parts
    }


def calculate_clarity_score(answer):

    words = answer.split()

    word_count = len(words)

    filler_count = detect_filler_words(
        answer
    )

    score = 100

    if word_count < 30:
        score -= 20

    if word_count > 250:
        score -= 15

    score -= filler_count * 5

    score = max(
        0,
        min(score, 100)
    )

    return {
        "clarity_score": round(score, 2),
        "word_count": word_count,
        "filler_count": filler_count
    }


def generate_answer_feedback(
    relevance_score,
    star_result,
    clarity_result
):

    feedback = []

    if relevance_score < 60:
        feedback.append(
            "Your answer is not strongly aligned with the question. Try to directly address what was asked."
        )

    else:
        feedback.append(
            "Your answer is relevant to the question."
        )

    if star_result["missing_star_parts"]:

        feedback.append(
            "Improve your STAR structure by adding: "
            +
            ", ".join(star_result["missing_star_parts"])
        )

    else:

        feedback.append(
            "Your answer follows the STAR method well."
        )

    if clarity_result["filler_count"] > 3:

        feedback.append(
            "Reduce filler words such as um, uh, like, basically, and actually."
        )

    if clarity_result["word_count"] < 30:

        feedback.append(
            "Your answer is too short. Add more details about your role, actions, and results."
        )

    return feedback


def evaluate_answer(question, answer):

    relevance_score = calculate_relevance_score(
        question,
        answer
    )

    star_result = analyze_star_method(
        answer
    )

    clarity_result = calculate_clarity_score(
        answer
    )

    answer_quality_score = round(
        (
            relevance_score * 0.40
        )
        +
        (
            star_result["star_score"] * 0.35
        )
        +
        (
            clarity_result["clarity_score"] * 0.25
        ),
        2
    )

    feedback = generate_answer_feedback(
        relevance_score,
        star_result,
        clarity_result
    )

    return {
        "question": question,
        "answer": answer,
        "relevance_score": relevance_score,
        "star_score": star_result["star_score"],
        "star_parts": star_result["star_parts"],
        "missing_star_parts": star_result["missing_star_parts"],
        "clarity_score": clarity_result["clarity_score"],
        "word_count": clarity_result["word_count"],
        "filler_count": clarity_result["filler_count"],
        "answer_quality_score": answer_quality_score,
        "feedback": feedback
    }