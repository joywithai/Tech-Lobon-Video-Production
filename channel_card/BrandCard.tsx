import React,{useEffect,useState} from 'react';
import {continueRender,delayRender,staticFile} from 'remotion';
import card from './card.json';

export type CardFormat='vertical'|'horizontal';
/** Only these content inputs are accepted. No page number, counter or extra chrome slot. */
export function BrandCard({format,visual,subtitle}:{format:CardFormat;visual:React.ReactNode;subtitle:string}){
 const [handle]=useState(()=>delayRender('Loading locked channel fonts'));
 const [ready,setReady]=useState(false);
 useEffect(()=>{Promise.all([
  new FontFace('TL Bangla',`url(${staticFile('card/fonts/NotoSansBengali-Bold.ttf')})`,{weight:'700'}),
  new FontFace('TL Latin',`url(${staticFile('card/fonts/DejaVuSans-Bold.ttf')})`,{weight:'700'})
 ].map(async f=>{await f.load();(document.fonts as FontFaceSet & {add:(x:FontFace)=>void}).add(f)})).then(()=>{setReady(true);continueRender(handle)}).catch(e=>{console.error(e);throw e})},[handle]);
 if(!ready)return null;
 const layout=card[format], [hx,hy,hw,hh]=layout.header,[sx,sy,sw,sh]=layout.stage,[cx,cy,cw,ch]=layout.subtitle;
 const isVertical=format==='vertical';
 return <div data-card="locked-channel-card" style={{position:'relative',width:layout.width,height:layout.height,overflow:'hidden',background:card.palette.background,color:card.palette.ink}}>
  <img src={staticFile('card/assets/bg.jpg')} style={{position:'absolute',inset:0,width:'100%',height:'100%',objectFit:'cover'}}/>
  <div data-card-region="brand" style={{position:'absolute',left:hx,top:hy,width:hw,height:hh,display:'flex',alignItems:'center',gap:isVertical?22:18}}>
   <div style={{width:isVertical?100:76,height:isVertical?100:76,borderRadius:'50%',border:'1px solid rgba(255,255,255,.2)',background:'rgba(0,0,0,.16)',display:'flex',alignItems:'center',justifyContent:'center'}}><img src={staticFile('card/assets/logo.png')} style={{width:'78%',height:'72%',objectFit:'contain'}}/></div>
   <div style={{fontFamily:'TL Latin',fontSize:isVertical?43:36,fontWeight:700,background:'rgba(0,0,0,.23)',borderRadius:18,padding:'12px 22px'}}>{card.channel_name}</div>
  </div>
  <div data-card-region="main-visual" style={{position:'absolute',left:sx,top:sy,width:sw,height:sh,borderRadius:isVertical?66:48,overflow:'hidden',border:'1.5px solid rgba(248,244,237,.25)',background:'#132220',boxShadow:'0 20px 65px rgba(0,0,0,.3)'}}>{visual}</div>
  <div data-card-region="subtitle" style={{position:'absolute',left:cx,top:cy,width:cw,height:ch,background:'rgba(10,16,16,.8)',border:'1px solid rgba(255,255,255,.17)',borderRadius:25,display:'flex',justifyContent:'center',alignItems:'center',padding:'0 22px',boxSizing:'border-box'}}>
   <span style={{fontFamily:'TL Latin, TL Bangla',fontWeight:700,fontSize:isVertical?46:42,color:card.palette.ink,textAlign:'center',lineHeight:1.22,textShadow:'0 2px 6px #000'}}>{subtitle}</span>
  </div>
 </div>;
}
