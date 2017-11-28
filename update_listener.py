#!/usr/bin/env python3
from io import StringIO
from http.server import *
import json
import syslogger

log = syslogger.getLogger()

PORT = 8000
CONF = "/tmp/doord.json"
MAX_REQUEST_LENGTH = 4 * 1024 * 1024

class RequestHandler(BaseHTTPRequestHandler):
  def do_POST(self):
    # Takes care of returning responses on errors
    if not self.validate_post_request():
      return

    # Read and buffer POST data
    buf = StringIO()
    buf_len = 0
    while (buf_len < int(self.headers["content-length"])):
      data = self.rfile.read(1).decode("utf8")
      buf_len += buf.write(data)

    # Parse JSON to verify its structure
    parsed = {}
    try:
      parsed = json.dumps(buf.getvalue(), indent=2)
    except json.JSONDecodeError as e:
      log.critical("Failed to parse JSON string", e)
      self.send_error(400, explain="Invalid JSON")
      return

    # Serialize and save configuration to disk
    with open(CONF, mode='w', encoding="utf8") as config_file:
      json.dump(parsed, config_file, ensure_ascii=True)

    self.send_response(204)

  def validate_post_request(self):
    if self.path != "/":
      self.send_error(404)
      return False

    if self.headers["content-type"] != "application/json":
      self.send_error(400, explain="Only accepts application/json")
      return False

    if not "content-length" in self.headers:
      self.send_error(400, explain="No content length set") 
      return False
    
    # TODO: this will throw if content-length is not a number
    content_length = int(self.headers["content-length"])

    # Valid JSON contains at least "{}"
    if content_length < 2:
      self.send_error(400, explain="Post data too short")
      return False

    if content_length > MAX_REQUEST_LENGTH:
      self.send_error(400, explain="Request too big") 
      return False

    # Trust that the request is legit if we're here
    return True


def run(server_class=HTTPServer, handler_class=RequestHandler):
    log.info("Serving on port %d" % PORT)
    server_address = ("", PORT)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

run()

