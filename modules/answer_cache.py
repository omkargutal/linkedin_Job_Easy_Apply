"""
Answer Cache Module - Stores and retrieves previously answered questions
This reduces API calls and improves performance significantly

Author: Performance Optimization
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from hashlib import md5

CACHE_FILE = "logs/question_cache.json"
CACHE_EXPIRY_DAYS = 30  # Answers expire after 30 days


class AnswerCache:
    """Intelligent cache for job application answers"""
    
    def __init__(self, cache_file: str = CACHE_FILE):
        self.cache_file = cache_file
        self.cache: Dict = self._load_cache()
        self._sanitize_old_entries()
    
    def _load_cache(self) -> Dict:
        """Load cache from file if exists"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self) -> None:
        """Save cache to file"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
    
    def _normalize_question(self, question: str) -> str:
        """Normalize question text for consistent matching"""
        # Remove extra spaces, convert to lowercase for fuzzy matching
        normalized = ' '.join(question.lower().split())
        # Remove common variations
        normalized = normalized.replace('how many ', 'how many')
        normalized = normalized.replace('do you have ', 'do you have')
        normalized = normalized.replace('of experience', 'of experience')
        return normalized
    
    def _get_question_hash(self, question: str) -> str:
        """Create hash of normalized question"""
        normalized = self._normalize_question(question)
        return md5(normalized.encode()).hexdigest()
    
    def get(self, question: str, question_type: str) -> Optional[str]:
        """
        Retrieve cached answer for a question
        
        Args:
            question: The question text
            question_type: Type of question (text, select, radio, textarea, checkbox)
        
        Returns:
            Cached answer if found and not expired, else None
        """
        question_hash = self._get_question_hash(question)
        
        if question_hash in self.cache:
            cache_entry = self.cache[question_hash]
            
            # Check if expired
            if not self._is_expired(cache_entry['timestamp']):
                if cache_entry.get('type') == question_type:
                    return cache_entry['answer']
        
        return None
    
    def set(self, question: str, answer: str, question_type: str) -> None:
        """
        Store answer in cache
        
        Args:
            question: The question text
            answer: The answer to cache
            question_type: Type of question
        """
        question_hash = self._get_question_hash(question)
        
        self.cache[question_hash] = {
            'question': question,
            'answer': answer,
            'type': question_type,
            'timestamp': datetime.now().isoformat()
        }
        
        self._save_cache()
    
    def _is_expired(self, timestamp_str: str) -> bool:
        """Check if cache entry is expired"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            age = datetime.now() - timestamp
            return age > timedelta(days=CACHE_EXPIRY_DAYS)
        except:
            return True
    
    def _sanitize_old_entries(self) -> None:
        """Remove expired entries from cache"""
        expired_keys = []
        
        for key, entry in self.cache.items():
            if self._is_expired(entry.get('timestamp', '')):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self._save_cache()
    
    def find_similar_answer(self, question: str, similarity_threshold: float = 0.7) -> Optional[Tuple[str, str]]:
        """
        Find similar cached question and return its answer
        Uses simple string matching approach (can be upgraded to fuzzy matching)
        
        Args:
            question: The question to find similar match for
            similarity_threshold: Minimum similarity score (0-1)
        
        Returns:
            Tuple of (cached_question, cached_answer) if found, else None
        """
        normalized_q = self._normalize_question(question)
        
        for entry in self.cache.values():
            cached_normalized = self._normalize_question(entry['question'])
            
            # Simple word overlap matching
            q_words = set(normalized_q.split())
            cached_words = set(cached_normalized.split())
            
            if q_words and cached_words:
                overlap = len(q_words & cached_words) / max(len(q_words), len(cached_words))
                
                if overlap >= similarity_threshold:
                    return (entry['question'], entry['answer'])
        
        return None
    
    def clear(self) -> None:
        """Clear entire cache"""
        self.cache = {}
        self._save_cache()
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'total_cached': len(self.cache),
            'by_type': self._count_by_type(),
            'oldest_entry': self._get_oldest_entry_date(),
            'cache_file': self.cache_file
        }
    
    def _count_by_type(self) -> Dict:
        """Count cached answers by type"""
        counts = {}
        for entry in self.cache.values():
            qtype = entry.get('type', 'unknown')
            counts[qtype] = counts.get(qtype, 0) + 1
        return counts
    
    def _get_oldest_entry_date(self) -> Optional[str]:
        """Get date of oldest cache entry"""
        if not self.cache:
            return None
        
        oldest = min(
            (entry['timestamp'] for entry in self.cache.values()),
            default=None
        )
        return oldest


# Global cache instance
_answer_cache: Optional[AnswerCache] = None


def get_cache() -> AnswerCache:
    """Get or create global cache instance"""
    global _answer_cache
    if _answer_cache is None:
        _answer_cache = AnswerCache()
    return _answer_cache


def cache_answer(question: str, answer: str, question_type: str) -> None:
    """Convenience function to cache an answer"""
    get_cache().set(question, answer, question_type)


def get_cached_answer(question: str, question_type: str) -> Optional[str]:
    """Convenience function to retrieve cached answer"""
    return get_cache().get(question, question_type)
