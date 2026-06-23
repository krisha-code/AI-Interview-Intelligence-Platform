import streamlit as st
import requests
import pandas as pd
import os
import time
import cv2
import av
import threading
import plotly.graph_objects as go

from streamlit_webrtc import (
    webrtc_streamer,
    WebRtcMode,
    VideoProcessorBase
)

# -----------------------------
# Constants
# -----------------------------
API_URL = "https://kgandhi03-ai-interview-backend.hf.space"

st.set_page_config(
    page_title="AI Interview Platform",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------
# Session State
# -----------------------------
if "candidate_id" not in st.session_state:
    st.session_state.candidate_id = None

if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = None

if "selected_job_title" not in st.session_state:
    st.session_state.selected_job_title = None

if "last_resume_result" not in st.session_state:
    st.session_state.last_resume_result = None

if "last_report" not in st.session_state:
    st.session_state.last_report = None


# -----------------------------
# Custom CSS
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .glass-card {
        background: hsla(0, 0%, 100%, 0.07);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(10px);
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 1rem;
        border: 1px solid hsla(0, 0%, 100%, 0.08);
    }

    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
    }

    .stat-value {
        font-size: 2.3rem;
        font-weight: 700;
        color: #fff;
        margin: 0;
    }

    .stat-label {
        font-size: 1rem;
        color: #a0aabf;
        margin: 0;
    }

    .accent-blue {
        color: #3F81EC;
    }

    .accent-pink {
        color: #e83e8c;
    }

    .section-title {
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-size: 1.6rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Helper Functions
# -----------------------------
def safe_request_get(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def get_rankings():
    data = safe_request_get(f"{API_URL}/rank_candidates", timeout=10)
    return data if data else []


def get_candidates():
    """
    Uses /candidates if available.
    Falls back to /rank_candidates so Candidate Report still works.
    """
    candidates = safe_request_get(f"{API_URL}/candidates", timeout=10)

    if candidates:
        return candidates

    rankings = get_rankings()

    if not rankings:
        return []

    cleaned_candidates = []

    for item in rankings:
        cleaned_candidates.append(
            {
                "candidate_id": item.get("candidate_id"),
                "filename": item.get("filename", "Candidate"),
                "final_score": item.get(
                    "final_candidate_score",
                    item.get("final_score", 0)
                )
            }
        )

    return cleaned_candidates


def get_candidate_report(candidate_id):
    try:
        response = requests.get(
            f"{API_URL}/candidate_report/{candidate_id}",
            timeout=20
        )

        if response.status_code == 200:
            return response.json()

        return None

    except Exception:
        return None


def get_final_score(candidate_id):
    try:
        response = requests.get(
            f"{API_URL}/final_candidate_score/{candidate_id}",
            timeout=20
        )

        if response.status_code == 200:
            return response.json(), None

        return None, response.text

    except Exception as error:
        return None, str(error)


def get_jobs():
    jobs = safe_request_get(f"{API_URL}/jobs", timeout=10)
    return jobs if jobs else []


def get_questions(job_id):
    questions = safe_request_get(
        f"{API_URL}/jobs/{job_id}/questions",
        timeout=10
    )
    return questions if questions else []


def make_dataframe(data):
    df = pd.DataFrame(data)

    if df.empty:
        return df

    numeric_cols = df.select_dtypes(
        include=["float64", "int64"]
    ).columns

    df[numeric_cols] = df[numeric_cols].round(2)

    return df


def show_api_error(response):
    st.error(f"Error {response.status_code}: {response.text}")


def get_active_candidate_id():
    return st.session_state.get("candidate_id")


def show_active_candidate_box():
    candidate_id = get_active_candidate_id()

    if candidate_id:
        st.success(f"Using Candidate ID from this session: {candidate_id}")
        return int(candidate_id)

    st.warning(
        "No Candidate ID in this session. Upload your resume first, or enter Candidate ID manually."
    )

    manual_id = st.text_input(
        "Candidate ID",
        placeholder="Enter Candidate ID only if already generated"
    )

    if manual_id and manual_id.isdigit():
        return int(manual_id)

    return None


def normalize_score(value):
    if value is None:
        return 0.0

    try:
        value = float(value)
    except Exception:
        return 0.0

    if value <= 1:
        value = value * 100

    return round(value, 2)


def first_available(data, keys, default=None):
    for key in keys:
        if isinstance(data, dict) and data.get(key) is not None:
            return data.get(key)

    return default


def split_text_items(value):
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]

    if isinstance(value, str):
        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    return [str(value)]


def render_skill_badges(title, value, empty_text):
    st.write(f"### {title}")

    items = split_text_items(value)

    if not items:
        st.info(empty_text)
        return

    st.write(", ".join(items))


def render_score_metric(label, value):
    st.metric(label, f"{normalize_score(value):.2f} / 100")


def create_radar_chart(resume_score, interview_score, answer_score, confidence_score, emotion_score):
    radar_labels = [
        "Resume",
        "Interview",
        "Answer Quality",
        "Confidence",
        "Emotion"
    ]

    radar_values = [
        normalize_score(resume_score),
        normalize_score(interview_score),
        normalize_score(answer_score),
        normalize_score(confidence_score),
        normalize_score(emotion_score)
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=radar_values,
            theta=radar_labels,
            fill="toself",
            name="Candidate Score"
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        margin=dict(l=30, r=30, t=30, b=30)
    )

    return fig


# -----------------------------
# Live Video Recorder Processor
# -----------------------------
class VideoRecorderProcessor(VideoProcessorBase):
    def __init__(self):
        self.frames = []
        self.lock = threading.Lock()

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")

        with self.lock:
            self.frames.append(image.copy())

            # Keep only latest 900 frames to avoid memory problem
            if len(self.frames) > 900:
                self.frames = self.frames[-900:]

        return av.VideoFrame.from_ndarray(image, format="bgr24")

    def get_frames(self):
        with self.lock:
            return list(self.frames)

    def clear_frames(self):
        with self.lock:
            self.frames = []


def save_frames_to_video(frames, output_path, fps=20):
    if not frames:
        return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    height, width, _ = frames[0].shape

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height)
    )

    if not writer.isOpened():
        return False

    for frame in frames:
        if frame.shape[0] != height or frame.shape[1] != width:
            frame = cv2.resize(frame, (width, height))

        writer.write(frame)

    writer.release()
    return True


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🤖 AI Interview")
st.sidebar.markdown("---")

