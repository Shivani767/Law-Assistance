import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from utils import preprocess_text, calculate_similarity

st.set_page_config(
    page_title="Case Search - Indian Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

st.title("Case Search")
st.markdown("### Search legal cases across different jurisdictions")

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Back to Home"):
    st.switch_page("app.py")

# Load state data (in a real application, this would come from a database)
def load_state_data():
    states = [
        "All States", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", 
        "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", 
        "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", 
        "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", 
        "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
        "Uttar Pradesh", "Uttarakhand", "West Bengal"
    ]
    return states

# Load jurisdiction data
def load_jurisdictions():
    jurisdictions = {
        "Supreme Court": {"level": 1, "location": "New Delhi"},
        "High Court": {"level": 2, "locations": {
            "Andhra Pradesh": "Amaravati",
            "Delhi": "New Delhi",
            "Maharashtra": "Mumbai",
            "Karnataka": "Bangalore",
            "Tamil Nadu": "Chennai",
            "Uttar Pradesh": "Allahabad",
            "West Bengal": "Kolkata",
            "Gujarat": "Ahmedabad",
            "Madhya Pradesh": "Jabalpur",
            "Kerala": "Kochi",
            "Punjab and Haryana": "Chandigarh",
            "Rajasthan": "Jodhpur",
            "Telangana": "Hyderabad",
            "Other States": "Various Locations"
        }},
        "District Courts": {"level": 3, "description": "Courts at district level"},
        "Sessions Courts": {"level": 3, "description": "Criminal courts at district level"},
        "Magistrate Courts": {"level": 4, "description": "Lower criminal courts"}
    }
    return jurisdictions

# Generate sample case data
def generate_sample_cases(num_cases=100):
    # Case types
    case_types = ["Criminal", "Civil", "Constitutional", "Family", "Property", "Taxation"]
    
    # Status options
    status_options = ["Pending", "Disposed", "Under Review", "Judgment Reserved", "Closed"]
    
    # Sample plaintiff/defendant names
    plaintiff_names = [
        "State of India", "Central Bureau of Investigation", "Income Tax Department",
        "Rajesh Kumar", "Sunita Sharma", "Vikram Singh", "Priya Patel", "Mohammed Ahmed",
        "Sanjay Enterprises", "Global Industries Ltd.", "Tech Solutions Pvt. Ltd."
    ]
    
    defendant_names = [
        "Arjun Mehta", "Kiran Reddy", "Suresh Gopal", "Neha Verma", "Anand Kumar",
        "Ravi Textiles Ltd.", "Sunshine Properties", "Northern Railways",
        "Department of Telecommunications", "Ministry of Finance", "Municipal Corporation"
    ]
    
    # District names for each state
    districts = {
        "Andhra Pradesh": ["Visakhapatnam", "Guntur", "Krishna", "Kurnool"],
        "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur"],
        "Delhi": ["New Delhi", "North Delhi", "South Delhi", "East Delhi"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
        "Karnataka": ["Bangalore Urban", "Mysore", "Belgaum", "Mangalore"],
        "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur"],
        "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur", "Gwalior"],
        "Maharashtra": ["Mumbai City", "Pune", "Nagpur", "Thane"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem"],
        "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra"],
        "West Bengal": ["Kolkata", "Howrah", "Asansol", "Siliguri"],
        "All States": ["Various Districts"]
    }
    
    cases = []
    
    # Generate random cases
    for i in range(1, num_cases + 1):
        # Select a random state
        state = random.choice(list(districts.keys()))
        
        # Determine court type and jurisdiction
        court_type_rand = random.random()
        if court_type_rand < 0.05:  # 5% Supreme Court cases
            court = "Supreme Court"
            jurisdiction = "Supreme Court of India, New Delhi"
        elif court_type_rand < 0.25:  # 20% High Court cases
            court = "High Court"
            jurisdiction = f"High Court of {state}"
        else:  # 75% Lower court cases
            court_choices = ["District Court", "Sessions Court", "Magistrate Court"]
            court = random.choice(court_choices)
            district = random.choice(districts.get(state, ["Central District"]))
            jurisdiction = f"{court} of {district}, {state}"
        
        # Generate a random case number
        case_number = f"{'CRL' if random.random() < 0.5 else 'CIV'}/{random.randint(1000, 9999)}/{random.randint(2010, 2024)}"
        
        # Generate random dates within the last 5 years
        filing_date = datetime.now() - timedelta(days=random.randint(1, 1825))
        
        # Set a status and possibly a judgment date
        status = random.choice(status_options)
        judgment_date = None
        if status in ["Disposed", "Closed"]:
            judgment_date = filing_date + timedelta(days=random.randint(30, 730))
        
        # Create a case entry
        case = {
            "case_number": case_number,
            "plaintiff": random.choice(plaintiff_names),
            "defendant": random.choice(defendant_names),
            "case_type": random.choice(case_types),
            "filing_date": filing_date.strftime("%d-%m-%Y"),
            "judgment_date": judgment_date.strftime("%d-%m-%Y") if judgment_date else "N/A",
            "status": status,
            "court": court,
            "jurisdiction": jurisdiction,
            "state": state,
            "description": f"This is a sample case for {court} in {state}."
        }
        
        cases.append(case)
    
    return cases

