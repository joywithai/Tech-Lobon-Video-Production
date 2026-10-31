from pathlib import Path
import hashlib,json,subprocess
from .media import probe
from .card_lock import check

def run(job,video,outputs,plan,timing):
 info=probe(video);streams=info['streams'];v=next((s for s in streams if s.get('codec_type')=='video'),None);a=next((s for s in streams if s.get('codec_type')=='audio'),None)
 if not v or not a or v.get('codec_name')!='h264':raise ValueError('Rendered video streams missing or invalid')
 if abs(float(info['format']['duration'])-plan['duration'])>.2:raise ValueError('Output duration differs from narration')
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
 for p in outputs:
  if not Path(p).is_file() or Path(p).stat().st_size==0:raise ValueError('Required output missing: '+str(p))
 motion=stage_motion_probe(video,plan['format'])
 report={'stage_motion_diagnostic':motion,'video':str(video),'sha256':hashlib.sha256(Path(video).read_bytes()).hexdigest(),'decoded_without_error':True,'locked_card':check(),'duration_seconds':plan['duration'],'word_timing_method':timing['method'],'human_listening_verified':False,'creative_review_required':True,'audio_listening_reviewed':False,'scene_motion_quality_verified':False,'resource_appropriateness_verified':False,'publishing_authorized':False}
 (Path(job)/'quality-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');return report

def stage_motion_probe(video,fmt):
 """Pixel-difference warning aid only; not a creative or speech-sync judgment."""
 import numpy as np
 x,y,w,h=(90,204,900,1398) if fmt=='vertical' else (72,128,1776,772)
 vf=f'fps=1,crop={w}:{h}:{x}:{y},scale=120:120:flags=area,format=gray'
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-an','-vf',vf,'-f','rawvideo','-'])
 a=np.frombuffer(raw,dtype=np.uint8)
 if len(a)<2*120*120:return {'sampled_intervals':0,'note':'Clip too short to measure'}
 a=a.reshape((-1,120,120)).astype('int16');d=np.abs(np.diff(a,axis=0)).mean(axis=(1,2))
 return {'sampled_intervals':len(d),'mean_delta':round(float(d.mean()),3),'near_static_intervals':int((d<.10).sum()),'note':'Excludes subtitle area. Pixels do not establish meaningful motion or quality.'}
