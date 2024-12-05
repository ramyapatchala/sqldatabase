# Fetch all professor names for auto-complete
all_professors_query = """
    SELECT DISTINCT full_name
    FROM researchers
"""
all_professors_data = fetch_data(all_professors_query)

# Ensure that we handle any NaN or None values in the 'full_name' column
all_professors_data = all_professors_data.dropna(subset=['full_name'])

# Search for professor by name with auto-complete feature
professor_name_search = st.text_input("Enter professor name to search for:", "", help="Start typing to search for a professor's name")

if professor_name_search:
    # Filter professors by the search term
    filtered_professors = all_professors_data[all_professors_data['full_name'].str.contains(professor_name_search, case=False, na="")]

    professor_names = filtered_professors['full_name'].tolist()
    selected_professor_name = st.selectbox("Select Professor", options=professor_names, key="professor_select_box")

    # Fetch publications and other details for the selected professor
    query_publications = """
        SELECT researchers.full_name, publications.*
        FROM publications
        INNER JOIN researchers ON publications.orcid_id = researchers.orcid_id
        WHERE researchers.full_name = ?
        ORDER BY publications.publication_year DESC
    """
    publications_data = fetch_data(query_publications, params=(selected_professor_name,))

    if not publications_data.empty:
        st.markdown(f"### **Publications by Professor {selected_professor_name}:**")
        for _, row in publications_data.iterrows():
            # Expander for each publication with title, year, and publication URL
            with st.expander(f"📄 {row['publication_title'].lower()}", expanded=True):
                st.markdown(f"**Year:** {row['publication_year']}")
                if pd.notna(row['work_url']):
                    st.markdown(f"[Read more]({row['work_url']})")
    else:
        st.warning("No publications found for the selected professor.")
else:
    st.info("Start typing a professor's name to search for their publications.")
