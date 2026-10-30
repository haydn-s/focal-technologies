// Build with @oai/artifact-tool. See README.md for runtime arguments.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const [runtimeModules, python, skillDir] = process.argv.slice(2);
if (!runtimeModules || !python || !skillDir) throw new Error('Usage: node build.mjs <runtime node_modules> <python> <presentations skill directory>');
process.env.RUNTIME_NODE_MODULES=runtimeModules;
const require = createRequire(path.join(runtimeModules, 'focal-loader.cjs'));
const { FileBlob, PresentationFile } = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const { finalizePresentation, applyPresentationChartFont } = await import(pathToFileURL(path.join(skillDir, 'container_tools/artifact_tool_utils.mjs')).href);
const model = JSON.parse(await fs.readFile(path.join(here, 'model.json'), 'utf8'));
const notes = JSON.parse(await fs.readFile(path.join(here, 'notes.json'), 'utf8'));
const temp = path.join(root, 'build/executive-pitch');
await fs.mkdir(path.join(temp, 'renders'), { recursive: true });
await fs.mkdir(path.join(temp, 'final'), { recursive: true });
try { await fs.symlink(runtimeModules, path.join(temp,'node_modules')); } catch(e) { if(e.code!=='EEXIST') throw e; }
process.chdir(temp);

const unitCogs = Object.values(model.annualCogsPerSite).reduce((a,b) => a+b, 0);
const periods = model.halfYears.map(h => {
  const averageSites = (h.startSites+h.endSites)/2;
  const revenue = averageSites*model.annualPricePerSite*h.months/12;
  const cogs = averageSites*unitCogs*h.months/12;
  const opex = h.product+h.sales+h.privacy+h.admin;
  return {...h, averageSites, revenue, cogs, opex, result:revenue-cogs-opex};
});
const years = [0,2,4].map((i) => {
  const hs=periods.slice(i,i+2); const sum=k=>hs.reduce((a,h)=>a+h[k],0);
  return {year:i/2+1, averageSites:sum('averageSites')/2, endSites:hs[1].endSites,
    revenue:sum('revenue'), cogs:sum('cogs'), opex:sum('opex'), result:sum('result'), arr:hs[1].endSites*model.annualPricePerSite};
});
const first18=periods.slice(0,3);const total18=k=>first18.reduce((a,h)=>a+h[k],0);
const spend18=total18('cogs')+total18('opex');
const funding=[['Product and research',total18('product')],['Pilots and sales',total18('sales')],['Privacy, security and review',total18('privacy')],['Administration and insurance',total18('admin')],['Service delivery (COGS)',total18('cogs')],['Reserve',model.raise-spend18]];
assert.equal(notes.slice(0,14).reduce((a,n)=>a+n.seconds,0),840);
assert.equal(notes[4].seconds,180);
assert.equal(funding.reduce((a,r)=>a+r[1],0),model.raise);
assert.equal(spend18,546000);
assert.equal(total18('revenue'),144000);
assert.equal(years[2].arr,1320000);
assert.equal(years[2].result,60000);
const calculations={periods,years,unitCogs,grossMargin:1-unitCogs/model.annualPricePerSite,funding,
  eighteenMonths:{grossSpend:spend18,revenue:total18('revenue'),netBurn:spend18-total18('revenue'),endingCash:model.raise-spend18+total18('revenue')},
  market:{nationalAnnual:model.market.usPublicElementarySchools*model.annualPricePerSite,serviceableAnnual:model.market.usPublicElementarySchools*model.market.serviceableShareAssumption*model.annualPricePerSite},
  valuation:{postMoney:model.raise/(model.equityPercent/100),preMoney:model.raise/(model.equityPercent/100)-model.raise}};
await fs.writeFile(path.join(here,'calculated-model.json'),JSON.stringify(calculations,null,2)+'\n');

