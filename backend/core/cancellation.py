from threading import Lock
from typing import Set

class CancellationManager:
    """
    Manages cancellation tokens for long-running workflow stages.
    Thread-safe set of cancelled manuscript IDs.
    """
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CancellationManager, cls).__new__(cls)
                cls._instance._cancelled_ids = set()
                cls._instance._set_lock = Lock()
            return cls._instance
            
    def cancel(self, manuscript_id: str):
        """Mark a manuscript's current operation as cancelled"""
        with self._set_lock:
            self._cancelled_ids.add(manuscript_id)
            
    def reset(self, manuscript_id: str):
        """Reset cancellation status (start new operation)"""
        with self._set_lock:
            if manuscript_id in self._cancelled_ids:
                self._cancelled_ids.remove(manuscript_id)
                
    def is_cancelled(self, manuscript_id: str) -> bool:
        """Check if operation should be cancelled"""
        with self._set_lock:
            return manuscript_id in self._cancelled_ids

# Global instance
cancellation_manager = CancellationManager()
