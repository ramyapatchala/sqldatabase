import streamlit as st
import sqlite3
import pandas as pd


# Function to get data from the SQLite database
def fetch_data(query, params=None):
    conn = sqlite3.connect('researchers.db')
    data = pd.read_sql(query, conn, params=params)
    conn.close()
    return data


# Streamlit app title
st.title('Syracuse University Researchers')

# Input box to search for a professor's name
professor_name = st.text_input('Enter the name of the professor:', '')

# If the professor name is provided
if professor_name:
    # Query to fetch the professor's details (researcher table)
    query_researchers = "SELECT * FROM researchers WHERE full_name LIKE ?"
    researchers_data = fetch_data(query_researchers, params=(f'%{professor_name}%',))

    if not researchers_data.empty:
        # Display the professor's details
        professor = researchers_data.iloc[0]
        st.subheader(f"Professor: {professor['full_name']}")
        st.markdown(f"**Email:** {professor['email']}")

        # Display Professor's Employment Information
        query_employment = "SELECT * FROM employment WHERE orcid_id = ?"
        employment_data = fetch_data(query_employment, params=(professor['orcid_id'],))
        if not employment_data.empty:
            st.markdown("### Employment Information")
            for _, row in employment_data.iterrows():
                st.write(f"**Organization:** {row['employment']}")
                st.write(f"**Department:** {row['department']}")
                st.write(f"**Role:** {row['role']}")
                st.write(f"**Start Year:** {row['start_year']}")
                st.write(f"**End Year:** {row['end_year']}")
                st.write("---")
        else:
            st.write("No employment information available.")

        # Display Professor's Published Works
        query_works = "SELECT * FROM works WHERE orcid_id = ?"
        works_data = fetch_data(query_works, params=(professor['orcid_id'],))
        if not works_data.empty:
            st.markdown("### Published Works")
            for _, row in works_data.iterrows():
                st.write(f"**Title:** {row['work_title']}")
                st.write(
                    f"**DOI:** [{row['DOI_URL']}]({row['DOI_URL']})" if row['DOI_URL'] != 'N/A' else "No DOI available")
                st.write(f"**Work URL:** [{row['work_url']}]({row['work_url']})" if row[
                                                                                        'work_url'] != 'N/A' else "No URL available")
                st.write("---")
        else:
            st.write("No publications available.")

    else:
        st.write("Professor not found. Please try a different name.")
else:
    st.write("Please enter a professor's name to search.")
