import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

class LegalPredictor:
    """
    A class that provides predictive functionality for legal cases,
    including rights identification and defense option recommendations.
    """
    
    def __init__(self):
        """
        Initialize the legal predictor with necessary models and data.
        """
        self.tfidf_vectorizer = TfidfVectorizer(max_features=5000)
        self.rights_classifier = None
        self.defense_classifier = None
        self.precedent_data = None
        self.legal_code_data = None
        self.sample_data_loaded = False
        
        # Load sample data for demonstration
        self.load_sample_data()
    
    def load_sample_data(self):
        """
        Load sample data for demonstration purposes.
        In a real system, this would load trained models from files.
        """
        # Create sample case data
        # This is simplified for demonstration purposes
        
        from legal_data import ipc_sections, it_act_sections, mv_act_sections, legal_precedents
        
        self.legal_code_data = {
            "IPC": ipc_sections,
            "IT Act": it_act_sections,
            "MV Act": mv_act_sections
        }
        
        self.precedent_data = legal_precedents
        
        self.sample_data_loaded = True
    
    def preprocess_text(self, text):
        """
        Preprocess text for NLP tasks.
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [word for word in tokens if word not in stop_words]
        
        # Join tokens back into string
        return ' '.join(filtered_tokens)
    
    def predict_rights(self, section, act, case_description):
        """
        Predict the rights applicable to a defendant based on the section, act, and case description.
        """
        if not self.sample_data_loaded:
            return {"error": "Model data not loaded"}
        
        # In a real system, this would use the trained classifier
        # For demonstration, use rule-based approach with sample data
        
        from legal_data import defendant_rights, get_offense_details
        
        # Get basic rights for all cases
        basic_rights = defendant_rights["general"]
        
        # Get offense details
        offense_details = get_offense_details(section, act)
        
        if offense_details:
            # Add bail information
            bail_info = offense_details.get("bail_info", {})
            bail_type = "non_bailable" if "non_bailable" in str(bail_info) else "bailable"
            
            # Get additional rights based on bail type
            bail_rights = defendant_rights["bail"]
            
            # Get trial rights
            trial_rights = defendant_rights["trial"]
            
            # Combine all rights
            all_rights = basic_rights + bail_rights + trial_rights
            
            # Calculate relevance score (simple heuristic for demo)
            relevance_scores = {}
            for right in all_rights:
                # Simple relevance calculation
                # In a real system, this would use ML model predictions
                if "bail" in right.lower() and bail_type == "non_bailable":
                    relevance_scores[right] = 0.9
                elif "bail" in right.lower() and bail_type == "bailable":
                    relevance_scores[right] = 0.7
                elif "appeal" in right.lower():
                    relevance_scores[right] = 0.8
                elif "legal representation" in right.lower():
                    relevance_scores[right] = 1.0
                else:
                    relevance_scores[right] = 0.6
            
            # Sort by relevance
            sorted_rights = sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True)
            
            return {
                "rights": [{"right": r[0], "relevance": r[1]} for r in sorted_rights],
                "section_info": offense_details
            }
        
        return {
            "rights": [{"right": r, "relevance": 0.5} for r in basic_rights],
            "section_info": None
        }
    
    def suggest_defense_options(self, section, act, case_description):
        """
        Suggest defense options based on the section, act, and case description.
        """
        if not self.sample_data_loaded:
            return {"error": "Model data not loaded"}
        
        # For demonstration, use rule-based approach
        
        # Common defense options across various cases
        common_options = [
            "Challenge the admissibility of evidence",
            "Question witness credibility",
            "Establish alibi",
            "Claim lack of intent (mens rea)",
            "Procedural violations in investigation"
        ]
        
        # Specific defenses based on acts and sections
        specific_options = []
        
        if act == "IPC":
            if section == "302":  # Murder
                specific_options = [
                    "Self-defense",
                    "Accident or misfortune without criminal intention",
                    "Sudden and grave provocation",
                    "Mental disability or insanity",
                    "Challenge cause of death"
                ]
            elif section == "376":  # Rape
                specific_options = [
                    "Consent defense",
                    "Challenge identification",
                    "Medical evidence inconsistencies",
                    "Alibi defense",
                    "Delay in filing FIR"
                ]
            elif section == "420":  # Cheating
                specific_options = [
                    "No fraudulent or dishonest intention",
                    "Civil dispute, not criminal matter",
                    "Legitimate business transaction",
                    "No inducement to deliver property",
                    "Lack of deception"
                ]
        elif act == "IT Act":
            if section == "66":  # Computer-related offenses
                specific_options = [
                    "Authorized access",
                    "Legitimate security testing",
                    "No damage or harm caused",
                    "Challenge technical evidence",
                    "Challenge chain of custody for electronic evidence"
                ]
            elif section == "67":  # Obscene material
                specific_options = [
                    "Content not obscene by legal standards",
                    "Freedom of expression defense",
                    "No intent to publish/transmit",
                    "Account was hacked",
                    "Educational or scientific purpose"
                ]
        elif act == "MV Act":
            if section == "184":  # Dangerous driving
                specific_options = [
                    "Challenge speed measurement accuracy",
                    "Road conditions defense",
                    "Medical emergency",
                    "Vehicle mechanical failure",
                    "Necessary evasive action"
                ]
            elif section == "185":  # Drunk driving
                specific_options = [
                    "Challenge breathalyzer calibration",
                    "Improper testing procedure",
                    "Medical condition affecting test",
                    "Consumption after driving (hip flask defense)",
                    "Necessity in emergency"
                ]
        
        # Combine options and calculate relevance scores
        all_options = common_options + specific_options
        
        # Calculate relevance (simplified for demo)
        relevance_scores = {}
        for option in all_options:
            # Specific options are more relevant
            if option in specific_options:
                relevance_scores[option] = 0.9
            else:
                relevance_scores[option] = 0.7
                
            # Boost score if terms from the option appear in the case description
            option_terms = set(self.preprocess_text(option).split())
            description_terms = set(self.preprocess_text(case_description).split())
            common_terms = option_terms.intersection(description_terms)
            
            if common_terms:
                boost = min(0.3, len(common_terms) * 0.1)  # Max boost of 0.3
                relevance_scores[option] += boost
                
            # Cap at 1.0
            relevance_scores[option] = min(1.0, relevance_scores[option])
        
        # Sort by relevance
        sorted_options = sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "defense_options": [{"option": o[0], "relevance": o[1]} for o in sorted_options]
        }
    
    def find_similar_precedents(self, case_description, section=None, act=None, top_k=5):
        """
        Find similar legal precedents based on case description and optionally section and act.
        """
        if not self.sample_data_loaded or not self.precedent_data:
            return {"error": "Precedent data not loaded"}
        
        # Filter precedents by section and act if provided
        filtered_precedents = self.precedent_data
        if section and act:
            filtered_precedents = [p for p in self.precedent_data 
                                 if p["act"] == act and section in p["section"]]
        
        if not filtered_precedents:
            return {"precedents": []}
        
        # Create document corpus from precedent summaries
        corpus = [p["summary"] for p in filtered_precedents]
        corpus.append(case_description)  # Add the query case at the end
        
        # Vectorize
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
            
            # Calculate similarity between query case and all precedents
            query_idx = len(corpus) - 1
            similarities = cosine_similarity(tfidf_matrix[query_idx], tfidf_matrix[:-1])[0]
            
            # Get top-k most similar precedents
            top_indices = similarities.argsort()[-top_k:][::-1]
            
            similar_precedents = []
            for idx in top_indices:
                precedent = filtered_precedents[idx]
                similar_precedents.append({
                    "case_name": precedent["case_name"],
                    "citation": precedent["citation"],
                    "similarity": float(similarities[idx]),
                    "summary": precedent["summary"],
                    "key_points": precedent["key_points"]
                })
            
            return {"precedents": similar_precedents}
        except Exception as e:
            # Fallback if vectorization fails
            return {"precedents": filtered_precedents[:min(top_k, len(filtered_precedents))], 
                    "note": "Similarity calculation failed, showing relevant precedents without ranking"}

# Initialize the legal predictor
legal_predictor = LegalPredictor()
