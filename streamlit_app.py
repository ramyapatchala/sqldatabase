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

# Input box to search for a professor's name
professor_name = st.text_input("Enter the name of the professor:", "")

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
        st.markdown(f"### Professors in the Department: {department_name}")
        for _, row in department_data.iterrows():
            st.markdown(f"👩‍🏫 **Professor:** {row['full_name']}  \n📧 **Email:** {row['email']}")
    else:
        st.warning("No professors found in the specified department.")

# Fetch details of professor based on the name
if professor_name:
    query_researchers = "SELECT * FROM researchers WHERE full_name LIKE ?"
    researchers_data = fetch_data(query_researchers, params=(f"%{professor_name}%",))

    if not researchers_data.empty:
        professor = researchers_data.iloc[0]
        st.markdown(
            f"<div class='professor-name'>👩‍🏫 Professor: {professor['full_name']}</div>",
            unsafe_allow_html=True,
        )
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
            # Lowercase titles and prioritize rows with non-null work_url
            works_data["work_title"] = works_data["work_title"].str.lower()
            works_data = (
                works_data.sort_values(by=["work_title", "work_url"], ascending=[True, False])
                .drop_duplicates(subset="work_title", keep="first")
            )

            st.markdown("### 📚 Published Works")

            # Pagination for published works
            items_per_page = 10
            total_items = len(works_data)
            total_pages = (total_items - 1) // items_per_page + 1

            # Initialize the page number in session state
            if "page" not in st.session_state:
                st.session_state.page = 1

            # Allow user to change page number
            page = st.number_input(
                "Page", min_value=1, max_value=total_pages, step=1, value=st.session_state.page
            )
            st.session_state.page = page  # Update session state with the current page number

            # Calculate indices for pagination
            start_idx = (st.session_state.page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            paginated_data = works_data.iloc[start_idx:end_idx]

            # Display paginated publications
            for _, row in paginated_data.iterrows():
                with st.expander(f"📄 {row['work_title']}", expanded=False):
                    st.markdown(
                        f"**DOI:** [{row['DOI_URL']}]({row['DOI_URL']})" if row["DOI_URL"] != "N/A" else "**DOI:** No DOI available"
                    )
                    st.markdown(
                        f"**Work URL:** [{row['work_url']}]({row['work_url']})" if row["work_url"] != "N/A" else "**Work URL:** No URL available"
                    )

            # Display pagination info at the bottom
            st.markdown("---")
            st.markdown(f"**Page {st.session_state.page} of {total_pages}**")
        else:
            st.write("No publications available.")
    else:
        st.warning("Professor not found. Please try a different name.")
else:
    st.info("Please enter a professor's name to search.")
