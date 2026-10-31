import argparse,json,sys
from pathlib import Path
from . import learning,pipeline,card_lock

def main():
 parser=argparse.ArgumentParser(description='Tech Lobon AI video production V1');sub=parser.add_subparsers(dest='cmd',required=True)
 p=sub.add_parser('run');p.add_argument('--input',default='input');p.add_argument('--project')
 p=sub.add_parser('revise');p.add_argument('job_id')
 sub.add_parser('card-check')
 f=sub.add_parser('feedback');fs=f.add_subparsers(dest='action',required=True)
 p=fs.add_parser('add');p.add_argument('--observation',required=True);p.add_argument('--instruction',required=True);p.add_argument('--scope',choices=['project','channel','global'],default='channel');p.add_argument('--channel',default='Tech Lobon');p.add_argument('--project');p.add_argument('--job')
 fs.add_parser('list');p=fs.add_parser('disable');p.add_argument('rule_id');p.add_argument('--reason',required=True)
 args=parser.parse_args()
 try:
  if args.cmd=='run':result=pipeline.production(args.input,args.project)
  elif args.cmd=='revise':result=pipeline.revise(args.job_id)
  elif args.cmd=='card-check':result=card_lock.check()
  elif args.action=='list':result=learning.read()
  elif args.action=='disable':result=learning.disable(args.rule_id,args.reason)
  else:result=learning.add(args.instruction,args.observation,args.scope,args.channel,args.project,args.job)
  print(json.dumps(result,ensure_ascii=False,indent=2));return 0
 except Exception as e:print('BLOCKED:',e,file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
