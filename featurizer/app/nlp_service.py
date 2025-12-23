"""NLP service for clinical text processing."""
import re
from typing import Dict, Any, List, Optional, Tuple
import structlog

logger = structlog.get_logger()

# Lazy load models
_spacy_model = None
_biobert_tokenizer = None
_biobert_model = None


def get_spacy_model():
    """Lazy load spaCy model."""
    global _spacy_model
    if _spacy_model is None:
        import spacy
        try:
            _spacy_model = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded")
        except OSError:
            logger.warning("spaCy model not found, downloading...")
            from spacy.cli import download
            download("en_core_web_sm")
            _spacy_model = spacy.load("en_core_web_sm")
    return _spacy_model


def get_biobert_model():
    """Lazy load BioBERT model and tokenizer."""
    global _biobert_tokenizer, _biobert_model
    if _biobert_tokenizer is None or _biobert_model is None:
        try:
            from transformers import AutoTokenizer, AutoModel
            model_name = "dmis-lab/biobert-base-cased-v1.2"
            _biobert_tokenizer = AutoTokenizer.from_pretrained(model_name)
            _biobert_model = AutoModel.from_pretrained(model_name)
            logger.info("BioBERT model loaded")
        except Exception as e:
            logger.warning(f"Could not load BioBERT: {e}")
            return None, None
    return _biobert_tokenizer, _biobert_model


# Medical entity patterns
MEDICATION_PATTERNS = [
    r'\b(aspirin|ibuprofen|acetaminophen|metformin|lisinopril|atorvastatin|omeprazole|losartan|amlodipine|metoprolol)\b',
    r'\b(\w+)(azole|mycin|cillin|pril|sartan|statin|prazole|olol|dipine)\b',
    r'\b\d+\s*(mg|ml|mcg|g)\b'
]

SYMPTOM_PATTERNS = [
    r'\b(pain|fever|cough|dyspnea|nausea|vomiting|diarrhea|fatigue|weakness|dizziness)\b',
    r'\b(headache|chest pain|shortness of breath|difficulty breathing|swelling|edema)\b',
    r'\b(confusion|altered mental status|syncope|palpitations|weight loss|weight gain)\b'
]

URGENCY_KEYWORDS = {
    'high': ['emergency', 'urgent', 'critical', 'severe', 'acute', 'immediate', 'stat'],
    'medium': ['moderate', 'concerning', 'worsening', 'persistent'],
    'low': ['stable', 'improving', 'chronic', 'routine', 'follow-up']
}

NEGATION_PATTERNS = [
    r'no\s+',
    r'denies?\s+',
    r'without\s+',
    r'negative\s+for\s+',
    r'ruled\s+out\s+'
]