const reference = path.join(root,'docs/presentations/Focal Prototype Presentation.pptx');
const presentation=await PresentationFile.importPptx(await FileBlob.load(reference));
const originals=[...presentation.slides.items];
for(const n of notes) {const s=originals[n.template].duplicate();s.moveTo(presentation.slides.items.length-1);}
presentation.slides.keep(Array.from({length:notes.length},(_,i)=>originals.length+i));
const slides=presentation.slides.items;
const C={navy:'#16234B',blue:'#1475AA',teal:'#286B70',lightTeal:'#79B5B4',muted:'#53627A',pale:'#EAF1F6',bg:'#F6F9FC',white:'#FFFFFF'};
const font='Helvetica Neue';
const k=v=>'$'+(v/1000).toLocaleString('en-US',{maximumFractionDigits:1})+'K';

function txt(s,text,x,y,w,h,size=32,color=C.navy,bold=false){
  const q=s.shapes.add({geometry:'textbox',name:text.slice(0,55),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  q.text=text;q.text.style={typeface:font,fontSize:size,bold,color,insets:0,verticalAlignment:'top',wrap:'square',autoFit:'none'};return q;
}
function replace(s,old,text){const q=s.shapes.items.find(x=>String(x.text)===old);if(!q)throw new Error('Missing template text: '+old);q.text=text;return q;}
function base(s,i,dark=false){
  const keep=s.shapes.items.filter(q=>q.position.top<170 || q.position.top>=830);
  for(const q of [...s.shapes.items])if(!keep.includes(q))q.delete();
  const title=keep.find(q=>q.position.top<170);title.text=notes[i].title;
  title.text.style={typeface:font,fontSize:56,bold:true,color:dark?C.white:C.navy,insets:0,wrap:'square',autoFit:'none'};
  const num=keep.find(q=>q.position.top>=830);if(num)num.text=String(i+1).padStart(2,'0');
}
function foot(s,text,dark=false){txt(s,text,80,786,1360,62,22,dark?'#C0D0E3':C.muted);}
function table(s,values,x=80,y=220,w=1440,h=500,widths=null,size=28){
  const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,...(widths?{columnWidths:widths}:{})});
  t.borders.assign({fill:'#D7E3EC',width:1,style:'solid'});
  t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({
    textStyle:{typeface:font,fontSize:size,color:C.navy},margins:{left:18,right:18,top:16,bottom:12},anchor:'top'});
  for(let r=0;r<values.length;r++){
    t.rows[r].height=h/values.length;
    for(let c=0;c<values[0].length;c++){
      const a=t.getCell(r,c);a.fill=r===0?C.navy:r%2===0?C.pale:C.white;
      a.text.style={typeface:font,fontSize:size,color:r===0?C.white:C.navy,bold:r===0};
    }
  }
  return t;
}
function columns(s,items,y=230){
  items.forEach((a,i)=>{const x=80+i*500;txt(s,a[0],x,y,440,95,76,C.teal,true);txt(s,a[1],x,y+110,440,90,32,C.navy,true);txt(s,a[2],x,y+220,420,210,30,C.muted);});
}

// 1: preserve source cover, logo, typography and alignment.
replace(slides[0],'Focal Prototype\nPresentation','Focal Family\nInvestor pitch');
replace(slides[0],'Three approaches to the next vision-care decision','A prepared next step for parents');
replace(slides[0],'MENG 570   Team 5','Focal Technologies   Team 5');
replace(slides[0],'Fan, Hadley, Haydn, Burak and Qingyi','Haydn, Fan, Qingyi, Burak and Hadley');

base(slides[1],1);
txt(slides[1],'Pat has a concern',80,220,640,55,30,C.teal,true);
txt(slides[1],'A school letter.\nAn observation at home.\nA conversation to prepare.',80,315,670,300,48,C.navy,true);
txt(slides[1],'The unfinished work',875,220,600,55,30,C.teal,true);
txt(slides[1],'Parents need to organize what they noticed and ask for help.',875,315,610,180,42,C.navy,true);
txt(slides[1],'Staff still have to support and follow up with families.',875,550,610,130,32,C.muted);
foot(slides[1],'Pat is an illustrative parent. Head Start guidance describes support and follow-up after a referral.');

