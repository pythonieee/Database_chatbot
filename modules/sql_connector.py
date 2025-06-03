import pymysql
import pandas as pd
def create_connection(host, user, password, database):
    """Create a connection to the MySQL database."""
 
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
        )
    return connection
        
    
def close_connection(connection):
    """Close the connection to the MySQL database."""
    
    connection.close()
    print("Connection to the database has been closed.")


def execute_query(connection, query):
    """Execute a SQL query on the connected database."""
    if connection is None :
        print("No valid database connection.")
        return None
    
    if  query.lower().strip().startswith("select") or query.lower().strip().startswith("show") or query.lower().strip().startswith("describe")or query.lower().strip().startswith("explain"):
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except pymysql.Error as err:
            print(f"Error executing query: {err}")
            return None
        finally:
            cursor.close()
    else :
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            connection.commit()
            print("Update executed successfully.")
        except pymysql.Error as err:
            print(f"Error executing update: {err}")
            connection.rollback()
        finally:
            cursor.close()
    


    

def fetch_all_tables(connection):
    """Fetch all tables in the connected database."""
    if connection is None:
        print("No valid database connection.")
        return None
    
    query = "SHOW TABLES"
    return [tables.values() for tables in execute_query(connection, query)]

def fetch_table_schema(connection, table_name):
    """Fetch the schema of a specific table in the connected database."""
    if connection is None:
        print("No valid database connection.")
        return None
    
    query = f"DESCRIBE {table_name}"
    return pd.DataFrame(execute_query(connection, query))

def fetch_database_info(connection):
    """Fetch information about the connected database."""
    if connection is None:
        print("No valid database connection.")
        return None
    
    query = "show databases ; "
    return pd.DataFrame(execute_query(connection, query))