# Convert the list of cases to a DataFrame
def get_case_df():
    cases = generate_sample_cases(200)
    return pd.DataFrame(cases)

# Main search interface
st.markdown("## Search Cases by Criteria")
st.markdown("Enter search criteria to find relevant cases across jurisdictions")

# Create a container for the search form
search_container = st.container()

with search_container:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # State selection
        states = load_state_data()
        selected_state = st.selectbox("Select State", options=states)
        
        # Plaintiff name
        plaintiff_name = st.text_input("Plaintiff Name")
    
    with col2:
        # District input
        district = st.text_input("Enter District")
        
        # Defendant name
        defendant_name = st.text_input("Defendant Name")
    
    with col3:
        # Case number
        case_number = st.text_input("Case Number")
        
        # Case status
        status_options = ["All", "Pending", "Disposed", "Under Review", "Judgment Reserved", "Closed"]
        selected_status = st.selectbox("Case Status", options=status_options)

# Court type selection
court_types = ["All Courts", "Supreme Court", "High Court", "District Court", "Sessions Court", "Magistrate Court"]
selected_court = st.selectbox("Select Court Type", options=court_types)

# Button to search cases
if st.button("🔍 Search Cases", use_container_width=True):
    with st.spinner("Searching for cases..."):
        # Get sample case data
        case_df = get_case_df()
        
        # Apply filters
        if selected_state != "All States":
            case_df = case_df[case_df["state"] == selected_state]
        
        if district:
            case_df = case_df[case_df["jurisdiction"].str.contains(district, case=False)]
        
        if plaintiff_name:
            case_df = case_df[case_df["plaintiff"].str.contains(plaintiff_name, case=False)]
        
        if defendant_name:
            case_df = case_df[case_df["defendant"].str.contains(defendant_name, case=False)]
        
        if case_number:
            case_df = case_df[case_df["case_number"].str.contains(case_number, case=False)]
        
        if selected_status != "All":
            case_df = case_df[case_df["status"] == selected_status]
        
        if selected_court != "All Courts":
            case_df = case_df[case_df["court"] == selected_court]
        
        # Display results
        if len(case_df) > 0:
            st.markdown(f"### Found {len(case_df)} matching cases")
            
            # Display in a table format
            st.dataframe(
                case_df[["case_number", "plaintiff", "defendant", "status", "court", "state", "filing_date"]],
                use_container_width=True
            )
            
            # Allow viewing case details
            selected_case_number = st.selectbox("Select a case to view details", options=case_df["case_number"].tolist())
            
            if selected_case_number:
                case_details = case_df[case_df["case_number"] == selected_case_number].iloc[0]
                
                st.markdown(f"### Case Details: {selected_case_number}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Plaintiff:** {case_details['plaintiff']}")
                    st.markdown(f"**Defendant:** {case_details['defendant']}")
                    st.markdown(f"**Case Type:** {case_details['case_type']}")
                    st.markdown(f"**Status:** {case_details['status']}")
                
                with col2:
                    st.markdown(f"**Filing Date:** {case_details['filing_date']}")
                    st.markdown(f"**Judgment Date:** {case_details['judgment_date']}")
                    st.markdown(f"**Court:** {case_details['court']}")
                    st.markdown(f"**Jurisdiction:** {case_details['jurisdiction']}")
                
                st.markdown("### Case History")
                
                # Generate sample case history
                history_entries = [
                    {"date": (datetime.strptime(case_details['filing_date'], "%d-%m-%Y") + timedelta(days=random.randint(5, 20))).strftime("%d-%m-%Y"), 
                     "action": "First Hearing", 
                     "remarks": "Case admitted and notice issued to respondents"},
                    {"date": (datetime.strptime(case_details['filing_date'], "%d-%m-%Y") + timedelta(days=random.randint(30, 60))).strftime("%d-%m-%Y"), 
                     "action": "Respondent Appearance", 
                     "remarks": "Respondent appeared through counsel and sought time to file reply"},
                    {"date": (datetime.strptime(case_details['filing_date'], "%d-%m-%Y") + timedelta(days=random.randint(70, 100))).strftime("%d-%m-%Y"), 
                     "action": "Arguments", 
                     "remarks": "Partial arguments heard. Matter adjourned"}
                ]
                
                # If case is disposed, add a judgment entry
                if case_details['status'] in ["Disposed", "Closed"] and case_details['judgment_date'] != "N/A":
                    history_entries.append({
                        "date": case_details['judgment_date'],
                        "action": "Judgment Pronounced",
                        "remarks": "Final order passed. Case disposed."
                    })
                
                # Display history as a table
                history_df = pd.DataFrame(history_entries)
                st.table(history_df)
                
                # Provide options for actions
                st.markdown("### Available Actions")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Download Case Details", use_container_width=True):
                        st.info("In a real system, this would download a PDF of the case details.")
                
                with col2:
                    if st.button("Track This Case", use_container_width=True):
                        st.success("Case added to tracking. You will receive updates when the status changes.")
                
                with col3:
                    if st.button("Check Similar Cases", use_container_width=True):
                        st.info("In a real system, this would show cases with similar facts or legal issues.")
        else:
            st.warning("No cases found matching your search criteria. Please try different search parameters.")

