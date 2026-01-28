import hashlib
import json
import time
from typing import Dict, Any, Optional
from functools import wraps
import os

# Simple in-memory cache with TTL
class CacheManager:
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def _generate_key(self, topic: str, level: str, language: str) -> str:
        """Generate cache key from request parameters."""
        key_data = f"{topic}_{level}_{language}".lower().strip()
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, topic: str, level: str, language: str) -> Optional[Dict[str, Any]]:
        """Get cached lesson data if available and not expired."""
        key = self._generate_key(topic, level, language)
        
        if key in self.cache:
            cache_entry = self.cache[key]
            if time.time() - cache_entry['timestamp'] < self.ttl_seconds:
                return cache_entry['data']
            else:
                # Remove expired entry
                del self.cache[key]
        
        return None
    
    def set(self, topic: str, level: str, language: str, data: Dict[str, Any]):
        """Cache lesson data with timestamp."""
        key = self._generate_key(topic, level, language)
        
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl_seconds
        }

# Global cache instance
cache_manager = CacheManager(max_size=50, ttl_seconds=1800)  # 30 minutes TTL

def cached_lesson(func):
    """Decorator to cache lesson generation results."""
    @wraps(func)
    def wrapper(topic=None, level="HSK 5", language="chinese", *args, **kwargs):
        # Use provided topic or generate cache key for auto-generated topics
        cache_topic = topic or "auto_generated"
        
        # Try to get from cache
        cached_result = cache_manager.get(cache_topic, level, language)
        if cached_result:
            print(f"🎯 Cache hit for: {cache_topic} ({level}) - {language}")
            return (
                cached_result['topic'],
                cached_result['markdown'],
                cached_result['html'],
                cached_result['lesson_data']
            )
        
        # Generate new content
        print(f"🔄 Cache miss, generating: {cache_topic} ({level}) - {language}")
        result = func(topic, level, language, *args, **kwargs)
        
        # Cache the result
        if result and len(result) == 4:
            topic_name, markdown, html, lesson_data = result
            cache_manager.set(cache_topic, level, language, {
                'topic': topic_name,
                'markdown': markdown,
                'html': html,
                'lesson_data': lesson_data
            })
        
        return result
    
    return wrapper

# File-based cache for persistence (optional)
class FileCache:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data from file."""
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Check TTL (30 minutes)
                if time.time() - data.get('timestamp', 0) < 1800:
                    return data.get('data')
                else:
                    # Remove expired file
                    os.remove(cache_path)
            except:
                pass
        return None
    
    def set(self, key: str, data: Dict[str, Any]):
        """Save data to cache file."""
        cache_path = self._get_cache_path(key)
        cache_data = {
            'data': data,
            'timestamp': time.time()
        }
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to cache data: {e}")

# Optional: Use file cache for persistence
file_cache = FileCache()
