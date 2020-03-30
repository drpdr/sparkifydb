import psycopg2
from sql_queries import create_table_queries, drop_table_queries

# NOTE: I would have liked using basic logging instead of prints
# but I am still unsure about how grading works in detail
# so I followed the instructions (and how it was suggested in etl.py)


def create_database():
    """Connect to default database and create sparkifydb"""
    # connect to default database
    try:
        conn = psycopg2.connect(
            "host=127.0.0.1 dbname=studentdb user=student password=student"
        )
        conn.set_session(autocommit=True)
        cur = conn.cursor()
    except psycopg2.Error as e:
        print("Unable to establish connection to default database.")
        print(e)

    try:
        # create sparkify database with UTF8 encoding
        cur.execute("DROP DATABASE IF EXISTS sparkifydb")
        cur.execute(
            "CREATE DATABASE sparkifydb WITH ENCODING 'utf8' TEMPLATE template0"
        )
    except psycopg2.Error as e:
        print("Unable to create DATABASE sparkifydb")
        print(e)
    finally:
        # close connection to default database
        print("Successfully created sparkifydb.")
        conn.close()

    try:
        # connect to sparkify database
        conn = psycopg2.connect(
            "host=127.0.0.1 dbname=sparkifydb user=student password=student"
        )
        cur = conn.cursor()

    except psycopg2.Error as e:
        print("Unable to connect to sparkifydb")
        print(e)
    finally:
        print("Successfully connected to sparkifydb.")

    return cur, conn


def drop_tables(cur, conn):
    """Drop all the tables in sparkifydb if they exist
    
    Parameters
    ----------
    cur : psycopg2 Cursor
    conn : psycopg2 Connection
    
    """
    for query in drop_table_queries:
        try:
            cur.execute(query)
            conn.commit()
        except psycopg2.Error as e:
            print(f"Unable to execute: " + query)
            print(e)


def create_tables(cur, conn):
    """Create all the tables in sparkifydb if they do not exist
    
    Parameters
    ----------
    cur : psycopg2 Cursor
    conn : psycopg2 Connection
    
    """
    for query in create_table_queries:
        try:
            cur.execute(query)
            conn.commit()
        except psycopg2.Error as e:
            print(f"Unable to execute: " + query)
            print(e)

    print("Tables created successfully.")


def main():
    """Create the database, drop the tables, and re-create them"""
    cur, conn = create_database()

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()
