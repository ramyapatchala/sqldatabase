import pandas as pd
import sqlite3
import streamlit as st

# Connect to SQLite database
conn = sqlite3.connect("researchers.db")
cursor = conn.cursor()

# Fetch data from tables
def fetch_data(query):
    return pd.read_sql(query, conn)

# Fetch all professors
all_professors_query = "SELECT * FROM researchers"
all_professors_data = fetch_data(all_professors_query)

# Fetch all works (publications)
all_works_query = "SELECT * FROM works"
all_works_data = fetch_data(all_works_query)

# Streamlit interface for Professor Search
st.title("University Researcher and Publications Search")

# Professor Search
professor_name_search = st.text_input("Search by Professor's Name:")

if professor_name_search:
    # Filter professors by name (case insensitive)
    filtered_professors = all_professors_data[all_professors_data['full_name'].str.contains(professor_name_search, case=False)]
    if not filtered_professors.empty:
        st.write(f"Found {len(filtered_professors)} professors matching '{professor_name_search}'")

        # Pagination for publications
        page_num = st.number_input('Select page number for publications', min_value=1, step=1)
        items_per_page = 10
        start_idx = (page_num - 1) * items_per_page
        end_idx = start_idx + items_per_page

        # Display filtered works for professor
        for _, row in filtered_professors.iterrows():
            professor_name = row['full_name']
            st.subheader(professor_name)

            # Fetch publications for this professor
            professor_works = all_works_data[all_works_data['orcid_id'] == row['orcid_id']]
            professor_works = professor_works.iloc[start_idx:end_idx]  # Paginate

            for _, work_row in professor_works.iterrows():
                work_title = work_row['work_title'].lower()  # Lowercase titles
                work_url = work_row['work_url'] if pd.notnull(work_row['work_url']) else "No URL"
                doi_url = work_row['DOI_URL'] if pd.notnull(work_row['DOI_URL']) else "No DOI"

                # Display work with expander
                with st.expander(f"📄 {work_title.capitalize()}"):
                    st.markdown(f"**Work URL**: {work_url}")
                    st.markdown(f"**DOI URL**: {doi_url}")

    else:
        st.write("No professors found with that name!")

# Department Search
department_name_search = st.text_input("Search by Department Name:")

if department_name_search:
    # Filter professors by department
    filtered_professors = all_professors_data[all_professors_data['full_name'].str.contains(department_name_search, case=False)]
    if not filtered_professors.empty:
        st.write(f"Found {len(filtered_professors)} professors in '{department_name_search}' department")

        # Pagination for professors
        page_num = st.number_input('Select page number for professors', min_value=1, step=1)
        items_per_page = 10
        start_idx = (page_num - 1) * items_per_page
        end_idx = start_idx + items_per_page

        # Display professors with email (if not null)
        for _, row in filtered_professors.iloc[start_idx:end_idx].iterrows():
            professor_name = row['full_name']
            email = row['email'] if pd.notnull(row['email']) else "No email"
            st.write(f"**Name**: {professor_name}, **Email**: {email}")
    else:
        st.write("No professors found in that department!")

# Close the database connection
conn.close()
