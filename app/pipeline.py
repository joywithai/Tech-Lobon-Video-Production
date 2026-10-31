from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,os,re,shutil,subprocess,uuid
import yaml
from PIL import Image,ImageFont
from . import brief,media,resources,learning,plan,sound,qa,resource_planning,card_lock
ROOT=Path(__file__).resolve().parents[1]

def save(path,obj):Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load_config():
 cfg=yaml.safe_load((ROOT/'config.yaml').read_text(encoding='utf-8'))
 if not isinstance(cfg,dict):raise ValueError('Invalid config.yaml')
 return cfg

def job_id():return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]

def copy_snapshot(src,dest):
 if not src.is_dir():raise ValueError('Input folder does not exist: '+str(src))
 for p in src.rglob('*'):
  if p.is_symlink() and not p.resolve().is_relative_to(src.resolve()):raise ValueError('Input symlink leaves input folder: '+str(p))
 shutil.copytree(src,dest,symlinks=False)

def make_sources(snapshot,job,config,parsed):
 dest=job/'resources';assets=resources.local(snapshot,dest)
 captures=parsed['meta'].get('capture_urls',[])
 if not isinstance(captures,list):raise ValueError('capture_urls must be a list of user-specified URLs or capture objects')
 for entry in captures:
  if isinstance(entry,str):url=entry;seconds=0
  elif isinstance(entry,dict):url=entry.get('url','');seconds=int(entry.get('record_seconds',0))
  else:raise ValueError('Invalid capture URL entry')
  assets.extend(resources.capture(url,dest,len(assets)+1,seconds))
 queries=resource_planning.discover(parsed,assets,config['providers'])
 for query in queries:
  if not config['resources'].get('allow_commons_search'):
   if query['essential']:raise ValueError('Essential resource missing: '+query['name']+'. Supply it in input/src or explicitly enable Commons search.')
   continue
  item=resources.commons(query['query'],dest,len(assets)+1)
  if item:assets.append(item)
  elif query['essential']:raise ValueError('No suitably licensed image found for '+query['name']+'; provide it in input/src')
 save(job/'resources.json',{'assets':assets,'search_queries':queries,'downloaded_assets_require_human_relevance_and_rights_review':True})
 return assets

def make_public(job_id,assets):
 pub=ROOT/'engines/video-making/public';card=pub/'card';jobs=pub/'jobs'/job_id
 if jobs.exists():raise ValueError('Public job folder exists; refusing overwrite')
 # The renderer copies the locked immutable assets; it never writes to channel_card/.
 for part in ['assets','fonts']:
  target=card/part
  if target.exists():shutil.rmtree(target)
  shutil.copytree(ROOT/'channel_card'/part,target)
 jobs.mkdir(parents=True)
 out=[]
 for a in assets:
  p=Path(a['path']);dest=jobs/p.name;shutil.copy2(p,dest)
  out.append({'id':a['id'],'public_path':f'jobs/{job_id}/{p.name}'})
 return out

def captions_fit(cues,fmt):
 size=46 if fmt=='vertical' else 42;limit=676 if fmt=='vertical' else 1256
 f=ImageFont.truetype(str(ROOT/'channel_card/fonts/NotoSansBengali-Bold.ttf'),size)
 for c in cues:
  if f.getlength(c['text'])>limit:raise ValueError('Subtitle too wide: split at real word boundaries or shorten display spelling; do not silently crop')

def render(job,output,fmt,timing,creative,assets,config):
 duration=timing['duration'];words=timing['words'];caps=media.captions(words,creative['display_words']);captions_fit(caps,fmt)
 media.write_srt(caps,output/'Subtitle.srt')
 public_assets=make_public(job.name,assets)
 render_plan={'format':fmt,'duration':duration,'fps':config['project']['frame_rate'],'words':words,'captions':caps,'scenes':creative['scenes'],'assets':public_assets}
 save(job/'render-plan.json',render_plan)
 if not (ROOT/'node_modules/@remotion/renderer').exists():raise ValueError('Node dependencies missing: run npm install in repository root')
 if not shutil.which('node') or not shutil.which('ffmpeg'):raise ValueError('Node.js and FFmpeg are required for rendering')
 visual=job/'visual.mp4'
 subprocess.run(['node',str(ROOT/'engines/video-making/render.mjs'),str(job/'render-plan.json'),str(visual),str(config['render']['concurrency']),str(config['render']['crf'])],cwd=ROOT,check=True)
 return render_plan,visual