portal = st.sidebar.radio(
    "Select Portal",
    [
        "Recruiter Side",
        "Candidate Side"
    ]
)

if portal == "Recruiter Side":

    page = st.sidebar.radio(
        "Recruiter Navigation",
        [
            "Recruiter Dashboard",
            "Add Job & Questions",
            "Candidate Rankings",
            "Candidate Report",
            "Final Hiring Decision"
        ]
    )

else:

    page = st.sidebar.radio(
        "Candidate Navigation",
        [
            "Candidate Resume Upload",
            "Give Interview",
            "Live Image & Video",
            "Answer Quality",
            "View Feedback"
        ]
    )


# -----------------------------
# Recruiter Dashboard Page
# -----------------------------
if page == "Recruiter Dashboard":

    st.markdown(
        "<h1 style='margin-bottom:0;'>Recruiter Dashboard</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='color: #a0aabf; margin-bottom:2rem;'>AI Interview Intelligence Platform</p>",
        unsafe_allow_html=True
    )

    rankings = get_rankings()

    total_interviews = 0
    avg_score = 0.0
    insights = 0
    df = None

    if rankings:
        df = make_dataframe(rankings)
        total_interviews = len(df)
        insights = total_interviews * 3

        if "final_candidate_score" in df.columns:
            avg_score = df["final_candidate_score"].mean()
        elif "final_score" in df.columns:
            avg_score = df["final_score"].mean()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="glass-card">
                <h3 class="stat-value">{total_interviews}</h3>
                <p class="stat-label">Total Interviews</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="glass-card">
                <h3 class="stat-value">{total_interviews}</h3>
                <p class="stat-label">Candidate Pipeline <span class="accent-pink">Active</span></p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="glass-card">
                <h3 class="stat-value">{avg_score:.1f}</h3>
                <p class="stat-label">Avg. AI Score <span class="accent-blue">/100</span></p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="glass-card">
                <h3 class="stat-value">{insights}</h3>
                <p class="stat-label">Insights Shared</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        "<h3 class='section-title'>Recent Candidate Activity</h3>",
        unsafe_allow_html=True
    )

    if df is not None and not df.empty:
        st.dataframe(
            df.head(5),
            width="stretch",
            hide_index=True
        )

    else:
        st.markdown(
            """
            <div class='glass-card'>
                No candidate activity yet. Add a job and submit a candidate resume to generate AI rankings and reports.
            </div>
            """,
            unsafe_allow_html=True
        )


# -----------------------------
# Recruiter: Add Job & Questions Page
# -----------------------------
elif page == "Add Job & Questions":

    st.markdown(
        "<h2 style='margin-bottom:1rem;'>Recruiter: Add Job & Interview Questions</h2>",
        unsafe_allow_html=True
    )

    st.info(
        "Create a job once here. Candidates will select this job from Candidate Side, so they do not need to type job title or job description."
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "Add Job",
            "Add Questions",
            "View Jobs"
        ]
    )

    with tab1:
        st.subheader("Add New Job")

        with st.form("add_job_form"):
            job_title = st.text_input(
                "Job Title",
                placeholder="Machine Learning Engineer"
            )

            job_description = st.text_area(
                "Job Description",
                height=180,
                placeholder="Looking for candidate with Python, ML, NLP, TensorFlow, Docker..."
            )

            submitted = st.form_submit_button(
                "Save Job",
                width="stretch"
            )

            if submitted:
                if not job_title:
                    st.warning("Please enter job title.")

                elif not job_description:
                    st.warning("Please enter job description.")

                else:
                    with st.spinner("Saving job..."):
                        response = requests.post(
                            f"{API_URL}/jobs",
                            json={
                                "job_title": job_title,
                                "job_description": job_description
                            },
                            timeout=30
                        )

                    if response.status_code == 200:
                        result = response.json()
                        st.success("Job saved successfully.")
                        st.json(result)

                    else:
                        show_api_error(response)

    with tab2:
        st.subheader("Add Interview Questions")

        jobs = get_jobs()

        if not jobs:
            st.warning(
                "No jobs found. Add a job first. Also make sure backend /jobs endpoint is deployed."
            )

        else:
            job_options = {
                f"{job['job_id']} - {job['job_title']}": job["job_id"]
                for job in jobs
            }

            selected_job_label = st.selectbox(
                "Select Job",
                list(job_options.keys()),
                key="recruiter_question_job"
            )

            selected_job_id = job_options[selected_job_label]

            existing_questions = get_questions(selected_job_id)

            if existing_questions:
                st.write("### Existing Questions")
                for q in existing_questions:
                    st.write(f"- {q['question']}")

            with st.form("add_question_form"):
                question = st.text_area(
                    "Interview Question",
                    height=100,
                    placeholder="Tell me about a machine learning project you worked on."
                )

                submitted = st.form_submit_button(
                    "Save Question",
                    width="stretch"
                )

                if submitted:
                    if not question:
                        st.warning("Please enter a question.")

                    else:
                        with st.spinner("Saving question..."):
                            response = requests.post(
                                f"{API_URL}/jobs/{selected_job_id}/questions",
                                json={
                                    "question": question
                                },
                                timeout=30
                            )

                        if response.status_code == 200:
                            st.success("Question saved successfully.")
                            st.json(response.json())

                        else:
                            show_api_error(response)

    with tab3:
        st.subheader("Saved Jobs")

        jobs = get_jobs()

        if not jobs:
            st.info("No jobs available.")

        else:
            for job in jobs:
                with st.expander(f"{job['job_id']} - {job['job_title']}"):
                    st.write(job["job_description"])

                    questions = get_questions(job["job_id"])

                    if questions:
                        st.write("### Questions")
                        for q in questions:
                            st.write(f"- {q['question']}")
                    else:
                        st.info("No questions added yet.")


