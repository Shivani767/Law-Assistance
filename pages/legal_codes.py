import streamlit as st
import pandas as pd
from legal_data import (
    ipc_sections, it_act_sections, mv_act_sections,
    crpc_sections, cpc_sections, evidence_act_sections,
    get_offense_details, search_legal_data
)

st.set_page_config(
    page_title="Legal Codes - Indian Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

st.markdown("""
<style>
    /* Global Styles */
    @keyframes fadeInPage {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
        color: #2c3e50;
        transition: all 0.3s ease;
        animation: fadeInPage 0.8s ease-out;
    }

    /* Section Styles */
    @keyframes sectionEntrance {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }

    .section-card {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 51, 102, 0.1);
        animation: sectionEntrance 0.6s ease-out;
        transition: all 0.3s ease;
    }

    .section-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }

    /* Search Results */
    @keyframes resultSlideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .search-result {
        padding: 15px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.5);
        margin-bottom: 15px;
        border: 1px solid rgba(0, 51, 102, 0.1);
        animation: resultSlideIn 0.4s ease-out;
        transition: all 0.3s ease;
    }

    .search-result:hover {
        background: rgba(255, 255, 255, 0.8);
        transform: scale(1.02);
    }

    /* Loading State */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.7; }
        100% { transform: scale(1); opacity: 1; }
    }

    .loading-spinner {
        text-align: center;
        padding: 20px;
        animation: pulse 1.5s ease-in-out infinite;
    }

    .loading-spinner::after {
        content: '';
        display: inline-block;
        width: 30px;
        height: 30px;
        border: 3px solid rgba(0, 51, 102, 0.1);
        border-radius: 50%;
        border-top-color: #003366;
        animation: spin 1s linear infinite;
    }
</style>
""", unsafe_allow_html=True)

st.title("Legal Codes Reference")
st.markdown("### Comprehensive reference for Indian Legal Codes")

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Back to Home"):
    st.switch_page("app.py")

# Search functionality
st.markdown("## Search Legal Codes")
search_query = st.text_input("Search by keyword or section number", 
                           placeholder="e.g., theft, murder, cyber, 302, bail, evidence")

if search_query:
    with st.spinner("Searching..."):
        search_results = search_legal_data(search_query)
        
        has_results = False
        for act, results in search_results.items():
            if results:
                has_results = True
                st.markdown(f"### {act} Results")
                for result in results:
                    if act == "Precedents":
                        st.markdown(f"- **{result['case_name']}** ({result['citation']}) - *{result['summary'][:100]}...*")
                    else:
                        st.markdown(f"- **Section {result['section']}**: {result['title']}")
        
        if not has_results:
            st.info("No matching results found. Try different keywords or check the full codes below.")

# Code type selector
code_type = st.selectbox(
    "Select Code Type",
    ["Criminal Laws", "Procedural Laws", "Evidence Law", "Special Laws", "Civil Laws"]
)

# Display search tips
st.markdown("""
**Search Tips:**
- Use specific terms like 'murder', 'theft', or 'cybercrime'
- Search by section numbers like '302' or '420'
- Try related terms like 'bail', 'arrest', or 'evidence'
- Include act names like 'IPC' or 'IT Act' for focused results
""")

if code_type == "Criminal Laws":
    tab1, tab2 = st.tabs(["Indian Penal Code (IPC)", "IT Act"])
    
    with tab1:
        # Existing IPC tab content
        st.markdown("## Indian Penal Code (IPC)")
        st.markdown("""
        The Indian Penal Code (IPC) is the official criminal code of India. It covers all substantive aspects of criminal law.
        Originally enacted in 1860 during the British Raj, it has undergone numerous amendments but remains the main criminal code.
        """)
        
        # Search in IPC sections
        ipc_results = []
        for section, title in ipc_sections.items():
            if search_query.lower() in section.lower() or search_query.lower() in title.lower():
                ipc_results.append({"Act": "IPC", "Section": section, "Title": title})
        
        # Search in IT Act sections
        it_results = []
        for section, title in it_act_sections.items():
            if search_query.lower() in section.lower() or search_query.lower() in title.lower():
                it_results.append({"Act": "IT Act", "Section": section, "Title": title})
        
        # Combine and display results
        all_results = ipc_results + it_results
        
        if all_results:
            st.success(f"Found {len(all_results)} matching sections")
            for result in all_results:
                with st.expander(f"{result['Act']} Section {result['Section']}: {result['Title']}"):
                    section_details = get_offense_details(result['Section'], result['Act'])
                    if section_details:
                        if 'rights' in section_details:
                            st.markdown("**Rights of the Defendant:**")
                            for right in section_details['rights']:
                                st.markdown(f"- {right}")
                        
                        if 'bail_info' in section_details:
                            st.markdown("**Bail Information:**")
                            bail_info = section_details['bail_info']
                            if "bailable" in str(bail_info).lower():
                                st.success("This is a **bailable** offense.")
                            else:
                                st.error("This is a **non-bailable** offense.")
        else:
            st.info("No matching sections found. Try different keywords or check your spelling.")
        
        # Section details
        st.markdown("### Section Details")
        selected_section = st.selectbox("Select a section for details", options=list(ipc_sections.keys()), key="ipc_detail")
        
        if selected_section:
            section_details = get_offense_details(selected_section, "IPC")
            if section_details:
                st.markdown(f"#### Section {selected_section}: {section_details.get('title', '')}")
                
                st.markdown("**Rights of the Defendant:**")
                for right in section_details.get("rights", []):
                    st.markdown(f"- {right}")
                
                st.markdown("**Bail Information:**")
                bail_info = section_details.get("bail_info", {})
                if "bailable" in str(bail_info).lower():
                    st.success("This is a **bailable** offense.")
                else:
                    st.error("This is a **non-bailable** offense.")
                
                # Display examples of similar offenses if available
                if bail_info and "examples" in bail_info:
                    st.markdown("**Similar Offenses:**")
                    for example in bail_info.get("examples", []):
                        st.markdown(f"- {example}")
    
    with tab2:
        # Existing IT Act tab content
        st.markdown("## Information Technology Act")
        st.markdown("""
        The Information Technology Act, 2000 (IT Act) provides legal framework for electronic governance and 
        electronic commerce in India. It also deals with cybercrime and digital evidence.
        """)
        
        # Convert sections to DataFrame for display
        it_df = pd.DataFrame([
            {"Section": section, "Title": title}
            for section, title in it_act_sections.items()
        ])
        
        # Allow filtering by keywords
        it_filter = st.text_input("Filter IT Act sections", placeholder="e.g., hacking, privacy", key="it_filter")
        
        if it_filter:
            filtered_df = it_df[
                it_df["Title"].str.contains(it_filter, case=False) | 
                it_df["Section"].str.contains(it_filter, case=False)
            ]
            if not filtered_df.empty:
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.info("No matching sections found.")
        else:
            st.dataframe(it_df, use_container_width=True)
        
        # Section details
        st.markdown("### Section Details")
        selected_it_section = st.selectbox("Select a section for details", options=list(it_act_sections.keys()), key="it_detail")
        
        if selected_it_section:
            section_details = get_offense_details(selected_it_section, "IT Act")
            if section_details:
                st.markdown(f"#### Section {selected_it_section}: {section_details.get('title', '')}")
                
                st.markdown("**Rights of the Defendant:**")
                for right in section_details.get("rights", []):
                    st.markdown(f"- {right}")
                
                st.markdown("**Bail Information:**")
                bail_info = section_details.get("bail_info", {})
                if "bailable" in str(bail_info).lower():
                    st.success("This is a **bailable** offense.")
                else:
                    st.error("This is a **non-bailable** offense.")

elif code_type == "Procedural Laws":
    tab1, tab2 = st.tabs(["Criminal Procedure Code (CrPC)", "Civil Procedure Code (CPC)"])
    
    with tab1:
        st.markdown("## Criminal Procedure Code (CrPC)")
        st.markdown("""
        The Code of Criminal Procedure (CrPC) is the main legislation on procedure for administration of criminal law in India. 
        It provides the machinery for investigation of crime, apprehension of suspected criminals, collection of evidence, 
        determination of guilt or innocence, and the imposition of suitable punishment on the guilty.
        """)
        
        # Convert sections to DataFrame for display
        crpc_df = pd.DataFrame([
            {"Section": section, "Title": title}
            for section, title in crpc_sections.items()
        ])
        
        # Allow filtering by keywords
        crpc_filter = st.text_input("Filter CrPC sections", placeholder="e.g., arrest, bail, trial", key="crpc_filter")
        
        if crpc_filter:
            filtered_df = crpc_df[
                crpc_df["Title"].str.contains(crpc_filter, case=False) | 
                crpc_df["Section"].str.contains(crpc_filter, case=False)
            ]
            if not filtered_df.empty:
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.info("No matching sections found.")
        else:
            st.dataframe(crpc_df, use_container_width=True)
        
        # Section details
        st.markdown("### Section Details")
        selected_crpc_section = st.selectbox("Select a section for details", options=list(crpc_sections.keys()), key="crpc_detail")
        
        if selected_crpc_section:
            section_details = get_offense_details(selected_crpc_section, "CrPC")
            if section_details:
                st.markdown(f"#### Section {selected_crpc_section}: {section_details.get('title', '')}")
    
    with tab2:
        st.markdown("## Civil Procedure Code (CPC)")
        st.markdown("""
        The Code of Civil Procedure (CPC) is a procedural law that provides the machinery for civil proceedings in India. 
        It consolidates and amends the laws relating to the procedure of the Courts of Civil Judicature in India.
        """)
        
        # Convert sections to DataFrame for display
        cpc_df = pd.DataFrame([
            {"Section": section, "Title": title}
            for section, title in cpc_sections.items()
        ])
        
        # Allow filtering by keywords
        cpc_filter = st.text_input("Filter CPC sections", placeholder="e.g., suit, decree, appeal", key="cpc_filter")
        
        if cpc_filter:
            filtered_df = cpc_df[
                cpc_df["Title"].str.contains(cpc_filter, case=False) | 
                cpc_df["Section"].str.contains(cpc_filter, case=False)
            ]
            if not filtered_df.empty:
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.info("No matching sections found.")
        else:
            st.dataframe(cpc_df, use_container_width=True)
        
        # Section details
        st.markdown("### Section Details")
        selected_cpc_section = st.selectbox("Select a section for details", options=list(cpc_sections.keys()), key="cpc_detail")
        
        if selected_cpc_section:
            section_details = get_offense_details(selected_cpc_section, "CPC")
            if section_details:
                st.markdown(f"#### Section {selected_cpc_section}: {section_details.get('title', '')}")

elif code_type == "Evidence Law":
    st.markdown("## Indian Evidence Act")
    st.markdown("""
    The Indian Evidence Act, 1872 contains a set of rules and allied issues governing admissibility of evidence in Indian Courts. 
    It deals with facts, evidence, examination of witnesses, confessions, oaths, affirmations, documentary evidence and how to determine 
    the admissibility of evidence in court.
    """)
    
    # Convert sections to DataFrame for display
    evidence_df = pd.DataFrame([
        {"Section": section, "Title": title}
        for section, title in evidence_act_sections.items()
    ])
    
    # Allow filtering by keywords
    evidence_filter = st.text_input("Filter Evidence Act sections", placeholder="e.g., witness, confession, document", key="evidence_filter")
    
    if evidence_filter:
        filtered_df = evidence_df[
            evidence_df["Title"].str.contains(evidence_filter, case=False) | 
            evidence_df["Section"].str.contains(evidence_filter, case=False)
        ]
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("No matching sections found.")
    else:
        st.dataframe(evidence_df, use_container_width=True)
    
    # Section details
    st.markdown("### Section Details")
    selected_evidence_section = st.selectbox("Select a section for details", options=list(evidence_act_sections.keys()), key="evidence_detail")
    
    if selected_evidence_section:
        section_details = get_offense_details(selected_evidence_section, "Evidence Act")
        if section_details:
            st.markdown(f"#### Section {selected_evidence_section}: {section_details.get('title', '')}")

elif code_type == "Special Laws":
    st.markdown("## Motor Vehicles Act")
    st.markdown("""
    The Motor Vehicles Act, 1988 is an Act of the Parliament of India that regulates motor vehicles
    in India. The Act provides in detail the legislative provisions regarding licensing of drivers and conductors,
    registration of motor vehicles, control of motor vehicles through permits, special provisions relating to
    state transport undertakings, traffic regulation, insurance, liability, offenses and penalties, etc.
    """)
    
    # Convert sections to DataFrame for display
    mv_df = pd.DataFrame([
        {"Section": section, "Title": title}
        for section, title in mv_act_sections.items()
    ])
    
    # Allow filtering by keywords
    mv_filter = st.text_input("Filter MV Act sections", placeholder="e.g., driving, alcohol", key="mv_filter")
    
    if mv_filter:
        filtered_df = mv_df[
            mv_df["Title"].str.contains(mv_filter, case=False) | 
            mv_df["Section"].str.contains(mv_filter, case=False)
        ]
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("No matching sections found.")
    else:
        st.dataframe(mv_df, use_container_width=True)
    
    # Section details
    st.markdown("### Section Details")
    selected_mv_section = st.selectbox("Select a section for details", options=list(mv_act_sections.keys()), key="mv_detail")
    
    if selected_mv_section:
        section_details = get_offense_details(selected_mv_section, "MV Act")
        if section_details:
            st.markdown(f"#### Section {selected_mv_section}: {section_details.get('title', '')}")
            
            st.markdown("**Rights of the Defendant:**")
            for right in section_details.get("rights", []):
                st.markdown(f"- {right}")
            
            st.markdown("**Bail Information:**")
            bail_info = section_details.get("bail_info", {})
            if "bailable" in str(bail_info).lower():
                st.success("This is a **bailable** offense.")
            else:
                st.error("This is a **non-bailable** offense.")

elif code_type == "Civil Laws":
    st.markdown("## Civil Laws Coming Soon")
    st.markdown("""
    This section for civil laws is under development. It will include:
    
    - Contract Act
    - Property Laws
    - Family Laws
    - Companies Act
    - Consumer Protection Act
    
    Check back soon for updates.
    """)
    
    st.info("This section is currently under development. Please check back later for more information.")

# Add a disclaimer at the bottom
st.markdown("---")
st.caption("""
**Disclaimer**: This information is provided for educational purposes only and does not constitute legal advice. 
Always refer to the official and up-to-date legal texts for accurate information.
""")