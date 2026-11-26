from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json
import os
import uuid


API_KEY = os.environ.get("EXTERNAL_API_KEY", "local-mock-key")
EXERCISES = [
    {"id": "ex-001", "name": "Goblet squat", "muscleGroup": "legs"},
    {"id": "ex-002", "name": "Dumbbell row", "muscleGroup": "back"},
    {"id": "ex-003", "name": "Push-up", "muscleGroup": "chest"},
]


class Handler(BaseHTTPRequestHandler):
    def _json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self):
        if self.headers.get("X-API-Key") == API_KEY:
            return True
        self._json(401, {"error": "invalid_api_key"})
        return False

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._json(200, {"status": "ok", "service": "external-mock"})
            return
        if parsed.path != "/api/v1/exercises":
            self._json(404, {"error": "not_found"})
            return
        if not self._authorized():
            return
        group = parse_qs(parsed.query).get("muscleGroup", [""])[0]
        exercises = [x for x in EXERCISES if not group or x["muscleGroup"] == group]
        self._json(200, {"exercises": exercises})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/v1/calendar/events":
            self._json(404, {"error": "not_found"})
            return
        if not self._authorized():
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(size) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._json(400, {"error": "invalid_json"})
            return
        if not isinstance(payload, dict):
            self._json(400, {"error": "expected_json_object"})
            return
        self._json(201, {"externalEventId": str(uuid.uuid4())})

    def log_message(self, format, *args):
        print("external-mock:", format % args, flush=True)


HTTPServer(("0.0.0.0", 8081), Handler).serve_forever()
