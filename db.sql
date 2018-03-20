--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: crawler_data; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE crawler_data (
    id integer NOT NULL,
    "time" timestamp with time zone DEFAULT now() NOT NULL,
    status boolean
);


ALTER TABLE public.crawler_data OWNER TO postgres;

--
-- Name: crawler_data_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE crawler_data_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.crawler_data_id_seq OWNER TO postgres;

--
-- Name: crawler_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE crawler_data_id_seq OWNED BY crawler_data.id;


--
-- Name: video_segment_data; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE video_segment_data (
    video_id character varying(100) NOT NULL,
    first_word_secs real,
    last_word_secs real,
    segment_start_secs real,
    segment_end_secs real,
    download_path character varying(1000),
    trimmed boolean
);


ALTER TABLE public.video_segment_data OWNER TO postgres;

--
-- Name: youtube_data; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE youtube_data (
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
    length character varying(10)
);


ALTER TABLE public.youtube_data OWNER TO postgres;

--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY crawler_data ALTER COLUMN id SET DEFAULT nextval('crawler_data_id_seq'::regclass);


--
-- Name: crawler_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY crawler_data
    ADD CONSTRAINT crawler_data_pkey PRIMARY KEY (id);


--
-- Name: video_segment_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY video_segment_data
    ADD CONSTRAINT video_segment_data_pkey PRIMARY KEY (video_id);


--
-- Name: youtube_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY youtube_data
    ADD CONSTRAINT youtube_data_pkey PRIMARY KEY (video_id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: crawler_data; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE crawler_data FROM PUBLIC;
REVOKE ALL ON TABLE crawler_data FROM postgres;
GRANT ALL ON TABLE crawler_data TO postgres;
GRANT ALL ON TABLE crawler_data TO sqa_downloader;


--
-- Name: crawler_data_id_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON SEQUENCE crawler_data_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE crawler_data_id_seq FROM postgres;
GRANT ALL ON SEQUENCE crawler_data_id_seq TO postgres;
GRANT SELECT,USAGE ON SEQUENCE crawler_data_id_seq TO sqa_downloader;


--
-- Name: video_segment_data; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE video_segment_data FROM PUBLIC;
REVOKE ALL ON TABLE video_segment_data FROM postgres;
GRANT ALL ON TABLE video_segment_data TO postgres;
GRANT ALL ON TABLE video_segment_data TO sqa_downloader;


--
-- Name: youtube_data; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE youtube_data FROM PUBLIC;
REVOKE ALL ON TABLE youtube_data FROM postgres;
GRANT ALL ON TABLE youtube_data TO postgres;
GRANT ALL ON TABLE youtube_data TO sqa_downloader;


--
-- PostgreSQL database dump complete
--

