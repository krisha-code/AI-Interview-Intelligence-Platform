def calculate_overall_score(
    emotion_score,
    speech_score,
    filler_score,
    face_score
):
    return round(
        (
            emotion_score +
            speech_score +
            filler_score +
            face_score
        ) / 4,
        2
    )