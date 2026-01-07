import streamlit as st
from router import router
from faq import faq_chain, ingest_faq_data
from sql import sql_chain
from small_talk import talk_chain
from pathlib import Path
st.title('E-Commerce Chatbot')

path = Path(__file__).parent.parent/"resources/faq_data.csv"
ingest_faq_data(path)

def check_query(query):
    route = router(query).name
    if route == 'faq':
        return faq_chain(query)
    elif route == 'product_search':
        return sql_chain(query)
    elif route == 'small_talk':
        return talk_chain(query)
    else:
        return 'Route not implemented yet.'
prompt = st.chat_input("Your Query here..")

if 'messages' not in  st.session_state:
    st.session_state['messages'] = []

for message in st.session_state['messages']:
    with st.chat_message(name = message['role']):
        st.markdown(message['content'])


if prompt:
    with st.chat_message(name='user'):
        st.markdown(prompt)
        st.session_state['messages'].append({'role':'user', 'content':prompt})
    response = check_query(prompt)
    with st.chat_message(name = 'assistant'):
        st.markdown(response)
        st.session_state['messages'].append({'role':'assistant', 'content':response})

