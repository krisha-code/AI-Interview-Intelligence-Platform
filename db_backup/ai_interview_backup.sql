--
-- PostgreSQL database dump
--

\restrict rxRCLT2CaqoWwlFjmavBszx25MQmpg58smPfaZmmWY9OejrsH2fOBUZoKjhLnve

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: answer_quality; Type: TABLE; Schema: public; Owner: ai_user
--

CREATE TABLE public.answer_quality (
    id integer NOT NULL,
    candidate_id integer,
    question text,
    answer text,
    relevance_score double precision,
    star_score double precision,
    clarity_score double precision,
    answer_quality_score double precision,
    feedback text
);


ALTER TABLE public.answer_quality OWNER TO ai_user;

--
-- Name: answer_quality_id_seq; Type: SEQUENCE; Schema: public; Owner: ai_user
--

CREATE SEQUENCE public.answer_quality_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.answer_quality_id_seq OWNER TO ai_user;

--
-- Name: answer_quality_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ai_user
--

ALTER SEQUENCE public.answer_quality_id_seq OWNED BY public.answer_quality.id;


--
-- Name: candidates; Type: TABLE; Schema: public; Owner: ai_user
--

CREATE TABLE public.candidates (
    id integer NOT NULL,
    filename character varying,
    skills character varying,
    matched_skills character varying,
    missing_skills character varying,
    semantic_score double precision,
    skill_match_percentage double precision,
    final_score double precision
);


ALTER TABLE public.candidates OWNER TO ai_user;

--
-- Name: candidates_id_seq; Type: SEQUENCE; Schema: public; Owner: ai_user
--

CREATE SEQUENCE public.candidates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidates_id_seq OWNER TO ai_user;

--
-- Name: candidates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ai_user
--

ALTER SEQUENCE public.candidates_id_seq OWNED BY public.candidates.id;


--
-- Name: image_analysis; Type: TABLE; Schema: public; Owner: ai_user
--

CREATE TABLE public.image_analysis (
    id integer NOT NULL,
    candidate_id integer,
    image_path character varying,
    dominant_emotion character varying,
    emotion_scores text,
    confidence_score double precision
);


ALTER TABLE public.image_analysis OWNER TO ai_user;

--
-- Name: image_analysis_id_seq; Type: SEQUENCE; Schema: public; Owner: ai_user
--

CREATE SEQUENCE public.image_analysis_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.image_analysis_id_seq OWNER TO ai_user;

--
-- Name: image_analysis_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ai_user
--

ALTER SEQUENCE public.image_analysis_id_seq OWNED BY public.image_analysis.id;


--
-- Name: interview_analysis; Type: TABLE; Schema: public; Owner: ai_user
--

CREATE TABLE public.interview_analysis (
    id integer NOT NULL,
    candidate_id integer,
    transcript text,
    sentiment character varying,
    sentiment_score double precision,
    filler_count integer,
    filler_score double precision,
    dominant_emotion character varying,
    emotion_score double precision,
    confidence_score double precision,
    overall_interview_score double precision
);


ALTER TABLE public.interview_analysis OWNER TO ai_user;

--
-- Name: interview_analysis_id_seq; Type: SEQUENCE; Schema: public; Owner: ai_user
--

CREATE SEQUENCE public.interview_analysis_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.interview_analysis_id_seq OWNER TO ai_user;

--
-- Name: interview_analysis_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ai_user
--

ALTER SEQUENCE public.interview_analysis_id_seq OWNED BY public.interview_analysis.id;


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: ai_user
--

CREATE TABLE public.jobs (
    id integer NOT NULL,
    job_title character varying,
    job_description character varying
);


ALTER TABLE public.jobs OWNER TO ai_user;

--
-- Name: jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: ai_user
--

CREATE SEQUENCE public.jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.jobs_id_seq OWNER TO ai_user;

--
-- Name: jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ai_user
--

ALTER SEQUENCE public.jobs_id_seq OWNED BY public.jobs.id;


--
-- Name: matches; Type: TABLE; Schema: public; Owner: ai_user
--

CREATE TABLE public.matches (
    id integer NOT NULL,
    candidate_id integer,
    job_id integer,
    semantic_score double precision,
    skill_match_percentage double precision,
    final_score double precision
);


ALTER TABLE public.matches OWNER TO ai_user;

--
-- Name: matches_id_seq; Type: SEQUENCE; Schema: public; Owner: ai_user
--

CREATE SEQUENCE public.matches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.matches_id_seq OWNER TO ai_user;

--
-- Name: matches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ai_user
--

ALTER SEQUENCE public.matches_id_seq OWNED BY public.matches.id;


--
-- Name: video_analysis; Type: TABLE; Schema: public; Owner: ai_user
--

