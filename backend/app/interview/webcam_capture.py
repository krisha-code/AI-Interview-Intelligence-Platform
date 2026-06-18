import cv2
import os
import time


def capture_webcam_image(
    output_path="interview_images/live_capture.jpg"
):

    os.makedirs(
        "interview_images",
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

    time.sleep(2)

    print("Webcam opened.")
    print("Click on the webcam window, then press 'q' to capture image.")

    while True:

        ret, frame = camera.read()

        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow(
            "Interview Camera - Press q to capture",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            cv2.imwrite(
                output_path,
                frame
            )

            print(f"Image saved at {output_path}")

            camera.release()
            cv2.destroyAllWindows()

            return {
                "status": "success",
                "image_path": output_path
            }

    camera.release()
    cv2.destroyAllWindows()

    return {
        "status": "error",
        "message": "Failed to capture image"
    }