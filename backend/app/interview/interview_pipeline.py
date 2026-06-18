from backend.app.interview.speech_to_text import transcribe_audio
from backend.app.interview.sentiment_analysis import analyze_sentiment
from backend.app.interview.filler_word_detection import detect_filler_words, filler_score
from backend.app.interview.emotion_detection import detect_emotion
from backend.app.interview.confidence_detection import face_visibility_score
from backend.app.interview.interview_scoring import calculate_overall_score


def sentiment_to_score(sentiment_result):

    sentiment = sentiment_result["sentiment"]
    confidence = sentiment_result["score"]

    if sentiment == "POSITIVE":
        return round(70 + confidence * 30, 2)

    return round(70 - confidence * 30, 2)


def emotion_to_score(emotion):

    emotion_scores = {
        "happy": 95,
        "neutral": 85,
        "surprise": 70,
        "sad": 45,
        "fear": 35,
        "angry": 40,
        "disgust": 30
    }

    return emotion_scores.get(emotion, 60)


def analyze_interview(audio_path, image_path):

    transcript = transcribe_audio(audio_path)

    sentiment_result = analyze_sentiment(transcript)

    sentiment_score = sentiment_to_score(
        sentiment_result
    )

    filler_count = detect_filler_words(
        transcript
    )

    filler_score_value = filler_score(
        filler_count
    )

    emotion_result = detect_emotion(
        image_path
    )

    dominant_emotion = emotion_result[
        "dominant_emotion"
    ]

    emotion_score = emotion_to_score(
        dominant_emotion
    )

    confidence_score = face_visibility_score(
        image_path
    )

    overall_score = calculate_overall_score(
        emotion_score=emotion_score,
        sentiment_score=sentiment_score,
        filler_score=filler_score_value,
        confidence_score=confidence_score
    )

    return {
        "transcript": transcript,
        "sentiment": sentiment_result,
        "sentiment_score": sentiment_score,
        "filler_count": filler_count,
        "filler_score": filler_score_value,
        "dominant_emotion": dominant_emotion,
        "emotion_score": emotion_score,
        "confidence_score": confidence_score,
        "overall_interview_score": overall_score
    }