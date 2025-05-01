import streamlit as st
import pandas as pd
from model import legal_predictor
from legal_data import (
    ipc_sections, it_act_sections, mv_act_sections,
    get_offense_details, get_bail_information
)

st.set_page_config(
    page_title="Defendant Rights - Indian Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

# Add custom CSS
st.markdown("""
<style>
    /* Global Styles */
    @keyframes pageLoad {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
        color: #2c3e50;
        transition: all 0.3s ease;
        animation: pageLoad 0.8s ease-out;
    }

    /* Rights Card */
    @keyframes cardReveal {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }

    .rights-card {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 51, 102, 0.1);
        animation: cardReveal 0.6s ease-out;
        transition: all 0.3s ease;
    }

    .rights-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }

    /* Category Section */
    @keyframes sectionSlide {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .category-section {
        background: linear-gradient(to right, #f8f9fa, #ffffff);
        border-left: 4px solid #003366;
        border-radius: 0 8px 8px 0;
        padding: 15px;
        margin-bottom: 15px;
        animation: sectionSlide 0.5s ease-out;
        transition: all 0.3s ease;
    }

    .category-section:hover {
        background: linear-gradient(to right, #f0f2f5, #ffffff);
        transform: scale(1.01);
    }

    /* Loading State */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @keyframes loadingPulse {
        0% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.1); opacity: 1; }
        100% { transform: scale(1); opacity: 0.8; }
    }

    .loading-state {
        text-align: center;
        padding: 20px;
        animation: loadingPulse 1.5s ease-in-out infinite;
    }

    .loading-state::after {
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

st.title("Understand Your Legal Rights")
st.markdown("### Learn about your rights and options as a defendant")

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Back to Home"):
    st.switch_page("app.py")

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Your Rights", "Bail Information", "Legal Process"])

with tab1:
    st.markdown("## Know Your Rights After Being Found Guilty")
    st.markdown("""
    If you have been found guilty or charged with an offense, understanding your legal rights is critical.
    Please provide information about your case below to get personalized information:
    """)
    
    # Select legal act
    act_options = {"Indian Penal Code (IPC)": "IPC", 
                   "Information Technology Act": "IT Act", 
                   "Motor Vehicles Act": "MV Act"}
    selected_act = st.selectbox("Select Legal Act", options=list(act_options.keys()))
    act_code = act_options[selected_act]
    
    # Show relevant sections based on selected act
    if act_code == "IPC":
        section_options = {f"Section {k}: {v}": k for k, v in ipc_sections.items()}
    elif act_code == "IT Act":
        section_options = {f"Section {k}: {v}": k for k, v in it_act_sections.items()}
    else:  # MV Act
        section_options = {f"Section {k}: {v}": k for k, v in mv_act_sections.items()}
    
    selected_section_display = st.selectbox("Select Section", options=list(section_options.keys()))
    selected_section = section_options[selected_section_display]
    
    # Case description
    case_description = st.text_area("Briefly describe your case (optional)", 
                                   help="Providing details helps us give more specific information")
    
    if st.button("Show My Rights", use_container_width=True):
        with st.spinner("Analyzing your case..."):
            # Get rights prediction
            rights_info = legal_predictor.predict_rights(
                selected_section, act_code, case_description
            )
            
            if "error" in rights_info:
                st.error(rights_info["error"])
            else:
                # Display section information
                section_info = rights_info.get("section_info", {})
                if section_info:
                    st.markdown(f"### {section_info.get('title', '')}")
                    st.markdown(f"**{act_code} Section {selected_section}**")
                
                # Display rights
                st.markdown("### Your Legal Rights")
                rights = rights_info.get("rights", [])
                
                for right in rights:
                    relevance = right["relevance"]
                    importance = "High" if relevance > 0.8 else "Medium" if relevance > 0.6 else "Standard"
                    
                    with st.expander(f"{right['right']} (Importance: {importance})"):
                        # Provide more detailed information about each right
                        if "legal representation" in right["right"].lower():
                            st.markdown("""
                            You have the right to be represented by a lawyer of your choice. If you cannot afford a lawyer, 
                            you have the right to free legal aid provided by the state under Section 304 of the Criminal 
                            Procedure Code and Article 39A of the Constitution of India.
                            
                            **How to exercise this right:**
                            - Contact the nearest Legal Services Authority
                            - Apply to the court for appointment of a legal aid lawyer
                            - You can change your lawyer if you are not satisfied
                            """)
                            
                        elif "appeal" in right["right"].lower():
                            st.markdown("""
                            You have the right to appeal your conviction and/or sentence to a higher court. 
                            
                            **Appeal process:**
                            - For magistrate court convictions: Appeal to Sessions Court
                            - For Sessions Court convictions: Appeal to High Court
                            - For High Court convictions: Appeal to Supreme Court (with special leave)
                            
                            **Time limit:** Usually 30-90 days from the date of judgment, depending on the court
                            """)
                            
                        elif "bail" in right["right"].lower():
                            st.markdown("""
                            Even after conviction, you may apply for bail pending appeal. The court may grant bail 
                            considering factors like:
                            - Severity of the offense
                            - Length of the sentence
                            - Likelihood of the appeal succeeding
                            - Whether you pose a flight risk
                            """)
                            
                        elif "cross-examine" in right["right"].lower():
                            st.markdown("""
                            You have the right to cross-examine prosecution witnesses to test their credibility 
                            and challenge their testimony. This is a fundamental aspect of the right to a fair trial.
                            """)
                            
                        elif "presumed innocent" in right["right"].lower():
                            st.markdown("""
                            The burden of proof is on the prosecution to prove guilt beyond reasonable doubt. 
                            You are presumed innocent until proven guilty, and this principle is fundamental to 
                            the Indian criminal justice system.
                            """)
                            
                        elif "remain silent" in right["right"].lower():
                            st.markdown("""
                            You have the right to remain silent and cannot be compelled to be a witness against yourself,
                            as guaranteed by Article 20(3) of the Constitution of India.
                            """)
                            
                        else:
                            st.markdown("""
                            This is an important legal right that applies to your case. Consult with your lawyer 
                            about how to effectively exercise this right in your specific situation.
                            """)
                
                # Defense options
                st.markdown("### Potential Defense Options")
                defense_options = legal_predictor.suggest_defense_options(
                    selected_section, act_code, case_description
                )
                
                if "error" in defense_options:
                    st.error(defense_options["error"])
                else:
                    options = defense_options.get("defense_options", [])
                    for option in options[:5]:  # Show top 5 options
                        st.markdown(f"- **{option['option']}**")
                    
                    st.info("Discuss these defense options with your lawyer to determine which are most relevant to your specific case.")

with tab2:
    st.markdown("## Bail Information")
    st.markdown("""
    Understanding bail provisions is crucial for defendants. Bail allows temporary release 
    during trial or appeal, with the court's permission.
    """)
    
    # Select offense for bail information
    bail_act_options = {"Indian Penal Code (IPC)": "IPC", 
                      "Information Technology Act": "IT Act", 
                      "Motor Vehicles Act": "MV Act"}
    bail_selected_act = st.selectbox("Select Legal Act", options=list(bail_act_options.keys()), key="bail_act")
    bail_act_code = bail_act_options[bail_selected_act]
    
    # Show relevant sections based on selected act
    if bail_act_code == "IPC":
        bail_section_options = {f"Section {k}: {v}": k for k, v in ipc_sections.items()}
    elif bail_act_code == "IT Act":
        bail_section_options = {f"Section {k}: {v}": k for k, v in it_act_sections.items()}
    else:  # MV Act
        bail_section_options = {f"Section {k}: {v}": k for k, v in mv_act_sections.items()}
    
    bail_selected_section_display = st.selectbox("Select Section", options=list(bail_section_options.keys()), key="bail_section")
    bail_selected_section = bail_section_options[bail_selected_section_display]
    
    if st.button("Show Bail Information", use_container_width=True):
        with st.spinner("Fetching bail information..."):
            # Get bail information
            bail_info = get_bail_information(bail_selected_section, bail_act_code)
            
            if not bail_info:
                st.error("Could not retrieve bail information for the selected section.")
            else:
                # Display bail category
                if "bailable" in str(bail_info).lower():
                    st.success("### Bailable Offense")
                    st.markdown("""
                    This is a **bailable offense**, which means bail is a matter of right. 
                    The police or court must grant bail in such cases, subject to fulfilling 
                    certain conditions like providing a bail bond.
                    """)
                else:
                    st.error("### Non-Bailable Offense")
                    st.markdown("""
                    This is a **non-bailable offense**, which means bail is not a matter of right 
                    but is at the discretion of the court. The court will consider various factors 
                    before granting or denying bail.
                    """)
                
                # Display bail procedure
                st.markdown("### Bail Procedure")
                if bail_info.get("procedure"):
                    for step in bail_info.get("procedure", []):
                        st.markdown(f"- {step}")
                
                # Display bail examples
                if bail_info.get("examples"):
                    st.markdown("### Similar Offenses")
                    for example in bail_info.get("examples", []):
                        st.markdown(f"- {example}")
                
                # Special provisions
                if "non_bailable" in str(bail_info).lower():
                    st.markdown("### Special Considerations for Bail")
                    st.markdown("""
                    Even for non-bailable offenses, bail may be granted under special circumstances:
                    
                    1. **Medical grounds**: Serious illness or medical condition
                    2. **Age factor**: Very young or elderly accused
                    3. **Women with children**: Special consideration for women with young children
                    4. **Long trial period**: When trial is taking unusually long time
                    5. **Weak prima facie case**: When evidence against accused is weak
                    """)
                    
                    st.warning("""
                    **Note**: If bail is denied by the Magistrate's Court, you can approach the Sessions Court, 
                    and thereafter the High Court and Supreme Court.
                    """)

with tab3:
    st.markdown("## Understanding the Legal Process")
    st.markdown("""
    The Indian legal process follows several stages from arrest to final judgment and appeal.
    Understanding this process can help you navigate your case more effectively.
    """)
    
    # Display legal process stages
    stages = {
        "Investigation Stage": """
        - **FIR Registration**: First Information Report filed at police station
        - **Police Investigation**: Collecting evidence, questioning witnesses
        - **Arrest**: Taking the accused into custody if required
        - **Remand**: Police custody or judicial custody as determined by court
        """,
        
        "Pre-Trial Stage": """
        - **Bail Application**: Seeking temporary release during trial
        - **Charge Sheet**: Police files final report of investigation
        - **Cognizance**: Court takes judicial notice of the offense
        - **Charge Framing**: Formal accusation against the accused
        """,
        
        "Trial Stage": """
        - **Prosecution Evidence**: Witnesses and evidence presented by prosecution
        - **Statement of Accused**: Recorded under Section 313 CrPC
        - **Defense Evidence**: Witnesses and evidence presented by defense
        - **Final Arguments**: Closing arguments by both sides
        """,
        
        "Judgment and Post-Trial": """
        - **Judgment**: Court's decision on guilt or innocence
        - **Sentencing**: Punishment if found guilty
        - **Appeal**: Challenging the verdict in a higher court
        - **Review/Revision**: Further legal remedies
        """
    }
    
    selected_stage = st.selectbox("Select Stage of Legal Process", options=list(stages.keys()))
    
    st.markdown(f"### {selected_stage}")
    st.markdown(stages[selected_stage])
    
    # Display jurisdiction information
    st.markdown("### Jurisdiction Structure")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Judiciary_of_India_diagram_en.svg/800px-Judiciary_of_India_diagram_en.svg.png", 
            caption="Indian Judicial System Hierarchy")
    
    st.markdown("""
    **Important Notes on Jurisdiction:**
    
    1. **Territorial Jurisdiction**: Cases are tried in courts that have jurisdiction over the place where the offense was committed.
    
    2. **Hierarchy of Courts**:
       - **Magistrate Courts**: Handle less serious offenses with imprisonment up to 3 years
       - **Sessions Courts**: Handle serious offenses with imprisonment above 3 years
       - **High Courts**: Have supervisory jurisdiction over all courts in the state
       - **Supreme Court**: Highest court of appeal in the country
    
    3. **Special Courts**: For specific offenses (NDPS, CBI cases, etc.)
    """)

# Add a disclaimer at the bottom
st.markdown("---")
st.caption("""
**Disclaimer**: This information is provided for educational purposes only and does not constitute legal advice. 
Always consult with a qualified legal professional for advice specific to your situation.
""")
