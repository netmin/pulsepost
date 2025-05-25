"""Minimal FastAPI stub with optional fallback to real package."""
import importlib.util
import sys
import os

_real_spec = None
for path in list(sys.path)[1:]:
    spec = importlib.util.find_spec('fastapi', [path])
    if spec and spec.origin != __file__:
        _real_spec = spec
        break
if _real_spec:
    _module = importlib.util.module_from_spec(_real_spec)
    _real_spec.loader.exec_module(_module)
    FastAPI = _module.FastAPI
else:
    class FastAPI:
        def __init__(self):
            self.routes = {}

        def get(self, path):
            def decorator(func):
                self.routes[path] = func
                return func
            return decorator
