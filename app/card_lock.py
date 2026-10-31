from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
CARD=ROOT/'channel_card'
def files():
 return sorted(p for p in CARD.rglob('*') if p.is_file() and p.name!='lock.json' and '__pycache__' not in p.parts)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check():
 lock=CARD/'lock.json'
 if not lock.is_file():raise ValueError('Locked card manifest is missing. User approval is required before changing the card.')
 expected=json.loads(lock.read_text())['files'];actual={str(p.relative_to(CARD)):digest(p) for p in files()}
 if actual!=expected:
  changed=sorted(k for k in set(expected)|set(actual) if expected.get(k)!=actual.get(k))
  raise ValueError('Locked channel card changed: '+', '.join(changed)+'. Do not update the lock without explicit user approval.')
 return {'status':'locked','file_count':len(actual)}
