"""
Application monitoring and metrics for the CAG System.
"""

import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)


@dataclass
class MetricData:
    """Container for metric data."""
    count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    recent_times: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def add_measurement(self, duration: float):
        """Add a new measurement."""
        self.count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.recent_times.append(duration)
    
    @property
    def avg_time(self) -> float:
        """Calculate average time."""
        return self.total_time / self.count if self.count > 0 else 0.0
    
    @property
    def recent_avg_time(self) -> float:
        """Calculate recent average time."""
        if not self.recent_times:
            return 0.0
        return sum(self.recent_times) / len(self.recent_times)


class ApplicationMonitor:
    """
    Application monitoring system to track performance and usage.
    """
    
    def __init__(self):
        self._metrics: Dict[str, MetricData] = defaultdict(MetricData)
        self._errors: Dict[str, int] = defaultdict(int)
        self._start_time = time.time()
        self._lock = threading.Lock()
        
        logger.info("Application monitoring initialized")
    
    def record_request(self, endpoint: str, duration: float, success: bool = True):
        """Record a request with its duration and success status."""
        with self._lock:
            metric_key = f"endpoint_{endpoint.replace('/', '_')}"
            self._metrics[metric_key].add_measurement(duration)
            
            if not success:
                error_key = f"error_{endpoint.replace('/', '_')}"
                self._errors[error_key] += 1
            
            logger.debug(f"Recorded request: {endpoint} - {duration:.3f}s - {'success' if success else 'error'}")
    
    def record_cache_hit(self, cache_type: str):
        """Record a cache hit."""
        with self._lock:
            metric_key = f"cache_hit_{cache_type}"
            self._metrics[metric_key].count += 1
    
    def record_cache_miss(self, cache_type: str):
        """Record a cache miss."""
        with self._lock:
            metric_key = f"cache_miss_{cache_type}"
            self._metrics[metric_key].count += 1
    
    def record_error(self, error_type: str, details: Optional[str] = None):
        """Record an error occurrence."""
        with self._lock:
            self._errors[error_type] += 1
            if details:
                logger.error(f"Error recorded: {error_type} - {details}")
            else:
                logger.error(f"Error recorded: {error_type}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        with self._lock:
            uptime = time.time() - self._start_time
            
            metrics_summary = {}
            for key, metric in self._metrics.items():
                if metric.count > 0:
                    metrics_summary[key] = {
                        "count": metric.count,
                        "avg_time": round(metric.avg_time, 3),
                        "min_time": round(metric.min_time, 3),
                        "max_time": round(metric.max_time, 3),
                        "recent_avg_time": round(metric.recent_avg_time, 3)
                    }
            
            # Calculate cache hit rates
            cache_stats = {}
            for cache_type in ["llm", "crawl"]:
                hits = self._metrics.get(f"cache_hit_{cache_type}", MetricData()).count
                misses = self._metrics.get(f"cache_miss_{cache_type}", MetricData()).count
                total = hits + misses
                hit_rate = (hits / total * 100) if total > 0 else 0
                cache_stats[f"{cache_type}_cache"] = {
                    "hits": hits,
                    "misses": misses,
                    "hit_rate": round(hit_rate, 2)
                }
            
            return {
                "uptime_seconds": round(uptime, 2),
                "uptime_formatted": self._format_uptime(uptime),
                "metrics": metrics_summary,
                "cache_stats": cache_stats,
                "errors": dict(self._errors),
                "total_requests": sum(m.count for m in self._metrics.values() if "endpoint_" in str(m)),
                "timestamp": time.time()
            }
    
    def _format_uptime(self, uptime_seconds: float) -> str:
        """Format uptime in human-readable format."""
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)."""
        with self._lock:
            self._metrics.clear()
            self._errors.clear()
            self._start_time = time.time()
            logger.info("Metrics reset")


# Global monitor instance
monitor = ApplicationMonitor()


def track_request(endpoint: str):
    """Decorator to track request performance."""
    def decorator(func):
        import functools
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                monitor.record_error(f"endpoint_error_{endpoint}", str(e))
                raise
            finally:
                duration = time.time() - start_time
                monitor.record_request(endpoint, duration, success)
        return wrapper
    return decorator