# Alternative search by text
st.markdown("---")
st.markdown("## Advanced Search")

text_query = st.text_area("Search by case description or keywords", 
                        placeholder="Enter keywords or phrases to search in case descriptions...")

if st.button("Perform Text Search", use_container_width=True):
    if not text_query:
        st.warning("Please enter text to search.")
    else:
        with st.spinner("Performing text search..."):
            # In a real system, this would use more sophisticated text search
            # For demonstration, we'll do a simple search
            case_df = get_case_df()
            
            # Preprocess the query
            processed_query = preprocess_text(text_query)
            
            # Calculate similarity for each case description
            case_df["relevance"] = case_df["description"].apply(
                lambda x: calculate_similarity(processed_query, preprocess_text(x))
            )
            
            # Sort by relevance and filter cases with some relevance
            relevant_cases = case_df[case_df["relevance"] > 0.1].sort_values("relevance", ascending=False)
            
            if len(relevant_cases) > 0:
                st.markdown(f"### Found {len(relevant_cases)} potentially relevant cases")
                
                # Display in a table format
                st.dataframe(
                    relevant_cases[["case_number", "plaintiff", "defendant", "status", "court", "state", "relevance"]],
                    use_container_width=True
                )
            else:
                st.warning("No relevant cases found. Please try different search terms.")

# Add a disclaimer at the bottom
st.markdown("---")
st.caption("""
**Disclaimer**: This is a demonstration system with sample data for educational purposes only. 
In a production environment, this would connect to official court databases. 
Always consult with a qualified legal professional for advice specific to your situation.
""")