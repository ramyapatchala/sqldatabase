import streamlit as st
import pandas as pd
import sqlite3

# Function to fetch data from the database
def fetch_data(query, params=None):
    try:
        # Connect to the SQLite database (replace with your database connection)
        conn = sqlite3.connect('researchers.db')  # Replace with your actual database connection
        # Fetch the data with the provided query and parameters (if any)
        if params:
            data = pd.read_sql(query, conn, params=params)
        else:
            data = pd.read_sql(query, conn)
        conn.close()
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Fetching all professors data from the database
all_professors_query = """
    SELECT DISTINCT full_name
    FROM researchers
"""
all_professors_data = fetch_data(all_professors_query)

# Display the professors data with pagination
if not all_professors_data.empty:
    professors_per_page = 10
    total_pages = len(all_professors_data) // professors_per_page + (1 if len(all_professors_data) % professors_per_page != 0 else 0)
    
    page = st.slider('Select page', 1, total_pages, 1)  # Streamlit slider to select page number
    start_idx = (page - 1) * professors_per_page
    end_idx = start_idx + professors_per_page
    
    # Display professors for the current page
    professors_on_page = all_professors_data.iloc[start_idx:end_idx]
    st.write("Professors:", professors_on_page)
else:
    st.warning("No professors found in the database.")

# Search functionality for professors
professor_name_search = st.text_input("Search for a professor by name:")

# If the user enters a name to search
if professor_name_search:
    filtered_professors = all_professors_data[all_professors_data['full_name'].str.contains(professor_name_search, case=False)]
    
    if not filtered_professors.empty:
        # Display the filtered professor(s)
        st.write("Matching professors:", filtered_professors)
        
        # Fetching publications based on the professor's name
        professor_publications_query = """
            SELECT title, work_url
            FROM publications
            WHERE professor_name = ?
        """
        professor_publications = fetch_data(professor_publications_query, params=(professor_name_search,))
        
        if not professor_publications.empty:
            # Lowercasing the titles for case-insensitive comparison
            professor_publications['title'] = professor_publications['title'].str.lower()
            
            # Sort by title and filter rows where work_url is not null
            professor_publications = professor_publications.sort_values(by='title')
            professor_publications_with_url = professor_publications[professor_publications['work_url'].notnull()]
            
            # Display publications of the professor
            for _, row in professor_publications_with_url.iterrows():
                st.write(f"📄 {row['title']} [Link]({row['work_url']})")
        else:
            st.write("No publications found for the professor.")
    else:
        st.write("No matching professors found.")
