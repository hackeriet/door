# I am a very slow backend.

import sys
import SocketServer
import BaseHTTPServer
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from pprint import pformat, pprint
import datetime
from time import sleep

SERVERPORT=9488
SERVERNAME="http://127.0.0.1:%s/" % SERVERPORT

HEAD_CONTENT="""<html><body><h1>Slow</h1>
<p>This is a test backend/web server that is very slow. </p>
URLs available:
<ul>
<li><a href="/one">/one</a>
<li><a href="/two">/two</a>
</ul>
"""
TAIL_CONTENT="""</body></html>"""

class requesthandler(BaseHTTPRequestHandler):
  # http://docs.python.org/library/basehttpserver.html#BaseHTTPServer.BaseHTTPRequestHandler
  def do_GET(self):
    # remove any GET-args
    if "?" in self.path:
      self.path = self.path[0:self.path.index("?")]
    if self.path == "/one":
      servicetime=10
      sleep(servicetime)
      self.send_response(200, "OK")
      self.send_header("Cache-Control", "max-age=15") # no idea if this matters
      self.send_header("Content-Type", "text/plain")
      self.end_headers()
      self.wfile.write("pretty page content that took %s seconds to create" % servicetime)
    elif self.path in ["/", "/content/"]:
      self.send_response(200, "OK")
      self.send_header("Cache-Control", "max-age=15")
      self.send_header("Content-Type", "text/html")
      self.end_headers()
      self.wfile.write(HEAD_CONTENT)
      self.wfile.write("<p>Complete header set:</p><pre>%s</pre>" % pformat(self.headers.items()))
      self.wfile.write("<p>This page was generated %s.</p>" % (datetime.datetime.now().isoformat()))
      self.wfile.write(TAIL_CONTENT)
    else:
      self.send_error(404, "Not found")
      self.end_headers()
      msg = "404 Not found"
      self.wfile.write(msg)

  def do_POST(self):
    if self.path == "/post":
      resp = "Done!\n"
      buf = ''
      while (len(buf) < int(self.headers["content-length"])):
        buf += self.rfile.read(1024)
        sleep(0.1)
        sys.stdout.write(".")
        sys.stdout.flush()

      self.send_response(200, "OK")
      self.send_header("Content-Type", "text/plain")
      self.send_header("Content-Length", len(resp))
      self.end_headers()
      self.wfile.write(resp)
    else:
      self.send_error(404, "Not found")
      self.end_headers()
      msg = "404 Not found"
      self.wfile.write(msg)

class ThreadedHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
  """Handle requests in a separate thread."""


if __name__ == "__main__":
  server_address = ('', SERVERPORT)
  print "Listening to %s" % SERVERNAME
  SocketServer.TCPServer.allow_reuse_address = True
  httpd = ThreadedHTTPServer(server_address, requesthandler)
  httpd.serve_forever()

