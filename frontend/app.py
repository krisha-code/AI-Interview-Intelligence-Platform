import streamlit as st
import requests
import json
import pandas as pd

# Constants
API_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Interview Platform", page_icon="🤖", layout="wide")

# Custom CSS for glass-morphism and styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

/* Glass-morphism cards */
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
    font-size: 2.5rem;
    font-weight: 700;
    color: #fff;
    margin: 0;
}
.stat-label {
    font-size: 1rem;
    color: #a0aabf;
    margin: 0;
}
.accent-blue { color: #3F81EC; }
.accent-pink { color: #e83e8c; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🤖 AI Interview")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation", ["Dashboard", "Upload Resume", "Interview Analysis", "Candidate Rankings"])

if page == "Dashboard":
    st.markdown("<h1 style='margin-bottom:0;'>Welcome Back!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #a0aabf; margin-bottom:2rem;'>AI Interview Intelligence Platform Dashboard</p>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="glass-card">
            <h3 class="stat-value">64</h3>
            <p class="stat-label">Total Interviews <span class="accent-blue">+12%</span></p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="glass-card">
            <h3 class="stat-value">215</h3>
            <p class="stat-label">Candidate Pipeline <span class="accent-pink">89 Active</span></p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="glass-card">
            <h3 class="stat-value">8.2</h3>
            <p class="stat-label">Avg. AI Score <span class="accent-blue">/10</span></p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="glass-card">
            <h3 class="stat-value">112</h3>
            <p class="stat-label">Insights Shared <span class="accent-pink">18 New</span></p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<h3 style='margin-top: 2rem;'>Recent Activity</h3>", unsafe_allow_html=True)
    
    # Try fetching real data, fallback to placeholder
    try:
        response = requests.get(f"{API_URL}/rank_candidates", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                df = pd.DataFrame(data)
                # Show top 5
                st.dataframe(df.head(5), use_container_width=True)
            else:
                st.markdown("<div class='glass-card'>No candidates found in the database.</div>", unsafe_allow_html=True)
        else:
             st.markdown("<div class='glass-card'>Could not load recent candidates.</div>", unsafe_allow_html=True)
    except Exception:
        st.markdown("""
        <div class='glass-card'>
            <p style='margin:0'><b>Backend Offline</b>: Currently no recent interviews to display. Connect backend (<code>http://localhost:8000</code>) to fetch candidate data.</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "Upload Resume":
    st.header("Candidate Resume Parsing")
    with st.form("resume_form"):
        job_title = st.text_input("Job Title")
        job_text = st.text_area("Job Description")
        resume_file = st.file_uploader("Upload Candidate Resume (PDF)", type=["pdf", "docx"])
        submitted = st.form_submit_button("Analyze Candidate")
        
        if submitted and resume_file and job_text:
            with st.spinner("Analyzing..."):
                try:
                    files = {"resume": (resume_file.name, resume_file, "application/pdf")}
                    data = {"job_text": job_text, "job_title": job_title}
                    response = requests.post(f"{API_URL}/upload_resume_and_analyze", files=files, data=data)
                    
                    if response.status_code == 200:
                        res = response.json()
                        st.success(f"Analyzed {res['filename']} successfully!")
                        st.metric("Final Match Score", f"{res['final_match_score'] * 100:.2f}%")
                        st.write("Matched Skills:", ", ".join(res['matched_skills']))
                        st.write("Missing Skills:", ", ".join(res['missing_skills']))
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection failed to {API_URL}. Is the backend running?")

elif page == "Interview Analysis":
    st.header("Upload Interview Media")
    with st.form("interview_form"):
        candidate_id = st.number_input("Candidate ID", min_value=1, step=1)
        audio_file = st.file_uploader("Upload Audio", type=["mp3", "wav", "m4a"])
        image_file = st.file_uploader("Upload Image/Frame", type=["jpg", "png", "jpeg"])
        
        submitted = st.form_submit_button("Run AI Analysis")
        
        if submitted and audio_file and image_file:
            with st.spinner("Processing Media..."):
                try:
                    files = {
                        "audio": (audio_file.name, audio_file, "audio/mpeg"),
                        "image": (image_file.name, image_file, "image/jpeg")
                    }
                    data = {"candidate_id": str(candidate_id)}
                    response = requests.post(f"{API_URL}/upload_interview_analysis", files=files, data=data)
                    
                    if response.status_code == 200:
                        res = response.json()
                        st.success("Analysis complete!")
                        st.write("Transcript:", res['transcript'])
                        st.write("Dominant Emotion:", res['dominant_emotion'])
                        st.metric("Overall Score", res['overall_interview_score'])
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection failed to {API_URL}. Is the backend running?")

elif page == "Candidate Rankings":
    st.header("Top Candidates")
    if st.button("Fetch Rankings"):
        with st.spinner("Fetching..."):
            try:
                response = requests.get(f"{API_URL}/rank_candidates")
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 0:
                        df = pd.DataFrame(data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No candidates found.")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection failed to {API_URL}. Is the backend running?")
