# Burak's draft deck

A second, independent draft of the class presentation (15 slides), built alongside Haydn's [Focal Prototype Presentation](<../Focal Prototype Presentation.pptx>). **The two decks have not been combined.** A teammate will decide what to keep from each.

- [PDF](<Focal Three Prototypes - Burak draft.pdf>): for reading and review
- [HTML](<Focal Three Prototypes - Burak draft.html>): opens in any browser; print it to get the PDF again
- The editable original is a Claude Slides artifact owned by Burak (https://claude.ai/artifact/4HihQp2Krc81Gp1ZxPjUYD). It is private until Burak shares it, and it can be exported to PowerPoint from its Share menu.

## What this draft adds

Compared with the PPTX, this draft adds a single framing for the comparison (**how much should Focal judge for you?**), customer quotes tied to the feature each one led to, the shift from “then” to “now”, a caveat on how to read the class vote (the room is mostly students, not parents), and a placeholder for the team’s pick before the vote. It does not have per-demo slides or a value/effort/complexity table; the PPTX does.

Placeholder still to fill: **[Team: which version, and why, in one sentence]** on slide 13.

## Speaker notes

**1. Three prototypes, three hypotheses**

About 10 seconds. We are Focal, Team 5. Today we show three prototypes of one product. Each tests a different hypothesis about how Focal should help people act on their vision. At the end, you vote on the one you would actually use.

**2. Convenient or thorough: pick one**

Part 1, problem and approach: under 2 minutes for this slide and the next. Early detection needs routine checks, and routine checks are hard to get. Today people choose between convenient (an online chart) and thorough (a clinic exam). We heard three pains: access, seeing change over time, and trusting an online result.

**3. What we knew then vs. now**

We started thinking the problem was access, and that institutions like DMVs and airlines were the big market. Ten interviews moved us. People avoid the answer, not just the appointment. Action needs an outside trigger. And a result only helps if people trust it and know what to do next. We dropped pilots because no interview supported them. Licensing agencies stay a hypothesis because we only reached that persona through AI-simulated interviews.

**4. Same job, three ways to help**

Part 2, the three versions: about 2 minutes per hypothesis across the next four slides. One job runs through every interview: has my vision changed, and do I need a doctor? We built three answers that differ in how much the product judges for you. B leaves the judgment with the parent. A shows a trend and lets you read it. C gives a verdict against an official rule. The vote tells us which degree of judgment people actually want.

**5. Prototype A · Focal Monitor**

About 2 minutes. Riley is our primary early adopter: a screen-heavy adult whose last exam was years ago. The bet is that seeing change over time is worth more than one score. The prototype shows the same result two ways, alone and on a trend, in random order, then asks neutral questions. The history is illustrative, so this tests preference, not whether people really come back. The acuity labels are illustrative and say so in the app.

**6. Prototype B · Focal Family**

About 2 minutes. Pat is a working parent who relies on school screenings. Kids can’t explain what they see, and they memorize home charts. So B does not measure anything. A parent and child play a short matching game together, the parent records what they’ve noticed, and Focal helps them prepare a concrete next step. The bet is that parents value preparation and support over a number. The success signals are proposed targets for a small test with parents.

**7. Prototype C · DMV Pre-Check**

About 2 minutes. Alex is a college student getting a first license. He doesn’t want a number; he wants to know whether he will pass his state’s test. C checks against the real rule for NC, CA, NY, TX and FL, each with an official source. Letters are sized to the screen with an ID card. Six letters sit at the deciding line, so a lucky guess can’t pass you. You get one honest retake. If it’s not a pass, you get a plan: an eye exam near you, your state’s form, and a reminder. This is also the free DMV checker from our Lean Canvas channels. Riskiest assumption: Alex said the road test worried him more than the eye test.

**8. What the comparison can teach us**

One slide to make the differences explicit before the demos. Each version ties to a different trigger, gives a different amount of judgment, and maps to a different part of our business model: premium tracking, a parent channel through schools and pediatricians, or the free DMV checker. Whichever wins tells us which of these to build first.

**9. See it work (live demos)**

Part 3, live demos: about 2 minutes each, roughly 6 minutes total. Open all three links before class, because idle Streamlit apps go to sleep. Let each product speak; don’t narrate every click. A: take the check, then switch between Single Result and Trend Tracking. B: practice picture, a few matches, one break, an observation, a next step, the summary. C: pick North Carolina, show the source link, hold up an ID card, tap Can’t tell on a few letters at the 20/40 line, then show the plan. Keep a second tab on a finished result in case live answering runs long.

**10. Built from customer quotes**

Part 4, justification and strategy. Each version starts from something a customer told us. Riley had no baseline. Pat wants a reason to act, not constant testing. Alex got a number and didn’t know whether it meant pass or fail. Be upfront that these quotes come from AI-simulated persona interviews. Real in-person interviews backed the same themes: Anna waits out a slipping prescription, Fan’s mother’s kids memorize home charts, and Kevin said a standalone app “wouldn’t even register.”

**11. What we kept, what we cut**

Each prototype tests exactly one decision, and we cut everything that didn’t serve it. A uses illustrative history, so it can measure preference but not whether people really return. B has no score on purpose; the open question is whether parents want one. C covers five states and tests both eyes together. That’s mostly right, but California and Texas also check each eye. Our biggest cut was the agency side, because that evidence is thinnest. Each prototype’s README has the full Feature Scope Card: value, effort, complexity and success signal.

**12. What these prototypes can’t tell us**

Keep this quick, about 30 seconds. All three are non-clinical practice prototypes. A’s acuity labels are illustrative and say so; C sizes its letters physically but hasn’t been validated against a clinical chart. Half our interviews were AI-simulated. No prototype touches the agency side yet. And a vote measures appeal: our real success signal is whether someone acts, like booking an exam.

**13. What three versions tell us**

What building three versions taught us. First, the hard part isn’t the test, it’s trust and action, so every version ends in a next step. Second, people act when something forces it: a prescription, a school letter, a DMV date. Each version attaches to one of those moments. Third, the underlying check could be shared; what changes is the front door and how the result is framed. State the team’s pre-vote lean here so the class vote has something to agree or disagree with.

**14. How we’ll read the vote**

Before the vote, say what each outcome would mean, so the result is something we can act on. Name the caveat out loud: the room is students, not parents, so we will weigh the vote alongside the in-app feedback from each prototype. If we disagree with the result, we will bring evidence to the teaching team.

**15. Which one would you actually use?**

Leave this up during the vote. Thank the class. After the results, record the tally and the team’s response in docs/assignment-readiness.md.
