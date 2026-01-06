import pandas as pd
from pathlib import Path
import chromadb
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
faq_path = Path(__file__).parent/"resources/faq_data.csv"
chroma_client = chromadb.Client()
collection_faq = 'faqs'
groq_client = Groq()
GROQ_MODEL = os.getenv('GROQ_MODEL')

def ingest_faq_data(path):
    if collection_faq not in [collection.name for collection in chroma_client.list_collections()]:
        print(f"Ingesting faq data into chromadb..")
        collection = chroma_client.get_or_create_collection(name = collection_faq)

        df = pd.read_csv(path)
        docs = df['question'].to_list()
        metadata = [{'Answer':meta}for meta in df['answer'].to_list()]
        ids = [f"id_{i}" for i in range(len(docs))]
        collection.add(
            documents = docs,
            metadatas = metadata,
            ids = ids
        )

    else:
        print(f"Collection {collection_faq} already exists")

def get_relevant_qa(query):
    collection = chroma_client.get_collection(collection_faq)
    result = collection.query(
        query_texts = query,
        n_results = 2
    )
    return result

def faq_chain(query):
    results = get_relevant_qa(query)
    context = ''.join([r.get('Answer')for r in results['metadatas'][0]])
    prompt = f'''Given the question and context below, generate the answer based on context only,
    and answer as you are telling to the user.
    If you don't find the answer inside the context, say I don't know.
    Do not make up things.
    
    Question: {query}
    Context: {context}'''

    completion = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}])

    return completion.choices[0].message.content
if __name__ == '__main__':
    ingest_faq_data(faq_path)
    query = "Which product I have ordered"
    print(faq_chain(query))

