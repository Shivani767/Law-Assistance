import streamlit as st
import pandas as pd
from legal_data import get_jurisdiction_info

st.set_page_config(
    page_title="Jurisdiction Assistant - Indian Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Global Styles */
    @keyframes pageEntrance {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
        color: #2c3e50;
        transition: all 0.3s ease;
        animation: pageEntrance 0.8s ease-out;
    }

    /* Jurisdiction Card */
    @keyframes cardSlideIn {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }

    .jurisdiction-card {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 51, 102, 0.1);
        animation: cardSlideIn 0.6s ease-out;
        transition: all 0.3s ease;
    }

    .jurisdiction-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }

    /* Court Info */
    @keyframes infoReveal {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .court-info {
        background: linear-gradient(to right, #f8f9fa, #ffffff);
        border-left: 4px solid #003366;
        border-radius: 0 8px 8px 0;
        padding: 15px;
        margin-bottom: 15px;
        animation: infoReveal 0.5s ease-out;
        transition: all 0.3s ease;
    }

    .court-info:hover {
        background: linear-gradient(to right, #f0f2f5, #ffffff);
        transform: scale(1.01);
    }

    /* Loading State */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @keyframes loadingBounce {
        0% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.1); opacity: 1; }
        100% { transform: scale(1); opacity: 0.8; }
    }

    .loading-indicator {
        text-align: center;
        padding: 20px;
        animation: loadingBounce 1.5s ease-in-out infinite;
    }

    .loading-indicator::after {
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

st.title("Jurisdiction Assistant")
st.markdown("### Understand court jurisdictions and their powers")

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Back to Home"):
    st.switch_page("app.py")

# Get jurisdiction information
jurisdiction_types = get_jurisdiction_info()

# Create tabs for different aspects of jurisdiction
tab1, tab2, tab3 = st.tabs(["Jurisdiction Types", "Court Hierarchy", "Jurisdiction Finder"])

with tab1:
    st.markdown("## Types of Jurisdiction in Indian Legal System")
    
    # Display information about different jurisdiction types
    for j_type, j_info in jurisdiction_types.items():
        with st.expander(f"{j_type.title()} Jurisdiction"):
            st.markdown(f"**Description:** {j_info.get('description', '')}")
            
            if "hierarchy" in j_info:
                st.markdown("**Hierarchy:**")
                for level in j_info.get("hierarchy", []):
                    st.markdown(f"- {level}")
            
            if "types" in j_info:
                st.markdown("**Types:**")
                for typ in j_info.get("types", []):
                    st.markdown(f"- {typ}")
            
            if "courts" in j_info:
                st.markdown("**Courts:**")
                for court in j_info.get("courts", []):
                    st.markdown(f"- {court}")
            
            if "limits" in j_info:
                st.markdown("**Limits:**")
                for limit in j_info.get("limits", []):
                    st.markdown(f"- {limit}")

with tab2:
    st.markdown("## Indian Court Hierarchy")
    
    # Create a visual representation of the court hierarchy
    st.markdown("""
    ### Supreme Court of India
    The highest judicial forum and final court of appeal under the Constitution of India
    
    ↓
    
    ### High Courts
    Each state has a High Court that serves as the principal civil court of original jurisdiction
    
    ↓
    
    ### District Courts
    Principal court of original jurisdiction in a district
    
    ↓
    
    ### Subordinate Courts
    Lower courts that operate under the district courts
    """)
    
    # Display a table with jurisdiction details
    court_jurisdiction = [
        {"Court": "Supreme Court", "Territorial Jurisdiction": "All of India", "Subject Matter": "Constitutional, Civil, Criminal", "Original/Appellate": "Original & Appellate"},
        {"Court": "High Courts", "Territorial Jurisdiction": "State/Union Territory", "Subject Matter": "Constitutional, Civil, Criminal", "Original/Appellate": "Original & Appellate"},
        {"Court": "District Courts", "Territorial Jurisdiction": "District", "Subject Matter": "Civil & Criminal", "Original/Appellate": "Primarily Original, Limited Appellate"},
        {"Court": "Sessions Courts", "Territorial Jurisdiction": "District", "Subject Matter": "Criminal", "Original/Appellate": "Original for serious offenses"},
        {"Court": "Magistrate Courts", "Territorial Jurisdiction": "Sub-district", "Subject Matter": "Criminal", "Original/Appellate": "Original for less serious offenses"},
        {"Court": "Civil Judge Courts", "Territorial Jurisdiction": "Sub-district", "Subject Matter": "Civil", "Original/Appellate": "Original for civil matters"}
    ]
    
    st.table(pd.DataFrame(court_jurisdiction))
    
    # Specialized courts
    st.markdown("### Specialized Courts and Tribunals")
    specialized_courts = [
        {"Court/Tribunal": "Family Courts", "Jurisdiction": "Matrimonial disputes, custody, maintenance"},
        {"Court/Tribunal": "Consumer Forums", "Jurisdiction": "Consumer disputes"},
        {"Court/Tribunal": "National Green Tribunal", "Jurisdiction": "Environmental matters"},
        {"Court/Tribunal": "Income Tax Appellate Tribunal", "Jurisdiction": "Income tax disputes"},
        {"Court/Tribunal": "Armed Forces Tribunal", "Jurisdiction": "Military service matters"},
        {"Court/Tribunal": "National Company Law Tribunal", "Jurisdiction": "Corporate law matters"}
    ]
    
    st.table(pd.DataFrame(specialized_courts))

with tab3:
    st.markdown("## Jurisdiction Finder")
    st.markdown("""
    Determine which court has jurisdiction over your case based on case details.
    This tool helps you understand which court would be appropriate for filing or addressing your legal matter.
    """)
    
    # Create a form for jurisdiction finder
    col1, col2 = st.columns(2)
    
    with col1:
        # Case type selection
        case_type = st.selectbox(
            "Case Type",
            options=[
                "Criminal Offense", "Civil Dispute", "Family Matter", 
                "Constitutional Issue", "Property Dispute", "Consumer Complaint",
                "Environmental Matter", "Corporate/Company Law", "Tax Dispute"
            ]
        )
        
        # Location information
        state = st.selectbox(
            "State/Union Territory",
            options=[
                "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", 
                "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", 
                "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", 
                "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", 
                "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
                "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi (NCT)"
            ]
        )
    
    with col2:
        # Monetary value for civil cases
        case_value = st.number_input(
            "Approximate Case Value (₹) (for civil matters)",
            min_value=0,
            value=100000
        )
        
        # Criminal case severity
        if "Criminal" in case_type:
            offense_type = st.selectbox(
                "Offense Category",
                options=[
                    "Petty Offense (imprisonment < 3 months)",
                    "Minor Offense (imprisonment < 3 years)",
                    "Serious Offense (imprisonment > 3 years)",
                    "Capital Offense"
                ]
            )
        
        # Constitutional question
        if "Constitutional" in case_type:
            const_question = st.checkbox("Involves interpretation of the Constitution")
        
        # Against government
        against_govt = st.checkbox("Case against Government/Public Authority")
    
    # Case description
    case_description = st.text_area(
        "Brief Case Description",
        placeholder="Provide a brief description of your legal matter..."
    )
    
    if st.button("Find Appropriate Jurisdiction", use_container_width=True):
        with st.spinner("Analyzing your case..."):
            # Determine jurisdiction based on inputs
            # This is a simplified logic for demonstration
            court_level = ""
            jurisdiction_type = ""
            specific_court = ""
            filing_location = ""
            
            # Initialize variables with default values
            const_question = False
            offense_type = "Minor Offense (imprisonment < 3 years)"
            
            # We'll access session state which is safer than locals
            if "Constitutional" in case_type and 'const_question' in st.session_state:
                const_question = st.session_state.const_question
            
            if "Criminal" in case_type and 'offense_type' in st.session_state:
                offense_type = st.session_state.offense_type
                
            # Also save current values to session state for future use
            if "Constitutional" in case_type:
                st.session_state.const_question = const_question
                
            if "Criminal" in case_type:
                st.session_state.offense_type = offense_type
            
            # Determine court level based on case type
            if "Constitutional" in case_type and const_question:
                court_level = "Supreme Court or High Court"
                jurisdiction_type = "Original Constitutional Jurisdiction"
                specific_court = "Supreme Court (if fundamental rights) or High Court (writ jurisdiction)"
                filing_location = "New Delhi (Supreme Court) or High Court of " + state
                
            elif "Criminal" in case_type:
                if "Petty" in offense_type:
                    court_level = "Magistrate Court"
                    jurisdiction_type = "Criminal Jurisdiction"
                    specific_court = "Judicial Magistrate First Class"
                    filing_location = "Local Magistrate Court in the district"
                elif "Minor" in offense_type:
                    court_level = "Magistrate Court"
                    jurisdiction_type = "Criminal Jurisdiction"
                    specific_court = "Chief Judicial Magistrate or JMFC"
                    filing_location = "District Court Complex"
                elif "Serious" in offense_type:
                    court_level = "Sessions Court"
                    jurisdiction_type = "Criminal Jurisdiction"
                    specific_court = "Sessions Judge"
                    filing_location = "District Court Complex"
                elif "Capital" in offense_type:
                    court_level = "Sessions Court (Trial) with High Court confirmation"
                    jurisdiction_type = "Criminal Jurisdiction"
                    specific_court = "Sessions Judge"
                    filing_location = "District Court Complex"
            
            elif "Civil" in case_type or "Property" in case_type:
                if case_value < 100000:
                    court_level = "Civil Judge (Junior Division)"
                    jurisdiction_type = "Civil Jurisdiction"
                    specific_court = "Civil Court"
                    filing_location = "Local Civil Court in the district"
                elif case_value < 1000000:
                    court_level = "Civil Judge (Senior Division)"
                    jurisdiction_type = "Civil Jurisdiction"
                    specific_court = "Civil Court"
                    filing_location = "District Court Complex"
                else:
                    court_level = "District Judge"
                    jurisdiction_type = "Civil Jurisdiction"
                    specific_court = "District Court"
                    filing_location = "District Court Complex"
            
            elif "Family" in case_type:
                court_level = "Family Court"
                jurisdiction_type = "Family Court Jurisdiction"
                specific_court = "Family Court Judge"
                filing_location = "Family Court in the district"
            
            elif "Consumer" in case_type:
                if case_value < 100000:
                    court_level = "District Consumer Forum"
                    jurisdiction_type = "Consumer Protection Jurisdiction"
                    specific_court = "District Consumer Disputes Redressal Commission"
                    filing_location = "District Consumer Forum"
                elif case_value < 10000000:
                    court_level = "State Consumer Commission"
                    jurisdiction_type = "Consumer Protection Jurisdiction"
                    specific_court = "State Consumer Disputes Redressal Commission"
                    filing_location = "State Capital"
                else:
                    court_level = "National Consumer Commission"
                    jurisdiction_type = "Consumer Protection Jurisdiction"
                    specific_court = "National Consumer Disputes Redressal Commission"
                    filing_location = "New Delhi"
            
            elif "Environmental" in case_type:
                court_level = "National Green Tribunal"
                jurisdiction_type = "Environmental Jurisdiction"
                specific_court = "National Green Tribunal"
                filing_location = "Principal or Regional Bench of NGT"
            
            elif "Corporate" in case_type:
                court_level = "National Company Law Tribunal"
                jurisdiction_type = "Corporate Law Jurisdiction"
                specific_court = "NCLT"
                filing_location = "NCLT Bench having jurisdiction over registered office"
            
            elif "Tax" in case_type:
                court_level = "Income Tax Appellate Tribunal"
                jurisdiction_type = "Tax Jurisdiction"
                specific_court = "ITAT"
                filing_location = "ITAT Bench having jurisdiction over assessment"
            
            # Handle special case against government
            if against_govt and ("Civil" in case_type or "Property" in case_type):
                court_level = "High Court (possible)"
                jurisdiction_type = "Writ Jurisdiction"
                specific_court = "High Court of " + state
                filing_location = "High Court of " + state
            
            # Display the results
            st.markdown("### Jurisdiction Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Appropriate Court Level:** {court_level}")
                st.markdown(f"**Type of Jurisdiction:** {jurisdiction_type}")
            
            with col2:
                st.markdown(f"**Specific Court:** {specific_court}")
                st.markdown(f"**Filing Location:** {filing_location}")
            
            # Additional notes based on case type
            st.markdown("### Important Notes")
            
            if "Criminal" in case_type:
                st.markdown("""
                1. The jurisdiction in criminal cases is primarily determined by:
                   - The place where the offense was committed
                   - The severity of the offense
                   - The maximum punishment prescribed for the offense
                
                2. First Information Report (FIR) should be filed at the police station having jurisdiction over the place of offense.
                
                3. For cognizable offenses, police can investigate without court order. For non-cognizable offenses, police need court permission.
                """)
            
            elif "Civil" in case_type or "Property" in case_type:
                st.markdown("""
                1. The jurisdiction in civil cases is determined by:
                   - The location of the property (for immovable property disputes)
                   - The place where the defendant resides or works
                   - The place where the cause of action arose
                   - The monetary value of the suit
                
                2. Pecuniary jurisdiction limits vary from state to state and are subject to change.
                
                3. Specific civil matters may have exclusive forums (e.g., rent control matters, land acquisition cases)
                """)
            
            # Disclaimer
            st.warning("""
            **Disclaimer**: This jurisdiction recommendation is based on the information provided and general legal principles.
            The actual jurisdiction may vary based on specific details of your case. Always consult with a qualified legal
            professional before initiating legal proceedings.
            """)

# Add a disclaimer at the bottom
st.markdown("---")
st.caption("""
**Disclaimer**: This information is provided for educational purposes only and does not constitute legal advice. 
Always consult with a qualified legal professional for advice specific to your situation.
""")