base(slides[2],2);
txt(slides[2],'The user',80,220,630,55,30,C.teal,true);
txt(slides[2],'Parents of children\naged 4–10',80,295,650,150,50,C.navy,true);
txt(slides[2],'Trigger: a school letter or a concern raised by a parent or teacher.',80,490,630,150,34,C.muted);
txt(slides[2],'The proposed buyer',875,220,630,55,30,C.teal,true);
txt(slides[2],'District student services\nSchool nurse champion',875,295,635,150,44,C.navy,true);
txt(slides[2],'Reason to pay: less follow-up work and clearer family next steps.',875,490,620,150,34,C.muted);
foot(slides[2],'Discovery: 5 real interviews, including 1 parent, plus 5 AI simulations. Buyer demand and willingness to pay remain untested.');

// 4: preserve the reference Family screenshot and its layout.
replace(slides[3],'B   Focal Family',notes[3].title);
replace(slides[3],'05','04');
replace(slides[3],'Parent Pat','Focal Family today');
replace(slides[3],'Can a shared activity help Pat prepare a next step?','A shared activity.\nA parent-owned note.');
replace(slides[3],'The test','The parent decides');
replace(slides[3],'Practice, play six pictures, capture observations and prepare a note.','Record observations, choose a next step and edit the message.');
replace(slides[3],'Proposed signal: 4 of 5 finish unaided and 3 of 5 choose appointment or school preparation.','Our promise: help parents prepare a useful conversation about their child.');
replace(slides[3],'Picture matching supports interaction only. The parent chooses the next step.','Activity, not vision screening. Screenshot shows the labeled fictional example.');

// 5: retain the source's dark demo layout, real practice screenshot and URL.
replace(slides[4],'Live demo B',notes[4].title);
replace(slides[4],'08','05');
replace(slides[4],'Focal Family','3 minutes');
replace(slides[4],'Practice and picture activity\nParent observations\nEditable note and next step','0:00  Practice and play\n1:30  Add observations\n2:00  Prepare and export');
replace(slides[4],'Can Pat explain what to do after the activity?','The output is a parent note,\nnot a medical result');

base(slides[5],5);
table(slides[5],[['Working today','What the investment adds'],
  ['Shared activity and parent observations','10-site, 200-family feasibility pilot'],
  ['Parent-selected next step and editable note','Measure completed actions and staff time'],
  ['Session-only data and file export','Permissions, follow-up status and reporting']],80,220,1440,410,[670,770],31);
txt(slides[5],'Pilot gate: +15 percentage points in completed next steps',80,685,1430,60,34,C.teal,true);
foot(slides[5],'Proposed target versus usual information at 30 days. No completed pilot, paying customer or clinical validation is claimed.');

base(slides[6],6);
table(slides[6],[['Alternative','What it does well','Where Focal would compete'],
  ['Letters and staff calls','Familiar and personal','Guided preparation with less repeated staff work'],
  ['GoCheck Kids','Professional screening and EHR integration','Parent preparation outside the clinical visit'],
  ['Peek Vision','Screening, referral tracking and reminders','A focused parent-and-child experience at home']],80,220,1440,470,[290,520,630],29);
foot(slides[6],'Proposed differentiation, not proven superiority. A future advantage depends on outcomes, distribution and renewals. Sources in notes.');

base(slides[7],7);
columns(slides[7],[
  ['$125.9M','National school opportunity','52,450 public elementary schools × $2,400 per year'],
  ['$12.6M','Illustrative reachable subset','10% of sites assumed to fit the workflow and buying conditions'],
  ['$1.32M','Year-three exit ARR target','550 paid schools × $2,400 per year']]);
