from pathlib import Path
import re
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[2];FONT=ROOT/'channel_card/fonts/NotoSansBengali-Bold.ttf'
# Bilingual headlines: NotoSansBengali covers Bangla only, DejaVu covers Latin.
FONT_LATIN=ROOT/'channel_card/fonts/DejaVuSans-Bold.ttf'
def _runs(text):
 out=[];cur='';cur_bn=False
 for ch in text:
  bn='ঀ'<=ch<='৿'
  if cur and bn!=cur_bn:out.append((cur,cur_bn));cur=''
  cur+=ch;cur_bn=bn
 if cur:out.append((cur,cur_bn))
 return out
def _measure(text,f_bn,f_lt):
 return sum((f_bn if bn else f_lt).getlength(t) for t,bn in _runs(text))
def _draw_mixed(d,xy,text,f_bn,f_lt,fill,stroke_width=0,stroke_fill=None):
 x,y=xy
 for t,bn in _runs(text):
  f=f_bn if bn else f_lt
  d.text((x,y),t,font=f,fill=fill,stroke_width=stroke_width,stroke_fill=stroke_fill)
  x+=f.getlength(t)
def render(spec,assets,out,index):
 W,H=1280,720;style=spec.get('style','contrast');bg=['#182623','#23342d','#172b2c'][index%3];img=Image.new('RGB',(W,H),bg);d=ImageDraw.Draw(img)
 if style=='split' or index==1:d.polygon([(690,0),(1280,0),(1280,720),(500,720)],fill='#b96f2d')
 elif style=='focus' or index==2:d.ellipse((610,80,1220,690),fill='#c17631')
 else:d.rounded_rectangle((650,60,1220,660),radius=50,fill='#945526',outline='#ffd19d',width=4)
 item=next((x for x in assets if x['id']==spec.get('asset_id')),None)
 if item:
  im=Image.open(item['path']).convert('RGBA');im.thumbnail((560,540));img.paste(im,(940-im.width//2,360-im.height//2),im)
 text=spec['headline'];font=None;font_lt=None;lines=[]
 for size in range(104,45,-4):
  f=ImageFont.truetype(str(FONT),size);fl=ImageFont.truetype(str(FONT_LATIN),size);words=text.split();ls=[];line=''
  for word in words:
   trial=(line+' '+word).strip()
   if line and _measure(trial,f,fl)>570:ls.append(line);line=word
   else:line=trial
  if line:ls.append(line)
  if len(ls)<=4 and all(_measure(x,f,fl)<=570 for x in ls):font=f;font_lt=fl;lines=ls;break
 if font is None:raise ValueError('Thumbnail headline is too long; planner must shorten it without losing meaning')
 y=max(100,(H-len(lines)*(font.size+18))//2)
 for line in lines:_draw_mixed(d,(65,y),line,font,font_lt,'#fff1dc',stroke_width=2,stroke_fill='#16211c');y+=font.size+18
 img.save(out,'PNG')
