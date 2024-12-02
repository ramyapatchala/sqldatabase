import streamlit as st
import sqlite3
import pandas as pd

# Function to get data from the SQLite database
def fetch_data(query):
    conn = sqlite3.connect('researchers.db')
    data = pd.read_sql(query, conn)
    conn.close()
    return data

# Streamlit app title
st.title('Syracuse University Researchers')

# Show researchers data
st.header('Researchers')
query_researchers = "SELECT * FROM researchers"
researchers_data = fetch_data(query_researchers)
st.dataframe(researchers_data)

# Show employment data
st.header('Employment Information')
query_employment = "SELECT * FROM employment"
employment_data = fetch_data(query_employment)
st.dataframe(employment_data)

# Show works data
st.header('Published Works')
query_works = "SELECT * FROM works"
works_data = fetch_data(query_works)
st.dataframe(works_data)
