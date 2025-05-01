import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
from utils import load_svg

# Configure the page
st.set_page_config(
    page_title="Indian Legal Assistant | NYĀYA",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Footer Styles */
    .footer-disclaimer {
        background: rgba(255, 255, 255, 0.8);
        border-top: 1px solid rgba(0, 51, 102, 0.1);
        padding: 20px;
        text-align:center;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 100;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        animation: footerSlideUp 0.8s ease-out;
    }

    .footer-disclaimer strong {
        color: #003366;
        font-weight: 600;
    }

    .footer-copyright {
        text-align: center;
        color: #4a5568;
        font-size: 0.9rem;
        margin-top: 10px;
        opacity: 0.8;
    }

    @keyframes footerSlideUp {
        from { transform: translateY(100%); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }

    /* Global Styles */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
        background-size: 200% 200%;
        animation: gradientBG 15s ease infinite;
        color: #2c3e50;
        transition: all 0.3s ease;
    }
    
    /* Glassmorphism Base */
    .stApp {
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        animation: fadeIn 1s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Header Styles */
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(45deg, #003366 30%, #0066cc 90%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
        font-weight: 700;
        letter-spacing: -0.5px;
        animation: fadeIn 0.8s ease-out, glow 2s ease-in-out infinite alternate;
    }
    
    .sub-header {
        font-size: 1.3rem;
        color: #4a5568;
        text-align: center;
        margin-top: 5px;
        font-style: italic;
        opacity: 0.9;
        animation: slideUp 0.6s ease-out;
    }
    
    /* Card Styles */
    @keyframes cardEntrance {
        from {
            opacity: 0;
            transform: translateY(20px);
            filter: blur(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
            filter: blur(0);
        }
    }

    .dashboard-card {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        animation: cardEntrance 0.8s ease-out forwards;
    }
    
    .dashboard-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            to right,
            transparent,
            rgba(255, 255, 255, 0.2),
            transparent
        );
        transition: 0.5s;
        pointer-events: none;
    }
    
    .dashboard-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    .dashboard-card:hover::before {
        left: 100%;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        border: 1px solid rgba(0, 51, 102, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            to right,
            transparent,
            rgba(0, 51, 102, 0.05),
            transparent
        );
        transition: 0.5s;
        pointer-events: none;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card:hover::before {
        left: 100%;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(45deg, #003366 30%, #0066cc 90%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            transform: scale(1);
        }
    }
    
    .metric-label {
        font-size: 1rem;
        color: #4a5568;
        font-weight: 500;
    }
    
    /* Button Styles */
    @keyframes buttonPulse {
        0% { transform: scale(1); box-shadow: 0 4px 15px rgba(0, 51, 102, 0.2); }
        50% { transform: scale(1.02); box-shadow: 0 8px 25px rgba(0, 51, 102, 0.3); }
        100% { transform: scale(1); box-shadow: 0 4px 15px rgba(0, 51, 102, 0.2); }
    }

    .nav-button {
        width: 100%;
        border-radius: 12px;
        margin-bottom: 15px;
        background: linear-gradient(135deg, #003366 0%, #004c99 100%);
        color: white;
        padding: 15px 25px;
        font-weight: 600;
        letter-spacing: 0.8px;
        border: none;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        box-shadow: 0 4px 15px rgba(0, 51, 102, 0.2);
        position: relative;
        overflow: hidden;
        z-index: 1;
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        animation: buttonPulse 3s infinite;
        background: linear-gradient(45deg, #003366 30%, #004c99 90%);
        color: white;
        padding: 12px 20px;
        font-weight: 600;
        letter-spacing: 0.5px;
        border: none;
        transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
        box-shadow: 0 4px 15px rgba(0, 51, 102, 0.2);
        position: relative;
        overflow: hidden;
        z-index: 1;
        animation: buttonPulse 2s infinite;
    }
    
    .nav-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, #004c99 30%, #0066cc 90%);
        transition: 0.5s;
        opacity: 0;
        z-index: -1;
    }
    
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 51, 102, 0.25);
    }
    
    .nav-button:hover::before {
        opacity: 1;
    }
    
    /* Section Styles */
    @keyframes sectionSlide {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    .popular-section {
        background: linear-gradient(to right, #f8f9fa, #ffffff);
        border-left: 4px solid #003366;
        border-radius: 0 8px 8px 0;
        padding: 12px 20px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        position: relative;
        overflow: hidden;
        animation: sectionSlide 0.6s ease-out forwards;
    }
    
    .popular-section::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            to right,
            transparent,
            rgba(0, 51, 102, 0.03),
            transparent
        );
        transform: translateX(-100%);
        transition: transform 0.6s ease;
    }
    
    .popular-section:hover {
        background: linear-gradient(to right, #f0f4f8, #ffffff);
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    .popular-section:hover::after {
        transform: translateX(100%);
    }
    
    /* Footer Styles */
    @keyframes footerFade {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .footer {
        font-size: 0.9rem;
        color: #4a5568;
        text-align: center;
        padding: 25px 0;
        margin-top: 50px;
        border-top: 1px solid rgba(0, 51, 102, 0.1);
        background: linear-gradient(to top, rgba(245, 247, 250, 0.8), transparent);
        animation: footerFade 1s ease-out forwards;
    }
    #footer{
        display : flex;
        align-items: end;
        justify-content : center;
        text-align : center;
  
    }
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideUp {
        from { 
            opacity: 0;
            transform: translateY(20px);
        }
        to { 
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes glow {
        from {
            text-shadow: 0 0 5px rgba(0, 51, 102, 0.2),
                         0 0 10px rgba(0, 51, 102, 0.2),
                         0 0 15px rgba(0, 51, 102, 0.2);
        }
        to {
            text-shadow: 0 0 10px rgba(0, 51, 102, 0.4),
                         0 0 20px rgba(0, 51, 102, 0.4),
                         0 0 30px rgba(0, 51, 102, 0.4);
        }
    }
</style>
""", unsafe_allow_html=True)

# Display logo with responsive styling
try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("assets/logo.svg", use_container_width=True)
except Exception as e:
    st.warning("Logo could not be loaded. Please ensure the logo file exists in the assets directory.")
    st.markdown("# NYĀYA: Indian Legal Assistant")

# Main title with custom styling
st.markdown('<h1 class="main-header">NYĀYA: Indian Legal Assistance System</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Navigate the complexities of Indian law with AI assistance</p>', unsafe_allow_html=True)

# Enhanced search interface with glassmorphism
st.markdown("""
<div class='search-container'>
    <div style='max-width: 800px; margin: 0 auto;'>
        <h3 style='color: #003366; margin-bottom: 20px; text-align: center;'>Search the Indian Legal System</h3>
        <div style='position: relative;'>
            <div class='search-box-container'>
                <style>
                    .search-box-container { position: relative; margin-bottom: 20px; }
                    .search-box {
                        width: 100%;
                        padding: 15px 25px;
                        font-size: 1.1rem;
                        border: 2px solid rgba(0, 51, 102, 0.1);
                        border-radius: 15px;
                        background: rgba(255, 255, 255, 0.9);
                        backdrop-filter: blur(10px);
                        -webkit-backdrop-filter: blur(10px);
                        transition: all 0.3s ease;
                    }
                    .search-box:focus {
                        outline: none;
                        border-color: #003366;
                        box-shadow: 0 0 20px rgba(0, 51, 102, 0.15);
                        transform: scale(1.01);
                    }
                    .search-button {
                        position: absolute;
                        right: 10px;
                        top: 50%;
                        transform: translateY(-50%);
                        padding: 10px 25px;
                        background: linear-gradient(135deg, #003366 0%, #004c99 100%);
                        color: white;
                        border: none;
                        border-radius: 10px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    }
                    .search-button:hover {
                        transform: translateY(-50%) scale(1.05);
                        box-shadow: 0 5px 15px rgba(0, 51, 102, 0.2);
                    }
                </style>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Search functionality
search_col1, search_col2 = st.columns([3, 1])
with search_col1:
    search_placeholder = "Search cases, sections, legal codes, precedents..."
    search_query = st.text_input("Search", placeholder=search_placeholder, label_visibility="collapsed")

with search_col2:
    if st.button("Search", key="search_button", use_container_width=True):
        if search_query:
            st.session_state.search_query = search_query
            st.switch_page("pages/case_search.py")

# Handle search query submission via Enter key
if search_query:
    # Redirect to case search with the query pre-filled
    st.session_state.search_query = search_query
    st.switch_page("pages/case_search.py")

# Application description
st.markdown("""
This system provides comprehensive legal assistance for both defendants and legal professionals.
- **For defendants**: Understand your legal rights, explore defense options, and learn about the legal process
- **For lawyers**: Generate arguments, search precedents, and prepare case strategies efficiently
""")

# Main navigation cards
col1, col2 = st.columns(2)

with col1:
    st.subheader("For Defendants")
    st.markdown("""
    - Understand your legal rights
    - Explore defense options based on your case
    - Learn about bail procedures
    - Get information about jurisdiction and appeals
    """)
    col11, col12, col13 = st.columns(3)
    with col11:
        if st.button('🔍 Defendant Rights', key='defendant_rights_btn', use_container_width=True):
            st.switch_page('pages/defendant_rights.py')
    with col12:
        if st.button('🧠 Rights Predictor', key='rights_predictor_btn', use_container_width=True):
            st.switch_page('pages/rights_predictor.py')
    with col13:
        if st.button('📱 Notifications', key='notifications_btn', use_container_width=True):
            st.switch_page('pages/notifications.py')

with col2:
    st.subheader("For Lawyers")
    st.markdown("""
    - Generate arguments for and against specific cases
    - Search legal precedents from Supreme Court cases
    - Access IPC, IT Act, and MV Act information
    - Get assistance with bail applications
    """)
    col21, col22 = st.columns(2)
    with col21:
        if st.button('⚖️ Lawyer Assistant', key='lawyer_assistant_btn', use_container_width=True):
            st.switch_page('pages/lawyer_assistant.py')
    with col22:
        if st.button('📝 Bail Assistant', key='bail_assistant_btn', use_container_width=True):
            st.switch_page('pages/bail_assistance.py')

# Second row for case services
st.markdown("---")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Case Services")
    st.markdown("""
    - Search cases across jurisdictions
    - Find appropriate court for your case
    - Track case status and updates
    - Understand jurisdiction rules
    """)
    col31, col32 = st.columns(2)
    with col31:
        if st.button('🔎 Case Search', key='case_search_btn', use_container_width=True):
            st.switch_page('pages/case_search.py')
    with col32:
        if st.button('🏛️ Jurisdiction Guide', key='jurisdiction_guide_btn', use_container_width=True):
            st.switch_page('pages/jurisdiction_assistant.py')

with col4:
    st.subheader("Legal Reference")
    st.markdown("""
    - Access legal codes and sections
    - Search legal precedents
    - Understand legal terminology
    - Find applicable sections for your case
    """)
    col41, col42 = st.columns(2)
    with col41:
        if st.button('📚 Legal Codes', key='legal_codes_btn', use_container_width=True):
            st.switch_page('pages/legal_codes.py')
    with col42:
        if st.button('🔖 Search Precedents', key='search_precedents_btn', use_container_width=True):
            st.switch_page('pages/search_precedents.py')

# Popular sections widget with modern design
st.markdown("""
<div class='popular-sections-container'>
    <style>
        .popular-sections-container {
            padding: 30px 20px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 51, 102, 0.1);
            margin: 30px 0;
        }
        
        .section-title {
            font-size: 1.8rem;
            background: linear-gradient(45deg, #003366 30%, #0066cc 90%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 25px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        
        .section-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 10px;
        }
        
        .section-card {
            background: rgba(255, 255, 255, 0.7);
            border-radius: 15px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .section-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                to right,
                transparent,
                rgba(255, 255, 255, 0.2),
                transparent
            );
            transition: 0.5s;
        }
        
        .section-card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 12px 30px rgba(0, 51, 102, 0.15);
            background: rgba(255, 255, 255, 0.9);
        }
        
        .section-card:hover::before {
            left: 100%;
        }
        
        .section-code {
            font-size: 1.2rem;
            font-weight: 600;
            color: #003366;
            margin-bottom: 8px;
        }
        
        .section-name {
            font-size: 1rem;
            color: #4a5568;
            font-weight: 500;
        }
    </style>
    
    <h3 class='section-title'>Commonly Searched Legal Sections</h3>
    <div class='section-grid'>
""", unsafe_allow_html=True)

# Create a grid of common legal sections
popular_sections = {
    "IPC 302: Murder": "pages/legal_codes.py",
    "IPC 420: Cheating": "pages/legal_codes.py",
    "IPC 376: Rape": "pages/legal_codes.py", 
    "IPC 498A: Cruelty by Husband": "pages/legal_codes.py",
    "IT Act 66: Cybercrime": "pages/legal_codes.py",
    "MV Act 184: Dangerous Driving": "pages/legal_codes.py"
}

for section, page in popular_sections.items():
    section_code = section.split(":")[0].strip()
    section_name = section.split(":")[1].strip()
    act = section_code.split(" ")[0]
    number = section_code.split(" ")[1]
    
    # Create a clickable card with modern styling
    st.markdown(f"""
    <div class='section-card' onclick='handleSectionClick("{act}", "{number}", "{page}")'>
        <div class='section-code'>{section_code}</div>
        <div class='section-name'>{section_name}</div>
    </div>
    """, unsafe_allow_html=True)

# Close the container
st.markdown("</div></div>", unsafe_allow_html=True)

# Add JavaScript for handling clicks
st.markdown("""
<script>
    function handleSectionClick(act, number, page) {
        // Update session state and navigate
        const event = new CustomEvent('section_selected', {
            detail: { act: act, number: number, page: page }
        });
        window.dispatchEvent(event);
    }
</script>
""", unsafe_allow_html=True)
# Enhanced footer with modern design
st.markdown("""
<footer class="modern-footer">
    <div class="footer-grid">
        <div class="footer-section">
            <h4 class="footer-title">About NYĀYA</h4>
            <p class="footer-text">NYĀYA is a comprehensive legal assistance system designed to help navigate the complexities of Indian law. The platform provides tools for defendants, lawyers, and legal professionals.</p>
        </div>
        <div class="footer-section">
            <h4 class="footer-title">Contact</h4>
            <div class="footer-contact">
                <div class="contact-item">
                    <span>📧</span>
                    <span>shivanibhandari9991@gmail.com</span>
                </div>
                <div class="contact-item">
                    <span>📍</span>
                    <span>Mohali, Punjab, India</span>
                </div> 
                <br><br>
                 <div class="disclaimer-content"><p>
            <strong>Disclaimer:</strong> This AI legal assistant is designed to provide general legal information and guidance.
            It is not a substitute for professional legal advice. Please consult with a qualified lawyer for specific legal matters.
        </div>
            </div>
        </div>    
        
   
    
<footer>
<div class="footer-disclaimer">
        © 2025 NYĀYA Legal Systems by Shivani Bhandari 
         </div>
</footer>
""", unsafe_allow_html=True)
# Resources section
st.sidebar.title("Resources")
# External resources with multiple reliable sources
st.sidebar.markdown("### External Resources")

# IPC with alternative sources
st.sidebar.markdown("""
📚 Indian Penal Code:
- <a href="https://www.indiacode.nic.in/handle/123456789/2263" target="_blank">India Code Repository</a>
- <a href="https://www.scconline.com/Members/NLDSearch.aspx" target="_blank">SCC Online</a>
- <a href="https://www.latestlaws.com/bare-acts/central-acts-rules/criminal-laws/indian-penal-code-1860" target="_blank">Latest Laws Portal</a>

💻 Information Technology Act:
- <a href="https://www.indiacode.nic.in/handle/123456789/1999" target="_blank">India Code Repository</a>
- <a href="https://www.scconline.com/Members/BareActsSearch.aspx" target="_blank">SCC Online</a>
- <a href="https://www.latestlaws.com/bare-acts/central-acts-rules/criminal-laws/information-technology-act-2000" target="_blank">Latest Laws Portal</a>

🚗 Motor Vehicles Act:
- <a href="https://www.indiacode.nic.in/handle/123456789/1798" target="_blank">India Code Repository</a>
- <a href="https://www.scconline.com/Members/BareActsSearch.aspx" target="_blank">SCC Online</a>
- <a href="https://parivahan.gov.in/parivahan/en/content/acts-and-rules-0" target="_blank">Transport Department</a>

⚖️ Supreme Court Cases:
- <a href="https://main.sci.gov.in/judgments" target="_blank">Supreme Court of India</a>
- <a href="https://www.scconline.com/Members/NLDSearch.aspx" target="_blank">SCC Online</a>
- <a href="https://indiankanoon.org/supremecourt/" target="_blank">Indian Kanoon</a>
- <a href="https://www.judis.nic.in/supremecourt/chejudis.aspx" target="_blank">JUDIS</a>
- <a href="https://doj.gov.in/judgments-supreme-court-india" target="_blank">Department of Justice</a>
""", unsafe_allow_html=True)

# Quick links
st.sidebar.title("Quick Links")

# Defendant Resources
st.sidebar.markdown("### For Defendants:")
st.sidebar.page_link("pages/defendant_rights.py", label="👤 Defendant Rights", use_container_width=True)
st.sidebar.page_link("pages/rights_predictor.py", label="🔮 Rights Predictor", use_container_width=True)
st.sidebar.page_link("pages/bail_assistance.py", label="🔓 Bail Assistance", use_container_width=True)
st.sidebar.page_link("pages/notifications.py", label="📱 Notifications", use_container_width=True)

# Lawyer Resources
st.sidebar.markdown("### For Lawyers:")
st.sidebar.page_link("pages/lawyer_assistant.py", label="⚖️ Lawyer Assistant", use_container_width=True)
st.sidebar.page_link("pages/search_precedents.py", label="🔖 Search Precedents", use_container_width=True)

# Reference Resources
st.sidebar.markdown("### Legal Reference:")
st.sidebar.page_link("pages/legal_codes.py", label="📚 Legal Codes", use_container_width=True)
st.sidebar.page_link("pages/case_search.py", label="🔎 Case Search", use_container_width=True)
st.sidebar.page_link("pages/jurisdiction_assistant.py", label="🏛️ Jurisdiction Assistant", use_container_width=True)
#  python -m streamlit run app.py
#  $env:TWILIO_ACCOUNT_SID = "ACca8293fa1e0fe2388b9124408390074b"
#  $env:TWILIO_AUTH_TOKEN = "75d5cb067390ca6f92ae280a0d06bcb8"
#  $env:TWILIO_PHONE_NUMBER = "+1 229 441 9981"
