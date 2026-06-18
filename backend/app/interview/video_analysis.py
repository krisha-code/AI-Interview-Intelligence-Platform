import cv2
import os
from collections import Counter

from backend.app.interview.emotion_detection import detect_emotion
from backend.app.interview.confidence_detection import face_visibility_score


def analyze_interview_video(
    video_path,
    frame_interval_seconds=2
):

    if not os.path.exists(video_path):
        return {
            "status": "error",
            "message": "Video file not found"
        }

    os.makedirs(
        "interview_frames",
        exist_ok=True
    )

    video = cv2.VideoCapture(
        video_path
    )

    if not video.isOpened():
        return {
            "status": "error",
            "message": "Could not open video"
        }

    fps = video.get(
        cv2.CAP_PROP_FPS
    )

    if fps == 0:
        fps = 20

    frame_gap = max(
        1,
        int(fps * frame_interval_seconds)
    )

    frame_count = 0
    analyzed_frame_count = 0

    detected_emotions = []
    confidence_scores = []
    saved_frames = []

    while True:

        ret, frame = video.read()

        if not ret:
            break

        if frame_count % frame_gap == 0:

            frame_path = (
                f"interview_frames/frame_{frame_count}.jpg"
            )

            cv2.imwrite(
                frame_path,
                frame
            )

            try:

                emotion_result = detect_emotion(
                    frame_path
                )

                dominant_emotion = emotion_result[
                    "dominant_emotion"
                ]

                confidence_score = face_visibility_score(
                    frame_path
                )

                detected_emotions.append(
                    dominant_emotion
                )

                confidence_scores.append(
                    confidence_score
                )

                saved_frames.append(
                    frame_path
                )

                analyzed_frame_count += 1

            except Exception as error:

                print(
                    f"Skipping frame {frame_count}: {error}"
                )

        frame_count += 1

    video.release()

    if analyzed_frame_count == 0:
        return {
            "status": "error",
            "message": "No frames could be analyzed"
        }

    emotion_distribution = dict(
        Counter(detected_emotions)
    )

    overall_dominant_emotion = Counter(
        detected_emotions
    ).most_common(1)[0][0]

    average_confidence_score = round(
        sum(confidence_scores)
        /
        len(confidence_scores),
        2
    )

    return {
        "status": "success",
        "video_path": video_path,
        "total_frames_read": frame_count,
        "analyzed_frames": analyzed_frame_count,
        "saved_frames": saved_frames,
        "emotion_distribution": emotion_distribution,
        "overall_dominant_emotion": overall_dominant_emotion,
        "average_confidence_score": average_confidence_score
    }