"""Tailnet-scoped map picker API and static host for the independent R3D viewer."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import sysconfig
import threading
import time
from urllib.parse import unquote, urlsplit

from acquisition import load_config, plan_area
from web_streaming import StreamCache

REPO = Path(__file__).resolve().parents[1]
WEB_ROOT = Path(os.environ.get('R3D_WEB_ROOT',REPO/'reports/generated/web-root')).resolve()
RUN_ROOT = Path(os.environ.get('R3D_WEB_RUNS',REPO/'reports/generated/web-runs')).resolve()
CONFIG = Path(os.environ.get('R3D_FETCH_CONFIG','/nonexistent')).resolve()
PUBLIC_ORIGIN = os.environ.get('R3D_ALLOWED_ORIGIN','https://ct104.taila8c9c.ts.net:8972').rstrip('/')
MAX_TILES = 24
MAX_RADIUS = 300
JOB_TTL = 24*60*60
LOCK = threading.Lock()
JOBS: dict[str,dict] = {}
ACTIVE: str|None = None
POOL = ThreadPoolExecutor(max_workers=1,thread_name_prefix='r3d-fetch')
STREAM = None
STREAM_LOCK = threading.Lock()


def stream_cache():
    global STREAM
    with STREAM_LOCK:
        if STREAM is None:
            STREAM = StreamCache(CONFIG, RUN_ROOT.parent/'stream-cache')
        return STREAM


class Handler(SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(WEB_ROOT),**kwargs)

    def log_message(self,fmt,*args):
        # HTTP bodies and user coordinates are intentionally never logged.
        sys.stderr.write('viewer-http '+fmt%args+'\n')

    def send_json(self,status,payload):
        body=json.dumps(payload,separators=(',',':')).encode()
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(body)

    def read_json(self):
        length=int(self.headers.get('Content-Length','0'))
        if not 1<=length<=2048:raise ValueError('入力サイズが不正です')
        value=json.loads(self.rfile.read(length))
        if not isinstance(value,dict):raise ValueError('入力形式が不正です')
        return value

    def origin_allowed(self):
        return self.headers.get('Origin','').rstrip('/')==PUBLIC_ORIGIN

    def do_GET(self):
        route=urlsplit(self.path).path
        # Serve the current UI for old generated scenes as well as the live root.
        ui_name=route.rsplit('/',1)[-1]
        if ui_name in ('app.js','stream-planner.mjs','stream-controller.mjs','stream-scene.mjs','index.html') or route.endswith('/'):
            translated=Path(self.translate_path(route))
            if route.endswith('/'):
                translated=translated/'index.html';ui_name='index.html'
            if translated.is_file() or ui_name.endswith('.mjs'):
                source=REPO/'viewer/independent'/ui_name
                if source.is_file():
                    body=source.read_bytes();self.send_response(200)
                    self.send_header('Content-Type','text/html; charset=utf-8' if ui_name=='index.html' else 'text/javascript; charset=utf-8')
                    self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store')
                    self.end_headers();self.wfile.write(body);return
        if route.endswith('/scene.json'):
            source=Path(self.translate_path(route))
            if source.is_file():
                self.send_json(200,{**json.loads(source.read_text()),'webStreaming':True});return
        if route=='/api/status':
            self.send_json(200,{'ready':CONFIG.is_file() and WEB_ROOT.is_dir(),'limitTiles':MAX_TILES,'limitRadiusMeters':MAX_RADIUS,
                               'streaming':CONFIG.is_file(),'streamZooms':[18,19,20],'streamIndexZoom':13,'streamWorkers':2})
            return
        match=re.fullmatch(r'/api/stream/jobs/([0-9a-f]{32})',route)
        if match:
            state=STREAM.state(match.group(1)) if STREAM else None
            self.send_json(200 if state else 404,state or {'error':'タイル処理IDが見つかりません'})
            return
        match=re.fullmatch(r'/stream-assets/([0-9a-f]{24})/([0-9a-f]{32})/(mesh\.bin|splats\.bin|texture\.png)',route)
        if match:
            source=STREAM.asset(*match.groups()) if STREAM else None
            if source is None:
                self.send_json(404,{'error':'タイルのキャッシュがありません。再取得してください。'});return
            with source:
                self.send_response(200)
                self.send_header('Content-Type','image/png' if route.endswith('.png') else 'application/octet-stream')
                self.send_header('Content-Length',str(os.fstat(source.fileno()).st_size))
                self.send_header('Cache-Control','private, max-age=300, immutable')
                self.send_header('X-Content-Type-Options','nosniff');self.end_headers()
                shutil.copyfileobj(source,self.wfile)
            return
        if route.startswith('/stream-assets/'):
            self.send_json(404,{'error':'ファイルが見つかりません'});return
        match=re.fullmatch(r'/api/jobs/([0-9a-f]{20})',route)
        if match:
            with LOCK:job=JOBS.get(match.group(1))
            if not job:self.send_json(404,{'error':'処理IDが見つかりません'});return
            self.send_json(200,{k:v for k,v in job.items() if k not in ('runDir','future')});return
        super().do_GET()

    def do_POST(self):
        if not self.origin_allowed():self.send_json(403,{'error':'同じサイトからの操作だけ受け付けます'});return
        route=urlsplit(self.path).path
        if route=='/api/stream/request':
            try:
                tile=self.read_json()
                if not CONFIG.is_file():
                    self.send_json(503,{'error':'サーバーに取得設定がありません'});return
                cache=stream_cache();state=cache.request(tile)
                if state['status']=='queued':state=cache.settle(state['id']) or state
                self.send_json(202 if state['status']=='queued' else 200,state)
            except (ValueError,TypeError,KeyError,json.JSONDecodeError):
                self.send_json(400,{'error':'タイル座標が不正です。対応するズームは18〜20です。'})
            except BlockingIOError:
                self.send_json(429,{'error':'タイルの処理待ちです。少し待って再試行してください。','retryAfter':1})
            except PermissionError:
                self.send_json(503,{'error':'Apple Mapsの取得認証が失効しました。サーバーの取得設定を更新してください。','authenticationFailed':True})
            return
        try:
            request=self.read_json()
            lat=float(request['lat']);lon=float(request['lon']);radius=float(request['radiusMeters'])
            zoom=int(request.get('zoom',20))
            if radius>MAX_RADIUS:raise ValueError(f'1回の取得範囲は{MAX_RADIUS}m以下にしてください')
            if zoom!=20:raise ValueError('地図からの取得はz20です')
            if not CONFIG.is_file():self.send_json(503,{'error':'サーバーに取得設定がありません'});return
            load_config(CONFIG)
            plan=plan_area(lat,lon,radius,zoom,max_tiles=MAX_TILES)
        except (KeyError,TypeError,ValueError,OverflowError,FileNotFoundError,json.JSONDecodeError):
            self.send_json(400,{'error':'緯度・経度・範囲を確認してください。指定上限は範囲300m、1回24タイルです。'});return
        if route=='/api/plan':
            self.send_json(200,{'center':plan['center'],'radiusMeters':radius,'zoom':zoom,
                                'tileCount':len(plan['tiles']),'heightLayers':'auto','bounds':plan['boundsUnwrappedSWNE']});return
        if route!='/api/jobs':self.send_json(404,{'error':'APIが見つかりません'});return
        global ACTIVE
        with LOCK:
            if ACTIVE is not None:
                self.send_json(429,{'error':'別の取得処理が進行中です。完了してから再度お試しください。'});return
            job_id=secrets.token_hex(10)
            run_dir=RUN_ROOT/job_id
            state={'id':job_id,'status':'queued','stage':'取得準備','tileCount':len(plan['tiles']),
                   'started':time.time(),'runDir':str(run_dir)}
            JOBS[job_id]=state;ACTIVE=job_id
            future=POOL.submit(run_job,job_id,plan,run_dir)
            state['future']=future
        self.send_json(202,{'id':job_id,'tileCount':len(plan['tiles']),'status':'queued'})


def remove_old_jobs():
    cutoff=time.time()-JOB_TTL
    if not RUN_ROOT.exists():return
    for path in RUN_ROOT.iterdir():
        if re.fullmatch(r'[0-9a-f]{20}',path.name) and path.stat().st_mtime<cutoff:
            link=WEB_ROOT/'scenes'/path.name
            if link.is_symlink():link.unlink()
            shutil.rmtree(path,ignore_errors=True)


def run_job(job_id,plan,run_dir):
    global ACTIVE
    try:
        RUN_ROOT.mkdir(parents=True,exist_ok=True)
        run_dir.mkdir(parents=True,exist_ok=False)
        with LOCK:JOBS[job_id]['status']='running';JOBS[job_id]['stage']='全高さ層のR3D取得・独立復号・3D生成'
        # Reuse the exact interpreter serving this API and pass its package path
        # explicitly. The API and worker must not silently resolve different
        # Python environments under systemd.
        child_env=os.environ.copy()
        package_path=sysconfig.get_path('purelib')
        existing=child_env.get('PYTHONPATH')
        child_env['PYTHONPATH']=os.pathsep.join(p for p in (package_path,str(REPO/'pipeline'),existing) if p)
        command=[sys.executable,str(REPO/'pipeline/r3d_explorer.py'),
                 '--lat',str(plan['center'][0]),'--lon',str(plan['center'][1]),
                 '--radius-m',str(plan['radiusMeters']),'--zoom','20','--max-tiles',str(MAX_TILES),
                 '--max-height-requests','1536',
                 '--out-dir',str(run_dir),'--config',str(CONFIG)]
        with (run_dir/'web-run.log').open('w') as log:
            result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=900,check=False,env=child_env)
        manifest=run_dir/'run.json'
        if result.returncode or not manifest.is_file():
            output=(run_dir/'web-run.log').read_text(errors='replace')
            if 'ModuleNotFoundError:' in output:
                raise RuntimeError('サーバーのPython依存関係が不足しています。管理者が依存関係を復旧する必要があります。')
            raise RuntimeError(f'取得・復号の実行に失敗しました（処理ID: {job_id}）。場所を変えても解決しない場合はこのIDを添えてください。')
        run=json.loads(manifest.read_text())
        if not run.get('pass'):raise RuntimeError('R3Dを検証できませんでした。別の場所を選んでください。')
        scene=run_dir/'viewer'
        if not (scene/'scene.json').is_file():raise RuntimeError('3Dデータを生成できませんでした。')
        scenes=WEB_ROOT/'scenes';scenes.mkdir(parents=True,exist_ok=True)
        link=scenes/job_id;temporary=scenes/(job_id+'.tmp')
        temporary.symlink_to(scene,target_is_directory=True);temporary.replace(link)
        with LOCK:
            JOBS[job_id].update(status='ready',stage='表示できます',viewer=f'/scenes/{job_id}/',
                                 totals=run['steps'][-1].get('counts',{}),finished=time.time())
    except subprocess.TimeoutExpired:
        set_failed(job_id,'取得が15分を超えました。範囲を小さくして再試行してください。')
    except Exception as error:
        set_failed(job_id,str(error) if isinstance(error,RuntimeError) else '取得処理に失敗しました。もう一度お試しください。')
    finally:
        with LOCK:
            if ACTIVE==job_id:ACTIVE=None


def set_failed(job_id,message):
    with LOCK:
        if job_id in JOBS:JOBS[job_id].update(status='failed',stage='失敗',message=message,finished=time.time())


def main():
    WEB_ROOT.mkdir(parents=True,exist_ok=True);RUN_ROOT.mkdir(parents=True,exist_ok=True)
    if not WEB_ROOT.joinpath('index.html').is_file():raise SystemExit('R3D web root is missing index.html')
    remove_old_jobs()
    port=int(os.environ.get('R3D_WEB_PORT','8972'))
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler);server.daemon_threads=True
    print(f'R3D map viewer listening on 127.0.0.1:{port}',flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        POOL.shutdown(wait=False,cancel_futures=True)
        if STREAM:STREAM.close()


if __name__=='__main__':main()
