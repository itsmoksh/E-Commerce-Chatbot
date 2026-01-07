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

comprehension_prompt = """You are an expert in understanding the context of the question and replying based on the data pertaining to the question provided. You will be provided with Question: and Data:. The data will be in the form of an array or a dataframe or dict. Reply based on only the data provided as Data for answering the question asked as Question. Do not write anything like 'Based on the data' or any other technical words. Just a plain simple natural language response.
The Data would always be in context to the question asked. For example is the question is “What is the average rating?” and data is “4.3”, then answer should be “The average rating for the product is 4.3”. So make sure the response is curated with the question and data. Make sure to note the column names to have some context, if needed, for your response.
There can also be cases where you are given an entire dataframe in the Data: field. Always remember that the data field contains the answer of the question asked. All you need to do is to always reply in the following format when asked about a product: 
Produt title, price in indian rupees, discount, and rating, and then product link. Take care that all the products are listed in list format, one line after the other. Not as a paragraph.
For example:
1. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
2. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
3. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>

"""

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

def data_compression(question,context):
    completion = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system",
             "content": comprehension_prompt
             },
            {"role":'user',
             "content": f'Question: {question} Data: {context}'
             }
        ],
        temperature=  0.2,
        max_completion_tokens=32768
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
    return data_compression(question,context)



if __name__ == '__main__':
    question = 'Give me top 3 puma shoes'
    response = sql_chain(question)
    print(response)

