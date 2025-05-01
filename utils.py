import streamlit as st
import pandas as pd
import numpy as np
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import json
import os

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

# Ensure NLTK data is downloaded
print("Downloading NLTK resources if needed...")
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

def load_svg(file_path):
    """Load an SVG file and return its contents as a string."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        st.error(f"Error loading SVG file: {e}")
        return ""

def preprocess_text(text):
    """
    Preprocess text by removing special characters, converting to lowercase,
    tokenizing, and removing stopwords.
    """
    if pd.isna(text) or text is None:
        return ""
    
    # Convert to string if it's not already
    text = str(text)
    
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # Rejoin tokens
    return ' '.join(tokens)

def extract_section_numbers(text):
    """Extract IPC, IT Act, or MV Act section numbers from text."""
    # Pattern for IPC sections (e.g., Section 302, Section 376, etc.)
    ipc_pattern = r'section\s+(\d+[A-Za-z]*)(?:\s+of\s+(?:the\s+)?(?:Indian\s+Penal\s+Code|IPC))?'
    
    # Pattern for IT Act sections
    it_pattern = r'section\s+(\d+[A-Za-z]*)(?:\s+of\s+(?:the\s+)?(?:Information\s+Technology\s+Act|IT\s+Act))?'
    
    # Pattern for MV Act sections
    mv_pattern = r'section\s+(\d+[A-Za-z]*)(?:\s+of\s+(?:the\s+)?(?:Motor\s+Vehicles\s+Act|MV\s+Act))?'
    
    # Find all matches
    ipc_sections = re.findall(ipc_pattern, text, re.IGNORECASE)
    it_sections = re.findall(it_pattern, text, re.IGNORECASE)
    mv_sections = re.findall(mv_pattern, text, re.IGNORECASE)
    
    return {
        'IPC': list(set(ipc_sections)),
        'IT Act': list(set(it_sections)),
        'MV Act': list(set(mv_sections))
    }

def calculate_similarity(text1, text2):
    """
    Calculate cosine similarity between two preprocessed text documents
    using a simple bag-of-words approach.
    """
    # Create vocabulary
    vocab = set(text1.split() + text2.split())
    
    # Create vectors
    vec1 = np.zeros(len(vocab))
    vec2 = np.zeros(len(vocab))
    
    # Fill vectors
    for i, word in enumerate(vocab):
        if word in text1.split():
            vec1[i] = 1
        if word in text2.split():
            vec2[i] = 1
    
    # Calculate cosine similarity
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 * norm2 == 0:
        return 0
    
    return dot_product / (norm1 * norm2)

def format_legal_section(section_text):
    """Format legal section text with proper indentation and structure."""
    if not section_text:
        return ""
    
    lines = section_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if re.match(r'^[0-9]+\.', line):  # If line starts with a number followed by a period
            formatted_lines.append(f"**{line}**")
        elif re.match(r'^[a-zA-Z]\)', line):  # If line starts with a letter followed by a parenthesis
            formatted_lines.append(f"- {line}")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def load_legal_data(act_type):
    """
    Load legal data for the specified act type.
    This is a placeholder that would load from a database in production.
    """
    # In a real application, this would load from a database or API
    # For now, we'll return limited placeholder data
    
    if act_type == "IPC":
        sections = {
            "302": {
                "title": "Punishment for murder",
                "description": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
                "rights": [
                    "Right to legal representation",
                    "Right to present evidence in defense",
                    "Right to cross-examine witnesses",
                    "Right to appeal to higher courts"
                ],
                "defense_options": [
                    "Claim of self-defense",
                    "Alibi defense",
                    "Mental health defense",
                    "Challenge the evidence"
                ]
            },
            "376": {
                "title": "Punishment for rape",
                "description": "Whoever commits rape shall be punished with rigorous imprisonment of either description for a term which shall not be less than seven years, but which may extend to imprisonment for life, and shall also be liable to fine.",
                "rights": [
                    "Right to legal representation",
                    "Right to in-camera trial",
                    "Right to present evidence in defense",
                    "Right to appeal to higher courts"
                ],
                "defense_options": [
                    "Consent defense",
                    "Alibi defense",
                    "Challenge the evidence",
                    "False accusation defense"
                ]
            },
            "420": {
                "title": "Cheating and dishonestly inducing delivery of property",
                "description": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, or anything which is signed or sealed, and which is capable of being converted into a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
                "rights": [
                    "Right to legal representation",
                    "Right to present evidence in defense",
                    "Right to cross-examine witnesses",
                    "Right to appeal to higher courts"
                ],
                "defense_options": [
                    "No intent to deceive",
                    "Lack of dishonest intention",
                    "Transaction was legitimate",
                    "Challenge the evidence"
                ]
            }
        }
    elif act_type == "IT Act":
        sections = {
            "66": {
                "title": "Computer related offences",
                "description": "If any person, dishonestly or fraudulently, does any act referred to in section 43, he shall be punishable with imprisonment for a term which may extend to three years or with fine which may extend to five lakh rupees or with both.",
                "rights": [
                    "Right to legal representation",
                    "Right to technical expert assistance",
                    "Right to present evidence in defense",
                    "Right to appeal to higher courts"
                ],
                "defense_options": [
                    "Lack of mens rea (guilty mind)",
                    "Authorization defense",
                    "Technical error or misinterpretation",
                    "Legitimate security testing"
                ]
            },
            "67": {
                "title": "Punishment for publishing or transmitting obscene material in electronic form",
                "description": "Whoever publishes or transmits or causes to be published or transmitted in the electronic form, any material which is lascivious or appeals to the prurient interest or if its effect is such as to tend to deprave and corrupt persons who are likely, having regard to all relevant circumstances, to read, see or hear the matter contained or embodied in it, shall be punished on first conviction with imprisonment of either description for a term which may extend to three years and with fine which may extend to five lakh rupees and in the event of second or subsequent conviction with imprisonment of either description for a term which may extend to five years and also with fine which may extend to ten lakh rupees.",
                "rights": [
                    "Right to legal representation",
                    "Right to present evidence in defense",
                    "Right to challenge the electronic evidence",
                    "Right to appeal to higher courts"
                ],
                "defense_options": [
                    "Material not obscene under legal standards",
                    "Freedom of expression defense",
                    "Lack of intent to publish/transmit",
                    "Technical error or hacking defense"
                ]
            }
        }
    elif act_type == "MV Act":
        sections = {
            "184": {
                "title": "Driving dangerously",
                "description": "Whoever drives a motor vehicle at a speed or in a manner which is dangerous to the public, having regard to all the circumstances of case including the nature, condition and use of the place where the vehicle is driven and the amount of traffic which actually is at the time or which might reasonably be expected to be in the place, shall be punishable for the first offence with imprisonment for a term which may extend to six months or with fine which may extend to one thousand rupees, and for any second or subsequent offence if committed within three years of the commission of a previous similar offence with imprisonment for a term which may extend to two years, or with fine which may extend to two thousand rupees, or with both.",
                "rights": [
                    "Right to legal representation",
                    "Right to present evidence in defense",
                    "Right to challenge the evidence",
                    "Right to appeal to higher courts"
                ],
                "defense_options": [
                    "Challenge speed measurement accuracy",
                    "Emergency situation defense",
                    "Medical emergency defense",
                    "Road conditions defense"
                ]
            },
            "185": {
                "title": "Driving by a drunken person or by a person under the influence of drugs",
                "description": "Whoever, while driving, or attempting to drive, a motor vehicle has, in his blood, alcohol exceeding 30 mg. per 100 ml. of blood detected in a test by a breath analyser, shall be punishable for the first offence with imprisonment for a term which may extend to six months, or with fine which may extend to two thousand rupees, or with both.",
                "rights": [
                    "Right to legal representation",
                    "Right to medical examination",
                    "Right to challenge breathalyzer/blood test results",
                    "Right to appeal to higher courts"
                ],
                "defense_options": [
                    "Challenge the accuracy of testing equipment",
                    "Improper testing procedure",
                    "Medical condition affecting test results",
                    "Necessity defense in emergency"
                ]
            }
        }
    else:
        sections = {}
    
    return sections
