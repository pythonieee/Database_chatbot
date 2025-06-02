import ollama


def generate_mysql_query(prompt: str) -> str:   
    """Generate a MySQL query based on the provided prompt using Ollama."""
    response = ollama.chat(model="qwen2.5-coder", messages=[
    {
    'role': 'user',
    'content': f"Generate a MySQL query based on the following prompt: {prompt}"
    ,
    },
  {
    'role': 'system',
    'content': 'You are a MySQL query generator. You will generate a MySQL query based on the user\'s request. The query should be formatted correctly and include a semicolon at the end. Do not include any additional text or explanations. The query should be formatted correctly and include a semicolon at the end.and only give me the query and nothing else not even a here is the query or any other text. Just the query itself.',
  }
])


    query=response['message']['content']
    new_query = query.replace("sql", "")
    new_query = new_query.replace("```", "")
    print(new_query)
    return new_query.strip()  # Return the generated query without leading/trailing whitespace

 