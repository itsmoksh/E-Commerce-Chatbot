import sqlite3
import pandas as pd
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
import re
import os

load_dotenv()
groq_client= Groq()
GROQ_MODEL = os.getenv('GROQ_MODEL')

db_path = Path(__file__).parent.parent/'resources/db.sqlite'

def run_query(query):
    if query.strip().upper().startswith('SELECT'):
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql(query, conn)
            return df

system_prompt = """You are an expert in understanding the database schema and generating SQL queries for a natural language question asked
pertaining to the data you have. The schema is provided in the schema tags. 
<schema> 
table: product 

fields: 
product_link - string (hyperlink to product)	
title - string (name of the product)	
brand - string (brand of the product)	
price - integer (price of the product in Indian Rupees)	
discount - float (discount on the product. 10 percent discount is represented as 0.1, 20 percent as 0.2, and such.)	
avg_rating - float (average rating of the product. Range 0-5, 5 is the highest.)	
total_ratings - integer (total number of ratings for the product)

</schema>
Make sure whenever you try to search for the brand name, the name can be in any case. 
So, make sure to use %LIKE% to find the brand in condition. Never use "ILIKE". 
Create a single SQL query for the question provided. 
The query should have all the fields in SELECT clause (i.e. SELECT *)

Just the SQL query is needed, nothing more. Always provide the SQL in between the <SQL></SQL> tags."""


def generate_sql_query(question):
    completion = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system",
             "content": system_prompt
             },
            {"role":'user',
             "content": question
             }
        ],
        temperature=  0.2,
        max_tokens=1024
    )

    return completion.choices[0].message.content

def sql_chain(question):
    query = generate_sql_query(question)
    pattern = '<SQL>(.*?)<\/SQL>'
    matches = re.findall(pattern,query,re.DOTALL)
    if len(matches)==0:
        return 'LLM is not able to generate SQL Query..'

    sql_query = matches[0].strip().replace('\n',' ')
    print(sql_query)
    response = run_query(sql_query)
    if response is None:
        return "Sorry, there's a problem executing sql query"

    context = response.to_dict(orient='records')
    return context

if __name__ == '__main__':
    question = 'Suggest me top 2 nike shoes'
    response = sql_chain(question)
    print(response)

