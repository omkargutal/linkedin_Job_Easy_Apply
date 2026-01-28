"""
Smart Select/Dropdown Answer Handler - Uses AI to intelligently pick from dropdown options
Instead of random selection, uses AI to choose best matching option

Author: Performance Optimization
"""

from typing import Optional, List
from modules.helpers import print_lg


def get_best_matching_option(
    question: str,
    available_options: List[str],
    ai_answer: str,
    job_description: str = None
) -> Optional[str]:
    """
    Find best matching option from available dropdown options using AI answer as guide
    
    Args:
        question: The question being asked
        available_options: List of available options in the dropdown
        ai_answer: The AI-suggested answer (may not exactly match available options)
        job_description: Job description for context
    
    Returns:
        Best matching option from available_options, or None if no match found
    """
    
    if not ai_answer or not available_options:
        return None
    
    ai_answer_lower = ai_answer.lower().strip()
    
    # Strategy 1: Exact match (case-insensitive)
    for option in available_options:
        if option.lower() == ai_answer_lower:
            return option
    
    # Strategy 2: Partial match - AI answer is substring of option
    for option in available_options:
        if ai_answer_lower in option.lower():
            return option
    
    # Strategy 3: Option is substring of AI answer (reverse matching)
    for option in available_options:
        if option.lower() in ai_answer_lower:
            return option
    
    # Strategy 4: Semantic matching for common answers
    return _semantic_match(ai_answer_lower, available_options)


def _semantic_match(ai_answer: str, available_options: List[str]) -> Optional[str]:
    """
    Semantic matching for common answer variations
    Maps common answer patterns to actual options
    """
    
    # Affirmative answers
    affirmative_keywords = ['yes', 'agree', 'willing', 'comfortable', 'confident', 'ok', 'fine', 'positive']
    negative_keywords = ['no', 'disagree', 'unwilling', 'uncomfortable', 'decline', 'prefer not']
    
    # Check if AI answer is affirmative
    is_affirmative = any(kw in ai_answer for kw in affirmative_keywords)
    is_negative = any(kw in ai_answer for kw in negative_keywords)
    
    if is_affirmative or is_negative:
        for option in available_options:
            option_lower = option.lower()
            
            if is_affirmative:
                if any(kw in option_lower for kw in affirmative_keywords):
                    return option
            
            if is_negative:
                if any(kw in option_lower for kw in negative_keywords):
                    return option
    
    # Check for specific patterns
    if 'experience' in ai_answer or 'years' in ai_answer or ai_answer.isdigit():
        # Try to find a numeric option
        for option in available_options:
            if any(char.isdigit() for char in option):
                return option
    
    # If AI answer mentions a technology/skill, look for it in options
    tech_words = ai_answer.split()
    for option in available_options:
        for word in tech_words:
            if len(word) > 3 and word.lower() in option.lower():
                return option
    
    return None


def validate_dropdown_answer(
    question: str,
    selected_option: str,
    available_options: List[str]
) -> bool:
    """
    Validate if selected option is valid for the question
    
    Returns:
        True if option exists in available_options, False otherwise
    """
    return selected_option in available_options


def rank_options_by_relevance(
    question: str,
    available_options: List[str],
    job_description: str = None
) -> List[tuple]:
    """
    Rank dropdown options by relevance to the question and job
    
    Returns:
        List of tuples (option, relevance_score) sorted by score (highest first)
    """
    
    q_lower = question.lower()
    ranked = []
    
    for option in available_options:
        score = 0
        option_lower = option.lower()
        
        # Keyword matching
        if 'yes' in q_lower and any(word in option_lower for word in ['yes', 'agree', 'willing']):
            score += 10
        elif 'no' in q_lower and any(word in option_lower for word in ['no', 'disagree', 'decline']):
            score += 10
        
        # Option length (prefer concise options for Yes/No questions)
        if len(option.split()) <= 3:
            score += 2
        
        # Relevance to job description
        if job_description:
            job_desc_lower = job_description.lower()
            common_words = len(set(option_lower.split()) & set(job_desc_lower.split()))
            score += common_words * 0.5
        
        ranked.append((option, score))
    
    # Sort by score (highest first)
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked


def suggest_option_with_fallback(
    question: str,
    available_options: List[str],
    question_type: str = "select"
) -> Optional[str]:
    """
    Suggest a safe fallback option if AI can't answer
    Uses heuristics to pick the most appropriate option
    
    Returns:
        Best guess option or first option if nothing else works
    """
    
    if not available_options:
        return None
    
    q_lower = question.lower()
    
    # For Yes/No questions, prefer "Yes"
    if any(word in q_lower for word in ['comfortable', 'willing', 'able', 'can']):
        for option in available_options:
            if 'yes' in option.lower():
                return option
        for option in available_options:
            if 'agree' in option.lower() or 'ok' in option.lower():
                return option
    
    # For preference questions, prefer "No"
    if 'prefer' in q_lower or 'decline' in q_lower:
        for option in available_options:
            if 'prefer not' in option.lower() or 'decline' in option.lower():
                return option
    
    # For skill/experience questions, prefer options with relevant keywords
    if any(word in q_lower for word in ['skill', 'experience', 'years', 'knowledge']):
        for option in available_options:
            if option.lower() not in ['select an option', 'choose one', 'none']:
                return option
    
    # Default: return first non-placeholder option
    for option in available_options:
        if option.lower() not in ['select an option', 'choose one', 'none', 'select', 'please select']:
            return option
    
    # Last resort: return first option
    return available_options[0] if available_options else None
