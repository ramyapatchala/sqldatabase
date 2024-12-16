import pandas as pd
import sqlite3
import streamlit as st
import requests  # For handling PDF downloads

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
    publications = cursor.fetchall()
    
    # Convert titles to lowercase and process duplicates based on non-null work_url
    processed_publications = {}
    for pub in publications:
        work_title = pub[2].lower()  # work_title is in column index 2
        
        if work_title not in processed_publications:
            processed_publications[work_title] = pub
        else:
            existing_pub = processed_publications[work_title]
            if pub[3]:  # Replace with non-null work_url if available
                processed_publications[work_title] = pub

    sorted_publications = list(processed_publications.values())
    sorted_publications.sort(key=lambda x: x[2].lower())  # Sort by title
    return sorted_publications

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
    professor_page_num = 1
    items_per_page = 10
    professors = fetch_professors_by_name(professor_name_search, professor_page_num, items_per_page)
    
    if professors:
        for professor in professors:
            professor_name = professor[1]  # full_name is in column index 1
            professor_orcid_id = professor[0]  # orcid_id is in column index 0
            st.subheader(professor_name)

            publication_page_num = st.number_input(f'Select page number for publications of {professor_name}', min_value=1, step=1, key=f"pub_{professor_orcid_id}")
            publications = fetch_publications_by_professor(professor_orcid_id, publication_page_num, items_per_page)
            
            if publications:
                for pub in publications:
                    work_title = pub[2].lower()  # work_title is in column index 2
                    doi_url = pub[3] if pub[3] else "No DOI"  # DOI_URL is in column index 4
                    arxiv_url = pub[4] if pub[4] else "No URL"  # arxiv_url is in column index 3

                    with st.expander(f"📄 {work_title.capitalize()}"):
                        st.markdown(f"**Arxiv URL**: {arxiv_url}")
                        st.markdown(f"**DOI URL**: {doi_url}")

                        # Show "Download Paper" button if arxiv_url exists
                        if arxiv_url and "arxiv.org" in arxiv_url:
                            pdf_url = arxiv_url.replace('/abs/', '/pdf/')
                            if st.button(f"Download Paper", key=f"download_{pub[0]}"):  # Use unique key for each button
                                try:
                                    response = requests.get(pdf_url)
                                    if response.status_code == 200:
                                        file_name = f"{work_title.replace(' ', '_')}.pdf"
                                        with open(file_name, "wb") as f:
                                            f.write(response.content)
                                        st.success(f"Downloaded {file_name} successfully!")
                                    else:
                                        st.error("Failed to download the paper.")
                                except Exception as e:
                                    st.error(f"An error occurred: {str(e)}")
            else:
                st.write("No publications found for this professor.")
    else:
        st.write("No professors found with that name!")

# Department Search
department_name_search = st.text_input("Search by Department Name:")

if department_name_search:
    department_page_num = st.number_input('Select page number for professors', min_value=1, step=1, key=f"department_{department_name_search}")
    items_per_page = 10
    professors = fetch_professors_by_department(department_name_search, department_page_num, items_per_page)
    
    if professors:
        for professor in professors:
            professor_name = professor[1]
            email = professor[2]
            if email:
                st.write(f"**Name**: {professor_name}, **Email**: {email}")
            else:
                st.write(f"**Name**: {professor_name}")
    else:
        st.write("No professors found in that department!")

# Close the database connection
conn.close()
