-- dwh.activity definition

-- Drop table

-- DROP TABLE dwh.activity;

CREATE TABLE dwh.activity (
	activity_id int8 NOT NULL,
	athlete_id int4 NOT NULL,
	act_name varchar(100) NULL,
	activity_type varchar(100) NULL,
	workout_type varchar(50) NULL,
	external_id varchar(200) NULL,
	upload_id int4 NULL,
	start_date date NULL,
	start_date_local date NULL,
	timezone varchar(100) NULL,
	utc_offset numeric NULL,
	start_lat numeric NULL,
	start_lng numeric NULL,
	end_lat numeric NULL,
	end_lng numeric NULL,
	location_city int4 NULL,
	location_state int4 NULL,
	location_country int4 NULL,
	achievement_count int4 NULL,
	kudos_count int4 NULL,
	comment_count int4 NULL,
	athlete_count int4 NULL,
	photo_count int4 NULL,
	trainer bool NULL,
	commute bool NULL,
	manual bool NULL,
	private bool NULL,
	visibility varchar(50) NULL,
	flagged bool NULL,
	gear_id varchar(100) NULL,
	description varchar(1000) NULL,
	CONSTRAINT activity_pk PRIMARY KEY (activity_id)
);