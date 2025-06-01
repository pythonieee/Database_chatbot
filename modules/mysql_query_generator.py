import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
import sql_connector as sql
 

endpoint = "https://models.github.ai/inference"
model = "mistral-ai/mistral-medium-2505"
token = "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"
print(token)

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)
connector = sql.create_connection(host="localhost",
                                  user="root",
                                  password="123",
                                  database="classicmodels")

response = client.complete(
    messages=[
        SystemMessage("So you are an expert at SQL querries and you can generate SQL queries from natural language questions. and you are given a schema " 
                    "of a database and you can generate SQL queries from natural language questions . Here is the schema of the database: "    
      ),
        UserMessage(""),
    ],
    temperature=1.0,
    top_p=1.0,
    max_tokens=1000,
    model=model
)

print(response.choices[0].message.content)


