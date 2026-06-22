import streamlit as st
import requests
import pandas as pd
import os
import time
import cv2
import av
import threading

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
def get_rankings():
    try:
        response = requests.get(
            f"{API_URL}/rank_candidates",
            timeout=5
        )

        if response.status_code == 200:
            return response.json()

        return []

    except Exception:
        return []


def get_candidate_report(candidate_id):
    try:
        response = requests.get(
            f"{API_URL}/candidate_report/{candidate_id}",
            timeout=5
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
            timeout=10
        )

        if response.status_code == 200:
            return response.json(), None

        return None, response.text

    except Exception as error:
        return None, str(error)


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
            "Add Job & Upload Resume",
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
                No candidates found or backend is offline.
               
            </div>
            """,
            unsafe_allow_html=True
        )


# -----------------------------
# Resume Upload Page
# Recruiter: Add Job & Upload Resume
# Candidate: Candidate Resume Upload
# -----------------------------
elif page in ["Add Job & Upload Resume", "Candidate Resume Upload"]:

    if page == "Add Job & Upload Resume":
        st.markdown(
            "<h2 style='margin-bottom:1rem;'>Recruiter: Add Job & Upload Candidate Resume</h2>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<h2 style='margin-bottom:1rem;'>Candidate: Upload Resume</h2>",
            unsafe_allow_html=True
        )

    with st.form("resume_form"):

        col1, col2 = st.columns(2)

        with col1:
            job_title = st.text_input(
                "Job Title",
                placeholder="Machine Learning Engineer"
            )

            resume_file = st.file_uploader(
                "Upload Candidate Resume PDF",
                type=["pdf"]
            )

        with col2:
            job_text = st.text_area(
                "Job Description",
                height=160,
                placeholder="Looking for candidate with Python, ML, NLP, TensorFlow, Docker..."
            )

        submitted = st.form_submit_button(
            "Analyze Candidate",
            width="stretch"
        )

        if submitted:

            if not resume_file:
                st.warning("Please upload a resume PDF.")

            elif not job_text:
                st.warning("Please enter job description.")

            else:
                with st.spinner("Analyzing resume..."):

                    try:
                        files = {
                            "resume": (
                                resume_file.name,
                                resume_file,
                                "application/pdf"
                            )
                        }

                        data = {
                            "job_text": job_text,
                            "job_title": job_title or "Not Provided"
                        }

                        response = requests.post(
                            f"{API_URL}/upload_resume_and_analyze",
                            files=files,
                            data=data,
                            timeout=120
                        )

                        if response.status_code == 200:
                            res = response.json()

                            st.success(
                                f"Analyzed {res['filename']} successfully!"
                            )

                            c1, c2, c3 = st.columns(3)

                            with c1:
                                st.metric(
                                    "Final Match Score",
                                    f"{res['final_match_score']:.2f}%"
                                )

                            with c2:
                                st.metric(
                                    "Skill Match",
                                    f"{res['skill_match_percentage']:.2f}%"
                                )

                            with c3:
                                st.metric(
                                    "Semantic Score",
                                    f"{res['semantic_match_score']:.2f}%"
                                )

                            st.write("### Candidate ID")
                            st.code(res["candidate_id"])

                            st.write("### Matched Skills")
                            st.write(
                                ", ".join(res["matched_skills"])
                                if res["matched_skills"]
                                else "No matched skills"
                            )

                            st.write("### Missing Skills")
                            st.write(
                                ", ".join(res["missing_skills"])
                                if res["missing_skills"]
                                else "No missing skills"
                            )

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

    with st.form("interview_form"):

        candidate_id = st.number_input(
            "Candidate ID",
            min_value=1,
            step=1
        )

        col1, col2 = st.columns(2)

        with col1:
            audio_file = st.file_uploader(
                "Upload Interview Audio",
                type=["mp3", "wav", "m4a","mp4"]
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

            if not audio_file:
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
                                    res["overall_interview_score"]
                                )

                            with c2:
                                st.metric(
                                    "Dominant Emotion",
                                    res["dominant_emotion"]
                                )

                            with c3:
                                st.metric(
                                    "Filler Count",
                                    res["filler_count"]
                                )

                            with c4:
                                st.metric(
                                    "Confidence Score",
                                    res["confidence_score"]
                                )

                            st.write("### Transcript")
                            st.write(res["transcript"])

                            st.write("### Sentiment")
                            st.json(res["sentiment"])

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

        live_candidate_id = st.number_input(
            "Candidate ID",
            min_value=1,
            step=1,
            key="live_image_candidate_id"
        )

        camera_image = st.camera_input(
            "Capture candidate face image"
        )

        if st.button(
            "Analyze Live Captured Image",
            key="analyze_live_image",
            width="stretch"
        ):

            if camera_image is None:
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
                            "candidate_id": str(live_candidate_id)
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
                                    res["dominant_emotion"]
                                )

                            with c2:
                                st.metric(
                                    "Confidence Score",
                                    res["confidence_score"]
                                )

                            st.write("### Emotion Scores")
                            st.json(res["emotion_scores"])

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

        upload_image_candidate_id = st.number_input(
            "Candidate ID",
            min_value=1,
            step=1,
            key="upload_image_candidate_id"
        )

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

            if not standalone_image:
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
                            "candidate_id": str(upload_image_candidate_id)
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
                                    res["dominant_emotion"]
                                )

                            with c2:
                                st.metric(
                                    "Confidence Score",
                                    res["confidence_score"]
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

        video_candidate_id = st.number_input(
            "Candidate ID",
            min_value=1,
            step=1,
            key="video_candidate_id"
        )

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

            if not video_file:
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
                            "candidate_id": str(video_candidate_id)
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

        live_video_candidate_id = st.number_input(
            "Candidate ID",
            min_value=1,
            step=1,
            key="live_video_candidate_id"
        )

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
                                                "candidate_id": str(
                                                    live_video_candidate_id
                                                )
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
        "<h2 style='margin-bottom:1rem;'>Candidate: Answer Quality Evaluation</h2>",
        unsafe_allow_html=True
    )

    with st.form("answer_quality_form"):

        candidate_id = st.number_input(
            "Candidate ID",
            min_value=1,
            step=1,
            key="answer_candidate_id"
        )

        question = st.text_area(
            "Interview Question",
            height=100,
            placeholder="Tell me about a machine learning project you worked on."
        )

        answer = st.text_area(
            "Candidate Answer",
            height=180,
            placeholder="I worked on a machine learning movie recommendation system..."
        )

        submitted = st.form_submit_button(
            "Evaluate Answer",
            width="stretch"
        )

        if submitted:

            if not question:
                st.warning("Please enter interview question.")

            elif not answer:
                st.warning("Please enter candidate answer.")

            else:
                with st.spinner("Evaluating answer quality..."):

                    try:
                        payload = {
                            "candidate_id": int(candidate_id),
                            "question": question,
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
                                    res["answer_quality_score"]
                                )

                            with c2:
                                st.metric(
                                    "STAR Score",
                                    res["star_score"]
                                )

                            with c3:
                                st.metric(
                                    "Clarity Score",
                                    res["clarity_score"]
                                )

                            st.write("### Feedback")
                            for item in res["feedback"]:
                                st.write(f"- {item}")

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
                st.info("No candidates found or backend is offline.")


# -----------------------------
# Recruiter Candidate Report Page
# -----------------------------
elif page == "Candidate Report":

    st.markdown(
        "<h2 style='margin-bottom:1rem;'>Recruiter: Detailed Candidate Report</h2>",
        unsafe_allow_html=True
    )

    rankings = get_rankings()

    if not rankings:
        st.info("No candidates available for reporting.")

    else:
        df = make_dataframe(rankings)

        if "filename" not in df.columns or "candidate_id" not in df.columns:
            st.error("Candidate data is incomplete.")

        else:
            candidate_options = {
                f"{row['candidate_id']} - {row['filename']}": int(row["candidate_id"])
                for _, row in df.iterrows()
            }

            selected_candidate = st.selectbox(
                "Select Candidate",
                list(candidate_options.keys())
            )

            candidate_id = candidate_options[selected_candidate]

            report = get_candidate_report(candidate_id)

            if report is None:
                st.error("Could not load candidate report from backend.")

            else:
                st.markdown("---")

                st.subheader(
                    f"Report for Candidate ID {candidate_id}"
                )

                final_result = report.get(
                    "final_result",
                    {}
                )

                c1, c2 = st.columns(2)

                with c1:
                    st.metric(
                        "Final Candidate Score",
                        f"{final_result.get('final_candidate_score', 0):.2f} / 100"
                    )

                with c2:
                    st.metric(
                        "Decision",
                        final_result.get("decision", "N/A")
                    )

                st.write("### Candidate")
                st.json(report.get("candidate", {}))

                st.write("### Resume Analysis")
                st.json(report.get("resume_analysis", {}))

                st.write("### Interview Delivery Analysis")
                st.json(report.get("interview_delivery_analysis", {}))

                st.write("### Answer Quality Analysis")
                st.json(report.get("answer_quality_analysis", {}))

                st.write("### Image Analysis")
                st.json(report.get("image_analysis", {}))

                st.write("### Video Analysis")
                st.json(report.get("video_analysis", {}))


# -----------------------------
# Recruiter Final Hiring Decision Page
# -----------------------------
elif page == "Final Hiring Decision":

    st.markdown(
        "<h2 style='margin-bottom:1rem;'>Recruiter: Final Hiring Decision</h2>",
        unsafe_allow_html=True
    )

    candidate_id = st.number_input(
        "Enter Candidate ID",
        min_value=1,
        step=1,
        key="final_decision_candidate_id"
    )

    if st.button(
        "Get Final Decision",
        width="stretch"
    ):

        with st.spinner("Calculating final hiring decision..."):

            result, error = get_final_score(candidate_id)

            if result is not None:

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric(
                        "Resume Score",
                        f"{result.get('resume_score', 0):.2f} / 100"
                    )

                with c2:
                    st.metric(
                        "Interview Score",
                        f"{result.get('interview_delivery_score', 0):.2f} / 100"
                    )

                with c3:
                    st.metric(
                        "Answer Quality",
                        f"{result.get('answer_quality_score', 0):.2f} / 100"
                    )

                st.markdown("---")

                st.metric(
                    "Final Candidate Score",
                    f"{result.get('final_candidate_score', 0):.2f} / 100"
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

    candidate_id = st.number_input(
        "Enter Your Candidate ID",
        min_value=1,
        step=1,
        key="feedback_candidate_id"
    )

    if st.button(
        "View My Feedback",
        width="stretch"
    ):

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
                    st.metric(
                        "Final Candidate Score",
                        f"{final_result.get('final_candidate_score', 0):.2f} / 100"
                    )

                with c2:
                    st.metric(
                        "Decision",
                        final_result.get("decision", "N/A")
                    )

                st.markdown("---")

                st.write("### Resume Feedback")
                st.json(resume_analysis)

                st.write("### Interview Delivery Feedback")

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric(
                        "Interview Score",
                        interview_delivery.get(
                            "overall_interview_score",
                            "N/A"
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

                st.json(interview_delivery)

                st.write("### Answer Quality Feedback")

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric(
                        "Relevance Score",
                        answer_quality.get(
                            "relevance_score",
                            "N/A"
                        )
                    )

                with c2:
                    st.metric(
                        "STAR Score",
                        answer_quality.get(
                            "star_score",
                            "N/A"
                        )
                    )

                with c3:
                    st.metric(
                        "Clarity Score",
                        answer_quality.get(
                            "clarity_score",
                            "N/A"
                        )
                    )

                st.json(answer_quality)