# -----------------------------
# Candidate Resume Upload Page
# -----------------------------
elif page == "Candidate Resume Upload":

    st.markdown(
        "<h2 style='margin-bottom:1rem;'>Candidate: Select Job & Upload Resume</h2>",
        unsafe_allow_html=True
    )

    st.info(
        "Select the job created by recruiter. The job description will automatically be used for resume matching."
    )

    jobs = get_jobs()

    if not jobs:
        st.warning("No jobs available yet. Recruiter must add a job first.")
        st.stop()

    job_options = {
        f"{job['job_id']} - {job['job_title']}": job
        for job in jobs
    }

    selected_job_label = st.selectbox(
        "Select Job",
        list(job_options.keys()),
        key="candidate_resume_job"
    )

    selected_job = job_options[selected_job_label]

    st.session_state.selected_job_id = selected_job["job_id"]
    st.session_state.selected_job_title = selected_job["job_title"]

    st.write("### Selected Job")
    st.success(selected_job["job_title"])

    with st.expander("View Job Description"):
        st.write(selected_job["job_description"])

    resume_file = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"]
    )

    if st.button(
        "Submit Resume",
        width="stretch"
    ):

        if resume_file is None:
            st.warning("Please upload your resume.")

        else:
            with st.spinner("Analyzing resume for selected job..."):
                try:
                    files = {
                        "resume": (
                            resume_file.name,
                            resume_file,
                            "application/pdf"
                        )
                    }

                    data = {
                        "job_id": str(st.session_state.selected_job_id)
                    }

                    response = requests.post(
                        f"{API_URL}/upload_resume_for_job",
                        files=files,
                        data=data,
                        timeout=180
                    )

                    if response.status_code == 200:
                        res = response.json()

                        st.session_state.candidate_id = res.get("candidate_id")
                        st.session_state.last_resume_result = res
                        st.session_state.selected_job_id = res.get(
                            "job_id",
                            st.session_state.selected_job_id
                        )
                        st.session_state.selected_job_title = res.get(
                            "job_title",
                            st.session_state.selected_job_title
                        )

                        st.success(
                            f"Resume submitted successfully for {res.get('job_title', 'selected job')}."
                        )

                        st.info(
                            f"Candidate ID saved for this session: {st.session_state.candidate_id}"
                        )

                        c1, c2, c3 = st.columns(3)

                        with c1:
                            st.metric(
                                "Final Match Score",
                                f"{normalize_score(res.get('final_match_score')):.2f}%"
                            )

                        with c2:
                            st.metric(
                                "Skill Match",
                                f"{normalize_score(res.get('skill_match_percentage')):.2f}%"
                            )

                        with c3:
                            st.metric(
                                "Semantic Score",
                                f"{normalize_score(res.get('semantic_match_score')):.2f}%"
                            )

                        render_skill_badges(
                            "Matched Skills",
                            res.get("matched_skills"),
                            "No matched skills."
                        )

                        render_skill_badges(
                            "Missing Skills",
                            res.get("missing_skills"),
                            "No missing skills."
                        )

                        if res.get("suggestions"):
                            st.write("### Suggestions")
                            if isinstance(res["suggestions"], list):
                                for item in res["suggestions"]:
                                    st.write(f"- {item}")
                            else:
                                st.write(res["suggestions"])

                    else:
                        show_api_error(response)

                except Exception as error:
                    st.error(
                        f"Connection failed to {API_URL}. Is backend running?"
                    )
                    st.exception(error)


