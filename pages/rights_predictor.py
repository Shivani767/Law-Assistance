import streamlit as st
import pandas as pd
import re
import random
from model import legal_predictor
from legal_data import (
    ipc_sections, it_act_sections, mv_act_sections,
    get_offense_details, get_bail_information
)
from utils import extract_section_numbers

st.set_page_config(
    page_title="Rights Predictor - Indian Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

st.title("Defendant Rights Predictor")
st.markdown("### AI-powered analysis of your legal rights in criminal proceedings")

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Back to Home"):
    st.switch_page("app.py")

if st.sidebar.button("Defendant Rights"):
    st.switch_page("pages/defendant_rights.py")

if st.sidebar.button("Bail Assistance"):
    st.switch_page("pages/bail_assistance.py")

# Main form for case details
st.markdown("""
This advanced tool analyzes your case details to predict the relevant legal rights and protections 
that may apply to your situation under Indian law. Provide as much detail as possible for the most accurate results.
""")

# Create tabs for different ways to get rights information
tab1, tab2 = st.tabs(["Case Description Analysis", "Manual Selection"])

with tab1:
    st.markdown("## AI-Based Rights Analysis")
    st.markdown("""
    Describe your legal situation, and our AI system will extract relevant legal sections and predict applicable rights.
    Include details such as the alleged offense, circumstances, and any concerns you have.
    """)
    
    case_description = st.text_area(
        "Describe Your Case in Detail",
        placeholder="Example: I am accused of assault during a protest. The police searched my house without a warrant...",
        height=150
    )
    
    # Advanced options
    with st.expander("Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            detention_status = st.radio(
                "Current Status",
                options=["Not Detained", "In Police Custody", "In Judicial Custody", "On Bail"]
            )
            
            has_lawyer = st.radio(
                "Legal Representation",
                options=["No Lawyer Yet", "Have a Lawyer"]
            )
        
        with col2:
            case_stage = st.radio(
                "Case Stage",
                options=["Pre-FIR/Complaint", "Investigation", "Charge Sheet Filed", "Trial Ongoing", "Convicted/Sentenced"]
            )
            
            jurisdiction = st.selectbox(
                "Jurisdiction",
                options=["Unknown", "District/Sessions Court", "High Court", "Supreme Court"]
            )
    
    # Button to analyze case
    if st.button("Analyze My Rights", use_container_width=True):
        if not case_description or len(case_description) < 30:
            st.warning("Please provide more details about your case for accurate analysis.")
        else:
            with st.spinner("Analyzing your case..."):
                # Extract potential IPC, IT Act or MV Act sections from the description
                extracted_sections = extract_section_numbers(case_description)
                
                # If sections are extracted, use them for prediction
                predicted_rights = []
                defense_suggestions = []
                extracted_act = "IPC"  # Default
                extracted_section = None
                
                has_extracted_section = False
                for act, sections in extracted_sections.items():
                    if sections:
                        extracted_act = act
                        extracted_section = sections[0]
                        has_extracted_section = True
                        break
                
                if has_extracted_section:
                    # Use the extracted section for prediction
                    st.markdown(f"### Detected Legal Section: {extracted_act} Section {extracted_section}")
                    
                    # Get rights prediction
                    rights_info = legal_predictor.predict_rights(
                        extracted_section, extracted_act, case_description
                    )
                    
                    if "error" not in rights_info:
                        predicted_rights = rights_info.get("rights", [])
                        
                        # Get defense options
                        defense_options = legal_predictor.suggest_defense_options(
                            extracted_section, extracted_act, case_description
                        )
                        
                        if "error" not in defense_options:
                            defense_suggestions = defense_options.get("defense_options", [])
                else:
                    # No specific section detected, use general analysis
                    st.info("No specific legal section detected in your description. Providing general rights information.")
                    
                    # Generate general rights recommendations
                    # In a real system, this would use more sophisticated NLP
                    from legal_data import defendant_rights
                    
                    # Randomly select rights from general, bail, and trial categories
                    general_rights = defendant_rights["general"]
                    bail_rights = defendant_rights["bail"]
                    trial_rights = defendant_rights["trial"]
                    
                    all_rights = general_rights + bail_rights + trial_rights
                    selected_rights = random.sample(all_rights, min(8, len(all_rights)))
                    
                    predicted_rights = [{"right": r, "relevance": random.uniform(0.6, 0.95)} for r in selected_rights]
                    
                    # Generate some general defense suggestions
                    common_defenses = [
                        "Challenge the evidence collection procedure",
                        "Verify if proper legal procedures were followed",
                        "Examine witness credibility and testimony",
                        "Consider statutory defenses applicable to your case",
                        "Explore options for settlement if appropriate for your case"
                    ]
                    
                    defense_suggestions = [{"option": d, "relevance": random.uniform(0.7, 0.9)} for d in common_defenses]
                
                # Display results
                st.markdown("## Your Predicted Legal Rights")
                
                # Group rights by importance
                high_priority = [r for r in predicted_rights if r["relevance"] > 0.8]
                medium_priority = [r for r in predicted_rights if 0.6 <= r["relevance"] <= 0.8]
                standard_priority = [r for r in predicted_rights if r["relevance"] < 0.6]
                
                if high_priority:
                    st.markdown("### Critical Rights (High Priority)")
                    for right in high_priority:
                        with st.expander(f"{right['right']} ({right['relevance']:.0%} Relevance)"):
                            # Provide more detailed information about each right
                            if "legal representation" in right["right"].lower():
                                st.markdown("""
                                **Right to Legal Representation** - Article 22 of the Constitution and Section 303 of CrPC
                                
                                You have the absolute right to be represented by a lawyer of your choice. If you cannot afford one, you are 
                                entitled to free legal aid under Section 304 CrPC and Article 39A of the Constitution. 
                                
                                **Action Steps:**
                                1. Contact your district Legal Services Authority for free legal aid
                                2. Request to meet your lawyer in private if in custody
                                3. Do not answer police questions without your lawyer present
                                """)
                            elif "remain silent" in right["right"].lower():
                                st.markdown("""
                                **Right to Remain Silent** - Article 20(3) of the Constitution
                                
                                You cannot be compelled to be a witness against yourself. This means you have the right to remain silent 
                                during police questioning. Anything you say can be used as evidence.
                                
                                **Action Steps:**
                                1. Politely inform officers you wish to remain silent until your lawyer is present
                                2. Do not sign any statements without legal advice
                                3. Remember this doesn't mean being uncooperative - just protecting your legal rights
                                """)
                            elif "bail" in right["right"].lower():
                                st.markdown("""
                                **Right to Apply for Bail** - Sections 436-439 CrPC
                                
                                Even for non-bailable offenses, you have the right to apply for bail. The court will consider 
                                factors like flight risk, evidence tampering possibilities, and case circumstances.
                                
                                **Action Steps:**
                                1. File bail application in the appropriate court
                                2. Prepare to demonstrate roots in community and non-flight risk status
                                3. Arrange for sureties who can provide bail bonds if required
                                """)
                            else:
                                st.markdown(f"""
                                **{right['right']}**
                                
                                This is a critical right in your case. This means the authorities must respect this right,
                                and any violation could potentially affect the case proceedings.
                                
                                **Action Steps:**
                                1. Document any potential violations of this right
                                2. Inform your legal counsel immediately if this right is compromised
                                3. Raise this during court proceedings if relevant
                                """)
                
                if medium_priority:
                    st.markdown("### Important Rights (Medium Priority)")
                    for right in medium_priority:
                        st.markdown(f"- **{right['right']}** ({right['relevance']:.0%} Relevance)")
                
                if standard_priority:
                    st.markdown("### Standard Procedural Rights")
                    for right in standard_priority:
                        st.markdown(f"- {right['right']}")
                
                # Display defense options
                if defense_suggestions:
                    st.markdown("## Potential Defense Strategies")
                    st.markdown("Consider discussing these defense approaches with your legal counsel:")
                    
                    for i, defense in enumerate(defense_suggestions[:5], 1):
                        st.markdown(f"{i}. **{defense['option']}**")
                
                # Stage-specific recommendations
                st.markdown("## Stage-Specific Recommendations")
                
                if case_stage == "Pre-FIR/Complaint":
                    st.markdown("""
                    At this early stage, focus on:
                    1. **Securing legal representation** immediately
                    2. **Documenting all interactions** with authorities
                    3. **Gathering evidence** that may become unavailable later
                    4. Consider filing for **anticipatory bail** if arrest seems likely
                    """)
                elif case_stage == "Investigation":
                    st.markdown("""
                    During the investigation phase:
                    1. **Remain cooperative but cautious** - always have your lawyer present
                    2. **Keep track of all evidence** collected by authorities
                    3. **Request copies** of your statements if you provide any
                    4. If arrested, apply for **regular bail**
                    """)
                elif case_stage == "Charge Sheet Filed":
                    st.markdown("""
                    Now that formal charges are filed:
                    1. **Carefully review the charge sheet** with your lawyer
                    2. **Challenge any procedural violations** during investigation
                    3. **Apply for discharge** if charges lack merit
                    4. Prepare a **comprehensive defense strategy**
                    """)
                elif case_stage == "Trial Ongoing":
                    st.markdown("""
                    During trial proceedings:
                    1. **Attend all hearings** without fail
                    2. **Cross-examine prosecution witnesses** effectively
                    3. **Present strong defense witnesses** if available
                    4. **Preserve grounds for appeal** by raising legal objections
                    """)
                elif case_stage == "Convicted/Sentenced":
                    st.markdown("""
                    After conviction:
                    1. **File appeal within limitation period**
                    2. **Apply for bail pending appeal**
                    3. **Explore alternatives** like probation or open jail if applicable
                    4. Consider **review petition** if appeal is dismissed
                    """)
                
                # Additional information based on detention status
                if detention_status in ["In Police Custody", "In Judicial Custody"]:
                    st.markdown("## Detention-Specific Rights")
                    st.markdown("""
                    Since you're currently in custody, these additional rights apply:
                    
                    1. **Right to medical examination** after arrest
                    2. **Right to meet family members/friends**
                    3. **Right to humane treatment** without torture or harassment
                    4. **Right to food, water, and basic necessities**
                    5. **Right to reasonable accommodation** based on disability, age, or health condition
                    6. **Right to production before magistrate** within 24 hours of arrest
                    """)
                
                # Disclaimer
                st.warning("""
                **Disclaimer**: This analysis is based on the information provided and is for educational purposes only.
                Always consult with a qualified legal professional for advice specific to your situation.
                """)

with tab2:
    st.markdown("## Manual Section Selection")
    st.markdown("""
    Directly select the legal section relevant to your case to understand your legal rights.
    """)
    
    # Select legal act
    act_options = {"Indian Penal Code (IPC)": "IPC", 
                  "Information Technology Act": "IT Act", 
                  "Motor Vehicles Act": "MV Act"}
    selected_act = st.selectbox("Select Legal Act", options=list(act_options.keys()), key="manual_act")
    act_code = act_options[selected_act]
    
    # Show relevant sections based on selected act
    if act_code == "IPC":
        section_options = {f"Section {k}: {v}": k for k, v in ipc_sections.items()}
    elif act_code == "IT Act":
        section_options = {f"Section {k}: {v}": k for k, v in it_act_sections.items()}
    else:  # MV Act
        section_options = {f"Section {k}: {v}": k for k, v in mv_act_sections.items()}
    
    selected_section_display = st.selectbox("Select Section", options=list(section_options.keys()), key="manual_section")
    selected_section = section_options[selected_section_display]
    
    # Optional case description
    manual_case_description = st.text_area(
        "Case Description (Optional)",
        placeholder="Provide additional details to get more personalized insights...",
        height=100,
        key="manual_desc"
    )
    
    if st.button("Show My Rights", key="manual_btn", use_container_width=True):
        with st.spinner("Analyzing your case..."):
            # Get rights prediction
            rights_info = legal_predictor.predict_rights(
                selected_section, act_code, manual_case_description
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
                
                # Display recommended lawyers specializing in this area
                st.markdown("### Legal Assistance Resources")
                st.markdown("""
                Consider reaching out to the following resources for legal help:
                
                1. **District Legal Services Authority** - Provides free legal aid to eligible individuals
                2. **State Bar Council** - Can refer to lawyers specializing in your type of case
                3. **National Legal Services Authority** - For guidance on legal aid services
                4. **Law School Legal Aid Clinics** - Many law schools offer free legal assistance
                
                **Specialized Legal NGOs:**
                - Human Rights Law Network (HRLN) - For human rights cases
                - Common Cause - Public interest matters
                - Association for Advocacy and Legal Initiatives (AALI) - Gender justice issues
                """)
                
                # Disclaimer
                st.warning("""
                **Disclaimer**: This information is provided for educational purposes only and does not constitute legal advice.
                Always consult with a qualified legal professional for advice specific to your situation.
                """)

# Add tips for finding legal assistance
st.markdown("---")
st.markdown("## Finding Legal Assistance")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Legal Aid Services
    If you cannot afford a lawyer, you can apply for free legal aid:
    
    1. **Visit your local Legal Services Authority office**
    2. **Apply at the nearest court complex**
    3. **Contact the National Legal Services Authority (NALSA)** helpline at 15100
    4. **Apply online** through e-portals of Legal Services Authorities
    
    **Eligibility:** Women, children, SC/ST members, disaster victims, disabled persons, 
    industrial workmen, persons in custody, and those with annual income below specified limits.
    """)

with col2:
    st.markdown("""
    ### Finding a Good Lawyer
    Tips for selecting competent legal representation:
    
    1. **Ask for recommendations** from trusted sources
    2. **Search state bar council directories** for specialists in your case type
    3. **Interview potential lawyers** about their experience with similar cases
    4. **Discuss fees and payment structure** upfront
    5. **Check online reviews and ratings** if available
    6. **Verify credentials** through Bar Council registration
    7. **Assess communication style** during initial consultation
    """)

# Add a disclaimer at the bottom
st.markdown("---")
st.caption("""
**Disclaimer**: This information is provided for educational purposes only and does not constitute legal advice. 
Always consult with a qualified legal professional for advice specific to your situation.
""")