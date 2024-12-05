import streamlit as st
import sqlite3
import pandas as pd

# Function to get data from the SQLite database
def fetch_data(query, params=None):
    conn = sqlite3.connect("researchers.db")
    data = pd.read_sql(query, conn, params=params)
    conn.close()
    return data

# Streamlit app configuration
st.set_page_config(page_title="Syracuse University Researchers", layout="wide")
st.markdown(
    """
    <style>
    h1 { font-size: 36px !important; }
    h2, h3, h4, h5 { font-size: 24px !important; }
    .st-expander { font-size: 18px !important; }
    .stMarkdown { font-size: 18px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("🔍 Syracuse University Researchers")
st.markdown("Search for professors, view their employment details, and explore their published works.")

# Search options: by name or department
search_option = st.radio("Search by:", ["Professor's Name", "Department"])
search_input = st.text_input(f"Enter the {search_option.lower()}:")

# Search by department
if search_option == "Department" and search_input:
    query_departments = """
        SELECT r.full_name, r.email, e.department, e.role, e.employment 
        FROM employment e 
        JOIN researchers r ON e.orcid_id = r.orcid_id 
        WHERE e.department LIKE ?
    """
    department_data = fetch_data(query_departments, params=(f"%{search_input}%",))
    if not department_data.empty:
        st.markdown(f"### Professors in the Department: {search_input}")
        for _, row in department_data.iterrows():
            with st.expander(f"👩‍🏫 Professor: {row['full_name']}", expanded=False):
                st.markdown(f"📧 **Email:** {row['email']}")
                st.markdown(f"🏢 **Organization:** {row['employment']}")
                st.markdown(f"**Role:** {row['role']}")
    else:
        st.warning("No professors found in the specified department.")

# Search by professor's name
elif search_option == "Professor's Name" and search_input:
    query_researchers = "SELECT * FROM researchers WHERE full_name LIKE ?"
    researchers_data = fetch_data(query_researchers, params=(f"%{search_input}%",))

    if not researchers_data.empty:
        professor = researchers_data.iloc[0]
        with st.expander(f"👩‍🏫 Professor: {professor['full_name']}", expanded=True):
            st.markdown(f"📧 **Email:** {professor['email']}")

            # Employment information
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

            # Published works
            query_works = "SELECT * FROM works WHERE orcid_id = ? ORDER BY work_title ASC"
            works_data = fetch_data(query_works, params=(professor["orcid_id"],))
            if not works_data.empty:
                st.markdown("### 📚 Published Works")

                # Pagination for published works
                items_per_page = 5
                total_items = len(works_data)
                total_pages = (total_items - 1) // items_per_page + 1

                # Display publications
                page = st.number_input(
                    "Page", min_value=1, max_value=total_pages, step=1, value=1, key="pagination"
                )
                start_idx = (page - 1) * items_per_page
                end_idx = start_idx + items_per_page
                paginated_data = works_data.iloc[start_idx:end_idx]

                for _, row in paginated_data.iterrows():
                    with st.expander(f"📄 {row['work_title']}", expanded=False):
                        st.write(
                            f"**DOI:** [{row['DOI_URL']}]({row['DOI_URL']})"
                            if row["DOI_URL"] != "N/A"
                            else "No DOI available"
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
    st.info(f"Please enter a {search_option.lower()} to search.")
