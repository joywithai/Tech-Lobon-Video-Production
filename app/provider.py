import json,os,re,requests

def chat(system,payload,config):
 base=os.getenv(config['llm_base_url_env'],'').strip().rstrip('/');model=os.getenv(config['llm_model_env'],'').strip();key=os.getenv(config['llm_api_key_env'],'').strip()
 if not base or not model:raise ValueError('Creative planner not configured: set VME_LLM_BASE_URL and VME_LLM_MODEL. A compatible local or hosted provider is required.')
 if not (base.startswith('https://') or base.startswith('http://localhost:') or base.startswith('http://127.0.0.1:')):raise ValueError('Planner endpoint must be HTTPS or explicit localhost')
 headers={'Content-Type':'application/json'}
 if key:headers['Authorization']='Bearer '+key
 body={'model':model,'temperature':0.25,'max_tokens':20000,'messages':[{'role':'system','content':system},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}]}
 r=requests.post(base+'/chat/completions',headers=headers,json=body,timeout=300)
 if r.status_code>=400:raise ValueError(f'Planner request failed with HTTP {r.status_code}; check model and provider configuration')
 result=r.json()['choices'][0]['message']['content'].strip();result=re.sub(r'^```(?:json)?\s*|\s*```$','',result,flags=re.I)
 try:return json.loads(result)
 except json.JSONDecodeError:raise ValueError('Planner returned invalid JSON; no partial creative plan will be rendered')
