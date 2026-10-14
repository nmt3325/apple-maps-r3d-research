"""One-time local setup from a supplied capture and signing source; never log credentials.

Run with a Python environment containing mitmproxy. Runtime fetch/decode/viewer
does not require a capture, mitmproxy, Simulator, or Apple library.
"""
import argparse
import json
import os
from pathlib import Path
import re
from urllib.parse import parse_qsl, urlsplit, urlunsplit
from mitmproxy import io

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--capture',type=Path,required=True);ap.add_argument('--signing-source',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);args = ap.parse_args()
    source = args.signing_source.read_text()
    parts = []
    for name in ('tokenP1','tokenP2'):
        match = re.search(r'var\s+'+name+r'\s*=\s*"([^"]+)"',source)
        if not match: raise ValueError('Signing source does not contain required pair')
        parts.append(match.group(1))
    template = None
    with args.capture.open('rb') as stream:
        for flow in io.FlowReader(stream).stream():
            if not flow.response or flow.response.status_code!=200: continue
            u = urlsplit(flow.request.pretty_url);q = parse_qsl(u.query,keep_blank_values=True);p = dict(q)
            if p.get('style')=='98' and p.get('z')=='20' and p.get('h')=='0' and flow.response.content.startswith(bytes.fromhex('3d96592e')):
                template = {'schemaVersion':1,'endpoint':urlunsplit((u.scheme,u.netloc,u.path,'','')),
                            'queryParameters':[[k,v] for k,v in q if k!='accessKey'],
                            'headers':{k:flow.request.headers[k] for k in ('user-agent','accept','accept-language','accept-encoding') if k in flow.request.headers},
                            'signingParts':parts};break
    if template is None: raise ValueError('No successful style98 z20 h0 template in supplied capture')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    fd = os.open(args.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as output: output.write(json.dumps(template,indent=2)+'\n')
    print('Local signing configuration prepared; no saved accessKey copied')

if __name__=='__main__':main()
