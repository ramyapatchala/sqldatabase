import pandas as pd
import sqlite3
import streamlit as st

# Connect to SQLite database
conn = sqlite3.connect("researchers.db")
cursor = conn.cursor()

# Streamlit interface for Professor and Department Search
st.title("University Researcher and Publications Search")

# Function to fetch filtered professors by name from the database
def fetch_professors_by_name(professor_name_search, page_num, items_per_page):
    query = f"""
        SELECT * 
        FROM researchers
        WHERE full_name LIKE ? 
        LIMIT ? OFFSET ?
    """
    offset = (page_num - 1) * items_per_page
    cursor.execute(query, ('%' + professor_name_search + '%', items_per_page, offset))
    return cursor.fetchall()

# Function to fetch publications for a specific professor
def fetch_publications_by_professor(professor_orcid_id, page_num, items_per_page):
    query = f"""
        SELECT * 
        FROM works
        WHERE orcid_id = ? 
        LIMIT ? OFFSET ?
    """
    offset = (page_num - 1) * items_per_page
    cursor.execute(query, (professor_orcid_id, items_per_page, offset))
    return cursor.fetchall()

# Function to fetch professors by department
def fetch_professors_by_department(department_name_search, page_num, items_per_page):
    query = f"""
        SELECT * 
        FROM researchers
        WHERE orcid_id IN (
            SELECT orcid_id 
            FROM employment 
            WHERE department LIKE ?
        )
        LIMIT ? OFFSET ?
    """
    offset = (page_num - 1) * items_per_page
    cursor.execute(query, ('%' + department_name_search + '%', items_per_page, offset))
    return cursor.fetchall()

# Professor Search
professor_name_search = st.text_input("Search by Professor's Name:")

if professor_name_search:
    # Pagination setup for professors
    professor_page_num = st.number_input('Select page number for professors', min_value=1, step=1)
    items_per_page = 10

    # Fetch professors matching the name search
    professors = fetch_professors_by_name(professor_name_search, professor_page_num, items_per_page)
    
    if professors:
        for professor in professors:
            professor_name = professor[1]  # full_name is in column index 1
            professor_orcid_id = professor[0]  # orcid_id is in column index 0
            st.subheader(professor_name)

            # Pagination setup for publications
            publication_page_num = st.number_input(f'Select page number for publications of {professor_name}', min_value=1, step=1, key=f"pub_{professor_orcid_id}")
            
            # Fetch publications for this professor
            publications = fetch_publications_by_professor(professor_orcid_id, publication_page_num, items_per_page)
            
            if publications:
                for pub in publications:
                    work_title = pub[2].lower()  # work_title is in column index 2
                    work_url = pub[3] if pub[3] else "No URL"  # work_url is in column index 3
                    doi_url = pub[4] if pub[4] else "No DOI"  # DOI_URL is in column index 4

                    # Display work with expander
                    with st.expander(f"📄 {work_title.capitalize()}"):
                        st.markdown(f"**Work URL**: {work_url}")
                        st.markdown(f"**DOI URL**: {doi_url}")
            else:
                st.write("No publications found for this professor.")
    else:
        st.write("No professors found with that name!")

# Department Search
department_name_search = st.text_input("Search by Department Name:")

if department_name_search:
    # Pagination setup for professors in a department
    department_page_num = st.number_input('Select page number for professors', min_value=1, step=1, key=f"department_{department_name_search}")
    items_per_page = 10

    # Fetch professors by department
    professors = fetch_professors_by_department(department_name_search, department_page_num, items_per_page)
    
    if professors:
        for professor in professors:
            professor_name = professor[1]  # full_name is in column index 1
            email = professor[2] if professor[2] else "No email"  # email is in column index 2
            st.write(f"**Name**: {professor_name}, **Email**: {email}")
    else:
        st.write("No professors found in that department!")

# Close the database connection
conn.close()
