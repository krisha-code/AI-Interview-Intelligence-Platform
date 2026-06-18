import cv2
import os
import time


def record_interview_video(
    output_path="interview_videos/test_interview.mp4",
    duration=10
):

    os.makedirs(
        "interview_videos",
        exist_ok=True
    )

    camera = cv2.VideoCapture(
        0,
        cv2.CAP_V4L2
    )

    if not camera.isOpened():
        return {
            "status": "error",
            "message": "Could not open webcam"
        }

    frame_width = int(
        camera.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    frame_height = int(
        camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    fps = 20

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    video_writer = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (
            frame_width,
            frame_height
        )
    )

    start_time = time.time()

    print("Recording started.")
    print("Press 'q' to stop early.")

    while True:

        ret, frame = camera.read()

        if not ret:
            print("Failed to grab frame")
            break

        video_writer.write(
            frame
        )

        cv2.imshow(
            "Recording Interview - Press q to stop",
            frame
        )

        elapsed_time = time.time() - start_time

        if elapsed_time >= duration:
            break

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()

    video_writer.release()

    cv2.destroyAllWindows()

    return {
        "status": "success",
        "video_path": output_path,
        "duration_seconds": duration
    }