# -----------------------------
# Candidate Interview Page
# -----------------------------
elif page == "Give Interview":

    st.markdown(
        "<h2 style='margin-bottom:1rem;'>Candidate: Give Interview</h2>",
        unsafe_allow_html=True
    )

    st.info(
        "Upload interview audio and interview image/frame. The backend will analyze transcript, sentiment, filler words, emotion, and confidence."
    )

    candidate_id = show_active_candidate_box()

    with st.form("interview_form"):

        col1, col2 = st.columns(2)

        with col1:
            audio_file = st.file_uploader(
                "Upload Interview Audio",
                type=["mp3", "wav", "m4a", "webm"]
            )

        with col2:
            image_file = st.file_uploader(
                "Upload Interview Image / Frame",
                type=["jpg", "jpeg", "png"]
            )

        submitted = st.form_submit_button(
            "Run Interview Analysis",
            width="stretch"
        )

        if submitted:

            if not candidate_id:
                st.warning("Please upload resume first or enter a valid Candidate ID.")

            elif not audio_file:
                st.warning("Please upload audio file.")

            elif not image_file:
                st.warning("Please upload image file.")

            else:
                with st.spinner("Processing interview media..."):

                    try:
                        files = {
                            "audio": (
                                audio_file.name,
                                audio_file,
                                "audio/mpeg"
                            ),
                            "image": (
                                image_file.name,
                                image_file,
                                "image/jpeg"
                            )
                        }

                        data = {
                            "candidate_id": str(candidate_id)
                        }

                        response = requests.post(
                            f"{API_URL}/upload_interview_analysis",
                            files=files,
                            data=data,
                            timeout=180
                        )

                        if response.status_code == 200:
                            res = response.json()

                            st.success("Interview analysis complete!")

                            c1, c2, c3, c4 = st.columns(4)

                            with c1:
                                st.metric(
                                    "Overall Interview Score",
                                    res.get("overall_interview_score", "N/A")
                                )

                            with c2:
                                st.metric(
                                    "Dominant Emotion",
                                    res.get("dominant_emotion", "N/A")
                                )

                            with c3:
                                st.metric(
                                    "Filler Count",
                                    res.get("filler_count", "N/A")
                                )

                            with c4:
                                st.metric(
                                    "Confidence Score",
                                    res.get("confidence_score", "N/A")
                                )

                            st.write("### Transcript")
                            st.write(res.get("transcript", "Transcript not available."))

                            st.write("### Sentiment")
                            st.json(res.get("sentiment", {}))

                        else:
                            show_api_error(response)

                    except Exception as error:
                        st.error(
                            f"Connection failed to {API_URL}. Is backend running?"
                        )
                        st.exception(error)


