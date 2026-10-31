#!/usr/bin/env python3
"""Re-lock channel card only after an explicit user request to change it."""
from pathlib import Path
import argparse,hashlib,json
p=argparse.ArgumentParser();p.add_argument('--user-explicitly-approved-card-change',action='store_true');a=p.parse_args()
if not a.user_explicitly_approved_card_change:raise SystemExit('Refusing: explicit user approval flag is required')
root=Path(__file__).resolve().parents[1]/'channel_card'
files=sorted(x for x in root.rglob('*') if x.is_file() and x.name!='lock.json' and '__pycache__' not in x.parts)
manifest={'version':1,'notice':'Locked channel card. Changes require explicit user approval.','files':{str(x.relative_to(root)):hashlib.sha256(x.read_bytes()).hexdigest() for x in files}}
(root/'lock.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Card lock created for',len(files),'files. This does not assert creative approval for any adaptation.')