foot(slides[7],'NCES 2021–22 site-count benchmark. Price, 10% filter and adoption are assumptions. Private schools and practices excluded.');

base(slides[8],8);
columns(slides[8],[
  ['40','Buyer conversations','Founder outreach to North Carolina school nurses and district leaders'],
  ['10','Pilot sites','Agree family and staff outcomes with the budget owner'],
  ['50','Paid sites by year-one end','Expand successful pilots through district contracts']]);
foot(slides[8],'Proposed funnel, not a committed pipeline. Districts may buy multiple schools. Procurement timing and budget fit require validation.');

base(slides[9],9);
txt(slides[9],'75%',80,230,570,125,100,C.teal,true);
txt(slides[9],'Modeled gross margin',80,380,610,55,34,C.navy,true);
txt(slides[9],'$1,800 gross profit per site\n16-month target CAC payback',80,470,630,150,34,C.muted);
table(slides[9],[['Annual unit economics','Per school'],['License revenue','$2,400'],['Hosting and messages','$240'],['Onboarding and support','$300'],['Billing and delivery tools','$60'],['Total COGS','$600']],775,220,745,475,[500,245],29);
foot(slides[9],'Proposed pricing and costs. Payback assumes $2,400 acquisition cost. Buyer test: 60 hours saved × assumed $40/hour = annual fee.');

base(slides[10],10);
txt(slides[10],'Illustrative forecast, starting when funded',80,175,1440,50,28,C.muted);
const chart=slides[10].charts.add('bar',{
  name:'Revenue and total expense forecast',position:{left:80,top:260,width:710,height:445},
  categories:['Year 1','Year 2','Year 3'],
  series:[{name:'Revenue',values:years.map(y=>y.revenue/1000),fill:C.teal},{name:'COGS + OPEX',values:years.map(y=>(y.cogs+y.opex)/1000),fill:C.navy}],
  barOptions:{direction:'column',grouping:'clustered',gapWidth:100},hasLegend:true,
  legend:{position:'bottom',overlay:false,textStyle:{fontSize:23,fill:C.navy}},
  xAxis:{textStyle:{fontSize:24,fill:C.navy},majorGridlines:null},
  yAxis:{min:0,max:1000,majorUnit:250,numberFormatCode:'$0"K"',textStyle:{fontSize:22,fill:C.muted},majorGridlines:{fill:'#D7E3EC',width:1}},
  dataLabels:{showValue:false},chartFill:C.bg,plotAreaFill:C.bg,
});
applyPresentationChartFont(chart,{fontFamily:font});
table(slides[10],[['USD thousands','Y1','Y2','Y3'],
  ['Revenue',...years.map(y=>String(y.revenue/1000))],['COGS',...years.map(y=>String(y.cogs/1000))],
  ['OPEX',...years.map(y=>String(y.opex/1000))],['Operating result',...years.map(y=>String(y.result/1000))],
  ['Year-end paid sites',...years.map(y=>String(y.endSites))]],840,245,680,465,[260,140,140,140],25);
foot(slides[10],'ARR is a year-end run rate, not annual revenue. Y3 break-even: 367 average sites. Assumes timely collections. Full model in backup.');

base(slides[11],11);
table(slides[11],[['Use of funds','18 months'],...funding.map(([name,value])=>[name,k(value)]),['Total',k(model.raise)]],80,220,800,510,[590,210],27);
txt(slides[11],'120 paid sites',960,240,560,90,58,C.teal,true);
txt(slides[11],'Target at month 18',960,345,555,55,31,C.navy,true);
txt(slides[11],'Pilot outcome evidence\nEarly renewal decisions',960,440,545,135,34,C.navy);
txt(slides[11],'$546K planned cost before revenue\n$54K reserve inside the raise',960,610,560,100,28,C.muted);
foot(slides[11],'Proposed budget. Base-case 18-month revenue: $144K. Ending cash: $198K. Labor included with lean founder compensation.');

