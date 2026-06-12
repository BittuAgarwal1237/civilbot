import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pipeline import run_pipeline

class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # Console spam band

    def do_GET(self):
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = json.loads(self.rfile.read(length))
        complaint = body.get("complaint", "").strip()

        if not complaint:
            self._json({"error": "Complaint empty hai"})
            return

        try:
            result = run_pipeline(complaint)
            self._json({
                "classifier_result": result["classifier_result"],
                "evidence": result["evidence"],
                "dept_result": result["dept_result"],
                "draft_result": {
                    "letter_type": result["draft_result"]["letter_type"],
                    "letter_text": result["draft_result"]["letter_text"],
                    "addressed_to": result["draft_result"]["addressed_to"],
                    "response_deadline": result["draft_result"]["response_deadline"],
                },
                "tasks": result["tasks"]
            })
        except Exception as e:
            self._json({"error": str(e)})

    def _json(self, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print("🚀 Server chal raha hai: http://localhost:8000")
    HTTPServer(("", 8000), Handler).serve_forever()