# -----------------------------
# Candidate Live Image & Video Page
# -----------------------------
elif page == "Live Image & Video":

    st.markdown(
        "<h2 style='margin-bottom:1rem;'>Candidate: Live Image Capture & Video Analysis</h2>",
        unsafe_allow_html=True
    )

    candidate_id = show_active_candidate_box()

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Live Camera Image",
            "Upload Image",
            "Upload Video",
            "Live Video Recorder"
        ]
    )

    # -----------------------------
    # Live Camera Image
    # -----------------------------
    with tab1:

        st.write("### Capture Live Image from Camera")

        camera_image = st.camera_input(
            "Capture candidate face image"
        )

        if st.button(
            "Analyze Live Captured Image",
            key="analyze_live_image",
            width="stretch"
        ):

            if not candidate_id:
                st.warning("Please upload resume first or enter a valid Candidate ID.")

            elif camera_image is None:
                st.warning("Please capture an image first.")

            else:
                with st.spinner("Analyzing live image..."):

                    try:
                        files = {
                            "image": (
                                "live_capture.jpg",
                                camera_image.getvalue(),
                                "image/jpeg"
                            )
                        }

                        data = {
                            "candidate_id": str(candidate_id)
                        }

                        response = requests.post(
                            f"{API_URL}/upload_image_analysis",
                            files=files,
                            data=data,
                            timeout=120
                        )

                        if response.status_code == 200:
                            res = response.json()

                            st.success("Live image analyzed successfully!")

                            c1, c2 = st.columns(2)

                            with c1:
                                st.metric(
                                    "Dominant Emotion",
                                    res.get("dominant_emotion", "N/A")
                                )

                            with c2:
                                st.metric(
                                    "Confidence Score",
                                    res.get("confidence_score", "N/A")
                                )

                            st.write("### Emotion Scores")
                            st.json(res.get("emotion_scores", {}))

                        else:
                            show_api_error(response)

                    except Exception as error:
                        st.error(
                            f"Connection failed to {API_URL}. Is backend running?"
                        )
                        st.exception(error)

    # -----------------------------
    # Upload Image
    # -----------------------------
    with tab2:

        st.write("### Upload Image for Analysis")

        standalone_image = st.file_uploader(
            "Upload face image",
            type=["jpg", "jpeg", "png"],
            key="standalone_image"
        )

        if st.button(
            "Analyze Uploaded Image",
            key="analyze_uploaded_image",
            width="stretch"
        ):

            if not candidate_id:
                st.warning("Please upload resume first or enter a valid Candidate ID.")

            elif not standalone_image:
                st.warning("Please upload an image.")

            else:
                with st.spinner("Analyzing uploaded image..."):

                    try:
                        files = {
                            "image": (
                                standalone_image.name,
                                standalone_image,
                                "image/jpeg"
                            )
                        }

                        data = {
                            "candidate_id": str(candidate_id)
                        }

                        response = requests.post(
                            f"{API_URL}/upload_image_analysis",
                            files=files,
                            data=data,
                            timeout=120
                        )

                        if response.status_code == 200:
                            res = response.json()

                            st.success("Image analyzed successfully!")

                            c1, c2 = st.columns(2)

                            with c1:
                                st.metric(
                                    "Dominant Emotion",
                                    res.get("dominant_emotion", "N/A")
                                )

                            with c2:
                                st.metric(
                                    "Confidence Score",
                                    res.get("confidence_score", "N/A")
                                )

                            st.write("### Full Image Result")
                            st.json(res)

                        else:
                            show_api_error(response)

                    except Exception as error:
                        st.error(
                            f"Connection failed to {API_URL}. Is backend running?"
                        )
                        st.exception(error)

    # -----------------------------
    # Upload Video
    # -----------------------------
    with tab3:

        st.write("### Upload Recorded Interview Video for Analysis")

        video_file = st.file_uploader(
            "Upload interview video",
            type=["mp4", "avi", "mov"],
            key="video_upload"
        )

        if st.button(
            "Analyze Video",
            key="analyze_video",
            width="stretch"
        ):

            if not candidate_id:
                st.warning("Please upload resume first or enter a valid Candidate ID.")

            elif not video_file:
                st.warning("Please upload a video file.")

            else:
                with st.spinner("Analyzing video frames..."):

                    try:
                        files = {
                            "video": (
                                video_file.name,
                                video_file,
                                "video/mp4"
                            )
                        }

                        data = {
                            "candidate_id": str(candidate_id)
                        }

                        response = requests.post(
                            f"{API_URL}/upload_video_analysis",
                            files=files,
                            data=data,
                            timeout=300
                        )

                        if response.status_code == 200:
                            res = response.json()

                            st.success("Video analysis complete!")

                            c1, c2, c3 = st.columns(3)

                            with c1:
                                st.metric(
                                    "Dominant Emotion",
                                    res.get(
                                        "overall_dominant_emotion",
                                        "N/A"
                                    )
                                )

                            with c2:
                                st.metric(
                                    "Avg Confidence",
                                    res.get(
                                        "average_confidence_score",
                                        0
                                    )
                                )

                            with c3:
                                st.metric(
                                    "Analyzed Frames",
                                    res.get(
                                        "analyzed_frames",
                                        0
                                    )
                                )

                            st.write("### Emotion Distribution")
                            st.json(
                                res.get(
                                    "emotion_distribution",
                                    {}
                                )
                            )

                            st.write("### Full Video Result")
                            st.json(res)

                        else:
                            show_api_error(response)

                    except Exception as error:
                        st.error(
                            f"Connection failed to {API_URL}. Is backend running?"
                        )
                        st.exception(error)

    # -----------------------------
    # Live Video Recorder
    # -----------------------------
    with tab4:

        st.write("### Record Live Interview Video from Browser Camera")

        st.info(
            "Click START, allow camera permission, record for 5-10 seconds, then click 'Save & Analyze Recorded Video' while the camera is still running."
        )

        ctx = webrtc_streamer(
            key="live-video-recorder",
            mode=WebRtcMode.SENDRECV,
            media_stream_constraints={
                "video": True,
                "audio": False
            },
            video_processor_factory=VideoRecorderProcessor,
            async_processing=True
        )

        if ctx.video_processor:

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "Clear Recording",
                    key="clear_live_video",
                    width="stretch"
                ):
                    ctx.video_processor.clear_frames()
                    st.success("Recording cleared. Start recording again.")

            with col2:
                if st.button(
                    "Save & Analyze Recorded Video",
                    key="save_live_video",
                    width="stretch"
                ):

                    if not candidate_id:
                        st.warning("Please upload resume first or enter a valid Candidate ID.")

                    else:
                        frames = ctx.video_processor.get_frames()

                        if len(frames) == 0:
                            st.warning(
                                "No video frames recorded yet. Keep camera running for 5-10 seconds, then try again."
                            )

                        else:
                            with st.spinner("Saving recorded video..."):

                                video_path = (
                                    f"interview_videos/live_recorded_{int(time.time())}.mp4"
                                )

                                saved = save_frames_to_video(
                                    frames,
                                    video_path,
                                    fps=20
                                )

                                if not saved:
                                    st.error("Could not save recorded video.")

                                else:
                                    st.success(
                                        f"Video recorded successfully with {len(frames)} frames."
                                    )

                                    st.video(video_path)

                                    with st.spinner("Analyzing recorded video..."):

                                        try:
                                            with open(video_path, "rb") as video_file_obj:

                                                files = {
                                                    "video": (
                                                        os.path.basename(video_path),
                                                        video_file_obj,
                                                        "video/mp4"
                                                    )
                                                }

                                                data = {
                                                    "candidate_id": str(candidate_id)
                                                }

                                                response = requests.post(
                                                    f"{API_URL}/upload_video_analysis",
                                                    files=files,
                                                    data=data,
                                                    timeout=300
                                                )

                                            if response.status_code == 200:
                                                res = response.json()

                                                st.success(
                                                    "Live recorded video analyzed successfully!"
                                                )

                                                c1, c2, c3 = st.columns(3)

                                                with c1:
                                                    st.metric(
                                                        "Dominant Emotion",
                                                        res.get(
                                                            "overall_dominant_emotion",
                                                            "N/A"
                                                        )
                                                    )

                                                with c2:
                                                    st.metric(
                                                        "Avg Confidence",
                                                        res.get(
                                                            "average_confidence_score",
                                                            0
                                                        )
                                                    )

                                                with c3:
                                                    st.metric(
                                                        "Analyzed Frames",
                                                        res.get(
                                                            "analyzed_frames",
                                                            0
                                                        )
                                                    )

                                                st.write("### Emotion Distribution")
                                                st.json(
                                                    res.get(
                                                        "emotion_distribution",
                                                        {}
                                                    )
                                                )

                                                st.write("### Full Video Result")
                                                st.json(res)

                                            else:
                                                show_api_error(response)

                                        except Exception as error:
                                            st.error(
                                                f"Connection failed to {API_URL}. Is backend running?"
                                            )
                                            st.exception(error)


