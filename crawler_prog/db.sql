--
-- PostgreSQL database dump
--

-- Dumped from database version 10.3
-- Dumped by pg_dump version 10.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: crawler_data; Type: TABLE; Schema: public; Owner: alexschneidman
--

CREATE TABLE public.crawler_data (
    id integer NOT NULL,
    column1 text,
    column2 text,
    column3 text
);


ALTER TABLE public.crawler_data OWNER TO alexschneidman;

--
-- Name: crawler_data_id_seq; Type: SEQUENCE; Schema: public; Owner: alexschneidman
--

CREATE SEQUENCE public.crawler_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.crawler_data_id_seq OWNER TO alexschneidman;

--
-- Name: crawler_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: alexschneidman
--

ALTER SEQUENCE public.crawler_data_id_seq OWNED BY public.crawler_data.id;


--
-- Name: video_segment_data; Type: TABLE; Schema: public; Owner: sqa_downloader
--

CREATE TABLE public.video_segment_data (
    video_id character varying(100) NOT NULL,
    first_word_secs real,
    last_word_secs real,
    segment_start_secs real,
    segment_end_secs real,
    download_path character varying(1000),
    trimmed boolean
);


ALTER TABLE public.video_segment_data OWNER TO sqa_downloader;

--
-- Name: youtube_data; Type: TABLE; Schema: public; Owner: sqa_downloader
--

CREATE TABLE public.youtube_data (
    video_id character varying(15) NOT NULL,
    search_term character varying(100) NOT NULL,
    channel_id character varying(100) NOT NULL,
    search_time timestamp with time zone DEFAULT now() NOT NULL,
    download_time timestamp without time zone,
    download_success boolean,
    download_path character varying(1000),
    face_detect_queue_time timestamp without time zone,
    face_detect_attempt_time timestamp without time zone,
    face_detect_percent integer,
    face_detect_success boolean,
    p2fa_queue_time timestamp without time zone,
    p2fa_attempt_time timestamp without time zone,
    p2fa_success boolean,
    punctuation_check_queue_time timestamp without time zone,
    punctuation_check_attempt_time timestamp without time zone,
    punctuation_check_success boolean,
    manual_check boolean,
    trim_duration real,
    length character varying(10),
    mturk_transcription character varying
);


ALTER TABLE public.youtube_data OWNER TO sqa_downloader;

--
-- Name: crawler_data id; Type: DEFAULT; Schema: public; Owner: alexschneidman
--

ALTER TABLE ONLY public.crawler_data ALTER COLUMN id SET DEFAULT nextval('public.crawler_data_id_seq'::regclass);


--
-- Name: crawler_data crawler_data_pkey; Type: CONSTRAINT; Schema: public; Owner: alexschneidman
--

ALTER TABLE ONLY public.crawler_data
    ADD CONSTRAINT crawler_data_pkey PRIMARY KEY (id);


--
-- Name: video_segment_data video_segment_data_pkey; Type: CONSTRAINT; Schema: public; Owner: sqa_downloader
--

ALTER TABLE ONLY public.video_segment_data
    ADD CONSTRAINT video_segment_data_pkey PRIMARY KEY (video_id);


--
-- Name: youtube_data youtube_data_pkey; Type: CONSTRAINT; Schema: public; Owner: sqa_downloader
--

ALTER TABLE ONLY public.youtube_data
    ADD CONSTRAINT youtube_data_pkey PRIMARY KEY (video_id);


--
-- Name: TABLE crawler_data; Type: ACL; Schema: public; Owner: alexschneidman
--

GRANT ALL ON TABLE public.crawler_data TO sqa_downloader;


--
-- Name: SEQUENCE crawler_data_id_seq; Type: ACL; Schema: public; Owner: alexschneidman
--

GRANT SELECT,USAGE ON SEQUENCE public.crawler_data_id_seq TO sqa_downloader;


--
-- PostgreSQL database dump complete
--

