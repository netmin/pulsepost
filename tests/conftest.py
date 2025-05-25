import asyncio

# Minimal asyncio marker support without pytest-asyncio

def pytest_pyfunc_call(pyfuncitem):
    if 'asyncio' in pyfuncitem.keywords:
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(pyfuncitem.obj())
        finally:
            loop.close()
        return True
    return None