class NLPService:
    """Service for NLP processing of clinical text."""
    
    def __init__(self):
        self.nlp = None
        self.tokenizer = None
        self.model = None
        
    def ensure_models_loaded(self):
        """Ensure NLP models are loaded."""
        if self.nlp is None:
            self.nlp = get_spacy_model()
        if self.tokenizer is None or self.model is None:
            self.tokenizer, self.model = get_biobert_model()
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from clinical text."""
        self.ensure_models_loaded()
        
        entities = []
        
        # Use spaCy for general NER
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                entities.append({
                    "entity_type": ent.label_,
                    "entity_text": ent.text,
                    "start_position": ent.start_char,
                    "end_position": ent.end_char,
                    "confidence": 0.85,  # spaCy doesn't provide confidence
                    "source": "spacy"
                })
        
        # Extract medications using patterns
        for pattern in MEDICATION_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append({
                    "entity_type": "MEDICATION",
                    "entity_text": match.group(),
                    "start_position": match.start(),
                    "end_position": match.end(),
                    "confidence": 0.75,
                    "source": "pattern"
                })
        
        # Extract symptoms using patterns
        for pattern in SYMPTOM_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Check for negation
                is_negated = self._check_negation(text, match.start())
                entities.append({
                    "entity_type": "SYMPTOM",
                    "entity_text": match.group(),
                    "start_position": match.start(),
                    "end_position": match.end(),
                    "confidence": 0.7,
                    "negated": is_negated,
                    "source": "pattern"
                })
        
        # Deduplicate entities
        seen = set()
        unique_entities = []
        for ent in entities:
            key = (ent["entity_text"].lower(), ent["entity_type"])
            if key not in seen:
                seen.add(key)
                unique_entities.append(ent)
        
        return unique_entities
    
    def _check_negation(self, text: str, position: int) -> bool:
        """Check if there's a negation before the given position."""
        # Look at 50 characters before the position
        start = max(0, position - 50)
        context = text[start:position].lower()
        
        for pattern in NEGATION_PATTERNS:
            if re.search(pattern, context):
                return True
        return False
    
    def compute_sentiment(self, text: str) -> float:
        """Compute sentiment score for clinical text."""
        self.ensure_models_loaded()
        
        # Simple rule-based sentiment for clinical context
        positive_terms = ['improving', 'stable', 'resolved', 'negative', 'normal', 'good', 'well']
        negative_terms = ['worsening', 'severe', 'critical', 'positive', 'abnormal', 'poor', 'failed']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for term in positive_terms if term in text_lower)
        negative_count = sum(1 for term in negative_terms if term in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.5  # Neutral
        
        return positive_count / total
    
    def compute_urgency_score(self, text: str) -> float:
        """Compute urgency score (0-1) for clinical text."""
        text_lower = text.lower()
        
        high_count = sum(1 for kw in URGENCY_KEYWORDS['high'] if kw in text_lower)
        medium_count = sum(1 for kw in URGENCY_KEYWORDS['medium'] if kw in text_lower)
        low_count = sum(1 for kw in URGENCY_KEYWORDS['low'] if kw in text_lower)
        
        # Weighted score
        score = (high_count * 1.0 + medium_count * 0.5 + low_count * 0.1)
        total_keywords = high_count + medium_count + low_count
        
        if total_keywords == 0:
            return 0.3  # Default moderate urgency
        
        # Normalize to 0-1
        return min(score / total_keywords, 1.0)
    
    def compute_complexity_score(self, text: str) -> float:
        """Compute complexity score based on text features."""
        self.ensure_models_loaded()
        
        if not self.nlp:
            return 0.5
        
        doc = self.nlp(text)
        
        # Factors contributing to complexity
        factors = {
            "sentence_count": len(list(doc.sents)),
            "word_count": len([t for t in doc if not t.is_punct]),
            "entity_count": len(doc.ents),
            "medical_term_density": len([t for t in doc if len(t.text) > 8]) / max(len(doc), 1)
        }
        
        # Simple complexity calculation
        base_complexity = min(factors["entity_count"] / 10, 1.0) * 0.4
        length_complexity = min(factors["word_count"] / 200, 1.0) * 0.3
        term_complexity = factors["medical_term_density"] * 0.3
        
        return base_complexity + length_complexity + term_complexity
    
    def count_medication_mentions(self, text: str) -> int:
        """Count medication mentions in text."""
        count = 0
        for pattern in MEDICATION_PATTERNS:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        return count
    
    def count_symptom_mentions(self, text: str) -> int:
        """Count symptom mentions in text."""
        count = 0
        for pattern in SYMPTOM_PATTERNS:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        return count
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Perform full NLP analysis on clinical text."""
        entities = self.extract_entities(text)
        
        return {
            "entities": entities,
            "sentiment_score": self.compute_sentiment(text),
            "urgency_score": self.compute_urgency_score(text),
            "complexity_score": self.compute_complexity_score(text),
            "medication_mentions": self.count_medication_mentions(text),
            "symptom_mentions": self.count_symptom_mentions(text)
        }
    
    def get_text_embedding(self, text: str) -> Optional[List[float]]:
        """Get BioBERT embedding for text."""
        self.ensure_models_loaded()
        
        if self.tokenizer is None or self.model is None:
            return None
        
        try:
            import torch
            
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512,
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Use [CLS] token embedding
            embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()
            return embedding
            
        except Exception as e:
            logger.error(f"Error computing embedding: {e}")
            return None


# Global service instance
nlp_service = NLPService()


