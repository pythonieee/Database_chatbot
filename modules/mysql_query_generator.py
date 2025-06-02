import ollama
import time 
t1 = time.time()
response = ollama.chat(model='mistral', messages=[
  {
    'role': 'user',
    'content': 'Generate a MySQL query to get all the records in the customers section '
    '. The query should be formatted correctly and include a semicolon at the end.and only give me the query and nothing else not even a here is the query or any other text. Just the query itself.',
  },
])
t2 = time.time()
print(f"Response time: {t2 - t1} seconds")
print(response['message']['content'])