--
-- PostgreSQL database dump
--

-- Dumped from database version 17.7
-- Dumped by pg_dump version 17.7

-- Started on 2026-06-10 22:03:32

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2 (class 3079 OID 38433)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 4970 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 221 (class 1259 OID 38496)
-- Name: family_members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.family_members (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    scenario_id uuid NOT NULL,
    member_index integer NOT NULL,
    name character varying(100) NOT NULL,
    gender character varying(10) NOT NULL,
    relationship_role character varying(100) NOT NULL,
    personality text NOT NULL,
    emotional_state text NOT NULL,
    interjection_triggers jsonb DEFAULT '[]'::jsonb NOT NULL
);


ALTER TABLE public.family_members OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 38457)
-- Name: game_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.game_sessions (
    id uuid NOT NULL,
    user_id uuid,
    difficulty character varying(10) NOT NULL,
    status character varying(20) DEFAULT 'briefing'::character varying NOT NULL,
    time_limit_seconds integer DEFAULT 480 NOT NULL,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    chat_messages jsonb DEFAULT '[]'::jsonb NOT NULL
);


ALTER TABLE public.game_sessions OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 38472)
-- Name: scenarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scenarios (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    session_id uuid NOT NULL,
    patient_name character varying(100) NOT NULL,
    patient_age integer NOT NULL,
    patient_gender character varying(10) NOT NULL,
    patient_diagnosis text NOT NULL,
    patient_medications jsonb DEFAULT '[]'::jsonb NOT NULL,
    patient_medical_history jsonb DEFAULT '[]'::jsonb NOT NULL,
    patient_allergies jsonb DEFAULT '[]'::jsonb NOT NULL,
    pain_location text NOT NULL,
    pain_severity integer NOT NULL,
    pain_type character varying(100) NOT NULL,
    pain_duration character varying(100) NOT NULL,
    pain_onset text NOT NULL,
    pain_aggravating_factors jsonb DEFAULT '[]'::jsonb NOT NULL,
    pain_relieving_factors jsonb DEFAULT '[]'::jsonb NOT NULL,
    pain_associated_symptoms jsonb DEFAULT '[]'::jsonb NOT NULL,
    communication_challenges jsonb DEFAULT '[]'::jsonb NOT NULL,
    correct_answers jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.scenarios OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 38511)
-- Name: score_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.score_results (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    session_id uuid NOT NULL,
    overall_score integer NOT NULL,
    level_label character varying(50) NOT NULL,
    score_empathy integer NOT NULL,
    score_guided_questioning integer NOT NULL,
    score_family_calming integer NOT NULL,
    score_info_gathering integer NOT NULL,
    score_response_fluency integer NOT NULL,
    strengths jsonb DEFAULT '[]'::jsonb NOT NULL,
    improvements jsonb DEFAULT '[]'::jsonb NOT NULL,
    key_moments jsonb DEFAULT '[]'::jsonb NOT NULL,
    evaluated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.score_results OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 38444)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    email character varying(255) NOT NULL,
    name character varying(255),
    picture_url character varying(512),
    google_id character varying(255),
    password_hash character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    last_login_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 4963 (class 0 OID 38496)
-- Dependencies: 221
-- Data for Name: family_members; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 4961 (class 0 OID 38457)
-- Dependencies: 219
-- Data for Name: game_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 4962 (class 0 OID 38472)
-- Dependencies: 220
-- Data for Name: scenarios; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 4964 (class 0 OID 38511)
-- Dependencies: 222
-- Data for Name: score_results; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 4960 (class 0 OID 38444)
-- Dependencies: 218
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 4805 (class 2606 OID 38504)
-- Name: family_members family_members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.family_members
    ADD CONSTRAINT family_members_pkey PRIMARY KEY (id);


--
-- TOC entry 4797 (class 2606 OID 38464)
-- Name: game_sessions game_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.game_sessions
    ADD CONSTRAINT game_sessions_pkey PRIMARY KEY (id);


--
-- TOC entry 4801 (class 2606 OID 38488)
-- Name: scenarios scenarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scenarios
    ADD CONSTRAINT scenarios_pkey PRIMARY KEY (id);


--
-- TOC entry 4803 (class 2606 OID 38490)
-- Name: scenarios scenarios_session_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scenarios
    ADD CONSTRAINT scenarios_session_id_key UNIQUE (session_id);


--
-- TOC entry 4808 (class 2606 OID 38522)
-- Name: score_results score_results_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.score_results
    ADD CONSTRAINT score_results_pkey PRIMARY KEY (id);


--
-- TOC entry 4810 (class 2606 OID 38524)
-- Name: score_results score_results_session_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.score_results
    ADD CONSTRAINT score_results_session_id_key UNIQUE (session_id);


--
-- TOC entry 4791 (class 2606 OID 38454)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 4793 (class 2606 OID 38456)
-- Name: users users_google_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_google_id_key UNIQUE (google_id);


--
-- TOC entry 4795 (class 2606 OID 38452)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4806 (class 1259 OID 38510)
-- Name: idx_family_members_scenario_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_family_members_scenario_id ON public.family_members USING btree (scenario_id);


--
-- TOC entry 4798 (class 1259 OID 38471)
-- Name: idx_game_sessions_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_game_sessions_created_at ON public.game_sessions USING btree (created_at DESC);


--
-- TOC entry 4799 (class 1259 OID 38470)
-- Name: idx_game_sessions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_game_sessions_user_id ON public.game_sessions USING btree (user_id);


--
-- TOC entry 4813 (class 2606 OID 38505)
-- Name: family_members family_members_scenario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.family_members
    ADD CONSTRAINT family_members_scenario_id_fkey FOREIGN KEY (scenario_id) REFERENCES public.scenarios(id) ON DELETE CASCADE;


--
-- TOC entry 4811 (class 2606 OID 38465)
-- Name: game_sessions game_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.game_sessions
    ADD CONSTRAINT game_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4812 (class 2606 OID 38491)
-- Name: scenarios scenarios_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scenarios
    ADD CONSTRAINT scenarios_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.game_sessions(id) ON DELETE CASCADE;


--
-- TOC entry 4814 (class 2606 OID 38525)
-- Name: score_results score_results_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.score_results
    ADD CONSTRAINT score_results_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.game_sessions(id) ON DELETE CASCADE;


-- Completed on 2026-06-10 22:03:32

--
-- PostgreSQL database dump complete
--

-- ──────────────────────────────────────────────────────────────────────────────
-- Migration: run ONLY if the table already existed before this change.
-- ──────────────────────────────────────────────────────────────────────────────
-- ALTER TABLE public.game_sessions ALTER COLUMN user_id DROP NOT NULL;
-- ALTER TABLE public.game_sessions ADD COLUMN IF NOT EXISTS chat_messages jsonb DEFAULT '[]'::jsonb NOT NULL;

