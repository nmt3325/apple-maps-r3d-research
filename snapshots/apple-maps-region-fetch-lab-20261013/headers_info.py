from mitmproxy import io
from urllib.parse import urlsplit,parse_qs
with open('/var/lib/mitmproxy-flyover/flows/applemaps-20261013.mitm','rb') as r:
 for f in io.FlowReader(r).stream():
  if f.response and parse_qs(urlsplit(f.request.pretty_url).query).get('style')==['98']:
   print('method',f.request.method,'host',f.request.host,'headers',sorted(f.request.headers.keys()))
   break
