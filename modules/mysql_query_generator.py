import ollama
import sql_connector as sql

def generate_mysql_query(prompt: str,connection) -> str:   
    """Generate a MySQL query based on the provided prompt using Ollama."""
    response = ollama.chat(model="qwen2.5-coder", messages=[
    {
    'role': 'user',
    'content': f"Generate a MySQL query based on the following prompt: {prompt}"
    'The schema for the database is as follows:'
    'the tables in the database are:'
    f"{sql.fetch_all_tables(connection)}"
    'The schema for each table is as follows:'
    f"{[sql.fetch_table_schema(connection, table_name) for table_name in sql.fetch_all_tables(connection)]}"
    "The query should be a valid MySQL query that can be executed on the database. and autocorrect the table names and column names if they are not correct. If the query is not valid, return an error message indicating that the query is invalid."  
    'as you have the schema make sure that the query is valid and the table names and column names are correct.'
    ,
    },
  {
    'role': 'system',
    'content': 'You are a MySQL query generator. You will generate a MySQL query based on the user\'s request. The query should be formatted correctly and include a semicolon at the end. Do not include any additional text or explanations. The query should be formatted correctly and include a semicolon at the end.and only give me the query and nothing else not even a here is the query or any other text. Just the query itself.'  
    ,
  }
])
    query=response['message']['content']
    new_query = query.replace("sql", "")
    new_query = new_query.replace("```", "")
    return new_query.strip()  # Return the generated query without leading/trailing whitespace

 