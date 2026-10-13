#!/usr/bin/env python3
import http.server,pathlib,re,secrets,os
PORT=8894
ROOT=pathlib.Path('/opt/flyover-viewer/decoded-native')
ROOT.mkdir(parents=True,exist_ok=True)
TOKEN=pathlib.Path('/opt/flyover-viewer/ingest.token').read_text().strip()
class Handler(http.server.BaseHTTPRequestHandler):
 def do_POST(self):
  name=self.path.removeprefix('/upload/')
  if not self.path.startswith('/upload/') or not re.fullmatch(r'[A-Za-z0-9._-]{5,100}',name) or '..' in name:
   self.send_error(404);return
  if not secrets.compare_digest(self.headers.get('X-Transfer-Token',''),TOKEN):
   self.send_error(403);return
  try:
   length=int(self.headers.get('Content-Length','0'))
  except ValueError:
   self.send_error(400);return
  if not 0<length<50_000_000:
   self.send_error(413);return
  body=self.rfile.read(length)
  if len(body)!=length:self.send_error(400);return
  out=ROOT/name
  out.write_bytes(body);os.chmod(out,0o600)
  self.send_response(200);self.end_headers();self.wfile.write(f'Saved {name}: {len(body)} bytes'.encode())
 def log_message(self,*args):pass
http.server.HTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