# -----------------------------
# Candidate Answer Quality Page
# -----------------------------
elif page == "Answer Quality":

    st.markdown(
        "<h2 style='margin-bottom:1rem;'>Candidate: Answer Recruiter Questions</h2>",
        unsafe_allow_html=True
    )

    candidate_id = show_active_candidate_box()

    jobs = get_jobs()

    if not jobs:
        st.warning("No jobs available. Recruiter must add a job and questions first.")
        st.stop()

    if st.session_state.selected_job_id:
        default_job_index = 0

        for index, job in enumerate(jobs):
            if job["job_id"] == st.session_state.selected_job_id:
                default_job_index = index
                break
    else:
        default_job_index = 0

    job_options = {
        f"{job['job_id']} - {job['job_title']}": job
        for job in jobs
    }

    job_labels = list(job_options.keys())

    selected_job_label = st.selectbox(
        "Select Job",
        job_labels,
        index=default_job_index,
        key="answer_quality_job"
    )

    selected_job = job_options[selected_job_label]

    st.session_state.selected_job_id = selected_job["job_id"]
    st.session_state.selected_job_title = selected_job["job_title"]

    questions = get_questions(selected_job["job_id"])

    if not questions:
        st.info("No recruiter questions added for this job yet.")
        st.stop()

    question_options = {
        q["question"]: q
        for q in questions
    }

    selected_question = st.selectbox(
        "Select Recruiter Question",
        list(question_options.keys())
    )

    answer = st.text_area(
        "Your Answer",
        height=180,
        placeholder="Write your answer here..."
    )

    if st.button(
        "Submit Answer",
        width="stretch"
    ):

        if not candidate_id:
            st.warning("Please upload resume first or enter a valid Candidate ID.")

        elif not answer:
            st.warning("Please write your answer.")

        else:
            with st.spinner("Evaluating answer quality..."):

                try:
                    payload = {
                        "candidate_id": int(candidate_id),
                        "question": selected_question,
                        "answer": answer
                    }

                    response = requests.post(
                        f"{API_URL}/analyze_answer_quality",
                        json=payload,
                        timeout=120
                    )

                    if response.status_code == 200:
                        res = response.json()

                        st.success("Answer evaluated successfully!")

                        c1, c2, c3 = st.columns(3)

                        with c1:
                            st.metric(
                                "Answer Quality Score",
                                res.get("answer_quality_score", "N/A")
                            )

                        with c2:
                            st.metric(
                                "STAR Score",
                                res.get("star_score", "N/A")
                            )

                        with c3:
                            st.metric(
                                "Clarity Score",
                                res.get("clarity_score", "N/A")
                            )

                        st.write("### Feedback")
                        feedback = res.get("feedback", [])

                        if isinstance(feedback, list):
                            for item in feedback:
                                st.write(f"- {item}")
                        else:
                            st.write(feedback)

                        st.write("### Full Result")
                        st.json(res)

                    else:
                        show_api_error(response)

                except Exception as error:
                    st.error(
                        f"Connection failed to {API_URL}. Is backend running?"
                    )
                    st.exception(error)


# -----------------------------
# Recruiter Candidate Rankings Page
# -----------------------------
elif page == "Candidate Rankings":

    st.markdown(
        "<h2 style='margin-bottom:1rem;'>Recruiter: Candidate Rankings</h2>",
        unsafe_allow_html=True
    )

    if st.button(
        "Fetch Rankings",
        width="stretch"
    ):

        with st.spinner("Fetching rankings..."):

            rankings = get_rankings()

            if rankings:
                df = make_dataframe(rankings)

                st.dataframe(
                    df,
                    width="stretch",
                    hide_index=True
                )

            else:
                st.info("No candidate activity yet. Add a job and submit a candidate resume to generate AI rankings and reports.")


