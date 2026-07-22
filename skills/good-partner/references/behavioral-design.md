# Behavioral Design for Attention Protection

Use this reference to justify operating rules, not to diagnose the user. The research supports reducing unnecessary switching, batching low-urgency notifications, interrupting at lower-cost task boundaries, and leaving concrete plans for unfinished work. It does not establish one universal notification interval or prove that every person responds identically.

## Evidence-to-Rule Map

| Finding | Operational rule | Boundary |
| --- | --- | --- |
| Switching away from an unfinished task can leave attention on the prior task and reduce performance on the next one. | Prefer one foreground workstream. Finish a coherent subgoal before switching; if switching is necessary, record a restart cue and specific next step. | “Attention residue” is an experimental effect, not a minute-by-minute timer. |
| Interrupted workers may compensate by working faster while reporting more stress, frustration, time pressure, and effort. | Do not measure success by response speed alone. Reduce unnecessary human interruptions and bundle decisions. | The result does not imply that every interruption reduces output quality. |
| A notification can impair attention even when the recipient does not interact with the device. | Treat a visible request as an interruption. Use silent ledger updates for information that does not require action. | Phone-notification experiments do not directly determine the perfect agent-message cadence. |
| Delivering notifications at task breakpoints can reduce frustration and reaction cost compared with immediate delivery. | Route nonurgent approvals to natural boundaries: completed investigation, artifact, test, or exhausted autonomous path. | A breakpoint must be inferred from work state; clock time alone is a weak proxy. |
| In one randomized field experiment, batching phone notifications three times per day improved several self-reported outcomes, while suppressing all notifications increased anxiety/FoMO. | Batch routine project updates into predictable digests; keep a path for urgent alerts instead of going completely silent. | Three batches per day is evidence for that study's setting, not a universal schedule. Learn the user's preferred window. |
| In a small workplace field study, five days without email were associated with fewer window switches, longer focus, and lower stress measured through heart-rate variability. | Avoid continuous project chatter and review pileups; create bounded periods in which the agent can work without demanding attention. | The study had 13 participants at one site, with usable heart data from seven; it supports cautious physiological plausibility, not a medical claim or a mandate to eliminate email. |
| Unfulfilled goals can intrude on unrelated work; forming a specific, credible plan can reduce that interference. | Every paused project gets a concrete next action, trigger/owner, and resume note. Avoid vague “follow up later” entries. | Plans should be usable and revisable; specificity can become rigidity when circumstances change. |
| If-then implementation intentions improve goal attainment across many studies. | Convert follow-up into trigger-action form: “When test X finishes, inspect Y; if it fails with Z, escalate with evidence.” | Use only when the underlying goal is actually endorsed and the trigger is observable. |

## Default Attention Policy

Use priority and task state before elapsed time:

- **P0:** immediate harm or invalidated decision — interrupt now.
- **P1:** blocks critical path or needs authority — deliver at the next natural breakpoint.
- **P2:** useful but nonblocking — batch into a digest or completion handoff.
- **P3:** useful only for audit/resumption — persist silently.

Use a 15-minute quiet window between nonurgent, attention-demanding requests only as a conservative starting heuristic. Change it when the user states or repeatedly demonstrates another preference. Do not describe it as a neurological threshold. A message that requires no response may still interrupt, so keep required platform progress signals short and predictable.

## Reduce Re-entry Cost

Before pausing or switching, externalize four items:

1. Current state.
2. Last verified evidence.
3. Unresolved question or blocker.
4. Exact next action and its trigger.

This “restart cue” is a practical synthesis of interruption-resumption research and plan-making findings. It prevents the user from having to reconstruct the project from raw logs.

## Avoid Weak or Harmful Claims

- Do not use popular claims such as “every interruption costs exactly 23 minutes” as a fixed rule; observed recovery varies with task, interruption, measurement, and context.
- Do not claim that a 15-, 25-, or 30-minute interval is biologically optimal.
- Do not invoke “decision fatigue,” ego depletion, dopamine, cortisol, or brain regions to add scientific tone unless the claim is necessary and directly supported. The Good Partner workflow only needs the stronger evidence around switching, interruption timing, batching, and concrete planning.
- Do not medicalize ordinary overload or claim to prevent burnout. Say that the workflow aims to reduce avoidable coordination and interruption load.
- Do not optimize solely for fewer messages. Missing an urgent approval or leaving the user uncertain can also create cognitive load. Use bounded deferral and predictable escalation.

## Sources

- Sophie Leroy, “Why Is It So Hard to Do My Work? The Challenge of Attention Residue When Switching Between Work Tasks,” *Organizational Behavior and Human Decision Processes* 109(2), 2009. DOI: [10.1016/j.obhdp.2009.04.002](https://doi.org/10.1016/j.obhdp.2009.04.002)
- Gloria Mark, Daniela Gudith, and Ulrich Klocke, “The Cost of Interrupted Work: More Speed and Stress,” CHI 2008. [Author-hosted paper](https://ics.uci.edu/~gmark/chi08-mark.pdf)
- Cary Stothart, Ainsley Mitchum, and Courtney Yehnert, “The Attentional Cost of Receiving a Cell Phone Notification,” *Journal of Experimental Psychology: Human Perception and Performance* 41(4), 2015. DOI: [10.1037/xhp0000100](https://doi.org/10.1037/xhp0000100)
- Shamsi T. Iqbal and Brian P. Bailey, “Effects of Intelligent Notification Management on Users and Their Tasks,” CHI 2008. DOI: [10.1145/1357054.1357070](https://doi.org/10.1145/1357054.1357070)
- Nicholas Fitz et al., “Batching Smartphone Notifications Can Improve Well-Being,” *Computers in Human Behavior* 101, 2019. DOI: [10.1016/j.chb.2019.07.016](https://doi.org/10.1016/j.chb.2019.07.016); [open dataset](https://doi.org/10.17632/jxzsxzt2mz.1)
- Gloria Mark, Stephen Voida, and Armand Cardello, “A Pace Not Dictated by Electrons: An Empirical Study of Work Without Email,” CHI 2012. [Author-hosted paper](https://stephen.voida.com/uploads/Publications/Publications/markvoida-chi12.pdf); DOI: [10.1145/2207676.2207754](https://doi.org/10.1145/2207676.2207754)
- E. J. Masicampo and Roy F. Baumeister, “Consider It Done! Plan Making Can Eliminate the Cognitive Effects of Unfulfilled Goals,” *Journal of Personality and Social Psychology* 101(4), 2011. [PubMed](https://pubmed.ncbi.nlm.nih.gov/21688924/); DOI: [10.1037/a0024192](https://doi.org/10.1037/a0024192)
- Peter M. Gollwitzer and Paschal Sheeran, “Implementation Intentions and Goal Achievement: A Meta-analysis of Effects and Processes,” *Advances in Experimental Social Psychology* 38, 2006. DOI: [10.1016/S0065-2601(06)38002-1](https://doi.org/10.1016/S0065-2601(06)38002-1)
- Jingya Guo et al., “Effects of Interventions to Reduce the Negative Consequences of Interruptions on Task Performance,” *Applied Ergonomics* 97, 2021. [PubMed](https://pubmed.ncbi.nlm.nih.gov/34273814/); DOI: [10.1016/j.apergo.2021.103506](https://doi.org/10.1016/j.apergo.2021.103506)
