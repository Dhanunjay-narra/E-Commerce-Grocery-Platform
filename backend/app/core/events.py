"""Asynchronous Domain Event Bus for decoupled inter-module messaging."""
import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine, Dict, List, Type
from app.core.logging import logger


@dataclass
class DomainEvent:
    """Base domain event class."""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str = field(default_factory=lambda: "")

    def __post_init__(self):
        if not self.event_id:
            import uuid
            self.event_id = str(uuid.uuid4())


EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]


class EventBus:
    """Pub/Sub Event Bus supporting async in-process dispatch and workers."""

    def __init__(self):
        self._subscribers: Dict[Type[DomainEvent], List[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """Subscribes an asynchronous handler to a domain event type."""
        self._subscribers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """Publishes a domain event to all subscribed listeners."""
        handlers = self._subscribers.get(type(event), [])
        if not handlers:
            return

        logger.info(f"Dispatching event {type(event).__name__} ({event.event_id}) to {len(handlers)} handlers.")
        tasks = []
        for handler in handlers:
            tasks.append(self._execute_handler(handler, event))
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_handler(self, handler: EventHandler, event: DomainEvent) -> None:
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error executing event handler {handler.__name__} for {type(event).__name__}: {str(e)}", exc_info=True)


event_bus = EventBus()
