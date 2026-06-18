def calculate_overall_score(
    emotion_score,
    sentiment_score,
    filler_score,
    confidence_score
):
    return (
        emotion_score * 0.30 +
        sentiment_score * 0.20 +
        filler_score * 0.20 +
        confidence_score * 0.30
    )