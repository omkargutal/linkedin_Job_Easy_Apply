"""
Performance Monitoring Module - Track bot efficiency and improvements

Author: Performance Optimization
"""

import time
from typing import Dict, List
from datetime import datetime


class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'total_questions': 0,
            'cached_answers_used': 0,
            'ai_answers_used': 0,
            'fallback_answers_used': 0,
            'random_answers_used': 0,
            'smart_selection_matches': 0,
            'api_calls_saved': 0,
            'total_time_seconds': 0,
            'questions_answered': [],
        }
        self.session_start = time.time()
    
    def log_question(self, question: str, answer: str, source: str):
        """
        Log a question and how it was answered
        
        Args:
            question: Question text
            answer: Answer given
            source: 'cache', 'ai', 'fallback', 'random', 'manual'
        """
        self.metrics['total_questions'] += 1
        
        if source == 'cache':
            self.metrics['cached_answers_used'] += 1
            self.metrics['api_calls_saved'] += 1
        elif source == 'ai':
            self.metrics['ai_answers_used'] += 1
        elif source == 'fallback':
            self.metrics['fallback_answers_used'] += 1
        elif source == 'random':
            self.metrics['random_answers_used'] += 1
        
        self.metrics['questions_answered'].append({
            'question': question,
            'answer': answer,
            'source': source,
            'timestamp': datetime.now().isoformat()
        })
    
    def log_smart_selection_match(self):
        """Log when smart selection successfully matches an option"""
        self.metrics['smart_selection_matches'] += 1
    
    def get_session_duration(self) -> float:
        """Get elapsed time since session start"""
        return time.time() - self.session_start
    
    def print_summary(self):
        """Print performance summary"""
        duration = self.get_session_duration()
        self.metrics['total_time_seconds'] = duration
        
        print("\n" + "="*60)
        print("PERFORMANCE SUMMARY")
        print("="*60)
        print(f"Total Questions: {self.metrics['total_questions']}")
        print(f"Cached Answers Used: {self.metrics['cached_answers_used']}")
        print(f"AI Answers Used: {self.metrics['ai_answers_used']}")
        print(f"Fallback Answers Used: {self.metrics['fallback_answers_used']}")
        print(f"Random Answers Used: {self.metrics['random_answers_used']}")
        print(f"Smart Selection Matches: {self.metrics['smart_selection_matches']}")
        print(f"API Calls Saved: {self.metrics['api_calls_saved']}")
        print(f"Session Duration: {duration:.2f}s")
        
        if self.metrics['total_questions'] > 0:
            cache_rate = (self.metrics['cached_answers_used'] / self.metrics['total_questions']) * 100
            ai_rate = (self.metrics['ai_answers_used'] / self.metrics['total_questions']) * 100
            fallback_rate = (self.metrics['fallback_answers_used'] / self.metrics['total_questions']) * 100
            random_rate = (self.metrics['random_answers_used'] / self.metrics['total_questions']) * 100
            
            print(f"\nAnswer Source Breakdown:")
            print(f"  Cached: {cache_rate:.1f}%")
            print(f"  AI: {ai_rate:.1f}%")
            print(f"  Fallback: {fallback_rate:.1f}%")
            print(f"  Random: {random_rate:.1f}%")
            
            avg_time_per_question = duration / self.metrics['total_questions']
            print(f"\nAverage Time per Question: {avg_time_per_question:.2f}s")
            print(f"Average Questions per Minute: {(60 / avg_time_per_question):.1f}")
        
        print("="*60 + "\n")
    
    def get_metrics(self) -> Dict:
        """Get all metrics as dictionary"""
        self.metrics['total_time_seconds'] = self.get_session_duration()
        return self.metrics
    
    def export_metrics(self, filepath: str = "logs/performance_metrics.txt"):
        """Export metrics to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("PERFORMANCE METRICS REPORT\n")
                f.write("="*60 + "\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                
                metrics = self.get_metrics()
                for key, value in metrics.items():
                    if key != 'questions_answered':
                        f.write(f"{key}: {value}\n")
                
                f.write("\nDetailed Question Log:\n")
                f.write("-"*60 + "\n")
                for q in metrics['questions_answered']:
                    f.write(f"Q: {q['question']}\n")
                    f.write(f"A: {q['answer']}\n")
                    f.write(f"Source: {q['source']}\n")
                    f.write(f"Time: {q['timestamp']}\n")
                    f.write("-"*60 + "\n")
            
            print(f"Metrics exported to {filepath}")
        except Exception as e:
            print(f"Failed to export metrics: {e}")


# Global monitor instance
_monitor: PerformanceMonitor = None


def get_monitor() -> PerformanceMonitor:
    """Get or create global monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor


def log_question(question: str, answer: str, source: str):
    """Convenience function to log a question"""
    get_monitor().log_question(question, answer, source)


def log_smart_match():
    """Convenience function to log smart selection match"""
    get_monitor().log_smart_selection_match()