base(slides[12],12);
table(slides[12],[['Team member','Role','Milestone owner'],
  ['Haydn Stucker','CEO','School access and fundraising'],['Fan Zhang','CCO','Customer evidence and messaging'],
  ['Qingyi Hu','CPO','Parent experience and usability'],['Burak Donbekci','CTO','Delivery, security and integration'],
  ['Hadley McCormack','CFO','Pricing, unit economics and runway']],80,220,1440,480,[425,190,825],30);
foot(slides[12],'Next capability to recruit: pediatric eye-care and school-health advisers. Working prototypes demonstrate execution, not clinical expertise.');

base(slides[13],13,true);
txt(slides[13],'18 months to prove the business',80,235,1410,85,54,C.white,true);
txt(slides[13],'Families take the next step',80,365,1400,65,42,C.lightTeal,true);
txt(slides[13],'Schools see value and renew',80,470,1400,65,42,C.lightTeal,true);
txt(slides[13],'Delivery supports sustainable economics',80,575,1400,65,42,C.lightTeal,true);
foot(slides[13],'Proposed terms: $3.4M pre-money / $4.0M post-money valuation. A working Family prototype, with outcomes and buyer demand still to prove.',true);

base(slides[14],14);
table(slides[14],[['Six-month period',...periods.map(p=>p.period)],
  ['Average paid sites',...periods.map(p=>String(p.averageSites))],
  ['Revenue ($K)',...periods.map(p=>String(p.revenue/1000))],['COGS ($K)',...periods.map(p=>String(p.cogs/1000))],
  ['OPEX ($K)',...periods.map(p=>String(p.opex/1000))],['Operating result ($K)',...periods.map(p=>String(p.result/1000))]],80,215,1440,390,[330,185,185,185,185,185,185],24);
txt(slides[14],'Y3 sensitivity: price −20% gives −$132K operating result. Unit COGS +25% gives $0.',80,645,1420,85,29,C.teal,true);
foot(slides[14],'Revenue uses average sites. Cash assumes same-period collection. Net site targets require replacement of churn. No taxes, interest or capex.');

base(slides[15],15);
table(slides[15],[['Proposed pilot','Decision rule'],['10 sites, about 200 families','Usual information compared with usual information plus Focal'],
  ['Usability and understanding','80% finish unaided. 90% understand this is not screening.'],
  ['30-day next-step completion','Target +15 percentage points. Separate reported and verified action.'],
  ['School buyer value','Measure staff effort and test willingness to renew at $2,400/site.']],80,220,1440,470,[540,900],29);
foot(slides[15],'Feasibility pilot, not a powered clinical efficacy claim. Preserve usual care. Predefine endpoints, missing-data treatment and consent.');

base(slides[16],16);
table(slides[16],[['Evidence we have','What it does not establish'],['5 real interviews, including 1 parent','Market demand, clinical accuracy or willingness to pay'],
  ['5 AI-simulated interviews','Independent customer evidence'],['Working Family activity and note','Completed care, retention or staff time savings'],
  ['Named alternatives already serve this area','Unique follow-up technology or a defensible moat']],80,220,1440,470,[660,780],30);
foot(slides[16],'Peek already offers referral tracking and reminders. Focal must demonstrate better fit for the proposed parent workflow.');

base(slides[17],17);
table(slides[17],[['Risk','How the funded plan addresses it'],['Parents mistake play for screening','Test comprehension. Keep clear limits and professional referrals.'],
  ['Sensitive family or school information','Minimum data, permissions, access controls and adviser review'],
  ['Slow purchasing or weak renewal','Pilot with a budget owner. Stage hiring against paid demand.'],
  ['Incumbents copy the workflow','Build outcome evidence and distribution. Integrate where useful.']],80,220,1440,470,[560,880],29);
