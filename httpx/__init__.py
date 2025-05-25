"""Minimal httpx stub with fallback to real package."""
import asyncio
import importlib.util
import sys

_real_spec = None
for path in list(sys.path)[1:]:
    spec = importlib.util.find_spec('httpx', [path])
    if spec and spec.origin != __file__:
        _real_spec = spec
        break
if _real_spec:
    _module = importlib.util.module_from_spec(_real_spec)
    _real_spec.loader.exec_module(_module)
    AsyncClient = _module.AsyncClient
    Response = _module.Response
else:
    class Response:
        def __init__(self, status_code: int, json_data):
            self.status_code = status_code
            self._json = json_data

        def json(self):
            return self._json

    class AsyncClient:
        def __init__(self, app, base_url: str = ""):
            self.app = app
            self.base_url = base_url

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, path: str):
            handler = self.app.routes.get(path)
            if handler is None:
                return Response(404, None)
            result = handler()
            if asyncio.iscoroutine(result):
                result = await result
            return Response(200, result)
