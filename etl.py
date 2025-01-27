import os
import glob
import psycopg2
import pandas as pd
from sql_queries import user_table_insert, artist_table_insert
from sql_queries import song_table_insert, time_table_insert, songplay_table_insert
from sql_queries import song_select


def process_song_file(cur, filepath):
    """Process a single song json file and populate the artists table with one record
    
    Parameters
    ----------
    cur : psycopg2 Cursor
    filepath : absolute path of the file
    """
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = song_data = df[
        ["song_id", "title", "artist_id", "year", "duration"]
    ].values[0]
    cur.execute(song_table_insert, song_data)

    # insert artist record
    artist_data = df[
        [
            "artist_id",
            "artist_name",
            "artist_location",
            "artist_latitude",
            "artist_longitude",
        ]
    ].values[0]
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """Process a single log json file and populate users and songplays tables.
    It filters data by NextSong action only.
    
    Parameters
    ----------
    cur : psycopg2 Cursor
    filepath : absolute path of the file
    """
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df["page"] == "NextSong"]

    # convert timestamp column to datetime
    t = pd.to_datetime(df.ts, unit="ms")

    # insert time data records
    time_data = (
        df.ts,
        t.dt.hour,
        t.dt.day,
        t.dt.week,
        t.dt.month,
        t.dt.year,
        t.dt.weekday,
    )
    column_labels = ("timestamp", "hour", "day", "week", "month", "year", "weekday")
    time_df = pd.DataFrame.from_dict(dict(zip(column_labels, time_data)))

    for _, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[["userId", "firstName", "lastName", "gender", "level"]]

    # insert user records
    for _, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for _, row in df.iterrows():

        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()

        song_id, artist_id = results if results else (None, None)

        # insert songplay record
        songplay_data = (
            row.ts,
            row.userId,
            row.level,
            song_id,
            artist_id,
            row.sessionId,
            row.location,
            row.userAgent,
        )
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """Process json files in accordance to the given func.

    Parameters
    ----------
    cur : psycopg2 Cursor
    filepath : absolute path of the file
    func : python function to process datafiles
    """
    # get all files matching extension from directory
    all_files = []
    for root, _, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, "*.json"))
        for f in files:
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print("{} files found in {}".format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        print(f"Processing {datafile} ...")
        func(cur, datafile)
        conn.commit()
        print("{}/{} files processed.".format(i, num_files))


def main():
    # connect to sparkifydb as student
    conn = psycopg2.connect(
        "host=127.0.0.1 dbname=sparkifydb user=student password=student"
    )
    cur = conn.cursor()

    # process songs
    process_data(
        cur,
        conn,
        filepath=os.path.join(os.path.dirname(__file__), "data/song_data"),
        func=process_song_file,
    )

    # process logs
    process_data(
        cur,
        conn,
        filepath=os.path.join(os.path.dirname(__file__), "data/log_data"),
        func=process_log_file,
    )

    conn.close()


if __name__ == "__main__":
    main()
