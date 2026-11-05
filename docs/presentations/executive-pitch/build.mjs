// Update the current 12-minute deck in place with @oai/artifact-tool.
// The archived 14-minute deck is intentionally not a build target.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../../..');
const [modules,python,skillDir,sourceArg]=process.argv.slice(2);
if(!modules||!python||!skillDir) throw new Error('Usage: node build.mjs <runtime node_modules> <python> <presentations skill directory> [source.pptx]');
process.env.RUNTIME_NODE_MODULES=modules;
const require=createRequire(path.join(modules,'focal-loader.cjs'));
const {FileBlob,PresentationFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const {finalizePresentation}=await import(pathToFileURL(path.join(skillDir,'container_tools/artifact_tool_utils.mjs')).href);
const canonical=path.join(here,'Focal Family Executive Pitch - Final 12min.pptx');
const source=sourceArg?path.resolve(sourceArg):canonical;
const work=path.join(root,'build/final-presentation-updates');
await fs.mkdir(path.join(work,'final'),{recursive:true});
await fs.mkdir(path.join(work,'renders'),{recursive:true});
const sourceBytes=await fs.readFile(source);
const sourceHash=crypto.createHash('sha256').update(sourceBytes).digest('hex');
const stamp=Date.now();
const reference=path.join(work,`reference-${stamp}.pptx`);
await fs.writeFile(reference,sourceBytes); // Preserve manual edits before every update.
const p=await PresentationFile.importPptx(await FileBlob.load(reference));
const notes=JSON.parse(await fs.readFile(path.join(here,'notes.json'),'utf8'));
const model=JSON.parse(await fs.readFile(path.join(here,'model.json'),'utf8'));
assert.equal(p.slides.items.length,19);assert.equal(notes.length,19);
assert.equal(notes.slice(0,14).reduce((a,n)=>a+n.seconds,0),690);assert.equal(notes[4].seconds,180);
const snapshot=await p.inspect({select:'$.slides[*]',include:['id','index','layout','elements.id','elements.kind','elements.text','elements.position','notes.text']});
await fs.writeFile(path.join(work,'before.ndjson'),snapshot.ndjson);
await fs.writeFile(path.join(work,'masters.json'),JSON.stringify({masters:p.masters.items.map(m=>({id:m.id,name:m.name})),placeholders:p.slides.items.map(s=>s.placeholders.summary())},null,2));
const S=n=>p.slides.items[n-1];
const C={navy:'#16234B',teal:'#286B70',muted:'#53627A',light:'#79B5B4',white:'#FFFFFF'};
const font='Helvetica Neue';
function style(q,size=32,color=C.navy,bold=false){q.text.style={typeface:font,fontSize:size,color,bold,insets:0,verticalAlignment:'top',wrap:'square',autoFit:'none'};}
function edit(n,oldText,text,size,color,bold,pos){
 const hits=S(n).shapes.items.filter(q=>String(q.text)===oldText||String(q.text)===text);
 assert.equal(hits.length,1,`Slide ${n}: expected one anchor for ${oldText}`);
 const q=hits[0];q.text=text;if(size)style(q,size,color,bold);if(pos)q.position={...q.position,...pos};return q;
}
function add(n,name,text,position,size=32,color=C.navy,bold=false){
 let q=S(n).shapes.items.find(q=>q.name===name);
 if(!q)q=S(n).shapes.add({geometry:'textbox',name,position,fill:'none',line:{fill:'none',width:0}});
 q.position=position;q.text=text;style(q,size,color,bold);return q;
}
function title(n,old){edit(n,old,notes[n-1].title,56,C.navy,true);}
function cell(n,r,c,text){const t=S(n).tables.items[0];assert.ok(t,`Missing table on ${n}`);t.getCell(r,c).value=text;t.getCell(r,c).text.style={typeface:font,fontSize:n===6?31:29,color:r===0?C.white:C.navy,bold:r===0};}

// Problem and decision: retain the published study; make the Family choice explicit.
title(2,'The gap after a school vision letter');
edit(2,'A parent still has to act','Why we chose Family',30,C.teal,true);
edit(2,'Pat receives a letter.\nFinding care and preparing\nthe next conversation\nstill take work.','A school letter creates\na clear moment to act.',48,C.navy,true,{height:170});
add(2,'family-choice-rationale','Interviews: long waits, extra visits\nand uncertainty between exams.\nWe chose to test parent preparation.',{left:80,top:535,width:670,height:155},32,C.muted);
edit(2,'Musch et al., 2020; study conducted in 2017.','Five real interviews, one with a parent. The school-letter use case is our proposal. Trial: Musch et al., 2020; conducted in 2017.',22,C.muted);

edit(3,'The proposed buyer','The budget owner and champion',30,C.teal,true);
edit(3,'District student services\nSchool nurse champion','District student-services buyer\nSchool nurse user and champion',40,C.navy,true);
edit(3,'Proposed license: parent preparation, permitted follow-up status and staff reporting.','Proposed license: parent preparation, permitted status and staff reporting.',34,C.muted);
add(3,'buyer-evidence-limit','School reporting remains to build. District budgets, demand and willingness to pay are unvalidated.',{left:80,top:786,width:1360,height:62},22,C.muted);

title(4,'A prepared next step after a school letter');
edit(4,'At home, parent assisted','The parent chooses the next step',34,C.teal,true);
edit(4,'Match screen size to a card.\nMeasure the viewing distance.\nThe child points; the parent taps.','Record observations, choose an action\nand edit a note for the school nurse\nor eye doctor.',32,C.navy);
edit(4,'A note ready for the next conversation','Optional task and history',34,C.teal,true,{top:500,height:55});
edit(4,'Capture observations, choose a next step and download an editable note.','Supporting activities, not a decision\nabout whether a child needs care.',32,C.navy,false,{top:575,height:120});
add(4,'parent-action-boundary','Screenshot: fictional example. Nothing is booked or sent. An existing professional referral still stands.',{left:80,top:786,width:1360,height:62},22,C.muted);

edit(5,'0:00  Set up and practice\n0:35  Complete a check\n1:30  Save and compare\n2:15  Prepare the next step','0:00  Choose a next step\n0:40  Prepare the parent note\n1:30  Optional task and history\n2:30  Return to the action',31,C.white);
edit(5,'Live check: software demonstration. Example history and parent note: clearly labelled fictional data.','Parent action first. Task inputs are a software demonstration; example history and parent note are fictional.',22,'#C0D0E3');

cell(6,1,0,'Parent observations and editable note');cell(6,1,1,'Permitted school status and staff reporting');
cell(6,2,0,'Optional 12-response direction task');cell(6,2,1,'Independent use and understanding');
cell(6,3,0,'Saved checks and 7 / 30 / 90-day history');cell(6,3,1,'10-site pilot: family action and net staff effort');

title(7,'Our focus is the parent action after referral');
cell(7,0,2,'Why a school might add Focal');
cell(7,1,1,'Familiar, personal contact');cell(7,1,2,'Test fewer repeat explanations with a reusable parent note and checklist.');
cell(7,2,1,'Professional screening and EHR integration');cell(7,2,2,'Complement screening with parent preparation at home.');
cell(7,3,1,'Referral tracking, reminders and reporting');cell(7,3,2,'Test a focused parent workflow; a fit advantage is unproven.');
edit(7,'Differentiation to test: parent completion and less staff effort. Peek already has referral tracking and reminders. Sources in notes.','To justify adding Focal: higher parent completion, lower net staff effort. No unique technology claimed. Sources in notes.',22,C.muted);

edit(8,'Illustrative reachable subset','Illustrative eligible subset',32,C.navy,true);
edit(8,'10% of sites assumed to fit the workflow and buying conditions','Pilot fit: referral workflow, nurse champion and district budget owner.\n10% is a planning allowance.',30,C.muted);
edit(8,'NCES 2021–22 site-count benchmark. Price, 10% filter and adoption are assumptions. Private schools and practices excluded.','North Carolina first; eligible sites not yet counted. NCES 2021–22 benchmark. Price, 10% and adoption are assumptions.',22,C.muted);

title(9,'One school pilot can open a district');
edit(9,'Buyer conversations','District-buyer conversations',32,C.navy,true);
edit(9,'Founder outreach to North Carolina school nurses and district leaders','Founder outreach in North Carolina. Confirm a budget owner and procurement path.',30,C.muted);
edit(9,'Pilot sites','Districts piloting a school',32,C.navy,true);
edit(9,'Agree family and staff outcomes with the budget owner','Agree family outcomes and staff-time measures before enrollment.',30,C.muted);
edit(9,'Expand successful pilots through district contracts','5 district contracts × 10 paid schools on average = 50 sites',30,C.muted);
edit(9,'Proposed funnel, not a committed pipeline. Districts may buy multiple schools. Procurement timing and budget fit require validation.','Assumed: 25% enter a pilot; 50% of pilot districts buy. No committed pipeline. Timing, scope and conversion need validation.',22,C.muted);

edit(10,'School follow-up','Free for families',44,C.teal,true);
edit(10,'Parent preparation materials\nPermitted follow-up status\nStaff reporting','School license:\nParent preparation materials\nPermitted status and reporting',32,C.navy,true);
edit(10,'75% modeled gross margin\n$1,800 gross profit per site\n16-month target CAC payback','Buyer break-even: 60 net staff hours/year\nat an assumed $40/hour.\nValue must exceed the license fee.',30,C.muted,false,{top:555,height:155});
edit(10,'Free for families. School status/reporting require funding. Price and costs are assumptions; staff-time savings remain unmeasured.','75% modeled gross margin; $1,800 gross profit/site. School reporting remains to build. Price, costs and staff savings are unvalidated.',22,C.muted);

edit(12,'0–3: usability and study design\n4–9: pilot and first contracts\n10–18: paid rollout and renewals','0–3: usability and buyer discovery\n4–9: pilots and district contracts\n10–18: paid expansion and renewals',31,C.navy);
edit(14,'18 months to prove the business','18 months to prove buyer value',54,C.white,true);
edit(14,'Families take the next step','Parents complete follow-up actions',42,C.light,true);
edit(14,'Schools see value and renew','Schools save time and renew',42,C.light,true);
cell(16,4,1,'Net staff-time value above $2,400/year; test an actual paid renewal.');
edit(19,'Demo recovery: task screenshot on slide 5; fictional parent note on slide 4.','Demo recovery: lead with the fictional parent note on slide 4; use slide 5 for optional task context.',30,C.teal,true);
edit(19,'Research and procurement evidence checked November 4, 2026. Full sources in notes. Pricing, forecasts and funding terms are proposals.','Reviewed November 5, 2026. Full sources in notes. Pricing, market filters, district conversions, forecasts and terms remain proposals.',22,C.muted);

// Recalculate from inputs; avoid separate, drifting financial numbers.
const unitCogs=Object.values(model.annualCogsPerSite).reduce((a,b)=>a+b,0);
const periods=model.halfYears.map(h=>{const averageSites=(h.startSites+h.endSites)/2;const revenue=averageSites*model.annualPricePerSite*h.months/12;const cogs=averageSites*unitCogs*h.months/12;const opex=h.product+h.sales+h.privacy+h.admin;return {...h,averageSites,revenue,cogs,opex,result:revenue-cogs-opex};});
const years=[0,2,4].map(i=>{const hs=periods.slice(i,i+2),sum=k=>hs.reduce((a,h)=>a+h[k],0);return {year:i/2+1,averageSites:sum('averageSites')/2,endSites:hs[1].endSites,revenue:sum('revenue'),cogs:sum('cogs'),opex:sum('opex'),result:sum('result'),arr:hs[1].endSites*model.annualPricePerSite};});
const sum18=k=>periods.slice(0,3).reduce((a,h)=>a+h[k],0),spend18=sum18('cogs')+sum18('opex');
const funding=[['Product and research',sum18('product')],['Pilots and sales',sum18('sales')],['Privacy, security and review',sum18('privacy')],['Administration and insurance',sum18('admin')],['Service delivery (COGS)',sum18('cogs')],['Reserve',model.raise-spend18]];
assert.equal(model.annualPricePerSite,2400);assert.equal(unitCogs,600);assert.equal(model.raise,600000);assert.equal(model.equityPercent,15);
assert.deepEqual(years.map(y=>y.revenue),[42000,324000,960000]);assert.equal(spend18,546000);assert.equal(sum18('revenue'),144000);
assert.equal(model.goToMarket.paidDistrictContracts*model.goToMarket.averagePaidSitesPerDistrict,years[0].endSites);
assert.equal(model.buyerValue.annualBreakEvenNetStaffHours*model.buyerValue.assumedStaffCostPerHour,model.annualPricePerSite);
const calculated={periods,years,unitCogs,grossMargin:1-unitCogs/model.annualPricePerSite,funding,eighteenMonths:{grossSpend:spend18,revenue:sum18('revenue'),netBurn:spend18-sum18('revenue'),endingCash:model.raise-spend18+sum18('revenue')},market:{nationalAnnual:model.market.usPublicElementarySchools*model.annualPricePerSite,serviceableAnnual:model.market.usPublicElementarySchools*model.market.serviceableShareAssumption*model.annualPricePerSite},valuation:{postMoney:model.raise/(model.equityPercent/100),preMoney:model.raise/(model.equityPercent/100)-model.raise}};
await fs.writeFile(path.join(here,'calculated-model.json'),JSON.stringify(calculated,null,2)+'\n');
const clock=s=>`${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`;let elapsed=0;
for(let i=0;i<notes.length;i++){const n=notes[i],timing=i<14?`${clock(elapsed)}–${clock(elapsed+n.seconds)} (${n.seconds} seconds)`:'Backup, outside the 12-minute presentation limit';S(i+1).speakerNotes.text=`${n.title}\nPresenter: ${n.speaker}\nTiming: ${timing}\n\n${n.script}\n\nSources and assumptions\n${n.sources.join('\n')}`;S(i+1).hidden=i>=14;elapsed+=n.seconds;}
const candidate=path.join(work,`candidate-${stamp}.pptx`),final=path.join(work,'final',`Focal Family Executive Pitch - review-${stamp}.pptx`);
await (await PresentationFile.exportPptx(p)).save(candidate);
// The slide 11 chart references a 'Chart Data' sheet that was never embedded (true of the
// committed deck too), so its cached values are the only data. Convert those references to
// literal series after checking them against the model; the finalizer then embeds a new,
// explicitly labelled workbook snapshot. No original formulas or workbook lineage are claimed.
{
 const JSZip=require('jszip');const zip=await JSZip.loadAsync(await fs.readFile(candidate));
 const parts=Object.keys(zip.files).filter(n=>/charts\/chart\d+\.xml$/.test(n));assert.equal(parts.length,1,'Expected one chart');
 let x=await zip.file(parts[0]).async('string');assert.ok(!/externalData/.test(x),'Chart unexpectedly has a workbook');
 x=x.replace(/<c:numRef>\s*<c:f>[^<]*<\/c:f>\s*<c:numCache>([\s\S]*?)<\/c:numCache>\s*<\/c:numRef>/g,'<c:numLit>$1</c:numLit>')
  .replace(/<c:strRef>\s*<c:f>[^<]*<\/c:f>\s*<c:strCache>([\s\S]*?)<\/c:strCache>\s*<\/c:strRef>/g,'<c:strLit>$1</c:strLit>');
 assert.ok(!/<c:(numRef|strRef|f)>/.test(x),'Chart still has worksheet references');
 const lit=tag=>[...x.matchAll(new RegExp(`<c:${tag}>[\\s\\S]*?</c:${tag}>`,'g'))].map(m=>[...m[0].matchAll(/<c:v>([^<]*)<\/c:v>/g)].map(v=>v[1]));
 assert.deepEqual(lit('numLit').map(s=>s.map(Number)),[years.map(y=>y.revenue/1000),years.map(y=>(y.cogs+y.opex)/1000)]);
 assert.deepEqual(lit('strLit'),[['Year 1','Year 2','Year 3'],['Year 1','Year 2','Year 3']]);
 zip.file(parts[0],x);await fs.writeFile(candidate,await zip.generateAsync({type:'nodebuffer',compression:'DEFLATE'}));
}
const tableOwners=[6,7,10,11,12,13,15,16,17,18];
const chartDirs=new Set((await fs.readdir(root)).filter(n=>n.startsWith('.chart-data-')));
await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:final,pythonExecutable:python,integrityValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_layout_geometry.py'),explicitTotalSlideCount:19,requiredNativeTableOwnerSlides:tableOwners,requiredNativeChartOwnerSlides:[11],materializeLiteralChartWorkbooks:true,tableArithmeticContracts:[{slide:10,table:1,label_column:0,total_row:5,value_columns:[1],component_rows:[2,3,4]},{slide:12,table:1,label_column:0,total_row:7,value_columns:[1],component_rows:[1,2,3,4,5,6]}],layoutArgs:['--expected-slide-size-emu','15240000,8572500','--validate-bullet-geometry','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],fontPolicy:{basis:'reference',families:[font],referencePath:reference,referenceSha256:sourceHash},verifyArtifactToolImport:true,receiptPath:path.join(work,`validation-${stamp}.json`)});
for(const name of await fs.readdir(root))if(name.startsWith('.chart-data-')&&!chartDirs.has(name))await fs.rm(path.join(root,name),{recursive:true});
await fs.writeFile(path.join(work,'latest.json'),JSON.stringify({source:reference,candidate,final,canonical,talkSeconds:elapsed,demoSeconds:180},null,2)+'\n');
console.log(JSON.stringify({final,canonical,slides:19,main:14,backups:5,talkSeconds:elapsed,demoSeconds:180}));
// Publish only after rendering and native PowerPoint review; see README.md.
