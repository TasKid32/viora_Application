from typing import Callable, Dict, List, Any
from app.core.logging import get_logger

logger = get_logger(__name__)

# Domain Event Constants
EVENT_USER_REGISTERED = "USER_REGISTERED"
EVENT_CV_ANALYSIS_COMPLETED = "CV_ANALYSIS_COMPLETED"
EVENT_ROADMAP_GENERATED = "ROADMAP_GENERATED"
EVENT_ROADMAP_PHASE_COMPLETED = "ROADMAP_PHASE_COMPLETED"
EVENT_COURSE_COMPLETED = "COURSE_COMPLETED"
EVENT_PROFILE_UPDATED = "PROFILE_UPDATED"

class EventDispatcher:
    """Central event dispatcher for a decoupled event-driven architecture."""
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def register(self, event_name: str, listener: Callable):
        """Register a listener for a specific event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(listener)
        logger.info(f"Registered listener {listener.__name__} for event {event_name}")

    def dispatch(self, event_name: str, payload: Dict[str, Any]):
        """Dispatch an event to all registered listeners."""
        if event_name not in self._listeners:
            logger.debug(f"No listeners registered for event {event_name}")
            return
            
        logger.info(f"Dispatching event {event_name} to {len(self._listeners[event_name])} listeners")
        for listener in self._listeners[event_name]:
            try:
                listener(payload)
            except Exception as e:
                # We catch exceptions to prevent one listener from crashing the whole process
                logger.error(f"Error in listener {listener.__name__} for event {event_name}: {e}")

# Global dispatcher instance
event_dispatcher = EventDispatcher()