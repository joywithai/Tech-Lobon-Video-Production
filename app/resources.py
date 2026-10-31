from pathlib import Path
import hashlib,json,shutil,requests
EXT={'.png','.jpg','.jpeg','.webp'}
VIDEO_EXT={'.mp4','.webm','.mov'}
UA={'User-Agent':'TechLobonVideoMaker/1.0 (resource attribution review)'}

def local(input_dir,dest):
 src=Path(input_dir)/'src';dest.mkdir(parents=True,exist_ok=True);out=[]
 if not src.is_dir():return out
 for p in sorted(src.rglob('*')):
  if not p.is_file() or p.suffix.lower() not in EXT|VIDEO_EXT:continue
  if not p.resolve().is_relative_to(src.resolve()):raise ValueError('Resource symlink leaves input/src')
  if p.stat().st_size>100*1024*1024:raise ValueError('User resource exceeds 100 MiB: '+p.name)
  content=p.read_bytes();name=hashlib.sha256(content).hexdigest()[:16]+p.suffix.lower();q=dest/name;q.write_bytes(content)
  out.append({'id':'asset-'+str(len(out)+1),'name':p.name,'path':str(q),'source':'user input','license':'user-provided; confirm reuse rights','sha256':hashlib.sha256(content).hexdigest()})
 return out

def commons(query,dest,index):
 api='https://commons.wikimedia.org/w/api.php';params={'action':'query','generator':'search','gsrsearch':query,'gsrnamespace':6,'gsrlimit':8,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':1400,'format':'json'}
 r=requests.get(api,params=params,headers=UA,timeout=30);r.raise_for_status();pages=r.json().get('query',{}).get('pages',{}).values()
 for page in pages:
  x=(page.get('imageinfo') or [{}])[0];meta=x.get('extmetadata',{});lic=meta.get('LicenseShortName',{}).get('value','')
  if not any(lic.upper().startswith(t) for t in ['CC BY','CC0','PUBLIC DOMAIN']):continue
  url=x.get('thumburl') or x.get('url','');suffix=Path(url.split('?')[0]).suffix.lower()
  if suffix not in EXT or not url.startswith('https://upload.wikimedia.org/'):continue
  with requests.get(url,headers=UA,stream=True,timeout=30) as r:
   r.raise_for_status();content=bytearray()
   for chunk in r.iter_content(65536):
    content.extend(chunk)
    if len(content)>15*1024*1024:raise ValueError('Remote image exceeds max download size')
  q=Path(dest)/(hashlib.sha256(content).hexdigest()[:16]+suffix);q.write_bytes(content)
  return {'id':'asset-'+str(index),'name':page.get('title'),'path':str(q),'source':x.get('descriptionurl'),'download_url':url,'license':lic,'license_url':meta.get('LicenseUrl',{}).get('value'),'author':meta.get('Artist',{}).get('value'),'sha256':hashlib.sha256(content).hexdigest(),'review_required':True}
 return None

def capture(url,dest,index,record_seconds=0):
 """Capture only a user-specified public HTTPS page. Never login or access private hosts."""
 from urllib.parse import urlparse
 import ipaddress,socket
 from playwright.sync_api import sync_playwright
 def public_https(u):
  p=urlparse(u)
  if p.scheme!='https' or not p.hostname or p.username or p.password:return False
  try:
   ips={x[4][0] for x in socket.getaddrinfo(p.hostname,p.port or 443,type=socket.SOCK_STREAM)}
   return bool(ips) and all(ipaddress.ip_address(x).is_global for x in ips)
  except (OSError,ValueError):return False
 if not public_https(url):raise ValueError('Capture requires a public HTTPS URL, not a private/local address')
 if not 0<=record_seconds<=30:raise ValueError('Screen recording duration must be 0..30 seconds')
 dest=Path(dest);dest.mkdir(parents=True,exist_ok=True);items=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True)
  kwargs={'viewport':{'width':1280,'height':720}}
  if record_seconds:kwargs.update({'record_video_dir':str(dest),'record_video_size':{'width':1280,'height':720}})
  context=browser.new_context(**kwargs)
  def route(request_route):
   if public_https(request_route.request.url):request_route.continue_()
   else:request_route.abort()
  context.route('**/*',route);page=context.new_page();page.goto(url,wait_until='domcontentloaded',timeout=30000)
  if record_seconds:page.wait_for_timeout(int(record_seconds*1000))
  image=dest/f'capture-{index}.png';page.screenshot(path=str(image),full_page=False);video=page.video
  context.close();vp=Path(video.path()) if video else None;browser.close()
  items.append({'id':'asset-'+str(index),'name':'User-requested page screenshot','path':str(image),'source':url,'license':'screenshot; site/content rights require review','sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'review_required':True})
  if vp:
   items.append({'id':'asset-'+str(index+1),'name':'User-requested screen recording','path':str(vp),'source':url,'license':'recording; site/content rights require review','sha256':hashlib.sha256(vp.read_bytes()).hexdigest(),'review_required':True})
 return items
