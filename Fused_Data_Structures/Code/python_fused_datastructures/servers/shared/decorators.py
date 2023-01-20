import functools
from typing import List, Optional

from .events import MutationEventObserver, MutationEventType, MutationEventAsyncObserver


def observed_by(
    observers: Optional[List[MutationEventObserver]] = None,
    async_observers: Optional[List[MutationEventAsyncObserver]] = None
):
    def observable_init(self) -> None:
        self._observers = observers
        self._async_observers = async_observers

        return self

    return observable_init


def emits(mutation: MutationEventType):
    async def emit(self, args):
        event = mutation(
            args,
            self.cluster_identifier,
            self.identifier,
            self.structure_type,
            self.backup_connection_manager if hasattr(self, 'backup_connection_manager') else None,
        )

        if self._observers:
            for observer in self._observers:
                observer(event)

        if self._async_observers:
            for observer in self._async_observers:
                await observer(event)

    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args):
            self, *_ = args
            await emit(self, func(*args))
        return wrapped
    return wrapper


def self_await(func):
    @functools.wraps(func)
    async def _self_await(*args, **kwargs):
        return await func(*args, **kwargs)
    return _self_await
