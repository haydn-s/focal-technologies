// Isolated per-slide preview rendering. Does not change the delivered PPTX.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
const [modules,pptx,output,slideNumber]=process.argv.slice(2);
const require=createRequire(path.join(modules,'focal-render.cjs'));
const {FileBlob,PresentationFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const p=await PresentationFile.importPptx(await FileBlob.load(pptx));
const s=p.slides.items[Number(slideNumber)-1];
if(!s)throw new Error('Slide does not exist: '+slideNumber);
const stem='slide-'+String(slideNumber).padStart(2,'0');
await fs.mkdir(output,{recursive:true});
await fs.writeFile(path.join(output,stem+'.png'),new Uint8Array(await (await p.export({slide:s,format:'png',scale:1})).arrayBuffer()));
await fs.writeFile(path.join(output,stem+'.json'),await (await s.export({format:'layout'})).text());
