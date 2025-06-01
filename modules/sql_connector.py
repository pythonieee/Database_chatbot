import pymysql
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
    if connection.is_connected():
        connection.close()
        print("Connection to the database has been closed.")
    else:
        print("Connection is already closed or was never established.")

def execute_query(connection, query):
    """Execute a SQL query on the connected database."""
    if connection is None :
        print("No valid database connection.")
        return None
    
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

def execute_update(connection, query):
    """Execute a SQL update query on the connected database."""
    if connection is None:
        print("No valid database connection.")
        return None
    
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