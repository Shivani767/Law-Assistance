import streamlit as st
import pandas as pd
from argument_generator import argument_generator
from model import legal_predictor
from legal_data import (
    ipc_sections, it_act_sections, mv_act_sections,
    get_offense_details, get_precedents_for_section, get_jurisdiction_info
)

st.set_page_config(
    page_title="Lawyer Assistant - Indian Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

st.title("Lawyer Assistant")
st.markdown("### Generate arguments and case strategies based on legal codes")

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Back to Home"):
    st.switch_page("app.py")

if st.sidebar.button("Legal Codes Reference"):
    st.switch_page("pages/legal_codes.py")

if st.sidebar.button("Search Legal Precedents"):
    st.switch_page("pages/search_precedents.py")

if st.sidebar.button("Bail Assistance"):
    st.switch_page("pages/bail_assistance.py")

# Create tabs for different functionalities
tab1, tab2, tab3, tab4 = st.tabs(["Argument Generator", "Case Analysis", "Precedent Finder", "Strategy Builder"])

with tab1:
    st.markdown("## Legal Argument Generator")
    st.markdown("""
    Generate legal arguments for defense or prosecution based on specific sections and case details.
    This tool helps lawyers prepare comprehensive arguments by analyzing legal provisions and precedents.
    """)
    
    # Input form for argument generation
    col1, col2 = st.columns(2)
    
    with col1:
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
        
        # Get section details to display
        section_details = get_offense_details(selected_section, act_code)
        if section_details:
            st.markdown(f"**{section_details.get('title', '')}**")
    
    with col2:
        # Case description
        case_description = st.text_area("Case Description", 
                                      placeholder="Describe the case facts and circumstances...",
                                      height=100)
        
        # Argument position
        position_options = {
            "Defense Arguments (for the accused)": True,
            "Prosecution Arguments (against the accused)": False
        }
        selected_position = st.radio("Generate Arguments For", options=list(position_options.keys()))
        favor_defense = position_options[selected_position]
        
        # Number of arguments
        num_arguments = st.slider("Number of Arguments", min_value=3, max_value=10, value=5)
    
    if st.button("Generate Arguments", use_container_width=True):
        if not case_description:
            st.warning("Please provide a case description to generate arguments.")
        else:
            with st.spinner("Generating legal arguments..."):
                # Generate arguments
                arguments_result = argument_generator.generate_arguments(
                    selected_section, act_code, case_description, favor_defense, num_arguments
                )
                
                if "error" in arguments_result:
                    st.error(arguments_result["error"])
                else:
                    # Display arguments
                    st.markdown(f"### {selected_position}")
                    arguments = arguments_result.get("arguments", [])
                    
                    for i, argument in enumerate(arguments, 1):
                        st.markdown(f"**Argument {i}:** {argument}")
                    
                    # Display supporting precedents if available
                    precedents = arguments_result.get("supporting_precedents", [])
                    if precedents:
                        st.markdown("### Supporting Legal Precedents")
                        for precedent in precedents:
                            with st.expander(f"{precedent['case_name']} ({precedent['citation']})"):
                                st.markdown(f"**Summary:** {precedent['summary']}")
                                st.markdown("**Key Points:**")
                                for point in precedent['key_points']:
                                    st.markdown(f"- {point}")
                    
                    # Additional information for context
                    with st.expander("Offense Details"):
                        offense_details = arguments_result.get("offense_details", {})
                        if offense_details:
                            st.markdown(f"**Section {selected_section}: {offense_details.get('title', '')}**")
                            st.markdown("**Defendant Rights:**")
                            for right in offense_details.get("rights", []):
                                st.markdown(f"- {right}")

with tab2:
    st.markdown("## Case Analysis")
    st.markdown("""
    Analyze case details to identify strengths, weaknesses, opportunities, and threats (SWOT analysis).
    This helps in preparing a comprehensive case strategy.
    """)
    
    # Case details form
    case_title = st.text_input("Case Title/Number")
    case_analysis_description = st.text_area("Case Facts and Description", 
                                           placeholder="Provide detailed facts of the case...",
                                           height=150)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Case type and relevant sections
        case_type = st.selectbox("Case Type", options=[
            "Criminal", "Civil", "Constitutional", "Family Law", 
            "Property Dispute", "Cybercrime", "Traffic Violation", "Other"
        ])
        
        representing = st.radio("Representing", options=["Defendant/Accused", "Plaintiff/Prosecution"])
    
    with col2:
        # Select legal acts and sections
        acts = st.multiselect("Relevant Acts", options=["IPC", "CrPC", "IT Act", "MV Act", "CPC", "Other"])
        
        sections_input = st.text_input("Relevant Sections (comma separated)", 
                                     placeholder="e.g., 302, 34, 120B")
    
    if st.button("Analyze Case", use_container_width=True):
        if not case_analysis_description:
            st.warning("Please provide case details for analysis.")
        else:
            with st.spinner("Analyzing case..."):
                # In a real application, this would use ML models for analysis
                # This is a simplified rule-based implementation for demonstration
                
                # Extract potential issues
                case_lower = case_analysis_description.lower()
                
                # Basic SWOT analysis based on keywords
                strengths = []
                weaknesses = []
                opportunities = []
                threats = []
                
                # Analyze for defense
                if representing == "Defendant/Accused":
                    # Check for potential strengths
                    if "no witness" in case_lower or "no eyewitness" in case_lower:
                        strengths.append("Lack of eyewitness testimony")
                    
                    if "alibi" in case_lower:
                        strengths.append("Potential alibi defense")
                    
                    if "inconsistent" in case_lower or "contradictory" in case_lower:
                        strengths.append("Inconsistencies in prosecution evidence")
                    
                    # Check for potential weaknesses
                    if "confession" in case_lower or "admitted" in case_lower:
                        weaknesses.append("Confession or admission by accused")
                    
                    if "caught red-handed" in case_lower or "direct evidence" in case_lower:
                        weaknesses.append("Strong direct evidence against accused")
                    
                    if "prior record" in case_lower or "previous conviction" in case_lower:
                        weaknesses.append("Prior criminal record may impact credibility")
                    
                    # Opportunities
                    opportunities.append("Challenge evidence collection procedure")
                    opportunities.append("Verify forensic evidence reliability")
                    opportunities.append("Examine witness credibility")
                    
                    # Threats
                    threats.append("New witnesses or evidence may emerge")
                    threats.append("Bail may be difficult if offense is serious")
                    threats.append("Media coverage may influence public perception")
                
                # Analyze for prosecution
                else:
                    # Strengths
                    if "witness" in case_lower or "eyewitness" in case_lower:
                        strengths.append("Eyewitness testimony available")
                    
                    if "evidence" in case_lower or "proof" in case_lower:
                        strengths.append("Material evidence supports the case")
                    
                    if "confession" in case_lower or "admitted" in case_lower:
                        strengths.append("Confession or admission by accused")
                    
                    # Weaknesses
                    if "delay" in case_lower:
                        weaknesses.append("Delay in reporting or investigation")
                    
                    if "no forensic" in case_lower:
                        weaknesses.append("Lack of forensic evidence")
                    
                    if "contradict" in case_lower or "inconsistent" in case_lower:
                        weaknesses.append("Potential contradictions in witness statements")
                    
                    # Opportunities
                    opportunities.append("Gather additional corroborative evidence")
                    opportunities.append("Request for expedited trial")
                    opportunities.append("Oppose bail application if appropriate")
                    
                    # Threats
                    threats.append("Defense may challenge evidence admissibility")
                    threats.append("Witnesses may turn hostile")
                    threats.append("Technical procedural issues may delay proceedings")
                
                # Display SWOT analysis
                st.markdown(f"### SWOT Analysis for: {case_title}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Strengths")
                    for item in strengths:
                        st.markdown(f"- {item}")
                    
                    st.markdown("#### Opportunities")
                    for item in opportunities:
                        st.markdown(f"- {item}")
                
                with col2:
                    st.markdown("#### Weaknesses")
                    for item in weaknesses:
                        st.markdown(f"- {item}")
                    
                    st.markdown("#### Threats")
                    for item in threats:
                        st.markdown(f"- {item}")
                
                # Recommended strategy
                st.markdown("### Recommended Strategy")
                
                if representing == "Defendant/Accused":
                    st.markdown("""
                    1. **Challenge evidence collection procedure** - Verify if all legal protocols were followed
                    2. **Focus on burden of proof** - Emphasize prosecution's responsibility to prove beyond reasonable doubt
                    3. **Explore alternative narratives** - Present alternative explanation of events
                    4. **Examine witness credibility** - Look for inconsistencies in testimonies
                    5. **Consider technical defenses** - Procedural or jurisdictional challenges if applicable
                    """)
                else:
                    st.markdown("""
                    1. **Strengthen witness testimony** - Prepare witnesses thoroughly
                    2. **Ensure all evidence is properly documented** - Maintain clear chain of custody
                    3. **Anticipate defense strategies** - Prepare counter-arguments
                    4. **Establish clear timeline** - Present a coherent narrative of events
                    5. **Focus on motive and opportunity** - Connect evidence to establish these elements
                    """)
                
                # Next steps
                st.markdown("### Recommended Next Steps")
                
                if representing == "Defendant/Accused":
                    st.markdown("""
                    1. Conduct detailed client interview to gather all facts
                    2. File for discovery of prosecution evidence
                    3. Consider bail application if currently in custody
                    4. Interview potential defense witnesses
                    5. Consult experts if technical or forensic evidence is involved
                    """)
                else:
                    st.markdown("""
                    1. Complete evidence collection and documentation
                    2. Prepare witnesses for testimony
                    3. Coordinate with investigating officers for any pending tasks
                    4. Prepare arguments opposing bail if appropriate
                    5. Review similar case precedents to strengthen arguments
                    """)

with tab3:
    st.markdown("## Legal Precedent Finder")
    st.markdown("""
    Find relevant legal precedents that can support your case arguments. 
    Enter a case description to find similar precedent cases from Indian courts.
    """)
    
    # Case description for precedent search
    precedent_query = st.text_area("Case Description", 
                                 placeholder="Describe the legal issues in your case...",
                                 height=150)
    
    # Optional filters
    col1, col2 = st.columns(2)
    
    with col1:
        # Optional section filter
        precedent_act = st.selectbox("Filter by Act (Optional)", 
                                   options=["Any", "IPC", "IT Act", "MV Act"])
    
    with col2:
        # Optional section filter
        precedent_section = st.text_input("Filter by Section (Optional)", 
                                        placeholder="e.g., 302")
    
    if st.button("Find Precedents", use_container_width=True):
        if not precedent_query:
            st.warning("Please provide a case description to search for precedents.")
        else:
            with st.spinner("Searching for relevant legal precedents..."):
                # Convert "Any" to None for the filter
                act_filter = None if precedent_act == "Any" else precedent_act
                section_filter = precedent_section if precedent_section else None
                
                # Find similar precedents
                similar_precedents = legal_predictor.find_similar_precedents(
                    precedent_query, section_filter, act_filter
                )
                
                if "error" in similar_precedents:
                    st.error(similar_precedents["error"])
                elif not similar_precedents.get("precedents"):
                    st.info("No relevant precedents found. Try broadening your search or using different keywords.")
                else:
                    precedents = similar_precedents.get("precedents", [])
                    
                    st.markdown(f"### Found {len(precedents)} Relevant Precedents")
                    
                    for i, precedent in enumerate(precedents, 1):
                        # Calculate a visual representation of similarity if available
                        similarity_str = ""
                        if "similarity" in precedent:
                            similarity = precedent["similarity"]
                            similarity_str = f" (Relevance: {similarity:.0%})"
                        
                        with st.expander(f"{i}. {precedent['case_name']}{similarity_str}"):
                            st.markdown(f"**Citation:** {precedent['citation']}")
                            st.markdown(f"**Summary:** {precedent['summary']}")
                            
                            st.markdown("**Key Points:**")
                            for point in precedent['key_points']:
                                st.markdown(f"- {point}")
                            
                            st.markdown("**Application to Your Case:**")
                            st.markdown("""
                            This precedent may be relevant to your case in establishing legal principles
                            regarding the interpretation and application of the law. Consider citing
                            this case in your arguments if the facts and legal issues align with your situation.
                            """)

with tab4:
    st.markdown("## Case Strategy Builder")
    st.markdown("""
    Build a comprehensive case strategy by identifying key legal issues, evidence requirements,
    procedural steps, and timeline planning.
    """)
    
    # Strategy form
    strategy_case_name = st.text_input("Case Name/Number", placeholder="e.g., State vs. John Doe")
    
    # Case type selection
    strategy_case_type = st.selectbox("Case Type", options=[
        "Criminal Trial", "Criminal Appeal", "Civil Suit", "Civil Appeal", 
        "Bail Application", "Anticipatory Bail", "Writ Petition", "Other"
    ])
    
    # Forum selection
    forum_options = [
        "Magistrate Court", "Sessions Court", "District Court",
        "High Court", "Supreme Court", "Special Court", "Tribunal"
    ]
    strategy_forum = st.selectbox("Forum", options=forum_options)
    
    # Case strategy description
    strategy_description = st.text_area("Case Brief", 
                                      placeholder="Summarize the case facts and key legal issues...",
                                      height=100)
    
    # Create columns for organized input
    col1, col2 = st.columns(2)
    
    with col1:
        # Evidence planning
        st.markdown("### Evidence Planning")
        
        evidence_types = st.multiselect("Evidence Types Required", options=[
            "Documentary Evidence", "Witness Testimony", "Expert Opinion",
            "Electronic Evidence", "Physical Evidence", "Medical Reports",
            "Official Records", "Financial Documents"
        ])
        
        key_witnesses = st.text_area("Key Witnesses", height=80, 
                                   placeholder="List important witnesses and their relevance")
    
    with col2:
        # Procedural strategy
        st.markdown("### Procedural Strategy")
        
        procedural_steps = st.multiselect("Anticipated Procedural Steps", options=[
            "Filing", "Service of Process", "Appearance", "Written Statement",
            "Evidence Recording", "Arguments", "Judgment", "Execution",
            "Appeal Preparation", "Interlocutory Applications"
        ])
        
        timeline_estimate = st.text_area("Timeline Estimate", height=80, 
                                      placeholder="Estimated timeline for key procedural milestones")
    
    # Legal issues identification
    st.markdown("### Legal Issues")
    legal_issues = st.text_area("Key Legal Issues to Address", 
                              placeholder="List the primary legal questions and issues in this case...",
                              height=100)
    
    if st.button("Generate Strategy Document", use_container_width=True):
        if not strategy_description or not legal_issues:
            st.warning("Please fill in the case brief and legal issues to generate a strategy.")
        else:
            with st.spinner("Generating comprehensive case strategy..."):
                # Here we would normally use ML models to analyze inputs and generate strategy
                # For this demo, we'll create a structured document based on inputs
                
                # Create strategy document
                st.markdown(f"## Case Strategy: {strategy_case_name}")
                st.markdown(f"**Case Type:** {strategy_case_type} | **Forum:** {strategy_forum}")
                
                st.markdown("### Case Summary")
                st.markdown(strategy_description)
                
                st.markdown("### Key Legal Issues")
                issues_list = legal_issues.split("\n")
                for i, issue in enumerate(issues_list, 1):
                    if issue.strip():
                        st.markdown(f"{i}. {issue}")
                
                st.markdown("### Evidence Strategy")
                
                if evidence_types:
                    st.markdown("#### Required Evidence Types")
                    for evidence in evidence_types:
                        actions = {
                            "Documentary Evidence": "Collect, authenticate, and organize all relevant documents",
                            "Witness Testimony": "Prepare witness statements and conduct pre-trial interviews",
                            "Expert Opinion": "Identify and engage qualified experts in relevant fields",
                            "Electronic Evidence": "Ensure proper forensic collection and authentication",
                            "Physical Evidence": "Document chain of custody and arrange proper storage",
                            "Medical Reports": "Obtain complete medical files and expert interpretation",
                            "Official Records": "File RTI applications or court requests as needed",
                            "Financial Documents": "Organize chronologically and prepare analysis"
                        }
                        st.markdown(f"- **{evidence}**: {actions.get(evidence, 'Collect and analyze')}")
                
                if key_witnesses:
                    st.markdown("#### Witness Strategy")
                    witnesses = key_witnesses.split("\n")
                    for witness in witnesses:
                        if witness.strip():
                            st.markdown(f"- {witness}")
                
                st.markdown("### Procedural Roadmap")
                
                if procedural_steps:
                    for step in procedural_steps:
                        guidelines = {
                            "Filing": "Ensure all required documents are complete and properly verified",
                            "Service of Process": "Follow proper service procedure to avoid procedural challenges",
                            "Appearance": "Ensure timely appearance at all hearings",
                            "Written Statement": "Draft comprehensive response addressing all claims/charges",
                            "Evidence Recording": "Prepare witnesses and organize evidence presentation",
                            "Arguments": "Structure arguments logically, focusing on strongest points first",
                            "Judgment": "Analyze for potential grounds of appeal or execution",
                            "Execution": "Prepare necessary applications for effective execution",
                            "Appeal Preparation": "Identify grounds for appeal and collect required documents",
                            "Interlocutory Applications": "Prepare supporting evidence and legal arguments"
                        }
                        st.markdown(f"- **{step}**: {guidelines.get(step, 'Plan and execute properly')}")
                
                if timeline_estimate:
                    st.markdown("#### Timeline Planning")
                    timeline_points = timeline_estimate.split("\n")
                    for point in timeline_points:
                        if point.strip():
                            st.markdown(f"- {point}")
                
                # Risk assessment and mitigation
                st.markdown("### Risk Assessment and Mitigation")
                
                # Create a simple risk matrix based on case type
                risks = []
                
                if "Criminal" in strategy_case_type:
                    risks.extend([
                        "Witness turning hostile",
                        "Procedural delays affecting custody status",
                        "Evidence admissibility challenges",
                        "Co-accused turning approver"
                    ])
                elif "Civil" in strategy_case_type:
                    risks.extend([
                        "Delay tactics by opposing party",
                        "Missing documentary evidence",
                        "Jurisdiction challenges",
                        "Counter-claims or set-off defenses"
                    ])
                elif "Bail" in strategy_case_type:
                    risks.extend([
                        "New facts emerging affecting bail consideration",
                        "Public pressure in high-profile cases",
                        "Previous bail history affecting current application",
                        "Flight risk perception"
                    ])
                
                # Add common risks
                risks.extend([
                    "Unexpected legal precedents from recent judgments",
                    "Resource constraints affecting case preparation",
                    "Communication gaps with client"
                ])
                
                for risk in risks:
                    st.markdown(f"- **{risk}**: Develop contingency plan and preemptive measures")
                
                # Success metrics
                st.markdown("### Success Metrics and Evaluation")
                st.markdown("""
                - **Primary Objective**: Define clear primary goal for the case
                - **Acceptable Outcomes**: Identify alternative satisfactory resolutions
                - **Ongoing Evaluation**: Regular case review at key milestones
                - **Client Communication**: Regular updates on strategy implementation
                - **Documentation**: Maintain comprehensive case diary for learning
                """)

# Add a disclaimer at the bottom
st.markdown("---")
st.caption("""
**Disclaimer**: This tool provides assistance for legal professionals but does not replace professional legal judgment. 
The arguments and strategies generated should be reviewed and adapted based on specific case circumstances.
""")
