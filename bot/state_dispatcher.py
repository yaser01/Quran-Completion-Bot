from typing import Callable, Awaitable

from telegram import Update
from telegram.ext import ContextTypes

_STATE_HANDLERS: dict[str, Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]] = {}


def register_state(state: str):
    def decorator(fn: Callable):
        _STATE_HANDLERS[state] = fn
        return fn
    return decorator


async def dispatch(state: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    handler = _STATE_HANDLERS.get(state)
    if handler is not None:
        await handler(update, context)
