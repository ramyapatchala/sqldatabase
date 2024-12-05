import streamlit as st
import sqlite3
import pandas as pd

# Function to get data from the SQLite database
def fetch_data(query, params=None):
    conn = sqlite3.connect("researchers.db")
    data = pd.read_sql(query, conn, params=params)
    conn.close()
    return data

# Streamlit app title and styling
st.set_page_config(page_title="Syracuse University Researchers", layout="wide")
st.markdown(
    """
    <style>
    h1 {
        font-size: 36px !important;
    }
    h2, h3, h4, h5 {
        font-size: 24px !important;
    }
    .st-expander {
        font-size: 18px !important;
    }
    .professor-name {
        font-size: 28px !important;
        font-weight: bold !important;
        color: #2C3E50 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("🔍 Syracuse University Researchers")
st.markdown("Search for professors, view their employment details, and explore their published works.")

# Input box to search by department
department_name = st.text_input("Enter the department name to search:", "")

# Fetch professors based on department search
if department_name:
    query_departments = """
        SELECT DISTINCT employment.*, researchers.full_name, researchers.email
        FROM employment
        INNER JOIN researchers ON employment.orcid_id = researchers.orcid_id
        WHERE department LIKE ?
    """
    department_data = fetch_data(query_departments, params=(f"%{department_name}%",))
    
    if not department_data.empty:
        # Pagination for department professors
        items_per_page = 10
        total_items = len(department_data)
        total_pages = (total_items - 1) // items_per_page + 1

        # Initialize the page number in session state
        if "department_page" not in st.session_state:
            st.session_state.department_page = 1

        # Allow user to change page number
        page = st.number_input(
            "Page", min_value=1, max_value=total_pages, step=1, value=st.session_state.department_page
        )
        st.session_state.department_page = page  # Update session state with the current page number

        # Calculate indices for pagination
        start_idx = (st.session_state.department_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_data = department_data.iloc[start_idx:end_idx]

        st.markdown(f"### Professors in the Department: {department_name}")

        # Display the paginated list of professors
        for _, row in paginated_data.iterrows():
            st.markdown(f"👩‍🏫 **Professor:** {row['full_name']}  \n📧 **Email:** {row['email']}")
        
        # Display pagination info at the bottom
        st.markdown("---")
        st.markdown(f"**Page {st.session_state.department_page} of {total_pages}**")
    else:
        st.warning("No professors found in the specified department.")
