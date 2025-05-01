"""
Advanced Case Law Retrieval System Using Semantic Search

This module implements advanced text embedding and semantic search 
capabilities for legal case retrieval. Since we cannot use sentence-transformers,
we'll implement a robust alternative using our existing scikit-learn and NLTK libraries.
"""

import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import re

# Ensure NLTK data is downloaded
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')

class EnhancedLegalCaseMatcher:
    """
    An advanced semantic search class for legal case matching that uses
    enhanced TF-IDF with contextual weighting to improve matches.
    """
    
    def __init__(self):
        """Initialize the legal case matcher with enhanced TF-IDF vectorization"""
        # Use max_features for dimensionality reduction, ngram_range to capture phrases
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,  # Increase feature count
            ngram_range=(1, 2),  # Include bigrams
            stop_words='english',  # Remove stopwords
            use_idf=True,
            smooth_idf=True,
            sublinear_tf=True  # Apply sublinear tf scaling
        )
        self.stop_words = set(stopwords.words('english'))
        self.legal_keywords_boost = self._load_legal_keywords()
        
    def _load_legal_keywords(self):
        """
        Load legal keywords to boost in the matching process.
        These are domain-specific terms that should have higher weights.
        """
        return {
            # General legal terms
            'murder': 1.5, 'homicide': 1.5, 'manslaughter': 1.5,
            'robbery': 1.3, 'theft': 1.3, 'burglary': 1.3, 'larceny': 1.3,
            'assault': 1.3, 'battery': 1.3, 'rape': 1.5, 'fraud': 1.3,
            'forgery': 1.3, 'perjury': 1.3, 'bribery': 1.3,
            'custody': 1.2, 'bail': 1.2, 'parole': 1.2, 'probation': 1.2,
            'dowry': 1.5, 'cybercrime': 1.5, 'terrorism': 1.5, 'sedition': 1.5,
            'defamation': 1.4, 'cheating': 1.3, 'extortion': 1.4, 'abetment': 1.3,
            'conspiracy': 1.4, 'negligence': 1.3, 'mischief': 1.2,
            
            # Procedural terms
            'evidence': 1.4, 'testimony': 1.4, 'witness': 1.4,
            'defendant': 1.2, 'plaintiff': 1.2, 'petitioner': 1.2,
            'appellant': 1.2, 'respondent': 1.2, 'prosecutor': 1.2,
            'acquittal': 1.4, 'conviction': 1.4, 'sentence': 1.3,
            'plea': 1.3, 'guilty': 1.3, 'not guilty': 1.3,
            'appeal': 1.3, 'revision': 1.3, 'review': 1.2,
            'investigation': 1.3, 'charge sheet': 1.4, 'chargesheet': 1.4,
            'summons': 1.2, 'warrant': 1.3, 'cognizable': 1.4, 'non-cognizable': 1.4,
            'bailable': 1.3, 'non-bailable': 1.3, 'compoundable': 1.2,
            
            # Legal reasoning terms
            'precedent': 1.5, 'ruling': 1.4, 'judgment': 1.4,
            'statute': 1.4, 'regulation': 1.3, 'code': 1.3,
            'constitution': 1.4, 'amendment': 1.3, 'right': 1.3,
            'reasonable': 1.2, 'burden of proof': 1.4, 'beyond reasonable doubt': 1.5,
            'preponderance of evidence': 1.4, 'motive': 1.3, 'intention': 1.3,
            'mens rea': 1.4, 'actus reus': 1.4, 'ratio decidendi': 1.5,
            'obiter dicta': 1.4, 'doctrine': 1.3, 'jurisprudence': 1.4,
            'interpretation': 1.3, 'construction': 1.2, 'harmonious': 1.2,
            
            # Indian legal terms
            'ipc': 1.8, 'crpc': 1.8, 'cpc': 1.8, 'it act': 1.7, 'mvc': 1.7,
            'section': 1.5, 'act': 1.4, 'code': 1.4, 'article': 1.4,
            'fir': 1.5, 'high court': 1.5, 'supreme court': 1.6, 'district court': 1.4,
            'writ': 1.5, 'petition': 1.3, 'habeas corpus': 1.5, 'mandamus': 1.5,
            'certiorari': 1.5, 'quo warranto': 1.5, 'prohibition': 1.4,
            'suo moto': 1.4, 'cognizance': 1.4, 'first information report': 1.5,
            'fundamental right': 1.6, 'directive principle': 1.5, 'constitutional': 1.5,
            'nyaya panchayat': 1.3, 'lok adalat': 1.3, 'uniform civil code': 1.5,
            'personal law': 1.4, 'hindu law': 1.4, 'muslim law': 1.4, 'family law': 1.4
        }
    
    def preprocess_text(self, text):
        """
        Enhance text preprocessing for legal documents to improve semantic matching.
        
        Args:
            text (str): The input text to preprocess
            
        Returns:
            str: Preprocessed text optimized for legal semantic matching
        """
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Replace section numbers with a standardized format 
        # (e.g., "section 302" becomes "section_302")
        text = re.sub(r'section\s+(\d+)', r'section_\1', text)
        
        # Preserve important legal phrases by replacing spaces with underscores
        legal_phrases = [
            "beyond reasonable doubt", "burden of proof", "prima facie",
            "mens rea", "actus reus", "habeas corpus", "amicus curiae",
            "sui generis", "sine qua non", "res judicata"
        ]
        
        for phrase in legal_phrases:
            if phrase in text:
                text = text.replace(phrase, phrase.replace(" ", "_"))
        
        # Remove special characters while preserving underscores
        text = re.sub(r'[^\w\s_]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def enhance_query(self, query):
        """
        Enhance the query with contextual legal information.
        
        Args:
            query (str): The original query string
            
        Returns:
            str: Enhanced query for better legal semantic matching
        """
        # Preprocess the query
        processed_query = self.preprocess_text(query)
        
        # Split into tokens
        tokens = processed_query.split()
        
        # Apply keyword boosting by duplicating important legal terms
        enhanced_tokens = []
        for token in tokens:
            enhanced_tokens.append(token)
            
            # If token is a legal keyword, add it again to boost its weight
            if token in self.legal_keywords_boost:
                boost_factor = int(self.legal_keywords_boost[token])
                for _ in range(boost_factor - 1):
                    enhanced_tokens.append(token)
        
        return ' '.join(enhanced_tokens)
    
    def find_similar_cases(self, query, case_texts, case_metadata=None, top_k=5):
        """
        Find similar cases using enhanced semantic search.
        
        Args:
            query (str): The query text describing the case scenario
            case_texts (list): List of case texts to search within
            case_metadata (list, optional): List of dictionaries containing metadata for each case
            top_k (int): Number of top matches to return
            
        Returns:
            list: Top matching cases with similarity scores
        """
        if not case_texts:
            return []
            
        # Enhance the query for better matching
        enhanced_query = self.enhance_query(query)
        
        # Create corpus by combining case texts with the query
        corpus = [self.preprocess_text(text) for text in case_texts]
        corpus.append(enhanced_query)
        
        # Vectorize the corpus
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
            
            # Calculate similarity between query and all cases
            query_idx = len(corpus) - 1
            similarities = cosine_similarity(tfidf_matrix[query_idx], tfidf_matrix[:-1])[0]
            
            # Get indices of top-k matches
            top_indices = similarities.argsort()[-top_k:][::-1]
            
            # Prepare results with metadata if available
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include if there's some similarity
                    case_result = {
                        'text': case_texts[idx],
                        'similarity': float(similarities[idx])
                    }
                    
                    # Add metadata if available
                    if case_metadata and idx < len(case_metadata):
                        case_result.update(case_metadata[idx])
                    
                    results.append(case_result)
            
            return results
        except Exception as e:
            print(f"Error in finding similar cases: {str(e)}")
            # Fallback to basic matching if vectorization fails
            return [{'text': text, 'similarity': 0.5} for text in case_texts[:min(top_k, len(case_texts))]]
    
    def extract_key_sentences(self, text, top_n=3):
        """
        Extract the most important sentences from a legal text.
        
        Args:
            text (str): The legal text to analyze
            top_n (int): Number of key sentences to extract
            
        Returns:
            list: Key sentences extracted from the text
        """
        # Split text into sentences
        sentences = sent_tokenize(text)
        if len(sentences) <= top_n:
            return sentences
            
        # Preprocess sentences
        preprocessed_sentences = [self.preprocess_text(s) for s in sentences]
        
        # Create sentence vectors
        sentence_vectors = self.tfidf_vectorizer.fit_transform(preprocessed_sentences)
        
        # Calculate sentence importance using centrality
        similarity_matrix = cosine_similarity(sentence_vectors)
        scores = np.sum(similarity_matrix, axis=1)
        
        # Get indices of top sentences
        top_indices = scores.argsort()[-top_n:][::-1]
        
        # Return original sentences in document order
        sorted_indices = sorted(top_indices)
        return [sentences[idx] for idx in sorted_indices]

# Create a singleton instance
legal_case_matcher = EnhancedLegalCaseMatcher()