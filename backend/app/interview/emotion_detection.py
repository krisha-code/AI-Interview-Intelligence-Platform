from deepface import DeepFace


def detect_emotion(image_path):
    result = DeepFace.analyze(
        img_path=image_path,
        actions=["emotion"],
        enforce_detection=False
    )

    return {
        "dominant_emotion": result[0]["dominant_emotion"],
        "emotions": result[0]["emotion"]
    }