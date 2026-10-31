from pathlib import Path
import re,yaml
JWT=re.compile(r'(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}(?![A-Za-z0-9_-])')
BLOB=re.compile(r'(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{45,}(?![A-Za-z0-9_-])')
def load(path):
 p=Path(path);raw=p.read_text(encoding='utf-8-sig');meta={};body=raw
 if raw.startswith('---\n'):
  parts=raw.split('---',2)
  if len(parts)!=3:raise ValueError('Invalid YAML front matter in brief.md')
  meta=yaml.safe_load(parts[1]) or {};body=parts[2].strip()
 if not isinstance(meta,dict):raise ValueError('Brief front matter must be a mapping')
 sections={};current=None;buf=[]
 for line in body.splitlines():
  m=re.match(r'^##\s+(.+?)\s*$',line)
  if m:
   if current:sections[current]='\n'.join(buf).strip()
   current=m.group(1).strip().lower();buf=[]
  elif current:buf.append(line)
 if current:sections[current]='\n'.join(buf).strip()
 text=meta.get('script') or sections.get('full script') or sections.get('script') or (body if not sections else None)
 if not isinstance(text,str) or not text.strip():raise ValueError('brief.md requires a ## Full Script section (or YAML script)')
 # Screen-only blocks are explicit. Never invent explanations or synthesize literals.
 visual=[]
 def remove(m):visual.append(m.group(1).strip());return ' '
 spoken=re.sub(r'\[SCREEN_ONLY\](.*?)\[/SCREEN_ONLY\]',remove,text,flags=re.S|re.I)
 spoken=re.sub(r'```[^\n]*\n(.*?)```',remove,spoken,flags=re.S)
 if '[SCREEN_ONLY]' in spoken.upper() or '[/SCREEN_ONLY]' in spoken.upper():raise ValueError('Unbalanced SCREEN_ONLY markers')
 if JWT.search(spoken) or BLOB.search(spoken) or re.search(r'\b(?:const|let|var)\s+\w+\s*=|\bjwt\.(?:sign|verify)\s*\(',spoken):
  raise ValueError('Raw token/code in spoken script. Put it in [SCREEN_ONLY]...[/SCREEN_ONLY] and provide natural narration; do not synthesize it literally.')
 spoken=re.sub(r'\n{3,}','\n\n',spoken).strip()
 if not spoken:raise ValueError('No spoken narration after separating screen-only material')
 return {'meta':meta,'spoken':spoken,'visual_only':visual,'sections':sections,'original':raw}
