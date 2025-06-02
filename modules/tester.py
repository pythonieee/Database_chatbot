import sql_connector as sql
import pandas as pd
import os
import pymysql


conncection=sql.create_connection("localhost","root","123","classicmodels")

response = sql.fetch_table_schema(conncection, "customers")
if response is not None:
    print("Table Schema:")
    for row in response:
        print(row)

##lets make it in a form of a dataframe
df = pd.DataFrame(response)
print("\nDataFrame:")
print(df)

response = sql.execute_query(conncection, "SELECT * FROM customers LIMIT 5")
df2 = pd.DataFrame(response)
print("\nDataFrame with Query Results:")
print(df2)

connection2 = pymysql.connect(
        host="localhost",
        user="root",
        password="123",
        cursorclass=pymysql.cursors.DictCursor
        )

response = sql.fetch_database_info(connection2)



print("\nDatabase Info:")
print(response)