import React from 'react';
import {Composition,registerRoot,useCurrentFrame,useVideoConfig,staticFile,OffthreadVideo,Sequence} from 'remotion';
import {BrandCard,type CardFormat} from '../../../channel_card/BrandCard';

type Word={word:string;start:number;end:number};
type NodeData={id:string;label:string;type:string;x:number;y:number;asset_id?:string|null};
type Scene={start:number;end:number;title:string;nodes:NodeData[];connections:{from:string;to:string}[];word_actions:{index:number;target:string;action:string}[]};
type Plan={format:CardFormat;duration:number;fps:number;words:Word[];captions:{start:number;end:number;text:string}[];scenes:Scene[];assets:{id:string;public_path:string}[]};
const empty:Plan={format:'vertical',duration:1,fps:30,words:[],captions:[],scenes:[],assets:[]};
const smooth=(x:number)=>{x=Math.min(1,Math.max(0,x));return x*x*(3-2*x)};
function Stage({plan,time}:{plan:Plan;time:number}){
 const {fps}=useVideoConfig();
 const scene=plan.scenes.find(s=>time>=s.start&&time<s.end)||plan.scenes[plan.scenes.length-1];
 if(!scene)return <div style={{width:'100%',height:'100%',background:'#132220'}}/>;
 const actions=scene.word_actions||[];let latest=actions[0];
 for(const a of actions)if(plan.words[a.index]?.start<=time)latest=a;
 const word=latest?plan.words[latest.index]:undefined,age=word?Math.max(0,time-word.start):0,pulse=Math.exp(-age*3.8);
 const nodes=scene.nodes||[],edges=scene.connections||[];
 const asset=(id?:string|null)=>plan.assets.find(x=>x.id===id)?.public_path;
 const active=nodes.find(n=>n.id===latest?.target);
 const drift=1+.008*Math.sin(time*.7),dx=4*Math.sin(time*.8),dy=4*Math.cos(time*.65);
 return <svg viewBox="0 0 1000 1000" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" role="img" aria-label={scene.title}>
  <defs><linearGradient id="scene-bg" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#142921"/><stop offset="1" stopColor="#0b1b1a"/></linearGradient><filter id="node-shadow"><feGaussianBlur in="SourceAlpha" stdDeviation="10"/><feOffset dy="8"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <rect width="1000" height="1000" fill="url(#scene-bg)"/>
  <g opacity={smooth((time-scene.start+.04)/.3)*smooth((scene.end-time+.04)/.3)} transform={`translate(${500*(1-drift)+dx} ${500*(1-drift)+dy}) scale(${drift})`}>
   {edges.map((e,i)=>{const a=nodes.find(n=>n.id===e.from),b=nodes.find(n=>n.id===e.to);if(!a||!b)return null;const progress=(time*.38+i*.27)%1;return <g key={i}><path d={`M${a.x} ${a.y} L${b.x} ${b.y}`} stroke="#789C8B" strokeWidth="5"/><circle cx={a.x+(b.x-a.x)*progress} cy={a.y+(b.y-a.y)*progress} r="9" fill="#FFC47D"/></g>})}
   {nodes.map((n,i)=>{
    const first=actions.find(a=>a.target===n.id);const start=first?plan.words[first.index]?.start:scene.start;
    const entered=smooth((time-(start??scene.start)+.25)/.5),focus=n.id===latest?.target?pulse:0;
    const action=n.id===latest?.target?latest?.action:'';
    const move=(action==='move'||action==='flow'||action==='connect')?14*focus:4*Math.sin(time*1.2+i);
    const scale=1+.045*focus; const w=['image','video','code'].includes(n.type)?310:230,h=['image','video','code'].includes(n.type)?210:135;
    const image=asset(n.asset_id);
    return <g key={n.id} opacity={.3+.7*entered} transform={`translate(${n.x+move} ${n.y-4*focus}) scale(${scale})`} filter="url(#node-shadow)">
     {['code','image','video','screen'].includes(n.type)?<rect x={-w/2} y={-h/2} width={w} height={h} rx="20" fill="#203A33" stroke="#9EC1A8" strokeWidth={3+focus*2}/>:null}
     {n.type==='server'?<g><rect x="-84" y="-62" width="168" height="124" rx="13" fill="#203C35" stroke="#9EC1A8" strokeWidth="4"/>{[-39,0,39].map((y,i)=><g key={i}><rect x="-68" y={y-13} width="136" height="26" rx="6" fill="#10241F" stroke="#6E9781" strokeWidth="2"/><circle cx="-48" cy={y} r="5" fill={focus>.2?'#FFB967':'#85DFA6'}/><path d={`M-30 ${y}H45`} stroke="#628775" strokeWidth="3"/></g>)}</g>:null}
     {n.type==='client'?<g><rect x="-96" y="-66" width="192" height="120" rx="14" fill="#1D3631" stroke="#9EC1A8" strokeWidth="4"/><rect x="-82" y="-51" width="164" height="89" fill="#10241F"/><path d="M-30 54V72H30V54" fill="#38584A" stroke="#9EC1A8" strokeWidth="4"/></g>:null}
     {n.type==='token'?<g><rect x="-92" y="-42" width="184" height="84" rx="30" fill="#B56D31" stroke="#FFD397" strokeWidth="4"/><circle cx="-58" r="12" fill="#284238"/><path d="M-28 0H65" stroke="#FFE0B2" strokeWidth="5" strokeDasharray="10 8"/></g>:null}
     {n.type==='person'?<g><circle cy="-34" r="34" fill="#E8BC98" stroke="#FFD8B9" strokeWidth="4"/><path d="M-70 62Q-62 7 0 7Q62 7 70 62Z" fill="#3B6554" stroke="#9EC1A8" strokeWidth="4"/></g>:null}
     {image&&n.type==='video'?<foreignObject x={-w/2+12} y={-h/2+12} width={w-24} height={h-56}><Sequence from={Math.round(scene.start*fps)} layout="none"><OffthreadVideo src={staticFile(image)} muted style={{width:'100%',height:'100%',objectFit:'contain'}}/></Sequence></foreignObject>:image?<image href={staticFile(image)} x={-w/2+12} y={-h/2+12} width={w-24} height={h-56} preserveAspectRatio="xMidYMid meet"/>:null}
     {n.type==='shield'?<path d="M0 -59 L53 -39 V8 Q53 47 0 72 Q-53 47 -53 8 V-39Z M-24 5 L-5 25 L29 -20" fill="#284238" stroke="#FFBE78" strokeWidth="6"/>:null}
     {n.type==='clock'?<g><circle r="54" fill="#203A33" stroke="#FFBE78" strokeWidth="5"/><path d="M0 -34V0L28 15" fill="none" stroke="#FFBE78" strokeWidth="5" transform={`rotate(${time*12})`}/></g>:null}
     {n.type==='code'?<foreignObject x={-w/2+14} y={-h/2+12} width={w-28} height={h-24}><div style={{fontFamily:'monospace',fontSize:13,color:'#FFF3E3',whiteSpace:'pre-wrap',overflowWrap:'anywhere',lineHeight:1.28}}>{n.label}</div></foreignObject>:<text textAnchor="middle" y={image?h/2-14:({shield:95,clock:83,person:90,server:96,client:100,token:75} as Record<string,number>)[n.type]||8} fill="#FFF3E3" fontFamily="TL Latin, TL Bangla" fontWeight="bold" fontSize={n.label.length>20?19:25}>{n.label}</text>}
    </g>
   })}
   {active?<g opacity=".6"><circle cx={active.x} cy={active.y} r={130+20*pulse} fill="none" stroke="#FFBC72" strokeWidth="3" strokeDasharray="24 18" transform={`rotate(${time*35} ${active.x} ${active.y})`}/></g>:null}
  </g>
 </svg>;
}
function Video({plan=empty}:{plan?:Plan}){
 const f=useCurrentFrame(),{fps}=useVideoConfig(),time=f/fps;
 const caption=plan.captions.find(c=>time>=c.start&&time<c.end)?.text||'';
 return <BrandCard format={plan.format} visual={<Stage plan={plan} time={time}/>} subtitle={caption}/>;
}
registerRoot(()=> <Composition id="Production" component={Video} defaultProps={{plan:empty}} width={1080} height={1920} fps={30} durationInFrames={30} calculateMetadata={({props})=>{const p=props.plan||empty;return {fps:p.fps,width:p.format==='horizontal'?1920:1080,height:p.format==='horizontal'?1080:1920,durationInFrames:Math.ceil(p.duration*p.fps)}}}/>);
