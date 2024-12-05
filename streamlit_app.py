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


# -------------------- 1. Professor's Publications Search ----------------------

# Input box to search for professor by name
professor_name_search = st.text_input("Search for a professor by name:")

if professor_name_search:
    # Fetching publications based on the professor's name
    professor_publications_query = """
        SELECT title, work_url, doi_url, professor_name
        FROM publications
        WHERE professor_name = ?
    """
    professor_publications = fetch_data(professor_publications_query, params=(professor_name_search,))
    
    if not professor_publications.empty:
        # Lowercasing the titles for case-insensitive comparison
        professor_publications['title'] = professor_publications['title'].str.lower()
        
        # Pagination for publications (10 per page)
        publications_per_page = 10
        total_pages = len(professor_publications) // publications_per_page + (1 if len(professor_publications) % publications_per_page != 0 else 0)
        
        page = st.slider('Select page for publications', 1, total_pages, 1)  # Streamlit slider for pagination
        start_idx = (page - 1) * publications_per_page
        end_idx = start_idx + publications_per_page
        
        # Display publications for the current page
        publications_on_page = professor_publications.iloc[start_idx:end_idx]
        st.write(f"### Publications by {professor_name_search}:")
        
        for _, row in publications_on_page.iterrows():
            with st.expander(f"📄 {row['title']}"):
                st.write(f"**Work URL**: [Link]({row['work_url']})")
                st.write(f"**DOI URL**: [Link]({row['doi_url']})")
                st.write(f"**Professor Name**: {row['professor_name']}")
    else:
        st.write("No publications found for the professor.")

# -------------------- 2. Professor's List by Department ----------------------

# Input box to search for professors by department
department_search = st.text_input("Search for professors by department:")

if department_search:
    # Fetching professors based on the department name
    department_professors_query = """
        SELECT full_name, email, department
        FROM researchers
        WHERE department = ?
    """
    department_professors = fetch_data(department_professors_query, params=(department_search,))
    
    if not department_professors.empty:
        # Pagination for professors (10 per page)
        professors_per_page = 10
        total_pages = len(department_professors) // professors_per_page + (1 if len(department_professors) % professors_per_page != 0 else 0)
        
        page = st.slider('Select page for professors', 1, total_pages, 1)  # Streamlit slider for pagination
        start_idx = (page - 1) * professors_per_page
        end_idx = start_idx + professors_per_page
        
        # Display professors for the current page
        professors_on_page = department_professors.iloc[start_idx:end_idx]
        st.write(f"### Professors in {department_search} Department:")
        
        for _, row in professors_on_page.iterrows():
            if pd.notnull(row['email']):
                st.write(f"**Professor**: {row['full_name']} | **Email**: {row['email']}")
            else:
                st.write(f"**Professor**: {row['full_name']} | **Email**: Not available")
    else:
        st.write(f"No professors found in the {department_search} department.")

