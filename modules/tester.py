import sql_connector as sql
import mysql_query_generator as query_gen
import pandas as pd
import os
import pymysql


conncection=sql.create_connection("localhost","root","123","classicmodels")

while True:
    request= str(input("Enter your request: "))
    if f"{request.lower()}".strip() == "exit":
        print("Exiting the program.")
        break
    query = query_gen.generate_mysql_query(request)
    sql.execute_query(conncection, query)
    df = pd.DataFrame(sql.execute_query(conncection, query))
    
    if df.empty:
        print("No data found for the query.")
    else:
        print("Query executed successfully. Here are the results:")
        print(df)
    
sql.close_connection(conncection)

