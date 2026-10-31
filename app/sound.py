from pathlib import Path
import array,math,subprocess,wave
ROOT=Path(__file__).resolve().parents[1]
def sfx_gain(path,target_db):
 with wave.open(str(path),'rb') as w:
  if w.getsampwidth()!=2:raise ValueError('SFX must be 16-bit PCM')
  samples=array.array('h',w.readframes(w.getnframes()))
 if not samples:raise ValueError('Empty SFX')
 peak=max(abs(x) for x in samples)/32768
 if peak==0:raise ValueError('Silent SFX')
 return min(8.0,10**(target_db/20)/peak)

def mux(visual,audio,plan,output,target=-18):
 if not -24<=target<=-12:raise ValueError('SFX peak target must be -24..-12 dBFS')
 events=sorted([e for s in plan['scenes'] for e in s.get('sfx',[])],key=lambda x:x['time'])
 if len(events)>80:raise ValueError('Too many SFX events; reduce to meaningful events')
 if any(b['time']-a['time']<.12 for a,b in zip(events,events[1:])):raise ValueError('SFX events too close; review overlap')
 cmd=['ffmpeg','-y','-v','error','-i',str(visual),'-i',str(audio)];filters=['[1:a]aresample=48000,aformat=channel_layouts=stereo[voice]'];labels=['[voice]']
 for i,e in enumerate(events,2):
  path=ROOT/'engines/video-making/public/sfx'/f"{e['kind']}.wav"
  if not path.is_file():raise ValueError('Missing SFX '+str(path))
  cmd+=['-i',str(path)];gain=sfx_gain(path,target);delay=round(e['time']*1000)
  filters.append(f'[{i}:a]aresample=48000,volume={gain:.6f},adelay={delay}|{delay},aformat=channel_layouts=stereo[s{i}]');labels.append(f'[s{i}]')
 filters.append(''.join(labels)+f'amix=inputs={len(labels)}:normalize=0:duration=first,alimiter=limit=0.89:level=0,loudnorm=I=-16:TP=-2.5:LRA=9[mix]')
 cmd+=['-filter_complex',';'.join(filters),'-map','0:v:0','-map','[mix]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t',str(plan['duration']),'-movflags','+faststart',str(output)]
 subprocess.run(cmd,check=True);return events