# -----------------------------
# Recruiter Candidate Report Page
# -----------------------------
elif page == "Candidate Report":

    st.markdown(
        "<h2 style='margin-bottom:1rem;'>Recruiter: Detailed Candidate Report</h2>",
        unsafe_allow_html=True
    )

    candidates = get_candidates()

    selected_candidate_id = st.session_state.get("candidate_id")

    if not candidates and not selected_candidate_id:
        st.info("No candidates available for reporting. Upload a resume first.")
        st.stop()

    if candidates:
        candidate_options = {}

        for candidate in candidates:
            candidate_id_value = candidate.get("candidate_id")

            if candidate_id_value is None:
                continue

            label = f"{candidate_id_value} - {candidate.get('filename', 'Candidate')}"
            candidate_options[label] = int(candidate_id_value)

        if not candidate_options:
            st.info("Candidate data is incomplete.")
            st.stop()

        labels = list(candidate_options.keys())

        default_index = 0

        if selected_candidate_id:
            for index, label in enumerate(labels):
                if label.startswith(f"{selected_candidate_id} -"):
                    default_index = index
                    break

        selected_candidate = st.selectbox(
            "Select Candidate",
            labels,
            index=default_index
        )

        candidate_id = candidate_options[selected_candidate]

    else:
        candidate_id = int(selected_candidate_id)

    report = get_candidate_report(candidate_id)

    if report is None:
        st.error("Could not load candidate report from backend.")
        st.stop()

    st.session_state.last_report = report

    candidate = report.get("candidate", {})
    resume = report.get("resume_analysis", {})
    interview = report.get("interview_delivery_analysis", {})
    answer_quality = report.get("answer_quality_analysis", {})
    image_analysis = report.get("image_analysis", {})
    video_analysis = report.get("video_analysis", {})
    final_result = report.get("final_result", {})

    candidate_filename = candidate.get("filename", "Candidate")

    st.markdown("---")
    st.subheader(f"Candidate #{candidate_id}: {candidate_filename}")

    resume_score = first_available(
        resume,
        ["resume_score", "final_match_score", "final_score"],
        0
    )

    interview_score = first_available(
        interview,
        ["interview_score", "overall_interview_score"],
        0
    )

    answer_score = first_available(
        answer_quality,
        ["answer_quality_score"],
        0
    )

    confidence_score = first_available(
        interview,
        ["confidence_score"],
        first_available(
            image_analysis,
            ["confidence_score"],
            0
        )
    )

    emotion_score = first_available(
        interview,
        ["emotion_score"],
        first_available(
            image_analysis,
            ["emotion_score", "confidence_score"],
            0
        )
    )

    final_score = first_available(
        final_result,
        ["final_candidate_score"],
        0
    )

    decision = final_result.get("decision", "N/A")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_score_metric("Resume Score", resume_score)

    with c2:
        render_score_metric("Interview Score", interview_score)

    with c3:
        render_score_metric("Answer Quality", answer_score)

    with c4:
        render_score_metric("Final Score", final_score)

    if decision == "Strong Candidate":
        st.success(f"Final Decision: {decision}")
    elif decision == "Good Candidate":
        st.info(f"Final Decision: {decision}")
    elif decision == "N/A":
        st.warning("Final Decision is not available yet.")
    else:
        st.warning(f"Final Decision: {decision}")

    st.markdown("---")

    st.subheader("Candidate Performance Radar")

    fig = create_radar_chart(
        resume_score,
        interview_score,
        answer_score,
        confidence_score,
        emotion_score
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.markdown("---")

    st.subheader("Resume Intelligence")

    c1, c2, c3 = st.columns(3)

    with c1:
        render_score_metric(
            "Skill Match",
            resume.get("skill_match_percentage", 0)
        )

    with c2:
        render_score_metric(
            "Semantic Match",
            resume.get("semantic_match_score", 0)
        )

    with c3:
        render_score_metric(
            "Resume Final",
            resume_score
        )

    col1, col2 = st.columns(2)

    with col1:
        render_skill_badges(
            "Matched Skills",
            resume.get("matched_skills"),
            "No matched skills available."
        )

    with col2:
        render_skill_badges(
            "Missing Skills",
            resume.get("missing_skills"),
            "No missing skills available."
        )

    st.markdown("---")

    st.subheader("Interview Intelligence")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Sentiment",
            interview.get("sentiment", "N/A")
        )

    with c2:
        st.metric(
            "Dominant Emotion",
            interview.get("dominant_emotion", "N/A")
        )

    with c3:
        st.metric(
            "Filler Count",
            interview.get("filler_count", "N/A")
        )

    with c4:
        render_score_metric(
            "Confidence",
            confidence_score
        )

    transcript = interview.get("transcript")

    if transcript:
        with st.expander("Whisper Transcript"):
            st.write(transcript)
    else:
        st.info("Whisper transcript is not available yet.")

    st.markdown("---")

    st.subheader("Answer Quality")

    if answer_quality.get("available") is False:
        st.info("Answer quality analysis is not submitted yet.")
    else:
        c1, c2, c3 = st.columns(3)

        with c1:
            render_score_metric(
                "Relevance",
                answer_quality.get("relevance_score", 0)
            )

        with c2:
            render_score_metric(
                "STAR",
                answer_quality.get("star_score", 0)
            )

        with c3:
            render_score_metric(
                "Clarity",
                answer_quality.get("clarity_score", 0)
            )

        feedback = answer_quality.get("feedback")

        if feedback:
            st.write("### Feedback")
            if isinstance(feedback, list):
                for item in feedback:
                    st.write(f"- {item}")
            else:
                st.write(feedback)
        else:
            st.info("No answer feedback available yet.")

    st.markdown("---")

    st.subheader("3-Point Recruiter Summary")

    feedback_points = []

    missing_skills = resume.get("missing_skills")
    matched_skills = resume.get("matched_skills")

    if missing_skills:
        feedback_points.append(
            f"Candidate should improve missing skills: {missing_skills}."
        )
    elif matched_skills:
        feedback_points.append(
            f"Candidate matches important skills: {matched_skills}."
        )
    else:
        feedback_points.append(
            "Resume skill analysis is not available yet."
        )

    if interview:
        feedback_points.append(
            f"Interview signal: emotion is {interview.get('dominant_emotion', 'N/A')}, confidence score is {normalize_score(confidence_score):.2f}."
        )
    else:
        feedback_points.append(
            "Interview analysis is not available yet."
        )

    if answer_quality and answer_quality.get("available") is not False:
        feedback_points.append(
            f"Answer quality score is {normalize_score(answer_score):.2f}."
        )
    else:
        feedback_points.append(
            "Answer quality analysis is pending."
        )

    for point in feedback_points[:3]:
        st.write(f"- {point}")

    with st.expander("Full Raw Candidate Report"):
        st.json(report)