CREATE TABLE public.video_analysis (
    id integer NOT NULL,
    candidate_id integer,
    video_path character varying,
    total_frames_read integer,
    analyzed_frames integer,
    emotion_distribution text,
    overall_dominant_emotion character varying,
    average_confidence_score double precision
);


ALTER TABLE public.video_analysis OWNER TO ai_user;

--
-- Name: video_analysis_id_seq; Type: SEQUENCE; Schema: public; Owner: ai_user
--

CREATE SEQUENCE public.video_analysis_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.video_analysis_id_seq OWNER TO ai_user;

--
-- Name: video_analysis_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ai_user
--

ALTER SEQUENCE public.video_analysis_id_seq OWNED BY public.video_analysis.id;


--
-- Name: answer_quality id; Type: DEFAULT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.answer_quality ALTER COLUMN id SET DEFAULT nextval('public.answer_quality_id_seq'::regclass);


--
-- Name: candidates id; Type: DEFAULT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.candidates ALTER COLUMN id SET DEFAULT nextval('public.candidates_id_seq'::regclass);


--
-- Name: image_analysis id; Type: DEFAULT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.image_analysis ALTER COLUMN id SET DEFAULT nextval('public.image_analysis_id_seq'::regclass);


--
-- Name: interview_analysis id; Type: DEFAULT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.interview_analysis ALTER COLUMN id SET DEFAULT nextval('public.interview_analysis_id_seq'::regclass);


--
-- Name: jobs id; Type: DEFAULT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.jobs ALTER COLUMN id SET DEFAULT nextval('public.jobs_id_seq'::regclass);


--
-- Name: matches id; Type: DEFAULT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.matches ALTER COLUMN id SET DEFAULT nextval('public.matches_id_seq'::regclass);


--
-- Name: video_analysis id; Type: DEFAULT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.video_analysis ALTER COLUMN id SET DEFAULT nextval('public.video_analysis_id_seq'::regclass);


--
-- Data for Name: answer_quality; Type: TABLE DATA; Schema: public; Owner: ai_user
--

COPY public.answer_quality (id, candidate_id, question, answer, relevance_score, star_score, clarity_score, answer_quality_score, feedback) FROM stdin;
\.


--
-- Data for Name: candidates; Type: TABLE DATA; Schema: public; Owner: ai_user
--

COPY public.candidates (id, filename, skills, matched_skills, missing_skills, semantic_score, skill_match_percentage, final_score) FROM stdin;
1	Krisha Gandhi-RESUME.pdf	deep learning, docker, fastapi, git, keras, machine learning, matplotlib, mysql, nlp, numpy, pandas, postgresql, power bi, python, scikit-learn, seaborn, sql, tensorflow	machine learning, python, nlp, docker, fastapi, tensorflow		59.36	100	71.55
2	Krisha Gandhi-RESUME.pdf	deep learning, docker, fastapi, git, keras, machine learning, matplotlib, mysql, nlp, numpy, pandas, postgresql, power bi, python, scikit-learn, seaborn, sql, tensorflow	machine learning, python, nlp, docker, fastapi, tensorflow		59.36	100	71.55
3	Krisha Gandhi-RESUME.pdf	deep learning, docker, fastapi, git, keras, machine learning, matplotlib, mysql, nlp, numpy, pandas, postgresql, power bi, python, scikit-learn, seaborn, sql, tensorflow	machine learning, python, nlp, docker, fastapi, tensorflow		59.36	100	71.55
4	Krisha Gandhi-RESUME.pdf	deep learning, docker, fastapi, git, keras, machine learning, matplotlib, mysql, nlp, numpy, pandas, postgresql, power bi, python, scikit-learn, seaborn, sql, tensorflow	python, docker, tensorflow		46.05	100	62.23
5	Krisha Gandhi-RESUME.pdf	deep learning, docker, fastapi, git, keras, machine learning, matplotlib, mysql, nlp, numpy, pandas, postgresql, power bi, python, scikit-learn, seaborn, sql, tensorflow	python, docker, tensorflow		46.05	100	62.23
6	Krisha Gandhi-RESUME.pdf	deep learning, docker, fastapi, git, keras, machine learning, matplotlib, mysql, nlp, numpy, pandas, postgresql, power bi, python, scikit-learn, seaborn, sql, tensorflow	python, docker, tensorflow		46.05	100	62.23
7	Krisha Gandhi-RESUME.pdf	deep learning, docker, fastapi, git, keras, machine learning, matplotlib, mysql, nlp, numpy, pandas, postgresql, power bi, python, scikit-learn, seaborn, sql, tensorflow	python, docker, tensorflow		46.05	100	62.23
8	Krisha Gandhi-RESUME.pdf	deep learning, docker, fastapi, git, keras, machine learning, matplotlib, mysql, nlp, numpy, pandas, postgresql, power bi, python, scikit-learn, seaborn, sql, tensorflow	python, docker, tensorflow		46.05	100	62.23
9	Krisha Gandhi-RESUME.pdf	deep learning, docker, fastapi, git, keras, machine learning, matplotlib, mysql, nlp, numpy, pandas, postgresql, power bi, python, scikit-learn, seaborn, sql, tensorflow	python, docker, tensorflow		46.05	100	62.23
10	Krisha Gandhi-RESUME.pdf	deep learning, docker, fastapi, git, keras, machine learning, matplotlib, mysql, nlp, numpy, pandas, postgresql, power bi, python, scikit-learn, seaborn, sql, tensorflow	python, docker, tensorflow		46.05	100	62.23
11	Krisha Gandhi-RESUME.pdf	deep learning, docker, fastapi, git, keras, machine learning, matplotlib, mysql, nlp, numpy, pandas, postgresql, power bi, python, scikit-learn, seaborn, sql, tensorflow	tensorflow, docker, python	pytorch, aws	50.22	60	53.15
12	Krisha Gandhi-RESUME.pdf	deep learning, docker, fastapi, git, keras, machine learning, matplotlib, mysql, nlp, numpy, pandas, postgresql, power bi, python, scikit-learn, seaborn, sql, tensorflow	python, tensorflow	pytorch, aws	46.8	50	47.76
\.


