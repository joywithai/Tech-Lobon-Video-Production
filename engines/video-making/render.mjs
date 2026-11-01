import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia} from '@remotion/renderer';
import fs from 'node:fs';import path from 'node:path';
const root=process.cwd(),planPath=process.argv[2],output=process.argv[3],concurrency=Number(process.argv[4]||2),crf=Number(process.argv[5]||20);
if(!planPath||!output)throw Error('Usage: node engines/video-making/render.mjs plan.json visual.mp4 [concurrency] [crf]');
if(fs.existsSync(output))throw Error('Refusing to overwrite an existing render');
const plan=JSON.parse(fs.readFileSync(planPath,'utf8'));const publicDir=path.join(root,'engines/video-making/public');
// Offline/air-gapped adapter: allow a locally supplied Chromium (e.g. @sparticuz/chromium)
// via REMOTION_BROWSER_EXECUTABLE. Unset keeps the stock Chrome Headless Shell behavior.
const browserExecutable=process.env.REMOTION_BROWSER_EXECUTABLE||null;
const serveUrl=await bundle({entryPoint:path.join(root,'engines/video-making/src/index.tsx'),publicDir});
const browser=await openBrowser('chrome',{...(browserExecutable?{browserExecutable}:{}),chromeMode:browserExecutable?'chrome-for-testing':'headless-shell',chromiumOptions:{gl:'swangle'}});
try{const opts={serveUrl,puppeteerInstance:browser,inputProps:{plan},timeoutInMilliseconds:120000,logLevel:'warn'};const composition=await selectComposition({...opts,id:'Production'});
 await renderMedia({...opts,composition,codec:'h264',pixelFormat:'yuv420p',crf,x264Preset:'veryfast',concurrency,outputLocation:path.resolve(output),onProgress:({progress})=>process.stdout.write(`\rVisual render ${Math.round(progress*100)}%`)});console.log();
}finally{await browser.close({silent:true})}