# -----------------------------
# Recruiter Final Hiring Decision Page
# -----------------------------
elif page == "Final Hiring Decision":

    st.markdown(
        "<h2 style='margin-bottom:1rem;'>Recruiter: Final Hiring Decision</h2>",
        unsafe_allow_html=True
    )

    candidates = get_candidates()

    if candidates:
        candidate_options = {
            f"{candidate['candidate_id']} - {candidate.get('filename', 'Candidate')}": int(candidate["candidate_id"])
            for candidate in candidates
            if candidate.get("candidate_id") is not None
        }

        selected_candidate = st.selectbox(
            "Select Candidate",
            list(candidate_options.keys())
        )

        candidate_id = candidate_options[selected_candidate]

    else:
        candidate_id = show_active_candidate_box()

    if st.button(
        "Get Final Decision",
        width="stretch"
    ):

        if not candidate_id:
            st.warning("Please select or enter a Candidate ID.")
            st.stop()

        with st.spinner("Calculating final hiring decision..."):

            result, error = get_final_score(candidate_id)

            if result is not None:

                c1, c2, c3 = st.columns(3)

                with c1:
                    render_score_metric(
                        "Resume Score",
                        result.get("resume_score", 0)
                    )

                with c2:
                    render_score_metric(
                        "Interview Score",
                        result.get("interview_delivery_score", 0)
                    )

                with c3:
                    render_score_metric(
                        "Answer Quality",
                        result.get("answer_quality_score", 0)
                    )

                st.markdown("---")

                render_score_metric(
                    "Final Candidate Score",
                    result.get("final_candidate_score", 0)
                )

                decision = result.get("decision", "N/A")

                if decision == "Strong Candidate":
                    st.success(f"Decision: {decision}")
                elif decision == "Good Candidate":
                    st.info(f"Decision: {decision}")
                else:
                    st.warning(f"Decision: {decision}")

                st.write("### Full Result")
                st.json(result)

            else:
                st.error(error or "Could not fetch final decision.")


# -----------------------------
# Candidate Feedback Page
# -----------------------------
elif page == "View Feedback":

    st.markdown(
        "<h2 style='margin-bottom:1rem;'>Candidate: View Feedback</h2>",
        unsafe_allow_html=True
    )

    candidate_id = show_active_candidate_box()

    if st.button(
        "View My Feedback",
        width="stretch"
    ):

        if not candidate_id:
            st.warning("Please upload resume first or enter a valid Candidate ID.")
            st.stop()

        with st.spinner("Loading feedback..."):

            report = get_candidate_report(candidate_id)

            if report is None:
                st.error("Could not load feedback. Check Candidate ID or backend.")

            else:
                final_result = report.get(
                    "final_result",
                    {}
                )

                resume_analysis = report.get(
                    "resume_analysis",
                    {}
                )

                interview_delivery = report.get(
                    "interview_delivery_analysis",
                    {}
                )

                answer_quality = report.get(
                    "answer_quality_analysis",
                    {}
                )

                st.write("### Final Result")

                c1, c2 = st.columns(2)

                with c1:
                    render_score_metric(
                        "Final Candidate Score",
                        final_result.get("final_candidate_score", 0)
                    )

                with c2:
                    st.metric(
                        "Decision",
                        final_result.get("decision", "N/A")
                    )

                st.markdown("---")

                st.write("### Resume Feedback")
                col1, col2 = st.columns(2)

                with col1:
                    render_skill_badges(
                        "Matched Skills",
                        resume_analysis.get("matched_skills"),
                        "No matched skills available."
                    )

                with col2:
                    render_skill_badges(
                        "Missing Skills",
                        resume_analysis.get("missing_skills"),
                        "No missing skills available."
                    )

                st.write("### Interview Delivery Feedback")

                c1, c2, c3 = st.columns(3)

                with c1:
                    render_score_metric(
                        "Interview Score",
                        first_available(
                            interview_delivery,
                            ["interview_score", "overall_interview_score"],
                            0
                        )
                    )

                with c2:
                    st.metric(
                        "Dominant Emotion",
                        interview_delivery.get(
                            "dominant_emotion",
                            "N/A"
                        )
                    )

                with c3:
                    st.metric(
                        "Filler Count",
                        interview_delivery.get(
                            "filler_count",
                            "N/A"
                        )
                    )

                if interview_delivery.get("transcript"):
                    with st.expander("Whisper Transcript"):
                        st.write(interview_delivery.get("transcript"))

                st.write("### Answer Quality Feedback")

                c1, c2, c3 = st.columns(3)

                with c1:
                    render_score_metric(
                        "Relevance Score",
                        answer_quality.get(
                            "relevance_score",
                            0
                        )
                    )

                with c2:
                    render_score_metric(
                        "STAR Score",
                        answer_quality.get(
                            "star_score",
                            0
                        )
                    )

                with c3:
                    render_score_metric(
                        "Clarity Score",
                        answer_quality.get(
                            "clarity_score",
                            0
                        )
                    )

                feedback = answer_quality.get("feedback")

                if feedback:
                    st.write("### Feedback")
                    if isinstance(feedback, list):
                        for item in feedback:
                            st.write(f"- {item}")
                    else:
                        st.write(feedback)

                with st.expander("Full Raw Feedback"):
                    st.json(report)