"""
Model optimization and configuration for faster AI responses.
"""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for AI model optimization."""
    model_name: str = "gpt-3.5-turbo"  # Faster than gpt-4
    temperature: float = 0.7  # Balanced creativity/consistency
    max_tokens: int = 1000  # Limit output length for speed
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # Performance optimizations
    use_streaming: bool = False  # Disabled for batch processing
    timeout: int = 30  # 30 seconds timeout
    max_retries: int = 2  # Limited retries for speed

class OptimizedAgentConfig:
    """Optimized configurations for different agent types."""
    
    @staticmethod
    def get_lesson_planner_config() -> ModelConfig:
        """Fast configuration for lesson planning."""
        return ModelConfig(
            model_name="gpt-3.5-turbo",
            temperature=0.3,  # More focused for planning
            max_tokens=800,   # Shorter plans
            timeout=20
        )
    
    @staticmethod
    def get_content_writer_config() -> ModelConfig:
        """Balanced configuration for content writing."""
        return ModelConfig(
            model_name="gpt-3.5-turbo",
            temperature=0.8,  # More creative
            max_tokens=1200,  # Longer content
            timeout=25
        )
    
    @staticmethod
    def get_linguist_config() -> ModelConfig:
        """Fast configuration for language analysis."""
        return ModelConfig(
            model_name="gpt-3.5-turbo",
            temperature=0.2,  # Very focused for analysis
            max_tokens=600,   # Concise analysis
            timeout=15
        )
    
    @staticmethod
    def get_examiner_config() -> ModelConfig:
        """Fast configuration for quiz creation."""
        return ModelConfig(
            model_name="gpt-3.5-turbo",
            temperature=0.4,  # Semi-focused for quizzes
            max_tokens=800,   # Moderate length
            timeout=20
        )
    
    @staticmethod
    def get_writing_assessor_config() -> ModelConfig:
        """Balanced configuration for writing assessment."""
        return ModelConfig(
            model_name="gpt-3.5-turbo",
            temperature=0.5,  # Balanced for assessment
            max_tokens=1000,  # Detailed feedback
            timeout=25
        )

def apply_optimization_config(agent, agent_type: str):
    """Apply optimization configuration to a CrewAI agent."""
    configs = {
        'lesson_planner': OptimizedAgentConfig.get_lesson_planner_config(),
        'content_writer': OptimizedAgentConfig.get_content_writer_config(),
        'linguist': OptimizedAgentConfig.get_linguist_config(),
        'examiner': OptimizedAgentConfig.get_examiner_config(),
        'writing_assessor': OptimizedAgentConfig.get_writing_assessor_config()
    }
    
    config = configs.get(agent_type, OptimizedAgentConfig.get_lesson_planner_config())
    
    # Override agent configuration if supported
    if hasattr(agent, 'model'):
        agent.model = config.model_name
    
    if hasattr(agent, 'temperature'):
        agent.temperature = config.temperature
    
    if hasattr(agent, 'max_tokens'):
        agent.max_tokens = config.max_tokens
    
    return agent

# Environment-based optimization
def get_optimized_model_name() -> str:
    """Get the best model based on environment and requirements."""
    # Check for custom model in environment
    custom_model = os.getenv("OPTIMIZED_MODEL")
    if custom_model:
        return custom_model
    
    # Use faster model for development/testing
    if os.getenv("ENVIRONMENT") == "development":
        return "gpt-3.5-turbo"
    
    # Use standard model for production
    return "gpt-3.5-turbo"

# Batch processing optimization
def create_batch_requests(items: list, batch_size: int = 3) -> list:
    """Split items into batches for parallel processing."""
    batches = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batches.append(batch)
    return batches

# Token optimization
def estimate_tokens(text: str) -> int:
    """Rough token estimation for optimization."""
    # GPT-3.5 turbo: ~1 token per 4 characters
    return len(text) // 4

def optimize_prompt_length(prompt: str, max_tokens: int = 500) -> str:
    """Optimize prompt length to stay within token limits."""
    if estimate_tokens(prompt) <= max_tokens:
        return prompt
    
    # Truncate to max_tokens
    max_chars = max_tokens * 4
    return prompt[:max_chars] + "..."

# Cache key optimization
def create_cache_key(*args, **kwargs) -> str:
    """Create optimized cache key."""
    import hashlib
    key_str = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_str.encode()).hexdigest()[:16]  # Shorter keys

# Performance metrics
class PerformanceMetrics:
    """Track performance metrics for optimization."""
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'avg_response_time': 0.0,
            'cache_hit_rate': 0.0,
            'error_rate': 0.0,
            'token_usage': 0
        }
    
    def record_request(self, duration: float, tokens: int, success: bool):
        """Record a request metric."""
        self.metrics['total_requests'] += 1
        self.metrics['token_usage'] += tokens
        
        # Update average response time
        total = self.metrics['total_requests']
        current_avg = self.metrics['avg_response_time']
        self.metrics['avg_response_time'] = (current_avg * (total - 1) + duration) / total
        
        # Update error rate
        if not success:
            current_errors = self.metrics['error_rate'] * (total - 1)
            self.metrics['error_rate'] = (current_errors + 1) / total
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()

# Global metrics instance
performance_metrics = PerformanceMetrics()

# Adaptive optimization based on performance
def adaptive_optimization() -> ModelConfig:
    """Adapt model configuration based on current performance."""
    metrics = performance_metrics.get_metrics()
    
    # If response times are high, use faster settings
    if metrics['avg_response_time'] > 10.0:
        return ModelConfig(
            model_name="gpt-3.5-turbo",
            temperature=0.3,
            max_tokens=600,
            timeout=15
        )
    
    # If error rate is high, use more conservative settings
    elif metrics['error_rate'] > 0.1:
        return ModelConfig(
            model_name="gpt-3.5-turbo",
            temperature=0.2,
            max_tokens=800,
            timeout=20
        )
    
    # Default balanced configuration
    return ModelConfig()
