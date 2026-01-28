import asyncio
import time
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import threading
from collections import deque
import uuid

class RequestPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class QueuedRequest:
    id: str
    func: Callable
    args: tuple
    kwargs: dict
    priority: RequestPriority
    created_at: float
    timeout: float = 300.0  # 5 minutes default timeout
    
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.timeout

class RequestQueue:
    """Advanced request queue with priority and timeout handling."""
    
    def __init__(self, max_concurrent: int = 3, max_queue_size: int = 50):
        self.max_concurrent = max_concurrent
        self.max_queue_size = max_queue_size
        self.queue = deque()
        self.active_requests: Dict[str, QueuedRequest] = {}
        self.completed_requests: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._workers = []
        self._running = False
        self._stats = {
            'total_requests': 0,
            'completed_requests': 0,
            'failed_requests': 0,
            'timeout_requests': 0,
            'queue_size': 0
        }
    
    def start(self):
        """Start the worker threads."""
        if self._running:
            return
        
        self._running = True
        self._workers = [
            threading.Thread(target=self._worker, name=f"RequestWorker-{i}")
            for i in range(self.max_concurrent)
        ]
        
        for worker in self._workers:
            worker.daemon = True
            worker.start()
        
        print(f"🚀 Request queue started with {self.max_concurrent} workers")
    
    def stop(self):
        """Stop the worker threads."""
        self._running = False
        with self._condition:
            self._condition.notify_all()
        
        for worker in self._workers:
            worker.join(timeout=5)
        
        print("🛑 Request queue stopped")
    
    def enqueue(self, func: Callable, args: tuple = (), kwargs: dict = None, 
                priority: RequestPriority = RequestPriority.NORMAL, 
                timeout: float = 300.0) -> str:
        """Enqueue a request for processing."""
        if kwargs is None:
            kwargs = {}
        
        request_id = str(uuid.uuid4())
        request = QueuedRequest(
            id=request_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            created_at=time.time(),
            timeout=timeout
        )
        
        with self._lock:
            if len(self.queue) >= self.max_queue_size:
                raise Exception("Queue is full")
            
            # Insert based on priority
            if priority == RequestPriority.URGENT:
                self.queue.appendleft(request)
            elif priority == RequestPriority.HIGH:
                # Insert after urgent requests
                pos = 0
                while pos < len(self.queue) and self.queue[pos].priority == RequestPriority.URGENT:
                    pos += 1
                self.queue.insert(pos, request)
            elif priority == RequestPriority.NORMAL:
                self.queue.append(request)
            else:  # LOW
                # Insert at end
                self.queue.append(request)
            
            self._stats['total_requests'] += 1
            self._stats['queue_size'] = len(self.queue)
            self._condition.notify()
        
        return request_id
    
    def get_status(self, request_id: str) -> Dict[str, Any]:
        """Get the status of a specific request."""
        with self._lock:
            if request_id in self.active_requests:
                return {"status": "processing", "request_id": request_id}
            elif request_id in self.completed_requests:
                return {
                    "status": "completed",
                    "request_id": request_id,
                    "result": self.completed_requests[request_id]
                }
            else:
                # Check if in queue
                for req in self.queue:
                    if req.id == request_id:
                        return {
                            "status": "queued",
                            "request_id": request_id,
                            "priority": req.priority.name,
                            "queue_position": list(self.queue).index(req)
                        }
        
        return {"status": "not_found", "request_id": request_id}
    
    def get_result(self, request_id: str, timeout: float = 30.0) -> Any:
        """Get the result of a request, waiting if necessary."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self._lock:
                if request_id in self.completed_requests:
                    result = self.completed_requests.pop(request_id)
                    return result
                elif request_id in self.active_requests:
                    pass  # Still processing
                else:
                    # Check if in queue
                    found = False
                    for req in self.queue:
                        if req.id == request_id:
                            found = True
                            break
                    if not found:
                        raise ValueError(f"Request {request_id} not found")
            
            time.sleep(0.1)
        
        raise TimeoutError(f"Timeout waiting for request {request_id}")
    
    def _worker(self):
        """Worker thread function."""
        while self._running:
            request = None
            
            with self._condition:
                # Wait for a request
                while not self.queue and self._running:
                    self._condition.wait(timeout=1.0)
                
                if not self._running:
                    break
                
                # Get next request
                request = self.queue.popleft()
                self.active_requests[request.id] = request
                self._stats['queue_size'] = len(self.queue)
            
            try:
                # Process the request
                start_time = time.time()
                result = request.func(*request.args, **request.kwargs)
                duration = time.time() - start_time
                
                with self._lock:
                    if request.id in self.active_requests:
                        del self.active_requests[request.id]
                    self.completed_requests[request.id] = {
                        'result': result,
                        'duration': duration,
                        'completed_at': time.time()
                    }
                    self._stats['completed_requests'] += 1
                
                print(f"✅ Request {request.id[:8]} completed in {duration:.2f}s")
                
            except Exception as e:
                with self._lock:
                    if request.id in self.active_requests:
                        del self.active_requests[request.id]
                    self.completed_requests[request.id] = {
                        'error': str(e),
                        'completed_at': time.time()
                    }
                    self._stats['failed_requests'] += 1
                
                print(f"❌ Request {request.id[:8]} failed: {e}")
            
            finally:
                # Clean up old completed requests (keep last 100)
                with self._lock:
                    if len(self.completed_requests) > 100:
                        oldest_keys = list(self.completed_requests.keys())[:-100]
                        for key in oldest_keys:
                            del self.completed_requests[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        with self._lock:
            return {
                **self._stats,
                'active_requests': len(self.active_requests),
                'queue_size': len(self.queue),
                'max_concurrent': self.max_concurrent,
                'max_queue_size': self.max_queue_size,
                'running': self._running
            }
    
    def cleanup_expired(self):
        """Remove expired requests from queue."""
        with self._lock:
            expired = [req for req in self.queue if req.is_expired()]
            for req in expired:
                self.queue.remove(req)
                self._stats['timeout_requests'] += 1
            
            if expired:
                print(f"🧹 Cleaned up {len(expired)} expired requests")

# Global request queue instance
request_queue = RequestQueue(max_concurrent=2, max_queue_size=20)

def queued_processing(priority: RequestPriority = RequestPriority.NORMAL):
    """Decorator to make functions use the request queue."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract async context if available
            is_async = kwargs.pop('_queued', False)
            
            if not is_async:
                # Enqueue for processing
                request_id = request_queue.enqueue(func, args, kwargs, priority)
                return request_queue.get_result(request_id)
            else:
                # Direct execution (for internal calls)
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Auto-cleanup expired requests every 5 minutes
def start_cleanup_task():
    """Start the cleanup task for expired requests."""
    def cleanup():
        while True:
            time.sleep(300)  # 5 minutes
            request_queue.cleanup_expired()
    
    cleanup_thread = threading.Thread(target=cleanup, daemon=True)
    cleanup_thread.start()
    print("🧹 Request cleanup task started")
