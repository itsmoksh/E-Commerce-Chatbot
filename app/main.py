import streamlit as st
from router import router
from faq import faq_chain, ingest_faq_data
from sql import sql_chain
from small_talk import talk_chain
from pathlib import Path
from google_sheet import log_feedback

st.title('E-Commerce Chatbot')

path = Path(__file__).parent.parent / "resources/faq_data.csv"
ingest_faq_data(path)


def check_query(query):
    route = router(query).name
    if route == 'faq':
        return faq_chain(query), route
    elif route == 'product_search':
        return sql_chain(query), route
    elif route == 'small_talk':
        return talk_chain(query), route
    else:
        return 'Route not implemented yet.', 'no_route'

welcome_msg = """👋 Welcome to our E-Commerce Chatbot! 

I can help you with:

- 🛍️ **Product Search**: Find products based on your requirements(Currently available for shoes)
- ❓ **FAQ**: Answer frequently asked questions about orders, shipping, returns, etc.
- 💬 **General Talk**: Have a casual conversation
Briefly explain your query for the above categories.
How can I assist you today?"""
# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
    st.markdown(welcome_msg)

if 'awaiting_route_selection' not in st.session_state:
    st.session_state['awaiting_route_selection'] = False

if 'pending_query' not in st.session_state:
    st.session_state['pending_query'] = None

if 'selected_route' not in st.session_state:
    st.session_state['selected_route'] = None

# Display chat history
for message in st.session_state['messages']:
    with st.chat_message(name=message['role']):
        st.markdown(message['content'])

# Handle route selection if awaiting
if st.session_state['awaiting_route_selection']:
    with st.chat_message(name='assistant'):
        st.write(
            "I apologize, but I couldn't understand your query correctly. Could you help me by selecting the appropriate category for your query?")

        col1, col2, col3, col4 = st.columns(4)

        if col1.button('General Talk'):
            st.session_state['selected_route'] = 'General_talk'
        elif col2.button('FAQ enquiry'):
            st.session_state['selected_route'] = 'faq'
        elif col3.button('Product Search'):
            st.session_state['selected_route'] = 'product_search'
        elif col4.button('None of these'):
            st.session_state['selected_route'] = 'None_of_these'

        # Display selected route
        if st.session_state['selected_route']:
            st.success(f"Selected: {st.session_state['selected_route']}")

        feedback_text = st.text_input("Any specific feedback about what went wrong?")

        if st.button("Submit feedback"):
            # Prepare feedback dictionary
            feedback_dict = {
                'query': st.session_state['pending_query'],
                'selected_route': st.session_state['selected_route'] if st.session_state[
                    'selected_route'] else 'Not selected',
                'suggestions': feedback_text
            }

            # Log the feedback
            log_feedback(feedback_dict)

            # Add apology message to chat
            apology_msg = "Thank you for your feedback! I apologize for not being able to help you properly this time. I'll use your feedback to improve."
            st.session_state['messages'].append({'role': 'assistant', 'content': apology_msg})

            # Reset the flags
            st.session_state['awaiting_route_selection'] = False
            st.session_state['selected_route'] = None
            st.rerun()

# Chat input
prompt = st.chat_input("Your Query here..")

if prompt:
    with st.chat_message(name='user'):
        st.markdown(prompt)
        st.session_state['messages'].append({'role': 'user', 'content': prompt})

    response, route = check_query(prompt)

    if route == 'no_route':
        st.session_state['awaiting_route_selection'] = True
        st.session_state['pending_query'] = prompt
        st.rerun()
    else:
        with st.chat_message(name='assistant'):
            if route == 'product_search':
                if len(response) != 0:
                    matches = "\n".join(response)
                else:
                    matches = 'Sorry, No product available of your requirements.'
                st.markdown(matches)
                st.session_state['messages'].append({'role': 'assistant', 'content': matches})
            else:
                st.markdown(response)
                st.session_state['messages'].append({'role': 'assistant', 'content': response})