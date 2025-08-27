try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ModuleNotFoundError:
    import sqlite3
    print("Warning: pysqlite3 not found. Using standard sqlite3, which may cause issues with ChromaDB.")

import sqlite3
import pandas as pd
from pathlib import Path
from groq import Groq    
import os
import re
import streamlit as st
from faq_handling import add_chat_history




file_path = Path(__file__).parent if "__file__" in locals() else Path.cwd()
db_path = str(file_path/"resources/product.db")

def run_query(query):
    if query.strip().upper().startswith("SELECT"):
        with sqlite3.connect(db_path) as connector:
            df = pd.read_sql_query(query, connector)
            return df
        


def generate_sql_query(question,  GROQ_API_KEY, GROQ_MODEL):
    sql_prompt = f''' 
You are an expert in generating SQL queries from natural language questions for an e-commerce product database. Your task is to evaluate the input query and either generate a single, complete SQL query based on the provided schema or return a message prompting the user to ask a relevant question.

<schema>
table: product
fields:
product_link - string (hyperlink to product)
title - string (name of the product)
brand - string (brand of the product)
price - integer (price of the product in Indian Rupees)
discount - float (discount on the product; 10 percent is 0.1, 20 percent is 0.2, etc.)
avg_rating - float (average rating of the product, range 0-5, 5 is highest)
total_ratings - integer (total number of ratings for the product)
</schema>


Instructions:
1.  Generate a SQL query to retrieve product information. Always include a **LIMIT 5** clause to restrict the number of results to five, unless the user explicitly requests more.
2.  If the input query is relevant to the product table (e.g., mentions products, brands, prices, discounts, ratings), generate a SQL query using SELECT * to include all fields. Use case-insensitive LIKE for brand searches (e.g., brand LIKE '%nike%'). Ensure the query is valid and matches the schema.
3.  If the input query is irrelevant (e.g., random letters, unrelated topics like weather), return only the message: "Please ask a question related to products, such as brand, price, or discount."
4.  Return the result in the format:
    -   For valid queries: Enclose the SQL query in <SQL> tags (e.g., <SQL>SELECT * FROM product WHERE brand LIKE '%nike%'</SQL>).
    -   For invalid queries: Enclose the message in <MESSAGE> tags (e.g., <MESSAGE>Please ask a question related to products, such as brand, price, or discount</MESSAGE>).
5.  Do not provide any additional text or explanations outside the specified tags.
        '''
    completion = Groq(api_key = GROQ_API_KEY).chat.completions.create(
        model = GROQ_MODEL,
        messages = [
            {
                "role": "system",
                "content" : sql_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ],
        temperature = 0.2
    )
    answer = completion.choices[0].message.content
    return answer


def data_comprehensive(question, context, GROQ_API_KEY, GROQ_MODEL):
    comprehension_prompt = ''' 
    You are an expert at crafting concise, natural language responses based solely on the provided data, tailored to the question's context. You will receive a Question: and Data: as a list of dictionaries from a database query. Answer using only the provided data in a simple, conversational tone, referencing column names (title, price, discount, avg_rating, product_link) where needed.

    For questions requesting product details (e.g., listing products by brand, price, or discount), format the response as a numbered list of up to 5 products, sorted by avg_rating (highest first). Include each product’s title, price in Indian Rupees, discount (as a percentage, e.g., 30% for 0.3), rating (from avg_rating), and product link. Example:
    1. Air Max: Rs. 5999 (20% off), Rating: 4.5, Link: http://example.com/nike1
    2. Ultraboost: Rs. 7999 (10% off), Rating: 4.2, Link: http://example.com/adidas
    3. Ultraboost: Rs. 7999 (10% off), Rating: 4.2, Link: http://example.com/adidas

    For other questions (e.g., average rating, total products), provide a concise answer using the data (e.g., "The average rating is 4.3"). If the data is an empty list, respond with "No products found matching the criteria." If the data is invalid, respond with "I don’t have enough information to answer that."

    Input format:
    Question: <question>
    Data: <list of dictionaries, e.g., [{"title": "Air Max", "price": 5999, "discount": 0.2, "avg_rating": 4.5, "product_link": "http://example.com/nike1"}]>

    Output only the response in plain text, using the specified format for product-related questions or a natural sentence for others.
    '''

    completion = Groq(api_key = GROQ_API_KEY).chat.completions.create(
    model = GROQ_MODEL,
    messages = [
        {
            "role": "system",
            "content" : comprehension_prompt
        },
        {
            "role": "user",
            "content": f"question: {question} Data: {context} "
        }
    ],
        temperature = 0.2
    )
    answer = completion.choices[0].message.content
    return answer


def sql_chain_with_history(question, GROQ_API_KEY, GROQ_MODEL, session_id = "default"):
    """SQL chain with chat history support"""
    
    # Generate SQL query
    sql_query = generate_sql_query(question, GROQ_API_KEY, GROQ_MODEL)
   
    pattern = "<SQL>(.*?)</SQL>"
    matches = re.findall(pattern, sql_query, re.DOTALL)
    
    if len(matches) == 0:
        # No SQL query generated, return the message
        pattern_msg = "<MESSAGE>(.*?)</MESSAGE>"
        msg_matches = re.findall(pattern_msg, sql_query, re.DOTALL)
        if msg_matches:
            response = msg_matches[0].strip()
        else:
            response = "Sorry, I couldn't generate a query for your question."
        return response
    
    # Execute the SQL query
    response = run_query(matches[0].strip())
    if response is None:
        error_msg = "Sorry, there was a problem executing SQL query"
        return error_msg
    
    # Generate comprehensive response
    context = response.to_dict(orient = "records")
    answer = data_comprehensive(question, context, GROQ_API_KEY, GROQ_MODEL)
    
    # Update history
    add_chat_history(session_id, "user", question)
    add_chat_history(session_id, "assistant", answer)
    
    return answer


# if __name__ == "__main__":
#       sql_query = generate_sql_query("List top 5 puma shoes products?", GROQ_API_KEY)
#       answer = sql_chain_with_history("List top 5 puma shoes products?",GROQ_API_KEY)
#       print(sql_query)
