from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder
from dotenv import load_dotenv
import os
from groq import Groq
load_dotenv()


GROQ_MODEL = os.getenv('GROQ_MODEL')
groq_client = Groq()
encoder = HuggingFaceEncoder(name="sentence-transformers/all-MiniLM-L6-v2",score_threshold=0.7)

faq = Route(
    name='faq',
    utterances=[
        "What is the return policy of the products?",
        "Do I get discount with the HDFC credit card?",
        "How can I track my order?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
        'Are there any ongoing sales or promotions?',
        'Can I cancel or modify my order after placing it?',
        'Do you offer international shipping?',
        'What should I do if I receive a damaged product?',
        'How do I use a promo code during checkout?'
    ]
)

product_search = Route(
    name = 'product_search',
    utterances = [
        'I want to buy nike shoes that have 50% discount.',
        'Are there any shoes under Rs. 3000?',
        'Do you have formal shoes in size 9?',
        'Are there any Puma shoes on sale?',
        'What is the price of puma running shoes?'
    ]
)
small_talk = Route(
    name = 'small_talk',
    utterances = ['How are you?',
                  "What's your name?",
                  "Are you a robot?",
                  "What do you do?",
                  "What are you?",
                  "What's the timing right now",
                  "Hello",
                  "Hello, how are you?",
                  "What's the time right now?"
                  ]
)
router = SemanticRouter(routes = [faq, product_search,small_talk],encoder = encoder,auto_sync="local")
system_prompt = """
You are an expert in finding the intent of the user's question. You are working in an E-commerce company which find out's the user intent and send it to the respective department for handling that query.
You will be provided with the user's query and based on that query you have to classify that into these three intents or routes.

1. FAQ: It includes all the queries that will be similar to the all customers who is using this E-commerce chatbot. This queries include general question's of an e-commerce company like
tracking the order, about the available promotions or discounts, refund policy, customer care, how many payment modes are accepted, etc. These queries are generally solved by customer support as it is common for all the user's.
2. Product search: Currently we only women shoes available. When the user wants to filter out products then only return this (especially shoes) because we have a sql database and that query will be converted to select statement further. So entertain only those types of queries only which can be used to retrieve products from db. 
2. Product Search: It contains all the queries who is retrieving different shoes(filtering), only shoes nothing else. Also that query will be considered as 'product search' which can be used to retrieve shoes from sql db. "ONLY SHOES, NO OTHER PRODUCTS"
3. Small Talk: They are the general queries which is generally asked at the beginning of the conversation with any chatbot, like hello, how are you, what services do you provide?,etc.
For Example: 
Query: What do you do? -> Intent: small_talk
Query: What are the available payment's method? -> Intent: faq
Query: Suggest me top 2 campus shoes. -? Intent: product_search

You have to classify in these three intents only -> small_talk, faq, product_search. 
If you are not confident enough, just say 'no_route'. Make sure to return these routes only, no reasoning, no preamble.

"""



def llm_classify(query):
    completion = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system",
             "content": system_prompt
             },
            {"role":'user',
             "content": query
             }
        ],
        max_tokens=1024
    )

    return completion.choices[0].message.content

def hybrid_intent_classification(query):
    route = router(query).name
    if route:
        return route
    else:
        return llm_classify(query)

if __name__ == '__main__':
    query = "Is cash on delivery available?"
    print(hybrid_intent_classification(query))
