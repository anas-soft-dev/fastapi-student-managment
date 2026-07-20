import os, sys, threading, traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

_app, _lock = None, threading.Lock()

def application(environ, start_response):
    global _app
    if _app is None:
        with _lock:
            if _app is None:
                try:
                    from a2wsgi import ASGIMiddleware
                    from main import app as fastapi_app
                    _app = ASGIMiddleware(fastapi_app)
                except Exception:
                    start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
                    return [traceback.format_exc().encode()]
    return _app(environ, start_response)