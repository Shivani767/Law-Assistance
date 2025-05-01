import streamlit as st
import pandas as pd
from legal_data import legal_precedents
from semantic_search import legal_case_matcher
import time
import re

st.set_page_config(
    page_title="Case Law Search - Indian Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

st.title("Advanced Case Law Search")
st.markdown("### Search legal precedents using semantic matching technology")

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Back to Home"):
    st.switch_page("app.py")

# Prepare case data
def prepare_case_data():
    # Extract texts and metadata from legal precedents
    case_texts = [p.get("summary", "") for p in legal_precedents]
    case_metadata = []
    
    for p in legal_precedents:
        metadata = {
            "case_name": p.get("case_name", "Unnamed Case"),
            "citation": p.get("citation", ""),
            "court": p.get("court", "Unknown Court"),
            "year": p.get("year", ""),
            "key_points": p.get("key_points", []),
            "section": p.get("section", ""),
            "act": p.get("act", "")
        }
        case_metadata.append(metadata)
    
    return case_texts, case_metadata

case_texts, case_metadata = prepare_case_data()

# Search functionality
st.markdown("## Semantic Search")

# Search options
search_container = st.container()
with search_container:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        query = st.text_area(
            "Enter case description or legal query",
            placeholder="Describe the case scenario, legal issue, or facts you want to find precedents for...",
            height=100
        )
    
    with col2:
        st.markdown("### Filter Options")
        
        # Create a dropdown of unique acts
        acts = ["All Acts"] + sorted(list(set([p["act"] for p in legal_precedents])))
        selected_act = st.selectbox("Select Act", acts)
        
        # Extract all sections from the precedent data
        all_sections = []
        for p in legal_precedents:
            sections = p["section"].split(",") if isinstance(p["section"], str) else [p["section"]]
            all_sections.extend([s.strip() for s in sections])
        
        unique_sections = ["All Sections"] + sorted(list(set([s for s in all_sections if s])))
        selected_section = st.selectbox("Select Section", unique_sections)
        
        # Year range
        # Extract years safely, handling missing keys and parsing from string citations
        years = []
        for p in legal_precedents:
            # Try to extract year from citation if available, e.g., "(2017) 10 SCC 1"
            if p.get("citation"):
                match = re.search(r'\((\d{4})\)', p.get("citation", ""))
                if match:
                    try:
                        years.append(int(match.group(1)))
                    except (ValueError, IndexError):
                        pass
            # Also check direct year field if it exists
            if p.get("year") and isinstance(p.get("year"), (int, float)):
                years.append(int(p.get("year")))
                
        # Default years if none found
        if not years:
            years = [1980, 2025]  # reasonable default range for Indian legal precedents
            
        min_year, max_year = min(years), max(years)
        
        year_range = st.slider(
            "Year Range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )
        
        # Number of results
        num_results = st.number_input("Number of Results", min_value=1, max_value=20, value=5)

# Search button
if st.button("Search Precedents"):
    if not query:
        st.warning("Please enter a case description or legal query.")
    else:
        with st.spinner("Searching for relevant precedents..."):
            # Filter precedents based on selected criteria
            filtered_indices = []
            
            for i, metadata in enumerate(case_metadata):
                # Apply act filter
                if selected_act != "All Acts" and metadata["act"] != selected_act:
                    continue
                
                # Apply section filter
                if selected_section != "All Sections":
                    sections = metadata["section"].split(",") if isinstance(metadata["section"], str) else [metadata["section"]]
                    sections = [s.strip() for s in sections]
                    if selected_section not in sections:
                        continue
                
                # Apply year filter
                year = metadata["year"]
                extracted_year = None
                
                # Try to extract year from citation if year field is empty or not numeric
                if not isinstance(year, (int, float)):
                    # First try to parse from year field if it's a string
                    if isinstance(year, str) and year.strip():
                        try:
                            year_match = re.search(r'\d{4}', year)
                            if year_match:
                                extracted_year = int(year_match.group(0))
                        except (ValueError, IndexError):
                            pass
                    
                    # If still no year, try to extract from citation
                    if not extracted_year and metadata.get("citation"):
                        try:
                            citation_match = re.search(r'\((\d{4})\)', metadata["citation"])
                            if citation_match:
                                extracted_year = int(citation_match.group(1))
                        except (ValueError, IndexError):
                            pass
                    
                    # If still no year, default to 0 (will be filtered out)
                    if not extracted_year:
                        extracted_year = 0
                else:
                    # If year is already numeric, use it directly
                    extracted_year = int(year)
                
                # Apply the year filter
                if extracted_year < year_range[0] or extracted_year > year_range[1]:
                    continue
                
                filtered_indices.append(i)
            
            # Prepare filtered data
            filtered_texts = [case_texts[i] for i in filtered_indices]
            filtered_metadata = [case_metadata[i] for i in filtered_indices]
            
            # No results after filtering
            if not filtered_texts:
                st.warning("No cases match your filter criteria. Try changing the filters.")
            else:
                # Add a slight delay to simulate processing
                time.sleep(0.5)
                
                # Find similar cases
                results = legal_case_matcher.find_similar_cases(
                    query, 
                    filtered_texts, 
                    filtered_metadata, 
                    top_k=num_results
                )
                
                if not results:
                    st.info("No similar precedents found. Try different search terms or filters.")
                else:
                    st.markdown(f"## Found {len(results)} Relevant Precedents")
                    
                    # Display results
                    for i, result in enumerate(results):
                        similarity_percentage = result["similarity"] * 100
                        
                        # Create expandable card for each result
                        with st.expander(f"{i+1}. {result['case_name']} ({similarity_percentage:.1f}% match)", expanded=i==0):
                            # Case details in columns
                            col1, col2 = st.columns([3, 2])
                            
                            with col1:
                                st.markdown(f"**Case:** {result['case_name']}")
                                st.markdown(f"**Citation:** {result['citation']}")
                                st.markdown(f"**Court:** {result['court']}")
                                st.markdown(f"**Year:** {result['year']}")
                                st.markdown(f"**Sections:** {result['section']}")
                                st.markdown(f"**Act:** {result['act']}")
                            
                            with col2:
                                # Show match quality with color
                                if similarity_percentage > 80:
                                    st.markdown(f"**Match Quality:** <span style='color:green'><strong>High ({similarity_percentage:.1f}%)</strong></span>", unsafe_allow_html=True)
                                elif similarity_percentage > 60:
                                    st.markdown(f"**Match Quality:** <span style='color:orange'><strong>Medium ({similarity_percentage:.1f}%)</strong></span>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"**Match Quality:** <span style='color:red'><strong>Low ({similarity_percentage:.1f}%)</strong></span>", unsafe_allow_html=True)
                            
                            # Case summary
                            st.markdown("### Summary")
                            st.markdown(result["text"])
                            
                            # Key points
                            if result.get("key_points"):
                                st.markdown("### Key Points")
                                for point in result["key_points"]:
                                    st.markdown(f"- {point}")
                            
                            # Extracted key sentences if not already in key points
                            if not result.get("key_points") and result.get("text"):
                                st.markdown("### Key Takeaways")
                                key_sentences = legal_case_matcher.extract_key_sentences(result["text"], top_n=3)
                                for sentence in key_sentences:
                                    st.markdown(f"- {sentence}")

# Information about the search technology
with st.expander("About Semantic Search Technology", expanded=False):
    st.markdown("""
    ### Advanced Semantic Search
    
    This tool uses semantic search technology to find relevant legal precedents based on meaning, not just keywords.
    
    **How it works:**
    - The system analyzes the meaning and legal context of your query
    - It uses enhanced TF-IDF with legal domain knowledge to identify semantically similar cases
    - Results are ranked by semantic similarity score
    
    **Benefits over traditional keyword search:**
    - Finds conceptually similar cases even when wording is different
    - Understands legal terminology in context
    - Prioritizes legally significant terms and concepts
    
    **For best results:**
    - Include specific legal issues and factual circumstances
    - Mention relevant sections or acts if known
    - Be as descriptive as possible about the legal scenario
    """)

# Add a disclaimer at the bottom
st.markdown("---")
st.caption("""
**Disclaimer**: This information is provided for educational purposes only and does not constitute legal advice. 
The precedent search uses advanced algorithms but may not identify all relevant cases.
Always consult with a qualified legal professional for specific legal matters.
""")