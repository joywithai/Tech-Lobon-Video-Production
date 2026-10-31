from pathlib import Path
import difflib,json,re,shutil,subprocess,unicodedata,wave,math

def probe(path):
 if not shutil.which('ffprobe'):raise ValueError('ffprobe is not installed; install FFmpeg before a production run')
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
def audio_duration(path):
 data=probe(path)
 if not any(s.get('codec_type')=='audio' for s in data['streams']):raise ValueError('Input has no audio stream')
 duration=float(data['format']['duration'])
 if not math.isfinite(duration) or duration<=0:raise ValueError('Invalid audio duration')
 return duration

def ensure_audio(input_dir,spoken,voice,out):
 found=[p for p in Path(input_dir).iterdir() if p.is_file() and p.suffix.lower() in {'.mp3','.wav','.m4a','.aac','.flac','.ogg'}]
 if len(found)>1:raise ValueError('Multiple narration files found in input/: keep one or select one explicitly')
 if found:shutil.copy2(found[0],out.with_suffix(found[0].suffix.lower()));return out.with_suffix(found[0].suffix.lower()),'supplied'
 if not voice:raise ValueError('No audio and no approved TTS voice: set providers.voice or provide input audio')
 if not shutil.which('edge-tts'):raise ValueError('edge-tts is missing; install requirements.txt before running')
 text=out.parent/'tts-input.txt';text.write_text(spoken,encoding='utf-8')
 target=out.with_suffix('.mp3');subprocess.run(['edge-tts','--voice',voice,'--file',str(text),'--write-media',str(target)],check=True)
 return target,'edge-tts'

def normalized(w):
 s=unicodedata.normalize('NFC',w).lower().replace('\u200c','').replace('\u200d','')
 return ''.join(c for c in s if not c.isspace() and not unicodedata.category(c).startswith(('P','Z')))

def validate_words(words,duration,spoken):
 if not isinstance(words,list) or not words:raise ValueError('Word timing list missing')
 last=0
 for w in words:
  if not isinstance(w,dict) or not isinstance(w.get('word'),str) or not w['word'].strip():raise ValueError('Each timing entry needs a word')
  try:a=float(w['start']);b=float(w['end'])
  except (KeyError,ValueError,TypeError):raise ValueError('Word timing needs finite start/end')
  if not math.isfinite(a) or not math.isfinite(b) or a<last-.001 or b<=a or b>duration+.05:raise ValueError('Word times must be ordered, positive and inside audio')
  w['start']=round(a,4);w['end']=round(b,4);last=a
 actual=''.join(normalized(w['word']) for w in words);expected=''.join(normalized(w) for w in spoken.split())
 if actual!=expected:raise ValueError('Timing words do not match spoken script in order. Supply reviewed timing JSON; no estimated words will be invented.')
 return words

def timing(audio,spoken,input_dir,out,config):
 duration=audio_duration(audio);supplied=Path(input_dir)/'word-timing.json'
 if supplied.is_file():
  data=json.loads(supplied.read_text());words=validate_words(data.get('words'),duration,spoken)
  result={'method':'user-supplied word timing','human_listening_verified':False,'duration':duration,'words':words}
 else:
  try:from faster_whisper import WhisperModel
  except ImportError:raise ValueError('faster-whisper not installed; install requirements or supply input/word-timing.json')
  model=WhisperModel(config['asr_model'],device=config['asr_device'],compute_type=config['asr_compute_type'])
  segs,info=model.transcribe(str(audio),language='bn',word_timestamps=True,vad_filter=True)
  asr=[{'word':w.word.strip(),'start':float(w.start),'end':float(w.end),'probability':float(w.probability)} for s in segs for w in (s.words or []) if w.word.strip()]
  target=spoken.split();aa=[normalized(w['word']) for w in asr];bb=[normalized(x) for x in target]
  matcher=difflib.SequenceMatcher(None,aa,bb,autojunk=False);coverage=matcher.ratio();matched=[None]*len(target)
  for tag,i,j,k,l in matcher.get_opcodes():
   if tag=='equal':
    for ai,bi in zip(range(i,j),range(k,l)):matched[bi]={'word':target[bi],'start':asr[ai]['start'],'end':asr[ai]['end'],'asr_word':asr[ai]['word'],'probability':asr[ai]['probability']}
  if coverage<float(config['asr_min_coverage']) or any(w is None for w in matched):
   diagnostic={'method':'faster-whisper ASR diagnostic','language':info.language,'coverage':coverage,'recognized':asr,'note':'Unmatched words require human-reviewed word-timing.json; no timestamps were fabricated.'}
   out.write_text(json.dumps(diagnostic,ensure_ascii=False,indent=2));raise ValueError(f'ASR/script timing coverage {coverage:.1%} with unmatched words; inspect {out} and provide input/word-timing.json. No estimated timings were generated.')
  words=validate_words(matched,duration,spoken)
  result={'method':'faster-whisper exact-token alignment','human_listening_verified':False,'duration':duration,'coverage':coverage,'words':words}
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result

def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
def captions(words,display_words):
 if len(words)!=len(display_words):raise ValueError('Planner must provide exactly one display word per timed word')
 out=[];group=[]
 for i,w in enumerate(words):
  text=str(display_words[i]).strip()
  if not text or len(text)>100:raise ValueError('Invalid subtitle word')
  if group and (len(group)>=4 or len(' '.join(x['text'] for x in group+[{'text':text}]))>36 or w['start']-group[-1]['end']>.5):
   out.append(group);group=[]
  group.append({'text':text,'start':w['start'],'end':w['end']})
  if re.search(r'[।?!,]$',text) and len(group)>=2:out.append(group);group=[]
 if group:out.append(group)
 cues=[]
 for g in out:cues.append({'text':' '.join(x['text'] for x in g),'start':g[0]['start'],'end':g[-1]['end']})
 for a,b in zip(cues,cues[1:]):
  if a['end']>b['start']:a['end']=b['start']
 if any(c['end']<=c['start'] for c in cues):raise ValueError('Overlapping audio timings cannot make valid subtitle cues; review timing JSON')
 return cues

def write_srt(cues,path):path.write_text('\n\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(cues,1))+'\n',encoding='utf-8')