foot(slides[17],'Current prototype: session memory and manual export only. No diagnosis, booking, sent messages, partner portal or compliance certification.');

base(slides[18],18);
const links=[['NCES: school count (2021–22)','https://nces.ed.gov/programs/digest/d22/tables/dt22_216.10.asp'],
 ['Head Start: referral follow-up','https://headstart.gov/publication/vision-screening-referrals'],['GoCheck Kids: professional screening','https://www.gocheckkids.com/'],
 ['Peek: screening and referral workflows','https://peekvision.org/'],['Focal Family: live demo','https://focal-demo-b.streamlit.app/']];
links.forEach(([label,url],i)=>{const q=txt(slides[18],label,80,220+i*75,1380,55,31,C.blue,true);q.text=[[{run:label,link:{uri:url,isExternal:true}}]];});
txt(slides[18],'Demo recovery: preloaded fictional example, then screenshots on slides 5 and 4.',80,650,1420,85,31,C.teal,true);
foot(slides[18],'External sources checked October 30, 2026. Local evidence and full URLs in notes. All pricing, projections and funding terms are proposals.');

let elapsed=0;
for(let i=0;i<slides.length;i++){
  const n=notes[i];const mm=v=>Math.floor(v/60)+':'+String(v%60).padStart(2,'0');
  const timing=i<14?`${mm(elapsed)}–${mm(elapsed+n.seconds)} (${n.seconds} seconds)`:'Backup, outside the 14-minute talk';
  slides[i].speakerNotes.text=`${n.title}\nPresenter: ${n.speaker}\nTiming: ${timing}\n\n${n.script}\n\nSources and assumptions\n${n.sources.join('\n')}`;
  slides[i].hidden=i>=14;elapsed+=n.seconds;
}
const candidate=path.join(temp,'candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidate);
const final=path.join(temp,'final',`Focal Family Executive Pitch-${Date.now()}.pptx`);
const receipt=path.join(temp,path.basename(final)+'.validation.json');
const tableOwners=[6,7,10,11,12,13,15,16,17,18];
const existingChartDirs=new Set((await fs.readdir(root)).filter(n=>n.startsWith('.chart-data-')));
await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:final,pythonExecutable:python,
  integrityValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_layout_geometry.py'),
  explicitTotalSlideCount:19,requiredNativeTableOwnerSlides:tableOwners,requiredNativeChartOwnerSlides:[11],
  materializeLiteralChartWorkbooks:true,
  tableArithmeticContracts:[
    {slide:10,table:1,label_column:0,total_row:5,value_columns:[1],component_rows:[2,3,4]},
    {slide:12,table:1,label_column:0,total_row:7,value_columns:[1],component_rows:[1,2,3,4,5,6]}
  ],
  layoutArgs:['--expected-slide-size-emu','15240000,8572500','--validate-bullet-geometry','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],
  fontPolicy:{basis:'reference',families:[font],referencePath:reference,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(reference)).digest('hex')},
  verifyArtifactToolImport:true,receiptPath:receipt});
await fs.copyFile(receipt,path.join(temp,'validation.json'));
for(const name of await fs.readdir(root)) {
  if(name.startsWith('.chart-data-') && !existingChartDirs.has(name)) await fs.rm(path.join(root,name),{recursive:true});
}
const output=path.join(here,'Focal Family Executive Pitch.pptx');
await fs.copyFile(final,output);
for(let i=0;i<notes.length;i++){
  // A fresh renderer avoids cross-slide glyph/table cache artifacts in previews.
  execFileSync(process.execPath,[path.join(here,'render-slide.mjs'),runtimeModules,output,path.join(temp,'renders'),String(i+1)],{stdio:'pipe'});
}
console.log(JSON.stringify({output,slides:notes.length,mainSlides:14,backupSlides:5,talkSeconds:elapsed,demoSeconds:notes[4].seconds,model:calculations.eighteenMonths}));