def production(input_dir,project=None,parent=None):
 cfg=load_config();card_lock.check();source=Path(input_dir).expanduser().resolve()
 if not (source/'brief.md').is_file():raise ValueError('Missing input/brief.md. Supply a brief and optionally audio and src/ files.')
 key=job_id();job=ROOT/'work'/key;output=ROOT/'output'/key
 if job.exists() or output.exists():raise ValueError('Job collision; refusing overwrite')
 job.mkdir(parents=True);output.mkdir(parents=True)
 try:
  copy_snapshot(source,job/'input');parsed=brief.load(job/'input/brief.md');meta=parsed['meta']
  project=project or str(meta.get('project_id') or key)
  if not re.fullmatch(r'[A-Za-z0-9_.-]{1,80}',project):raise ValueError('project_id must use letters, digits, dot, dash or underscore')
  fmt=str(meta.get('format') or cfg['project']['default_format']).lower()
  if fmt in {'9:16','portrait'}:fmt='vertical'
  if fmt in {'16:9','landscape'}:fmt='horizontal'
  if fmt not in {'vertical','horizontal'}:raise ValueError('Video format must be vertical/9:16 or horizontal/16:9')
  description_unit=meta.get('description_unit') or cfg['project'].get('description_unit')
  if description_unit not in {'words','characters'}:raise ValueError('Description unit is unspecified. Set description_unit: words or characters in brief.md/config.yaml.')
  rules=learning.active(cfg['learning']['channel'],project);save(job/'applied-rules.json',{'project_id':project,'rules':rules})
  audio,source_kind=media.ensure_audio(job/'input',parsed['spoken'],meta.get('voice') or cfg['providers'].get('voice'),job/'narration')
  timing=media.timing(audio,parsed['spoken'],job/'input',job/'audio-timing.json',cfg['providers'])
  assets=make_sources(job/'input',job,cfg,parsed)
  dmin=int(meta.get('description_min',cfg['project']['description_min']));dmax=int(meta.get('description_max',cfg['project']['description_max']))
  if dmin<1 or dmax<dmin:raise ValueError('Invalid description bounds')
  creative=plan.build(parsed,timing,assets,rules,cfg['providers'],dmin,dmax,description_unit)
  if creative.get('rule_conflicts'):raise ValueError('Planner detected conflicting learning rules; user review required: '+str(creative['rule_conflicts']))
  plan.validate(creative,timing,assets,dmin,dmax,description_unit,parsed['visual_only']);save(job/'creative-plan.json',creative)
  rplan,visual=render(job,output,fmt,timing,creative,assets,cfg)
  events=sound.mux(visual,audio,rplan,output/'Video.mp4',float(cfg['render']['sfx_target_peak_dbfs']));save(job/'sound-events.json',events)
  spec=importlib.util.spec_from_file_location('thumbnail_render',ROOT/'engines/thumbnail/render.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  for i,thumb in enumerate(creative['thumbnails'],1):module.render(thumb,assets,output/f'Thumbnail{i}.png',i-1)
  info='\n\n'.join([*(f'TITLE {i}:\n{t}' for i,t in enumerate(creative['titles'],1)),f'DESCRIPTION:\n{creative["description"]}'])+'\n'
  (output/'uploadInfo.txt').write_text(info,encoding='utf-8')
  required=[output/'Video.mp4',*[output/f'Thumbnail{i}.png' for i in range(1,4)],output/'uploadInfo.txt',output/'Subtitle.srt']
  report=qa.run(job,output/'Video.mp4',required,rplan,timing)
  save(job/'job.json',{'id':key,'project_id':project,'parent_job':parent,'source_input':str(source),'audio_source':source_kind,'status':'review_required','outputs':[str(p) for p in required],'qa':report})
  learning.record_output(key,project,cfg['learning']['channel'],[r['id'] for r in rules])
  return {'id':key,'project_id':project,'output':str(output),'status':'review_required'}
 except Exception as e:
  save(job/'job-error.json',{'id':key,'status':'blocked','error':str(e),'retry':'Fix input/configuration and start a new run; existing job is preserved.'})
  raise

def revise(previous_job):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+',previous_job):raise ValueError('Invalid job id')
 job=ROOT/'work'/previous_job;record=job/'job.json';snapshot=job/'input'
 if not record.is_file() or not snapshot.is_dir():raise ValueError('Completed previous job and input snapshot not found')
 data=json.loads(record.read_text());return production(snapshot,project=data['project_id'],parent=previous_job)
