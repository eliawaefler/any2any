
import psycopg2

def drop_tables_with_pattern(connection_string, pattern="_"):
    """
    Drops all tables in the database that contain a specific pattern (default is '_') in their name.

    Parameters:
        connection_string (str): The database connection string (e.g., in postgresql format).
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
        WHERE table_schema = 'public';
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
        connection_string (str): The database connection string (e.g., in postgresql format).
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
        connection_string (str): The database connection string (e.g., in postgresql format).
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
        connection_string (str): The database connection string (e.g., in postgresql format).
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

def delete_record(connection_string, table_name, column_name, value_to_delete):
    """
    Deletes a record from the specified table where the column matches the given value.

    Args:
        table_name (str): Name of the table.
        column_name (str): Name of the column to filter by.
        value_to_delete (str/int): Value of the record to delete.
        connection_string (str): Database connection parameters (host, database, user, password).

    Returns:
        str: Success message or error details.
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(connection_string)
        cur = conn.cursor()

        # Create the DELETE SQL query dynamically
        delete_query = f"DELETE FROM {table_name} WHERE {column_name} = %s"

        # Execute the DELETE query
        cur.execute(delete_query, (value_to_delete,))

        # Commit the changes
        conn.commit()

        # Return success message
        return f"{cur.rowcount} record(s) deleted from {table_name} where {column_name} = {value_to_delete}."

    except Exception as e:
        return f"Error occurred: {e}"

    finally:
        # Ensure resources are released
        if 'cursor' in locals() and cur is not None:
            cur.close()
        if 'connection' in locals() and conn is not None:
            conn.close()
