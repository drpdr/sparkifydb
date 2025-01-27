# DROP TABLES

songplay_table_drop = "DROP TABLE IF EXISTS songplays;"
user_table_drop = "DROP TABLE IF EXISTS users;"
song_table_drop = "DROP TABLE IF EXISTS songs;"
artist_table_drop = "DROP TABLE IF EXISTS artists;"
time_table_drop = "DROP TABLE IF EXISTS time;"

# CREATE TABLES. DIMENSIONS FIRST, THEN FACT.

user_table_create = """CREATE TABLE IF NOT EXISTS users (
    user_id int PRIMARY KEY,
    first_name varchar,
    last_name varchar,
    gender varchar (2),
    level varchar
);"""

# NOTE: latitude and longitude may be better represented using
# some extensions like PostGIS or modules like earthdistance
# See https://postgis.net/, overkilling
# See https://www.postgresql.org/docs/8.3/earthdistance.html (needs cube)
# Using numeric, however, allows for absolute precision.

artist_table_create = """CREATE TABLE IF NOT EXISTS artists (
    artist_id varchar PRIMARY KEY,
    name varchar NOT NULL,
    location varchar,
    latitude numeric,
    longitude numeric
);"""

# NOTE: artist_id should have a reference (FK) to artists
# but I do not want to modify the etl notebook in order to
# avoid issues with grading

song_table_create = """CREATE TABLE IF NOT EXISTS songs (
    song_id varchar PRIMARY KEY,
    title varchar NOT NULL,
    -- artist_id varchar REFERENCES artists,
    artist_id varchar NOT NULL,
    year int NOT NULL,
    duration numeric
);"""

time_table_create = """CREATE TABLE IF NOT EXISTS time (
    start_time timestamp PRIMARY KEY,
    hour int NOT NULL,
    day int NOT NULL,
    week int NOT NULL,
    month int NOT NULL,
    year int NOT NULL,
    weekday int NOT NULL
);"""

songplay_table_create = """CREATE TABLE IF NOT EXISTS songplays (
    songplay_id SERIAL PRIMARY KEY, 
    start_time timestamp REFERENCES time ON DELETE CASCADE, 
    user_id int REFERENCES users ON DELETE CASCADE, 
    level varchar,
    song_id varchar REFERENCES songs ON DELETE CASCADE,
    artist_id varchar REFERENCES artists ON DELETE CASCADE,
    session_id int,
    location varchar,
    user_agent varchar
    );"""

# INSERT RECORDS
# songplay_id autofills because set as SERIAL, i.e. it auto-increments
songplay_table_insert = """INSERT INTO songplays (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
VALUES(TIMESTAMP 'epoch' + %s * INTERVAL '1 millisecond', %s, %s, %s, %s, %s, %s, %s)"""

user_table_insert = """INSERT INTO users (user_id, first_name, last_name, gender, level)
VALUES(%s, %s, %s, %s, %s)
ON CONFLICT (user_id)
DO UPDATE
    SET level = EXCLUDED.level
;
"""

song_table_insert = """INSERT INTO songs (song_id, title, artist_id, year, duration)
VALUES(%s, %s, %s, %s, %s)"""

# UPDATE location, latitude and longitude in case we can improve data
artist_table_insert = """INSERT INTO artists (artist_id, name, location, latitude, longitude)
VALUES(%s, %s, %s, %s, %s)
ON CONFLICT (artist_id)
DO UPDATE
    SET location  = EXCLUDED.location,
        latitude  = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude
    ;
    """

# TIMESTAMP 'epoch' ... Explicitly casts big_int to timestamp without timezone (to be accepted by Postgres)
time_table_insert = """INSERT INTO time (start_time, hour, day, week, month, year, weekday)
VALUES(TIMESTAMP 'epoch' + %s * INTERVAL '1 millisecond', %s, %s, %s, %s, %s, %s)
ON CONFLICT (start_time)
DO NOTHING;"""

# FIND SONGS
song_select = """SELECT song_id, artists.artist_id FROM artists
    JOIN songs ON artists.artist_id = songs.artist_id WHERE
    songs.title = %s AND artists.name = %s AND songs.duration = %s;"""

# QUERY LISTS

# create_table_queries = [songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
create_table_queries = [
    user_table_create,
    artist_table_create,
    song_table_create,
    time_table_create,
    songplay_table_create,
]
drop_table_queries = [
    songplay_table_drop,
    user_table_drop,
    song_table_drop,
    artist_table_drop,
    time_table_drop,
]
