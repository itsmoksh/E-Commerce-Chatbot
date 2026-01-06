from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
groq_client = Groq()
GROQ_MODEL = os.getenv('GROQ_MODEL')

system_prompt = '''
You are an assistant at an E-commerce store, which is an expert in giving answers to user questions initially, before they ask about the product information or general faq questions. The user can ask questions about you, about the job you do, exchange greetings, names, etc. You have to answer the user as they are talking to the bot, which introduces them to the services provided or handles general questions. 
If the user asks about the work you do, or the services provided by the chatbot, then you can tell ‘We are here to handle your FAQs and suggest the products you need. 
Examples:

How are you? → Hello, I am good. How can I assist you?
What’s your name? → I am an E-commerce chatbot to assist you with your shopping.
Do not write too big sentences, and be concise.
'''

def talk_chain(query):
    completion = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "system", "content": system_prompt},
                  {'role': "user", "content": query}]
    )

    return completion.choices[0].message.content

if __name__ == '__main__':
    query = "Hello, What's you name?"
    response = talk_chain(query)
    print(response)