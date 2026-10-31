from pathlib import Path
from datetime import datetime,timezone
import json,os,tempfile,uuid
ROOT=Path(__file__).resolve().parents[1];DIR=ROOT/'learning_box';RULES=DIR/'rules.json';EVENTS=DIR/'events.jsonl'
def read():
 obj=json.loads(RULES.read_text(encoding='utf-8'))
 if not isinstance(obj.get('rules'),list):raise ValueError('Malformed learning-box rules')
 return obj

def active(channel='Tech Lobon',project=None):
 return [r for r in read()['rules'] if r.get('status')=='active' and (r.get('scope')=='global' or (r.get('scope')=='channel' and r.get('channel')==channel) or (r.get('scope')=='project' and r.get('project')==project))]

def atomic(data):
 fd,tmp=tempfile.mkstemp(prefix='.rules-',dir=DIR,text=True)
 try:
  with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  os.replace(tmp,RULES)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)

def log(event):
 with EVENTS.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())

def add(instruction,observation,scope='channel',channel='Tech Lobon',project=None,job=None):
 if not instruction.strip() or not observation.strip():raise ValueError('Explicit observation and correction instruction are required')
 if scope not in {'global','channel','project'}:raise ValueError('Invalid scope')
 if scope=='project' and not project:raise ValueError('Project-scope feedback needs --project')
 entry={'id':'L-'+uuid.uuid4().hex[:12],'scope':scope,'channel':channel if scope=='channel' else None,'project':project if scope=='project' else None,'instruction':instruction.strip(),'source':'explicit user feedback','status':'active'}
 event={'event_id':uuid.uuid4().hex,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'type':'rule_added','observation':observation.strip(),'job':job,'rule':entry}
 obj=read();obj['rules'].append(entry);log(event);atomic(obj)
 return entry

def disable(rule_id,reason):
 if not reason.strip():raise ValueError('Explicit reason required')
 obj=read();r=next((x for x in obj['rules'] if x['id']==rule_id),None)
 if not r:raise ValueError('Unknown rule')
 r['status']='inactive';log({'event_id':uuid.uuid4().hex,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'type':'rule_disabled','rule_id':rule_id,'reason':reason});atomic(obj)
 return r

def record_output(job_id,project_id,channel,rule_ids):
 """Record an output/review checkpoint; do not invent a correction before user feedback."""
 event={'event_id':uuid.uuid4().hex,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'type':'output_created','job':job_id,'project':project_id,'channel':channel,'applied_rule_ids':rule_ids,'review_status':'awaiting_user_feedback'}
 log(event);return event