--
-- Data for Name: image_analysis; Type: TABLE DATA; Schema: public; Owner: ai_user
--

COPY public.image_analysis (id, candidate_id, image_path, dominant_emotion, emotion_scores, confidence_score) FROM stdin;
1	1	interview_images/live_capture.jpg	neutral	{"angry": 1.6060571397247259e-06, "disgust": 1.3150581734677758e-09, "fear": 3.607012695283629e-05, "happy": 4.95399808883667, "sad": 14.841093063354492, "surprise": 9.045876825375387e-10, "neutral": 80.20486450195312}	0
2	1	interview_images/live_capture.jpg	neutral	{"angry": 1.6060571397247259e-06, "disgust": 1.3150581734677758e-09, "fear": 3.607012695283629e-05, "happy": 4.95399808883667, "sad": 14.841093063354492, "surprise": 9.045876825375387e-10, "neutral": 80.20486450195312}	0
3	1	interview_images/live_capture.jpg	neutral	{"angry": 1.6060571397247259e-06, "disgust": 1.3150581734677758e-09, "fear": 3.607012695283629e-05, "happy": 4.95399808883667, "sad": 14.841093063354492, "surprise": 9.045876825375387e-10, "neutral": 80.20486450195312}	0
4	1	interview_images/live_capture.jpg	happy	{"angry": 0.11135322600603104, "disgust": 0.004072208888828754, "fear": 0.6412949562072754, "happy": 70.76375579833984, "sad": 1.5397610664367676, "surprise": 0.11623335629701614, "neutral": 26.82352638244629}	0
\.


--
-- Data for Name: interview_analysis; Type: TABLE DATA; Schema: public; Owner: ai_user
--

COPY public.interview_analysis (id, candidate_id, transcript, sentiment, sentiment_score, filler_count, filler_score, dominant_emotion, emotion_score, confidence_score, overall_interview_score) FROM stdin;
\.


--
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: ai_user
--

COPY public.jobs (id, job_title, job_description) FROM stdin;
1	Machine Learning Engineer	Looking for candidate with Python, Machine Learning, NLP, TensorFlow, FastAPI, Docker
2	Machine Learning	Looking for candidate with Python, Machine Learning, NLP, TensorFlow, FastAPI, Docker
3	Machine Learning Engineer	Looking for candidate with Python, Machine Learning, NLP, TensorFlow, FastAPI, Docker
4	ml	python,ml,docker,tensorflow
5	ml	python,ml,docker,tensorflow
6	ml	python,ml,docker,tensorflow
7	ml,aws,pytorch	python,ml,docker,tensorflow
8	ml,aws,pytorch	python,ml,docker,tensorflow
9	ml,aws,pytorch	python,ml,docker,tensorflow
10	ml,aws,pytorch	python,ml,docker,tensorflow
11	ml	python,ml,docker,tensorflow,aws,pytorch
12	ml	python,pytorch,tensorflow,aws
\.


--
-- Data for Name: matches; Type: TABLE DATA; Schema: public; Owner: ai_user
--

