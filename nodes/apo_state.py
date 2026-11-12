"""Tiny in-process memory shared by the Chat and Unload nodes.

The Chat node records which model it asked the server for; the Unload node then unloads
exactly those models, so the model name only ever needs to be typed in the Chat node.
"""
import threading

_lock = threading.Lock()
_used = []


def note_model(model):
    model = (model or "").strip()
    if not model:
        return
    with _lock:
        if model in _used:
            _used.remove(model)
        _used.append(model)


def take_models():
    """Return the models used since the last unload (oldest first) and clear the list."""
    with _lock:
        models = list(_used)
        _used.clear()
    return models


def restore_models(models):
    for m in models:
        note_model(m)
