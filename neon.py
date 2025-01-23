import uuid

import psycopg2
import os

def drop_tables_with_pattern(connection_string, pattern="_"):
    """
    Drops all tables in the database that contain a specific pattern (default is '_') in their name.

    Parameters:
        connection_string (str): The database connection string (e.g., in PostgreSQL format).
        pattern (str, optional): The pattern to search for in table names (default is '_').

    Returns:
        list: A list of table names that were dropped.
    """
    try:
        # Establish database connection
        conn = psycopg2.connect(connection_string)
        cur = conn.cursor()

        # Query to get all table names with the specified pattern in their name
        query = f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name LIKE '%{pattern}%';
        """
        cur.execute(query)
        tables = cur.fetchall()

        # Drop each table
        dropped_tables = []
        for (table_name,) in tables:
            if pattern in table_name:
                drop_query = f"DROP TABLE IF EXISTS {table_name} CASCADE;"
                cur.execute(drop_query)
                dropped_tables.append(table_name)

        # Commit the changes
        conn.commit()

        # Close resources
        cur.close()
        conn.close()

        return dropped_tables
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def create_table(connection_string, table_name, columns):
    """
    Creates a new table in the database if it does not already exist.

    Parameters:
        connection_string (str): The database connection string (e.g., in PostgreSQL format).
        table_name (str): The name of the table to create.
        columns (dict): A dictionary where keys are column names and values are data types.

    Returns:
        str: A success message if the table is created successfully, or an error message if something goes wrong.
    """
    try:
        # Establish database connection
        conn = psycopg2.connect(connection_string)
        cur = conn.cursor()

        # Construct column definitions
        column_definitions = ', '.join([f"{col} {data_type}" for col, data_type in columns.items()])

        # Formulate SQL query
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"

        # Execute query
        cur.execute(query)
        conn.commit()

        # Close resources
        cur.close()
        conn.close()

        return f"Table '{table_name}' created successfully."
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)

def write_to_db(connection_string, table, data):
    """
    Inserts data into a specified table in the database.

    Parameters:
        connection_string (str): The database connection string (e.g., in PostgreSQL format).
        table (str): The name of the table where data should be inserted.
        data (dict): A dictionary where keys are column names and values are the respective data to insert.

    Returns:
        str: "success" if the data is inserted successfully, or an error message if something goes wrong.
    """
    try:
        # Establish database connection
        conn = psycopg2.connect(connection_string)
        cur = conn.cursor()

        # Prepare query components
        columns = ', '.join(data.keys())
        values = [data[col] for col in data.keys()]
        placeholders = ', '.join(['%s'] * len(data))

        # Formulate SQL query
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        # Execute query
        cur.execute(query, values)
        conn.commit()

        # Close resources
        if cur:
            cur.close()
        if conn:
            conn.close()

        return "success"
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)

def read_db(connection_string, table, condition='1=1', printout=False):
    """
    Reads and retrieves data from a specified table in the database based on a condition.

    Parameters:
        connection_string (str): The database connection string (e.g., in PostgreSQL format).
        table (str): The name of the table to read data from.
        condition (str, optional): A SQL condition to filter rows (default is '1=1', which retrieves all rows).
        printout (bool, optional): If True, prints each row to the console (default is False).

    Returns:
        list: A list of tuples containing the rows that match the condition, or an error message if something goes wrong.
    """
    try:
        # Establish database connection
        conn = psycopg2.connect(connection_string)
        cur = conn.cursor()

        # Formulate and execute SQL query
        cur.execute(f"SELECT * FROM {table} WHERE {condition}")
        rows = cur.fetchall()

        # Print rows if requested
        if printout:
            for row in rows:
                print(row)

        # Close resources
        if cur:
            cur.close()
        if conn:
            conn.close()

        return rows
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)

def test_create_tables():

    table_name = "users"
    columns = {
        "guid": "UUID PRIMARY KEY",  # Unique identifier
        "username": "VARCHAR(100) NOT NULL",  # Username (required)
        "email": "VARCHAR(255) NOT NULL",  # Email (required)
        "pw_hash": "VARCHAR(255) NOT NULL",  # Password hash (required)
        "first_name": "VARCHAR(100)",  # First name (optional)
        "last_name": "VARCHAR(100)",  # Last name (optional)
        "salt": "VARCHAR(255) NOT NULL",  # Salt for password hashing (required)
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"  # Auto-timestamp
    }

    """
    table_name = "rules"
    columns = {
        "guid": "SERIAL PRIMARY KEY",  # Unique identifier
        "rule": "VARCHAR(1000)", # the rule to execute (NAME)
        "rule_info": "VARCHAR(1000)",
        "created_by": "VARCHAR(100)",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
    """
    print(create_table(connection_string, table_name, columns))

def test_write():
    new_user = {
        "guid": str(uuid.uuid4()),
        "username": "e2",
        "email": "elia.w2aefler@gmail.com",  # Email (required)
        "pw_hash": "1234",  # Password hash (required)
        "first_name": "Elia",  # First name (optional)
        "last_name": "WAE",  # Last name (optional)
        "salt": "1234",  # Salt for password hashing (required)
    }
    write_to_db(connection_string, "users", new_user)


if __name__ == "__main__":
    #CONN_STRING = os.environ["NEON_KEY"] # streamlit secret
    connection_string = os.environ["NEON_URL_any"] # for local


    # to reset users tables:
    dropped = drop_tables_with_pattern(connection_string, pattern="_")
    print(f"Dropped tables: {dropped}")
    #test_create_tables()
    #test_write()
    #users_db = read_db(connection_string, "users", printout=False)
    #print(users_db)
