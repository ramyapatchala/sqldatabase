import streamlit as st
import sqlite3
import pandas as pd


# Function to get data from the SQLite database
def fetch_data(query, params=None):
    conn = sqlite3.connect('researchers.db')
    data = pd.read_sql(query, conn, params=params)
    conn.close()
    return data


# Streamlit app title and styling
st.set_page_config(page_title="Syracuse University Researchers", layout="wide")
st.title("🔍 Syracuse University Researchers")
st.markdown("Search for professors, view their employment details, and explore their published works.")


# Input box to search for a professor's name
professor_name = st.text_input("Enter the name of the professor:", "")

# If the professor name is provided
if professor_name:
    # Query to fetch the professor's details (researcher table)
    query_researchers = "SELECT * FROM researchers WHERE full_name LIKE ?"
    researchers_data = fetch_data(query_researchers, params=(f"%{professor_name}%",))

    if not researchers_data.empty:
        # Display the professor's details
        professor = researchers_data.iloc[0]
        st.subheader(f"Professor: {professor['full_name']}")
        st.markdown(f"📧 **Email:** {professor['email']}")

        # Display Professor's Employment Information
        query_employment = "SELECT * FROM employment WHERE orcid_id = ?"
        employment_data = fetch_data(query_employment, params=(professor["orcid_id"],))
        if not employment_data.empty:
            st.markdown("### 🏢 Employment Information")
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
        query_works = "SELECT * FROM works WHERE orcid_id = ? ORDER BY work_title ASC"
        works_data = fetch_data(query_works, params=(professor["orcid_id"],))
        if not works_data.empty:
            st.markdown("### 📚 Published Works")

            # Pagination for published works
            items_per_page = 10
            total_items = len(works_data)
            total_pages = (total_items - 1) // items_per_page + 1
            page = st.number_input(
                "Page", min_value=1, max_value=total_pages, step=1, value=1, key="pagination"
            )

            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            paginated_data = works_data.iloc[start_idx:end_idx]

            for _, row in paginated_data.iterrows():
                st.write(f"**Title:** {row['work_title']}")
                st.write(
                    f"**DOI:** [{row['DOI_URL']}]({row['DOI_URL']})" if row["DOI_URL"] != "N/A" else "No DOI available"
                )
                st.write(
                    f"**Work URL:** [{row['work_url']}]({row['work_url']})"
                    if row["work_url"] != "N/A"
                    else "No URL available"
                )
                st.write("---")

            st.markdown(f"**Page {page} of {total_pages}**")
        else:
            st.write("No publications available.")
    else:
        st.warning("Professor not found. Please try a different name.")
else:
    st.info("Please enter a professor's name to search.")
