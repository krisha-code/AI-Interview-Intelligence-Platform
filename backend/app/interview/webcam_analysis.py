from backend.app.interview.webcam_capture import capture_webcam_image
from backend.app.interview.emotion_detection import detect_emotion
from backend.app.interview.confidence_detection import face_visibility_score


def analyze_live_webcam_image():

    capture_result = capture_webcam_image()

    if capture_result["status"] != "success":

        return {
            "status": "error",
            "message": capture_result["message"]
        }

    image_path = capture_result["image_path"]

    emotion_result = detect_emotion(
        image_path
    )

    confidence_score = face_visibility_score(
        image_path
    )

    return {
        "status": "success",
        "image_path": image_path,
        "dominant_emotion": emotion_result["dominant_emotion"],
        "emotions": emotion_result["emotions"],
        "confidence_score": confidence_score
    }