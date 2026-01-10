import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from pathlib import Path
import streamlit as st

# cred= Path(__file__).parent.parent/"resources/credentials.json"
scopes = [
    'https://www.googleapis.com/auth/spreadsheets'
]

creds = Credentials.from_service_account_info(st.secrets['google_service_account'],scopes=scopes)
client = gspread.authorize(creds)

sheet_id = '1-GMp9JotffVArc1-hzD9-W9XoWIVmoWuMXt3kxFS2iI'
workbook= client.open_by_key(sheet_id)
sheet = workbook.worksheet('Sheet1')

def log_feedback(feedback):
    query = feedback['query']
    route = feedback['selected_route']
    suggestion = feedback['suggestions']
    sheet.append_row([datetime.now().isoformat(),query,route,suggestion])