COPY public.matches (id, candidate_id, job_id, semantic_score, skill_match_percentage, final_score) FROM stdin;
1	1	1	59.36	100	71.55
2	2	2	59.36	100	71.55
3	3	3	59.36	100	71.55
4	4	4	46.05	100	62.23
5	5	5	46.05	100	62.23
6	6	6	46.05	100	62.23
7	7	7	46.05	100	62.23
8	8	8	46.05	100	62.23
9	9	9	46.05	100	62.23
10	10	10	46.05	100	62.23
11	11	11	50.22	60	53.15
12	12	12	46.8	50	47.76
\.


--
-- Data for Name: video_analysis; Type: TABLE DATA; Schema: public; Owner: ai_user
--

COPY public.video_analysis (id, candidate_id, video_path, total_frames_read, analyzed_frames, emotion_distribution, overall_dominant_emotion, average_confidence_score) FROM stdin;
1	1	interview_videos/live_recorded_1781868125.mp4	190	5	{"neutral": 2, "fear": 2, "surprise": 1}	neutral	90.36
\.


--
-- Name: answer_quality_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ai_user
--

SELECT pg_catalog.setval('public.answer_quality_id_seq', 1, false);


--
-- Name: candidates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ai_user
--

SELECT pg_catalog.setval('public.candidates_id_seq', 12, true);


--
-- Name: image_analysis_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ai_user
--

SELECT pg_catalog.setval('public.image_analysis_id_seq', 4, true);


--
-- Name: interview_analysis_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ai_user
--

SELECT pg_catalog.setval('public.interview_analysis_id_seq', 1, false);


--
-- Name: jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ai_user
--

SELECT pg_catalog.setval('public.jobs_id_seq', 12, true);


--
-- Name: matches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ai_user
--

SELECT pg_catalog.setval('public.matches_id_seq', 12, true);


--
-- Name: video_analysis_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ai_user
--

SELECT pg_catalog.setval('public.video_analysis_id_seq', 1, true);


--
-- Name: answer_quality answer_quality_pkey; Type: CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.answer_quality
    ADD CONSTRAINT answer_quality_pkey PRIMARY KEY (id);


--
-- Name: candidates candidates_pkey; Type: CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.candidates
    ADD CONSTRAINT candidates_pkey PRIMARY KEY (id);


--
-- Name: image_analysis image_analysis_pkey; Type: CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.image_analysis
    ADD CONSTRAINT image_analysis_pkey PRIMARY KEY (id);


--
-- Name: interview_analysis interview_analysis_pkey; Type: CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.interview_analysis
    ADD CONSTRAINT interview_analysis_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: matches matches_pkey; Type: CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_pkey PRIMARY KEY (id);


--
-- Name: video_analysis video_analysis_pkey; Type: CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.video_analysis
    ADD CONSTRAINT video_analysis_pkey PRIMARY KEY (id);


--
-- Name: ix_answer_quality_id; Type: INDEX; Schema: public; Owner: ai_user
--

CREATE INDEX ix_answer_quality_id ON public.answer_quality USING btree (id);


--
-- Name: ix_candidates_id; Type: INDEX; Schema: public; Owner: ai_user
--

CREATE INDEX ix_candidates_id ON public.candidates USING btree (id);


--
-- Name: ix_image_analysis_id; Type: INDEX; Schema: public; Owner: ai_user
--

CREATE INDEX ix_image_analysis_id ON public.image_analysis USING btree (id);


--
-- Name: ix_interview_analysis_id; Type: INDEX; Schema: public; Owner: ai_user
--

CREATE INDEX ix_interview_analysis_id ON public.interview_analysis USING btree (id);


--
-- Name: ix_jobs_id; Type: INDEX; Schema: public; Owner: ai_user
--

CREATE INDEX ix_jobs_id ON public.jobs USING btree (id);


--
-- Name: ix_matches_id; Type: INDEX; Schema: public; Owner: ai_user
--

CREATE INDEX ix_matches_id ON public.matches USING btree (id);


--
-- Name: ix_video_analysis_id; Type: INDEX; Schema: public; Owner: ai_user
--

CREATE INDEX ix_video_analysis_id ON public.video_analysis USING btree (id);


--
-- Name: answer_quality answer_quality_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.answer_quality
    ADD CONSTRAINT answer_quality_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(id);


--
-- Name: image_analysis image_analysis_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.image_analysis
    ADD CONSTRAINT image_analysis_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(id);


--
-- Name: interview_analysis interview_analysis_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.interview_analysis
    ADD CONSTRAINT interview_analysis_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(id);


--
-- Name: matches matches_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(id);


--
-- Name: matches matches_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id);


--
-- Name: video_analysis video_analysis_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.video_analysis
    ADD CONSTRAINT video_analysis_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO ai_user;


--
-- PostgreSQL database dump complete
--

\unrestrict rxRCLT2CaqoWwlFjmavBszx25MQmpg58smPfaZmmWY9OejrsH2fOBUZoKjhLnve

