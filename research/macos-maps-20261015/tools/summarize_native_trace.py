#!/usr/bin/env python3
"""Summarize xctrace GPU XML with explicit target-process filtering."""
import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def summarize(path,pid):
    data=path.read_bytes()
    root=ET.fromstring(data)
    ids={e.get('id'):e for e in root.iter() if e.get('id')}
    selected=[]
    rows=root.findall('.//row')
    for row in rows:
        process=row.find('process')
        if process is None:
            continue
        process=ids.get(process.get('ref'),process)
        value=process.find('pid')
        if value is None:
            continue
        value=ids.get(value.get('ref'),value)
        if value.text and int(value.text)==pid:
            selected.append(row)
    return dict(source_sha256=hashlib.sha256(data).hexdigest(),target_pid=pid,
        total_gpu_rows=len(rows),target_gpu_rows=len(selected),excluded_gpu_rows=len(rows)-len(selected),
        has_target_gpu_activity=bool(selected),
        caveat='System GPU tables include other processes even with --attach. A successful recording alone is not proof of target activity.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('xml',type=Path)
    parser.add_argument('--pid',type=int,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=summarize(args.xml,args.pid)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
