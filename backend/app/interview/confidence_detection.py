from deepface import DeepFace
import cv2
import math


def face_visibility_score(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return 0

    image_height, image_width = image.shape[:2]

    try:
        faces = DeepFace.extract_faces(
            img_path=image_path,
            detector_backend="opencv",
            enforce_detection=True
        )

    except:
        return 0

    if len(faces) == 0:
        return 0

    face_data = faces[0]

    facial_area = face_data.get(
        "facial_area",
        {}
    )

    x = facial_area.get("x", 0)
    y = facial_area.get("y", 0)
    w = facial_area.get("w", 0)
    h = facial_area.get("h", 0)

    if w == 0 or h == 0:
        return 0

    # 1. Detection score
    detection_confidence = face_data.get(
        "confidence",
        0.8
    )

    if detection_confidence <= 1:
        detection_score = detection_confidence * 100
    else:
        detection_score = min(
            detection_confidence,
            100
        )

    # 2. Face size score
    face_area = w * h
    image_area = image_width * image_height

    face_ratio = face_area / image_area

    size_score = min(
        (face_ratio / 0.20) * 100,
        100
    )

    # 3. Face center score
    face_center_x = x + w / 2
    face_center_y = y + h / 2

    image_center_x = image_width / 2
    image_center_y = image_height / 2

    distance = math.sqrt(
        (face_center_x - image_center_x) ** 2
        +
        (face_center_y - image_center_y) ** 2
    )

    max_distance = math.sqrt(
        image_center_x ** 2
        +
        image_center_y ** 2
    )

    center_score = max(
        0,
        100 - (distance / max_distance) * 100
    )

    final_score = (
        detection_score * 0.40
        +
        size_score * 0.30
        +
        center_score * 0.30
    )

    return round(final_score, 2)