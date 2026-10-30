# English Academic AI-Tell Catalog

Each pattern: signal → fix → before/after. Examples are deliberately drawn from different fields; the rules are field-agnostic.

Patterns tagged [script] are detected by `scripts/scan.py`; [manual] patterns need human judgment.

---

## A. Vocabulary

### A1 AI-signature vocabulary [script]

**Signal**: delve, underscore, showcase, pivotal, intricate, tapestry, testament, realm, landscape (abstract), seamless(ly), foster, leverage (as filler), harness, unlock, unveil, embark, navigate (abstract), multifaceted, nuanced (as filler), holistic, robust (without a robustness test), cutting-edge, game-changer, synergy, paradigm shift, meticulous(ly), commendable, noteworthy, invaluable.

**Fix**: plain verb or concrete noun; delete if nothing remains.

> Before: *This study delves into the intricate interplay between soil moisture and yield, underscoring the pivotal role of irrigation timing.*
> After: *We relate soil moisture to yield across 42 plots; yield varies most with irrigation timing (Fig. 2).*

### A2 Boilerplate emphasis [script]

**Signal**: It is worth noting that; It should be noted that; It is important to note; Notably,; Importantly,; Interestingly,; Crucially,; Needless to say.

**Fix**: delete. If the sentence matters, its content shows it.

> Before: *Notably, the effect persists after controlling for income.*
> After: *The effect persists after controlling for income (Table 3, col. 4).*

### A3 Significance hype [script]

**Signal**: paves the way, opens new avenues, sheds light on, bridges the gap, a crucial/pivotal step toward, of paramount importance, has the potential to revolutionize, plays a vital/crucial/key role, lays a solid foundation.

**Fix**: state the specific consequence, or cut.

> Before: *Our findings shed light on the mechanisms of drug resistance and pave the way for new therapies.*
> After: *Resistant strains overexpress efflux pump AcrB, a target of two existing inhibitors.*

### A4 Empty intensifiers / vague magnitude [script]

**Signal**: significantly (without a test), substantially, dramatically, remarkably, considerably, greatly, extensive/comprehensive/thorough experiments, a wide range of, numerous, various, superior performance, excellent results.

**Fix**: a number with its comparison target, or drop the intensifier. Never invent a number; flag it for the author instead.

> Before: *We conduct extensive experiments showing that our model significantly outperforms baselines.*
> After: *On four benchmarks, our model exceeds the strongest baseline by 1.8–3.5 F1 points (Table 2).*

### A5 Nominalization / light verbs [script]

**Signal**: perform an analysis of, conduct an investigation into, achieve an improvement in, make a comparison, provide a description of, carry out, in order to, with the aim of, for the purpose of.

**Fix**: use the verb. "in order to" → "to".

> Before: *We performed an analysis of the residuals in order to make an assessment of model fit.*
> After: *We analyzed the residuals to assess model fit.*

### A6 Copula avoidance [script]

**Signal**: serves as, stands as, acts as (where "is" suffices), represents (where "is" suffices), boasts, features (as "has").

> Before: *Equation (3) serves as the objective function.* → After: *Equation (3) is the objective.*

### A7 Formulaic openers [script]

**Signal**: In recent years, … has attracted increasing attention; With the rapid development of …; In today's world; In the era of …; Despite recent advances, …; X has emerged as a promising …

**Fix**: open with the concrete problem or tension.

> Before: *In recent years, graph neural networks have attracted increasing attention.*
> After: *Graph neural networks degrade on heterophilous graphs, where linked nodes tend to have different labels.*

### A8 Formulaic closers [script]

**Signal**: In conclusion, (mid-paper); In summary, (at the end of every paragraph); Overall, these results demonstrate the effectiveness of …; This further validates …; This highlights the importance of …

**Fix**: delete summary sentences that only restate; keep any genuinely new inference.

### A9 Unfavorable result mishandling [manual]

**Signal**: Writing a weaker metric as a verdict on the whole method, or switching the evaluation criterion to avoid the result. Also: burying the favorable metric while headlining the unfavorable one.

**Fix**: state the specific tradeoff — which metric improved, which dropped, by how much. Do not present one weaker metric as a general defect. Do not switch evaluation criteria to avoid the result. Lead with the comparison against the strongest competitor, not the trivial baseline. Prefer ranges ("2–6 points") over single averages unless the averaging method is stated. Attach each number to its method, metric, and baseline.

> Before (results paragraph): *DistMix achieves higher accuracy than TFMix at every stage from D2 to D10. However, D6 MMD is 90.52%, slightly above DistMix's 90.45%, so the overall advantage cannot be stated as superior to every baseline at every stage. The ten-stage mean of 90.70% and D10 of 89.75% describe the full trajectory and the final cumulative state separately.*
> After: *At D6, MMD and DistMix reach 90.52% and 90.45%, respectively. DistMix achieves a ten-stage mean accuracy of 90.70% and a final-stage accuracy of 89.75%, demonstrating sustained adaptation across the long time-domain sequence.*
>
> Note: the original buries the positive result under a disclaimer ("cannot be stated as"). The fix states the D6 exception as a plain fact in one sentence, then leads the next sentence with the positive result. The exception is not hidden; it is no longer the headline.

### A10 Novelty and priority claims [script]

**Signal**: "to the best of our knowledge", "for the first time", "the first study/method/work to…", "a novel method/framework", "we are the first", "uniquely".

**Fix**: state what specifically distinguishes the contribution. Priority claims are often unverifiable and invite reviewer pushback; replace with what the work actually does differently. If the distinction is real, the description makes it clear without the claim.

> Before: *To the best of our knowledge, this is the first work to delve into temporal layer drift in frozen MLLMs.*
> After: *Prior probing-based methods fix the reading target at dataset level; we show that the locally optimal layer changes within individual events.*

### A11 Over-claiming verbs [script]

**Signal**: "proves", "demonstrates that", "confirms that", "validates that", "establishes that" — used where the evidence is a correlation, a single dataset, or an ablation rather than a controlled experiment ruling out alternatives.

**Fix**: match the verb to the evidence. A direct comparison with a number → "shows", "finds". An ablation → "indicates X contributes to Y". A correlation → "is associated with". A mechanism not directly tested → "suggests", "we hypothesize". Save "demonstrates" for a direct test that rules out the main alternative explanation.

| Evidence | Verb |
|---|---|
| Controlled experiment, direct measurement | outperforms, reduces, increases |
| Ablation showing component contribution | removing X lowers …, indicating X contributes |
| Correlation / observational | is associated with, is consistent with |
| Mechanism not directly tested | may, we hypothesize, suggests |
| Single dataset | holds on this dataset; cross-dataset generalisation not yet tested |

> Before (abstract closer): *These results support lightweight fingerprint learning and continual adaptation under the independently evaluated class-incremental and domain-incremental protocols.*
> After: *These results demonstrate the effectiveness of the proposed methods for lightweight RFF representations, device-class expansion, and sequential acquisition-domain changes.*
>
> Note: "support … under the independently evaluated protocols" uses a verb weaker than the evidence (direct numeric comparisons) and appends a scope qualifier already stated in the experiment section. `demonstrate` matches the evidence; the qualifier is removed.

---

## B. Sentence patterns

### B1 Connective overuse [script: sentence-initial count]

**Signal**: consecutive sentences opening with Moreover / Furthermore / Additionally / In addition / Also / In particular / Consequently.

**Fix**: keep a connective only for a real causal, contrastive, or additive relation; otherwise let order carry the logic.

> Before: *Moreover, the sensor is cheap. Furthermore, it is small. Additionally, it needs no calibration.*
> After: *The sensor is cheap, small, and needs no calibration.*

### B2 Negative parallelism [script]

**Signal**: not only X but also Y; not just X, but Y; It's not X — it's Y; rather than merely X; X is not about A, it is about B. Often X is a claim nobody made.

**Fix**: state Y directly. Keep the contrast only if X is an actual position in the literature or earlier text.

### B10 Reflexive "rather than" contrast [script]

**Signal**: "rather than [doing/being X], we [do/are Y]" — where X is not a position the reader holds or the literature maintains, but only something the author imagines as a misreading. Also: "instead of X, this paper Y" as a pre-emptive correction of nobody's assumption.

**Fix**: state the positive claim directly. Keep "rather than" only when contrasting with a real alternative that a reader might genuinely assume or that the literature actually advocates.

> Before: *Rather than focusing on a specific architecture, this paper studies the temporal dynamics of layer preference.*
> After: *This paper studies how the locally optimal reading layer changes over time within an event.*

> Before: *Instead of proposing a new backbone, we introduce a routing module that works on top of any frozen MLLM.*
> After: *We introduce a lightweight routing module that wraps any frozen MLLM without modifying its weights.*

### B10 Reflexive "rather than" contrast [script]

**Signal**: "rather than [doing/being X], we [do/are Y]" — where X is not a real position the reader holds or the literature maintains, but only something the author imagines as a misreading. Also: "instead of X, this paper Y" as a pre-emptive correction of nobody's assumption.

**Fix**: state the positive claim directly. Keep "rather than" only when contrasting with a real alternative that a reader might genuinely assume or that the literature actually advocates.

> Before: *Rather than focusing on a specific architecture, this paper studies the temporal dynamics of layer preference.*
> After: *This paper studies how the locally optimal reading layer changes over time within an event.*

> Before: *Instead of proposing a new backbone, we introduce a routing module that works on top of any frozen MLLM.*
> After: *We introduce a lightweight routing module that wraps any frozen MLLM without modifying its weights.*

### B11 High-impact position violation [manual]

**Signal**: limitations, caveats, and scope disclaimers placed in the abstract, the contribution list, the topic sentence of a paragraph, or the opening line of the conclusion — i.e., in positions where the reader's first impression is formed.

**Fix**: move necessary limitations to the methods, discussion, or limitations section. In high-impact positions, lead with the claim, finding, or contribution. The one exception: a limitation is essential to a specific sentence when omitting it would make that sentence misleading to someone who acts on it alone.

> Before (figure caption, last sentence): *The shared architecture has protocol-specific classifiers and objectives.*
> After: delete the sentence entirely.
>
> Note: a figure caption should describe what is shown. "Shared architecture has protocol-specific …" is a pre-emptive defence against a misreading the figure does not invite. The method section already explains the distinction; the caption does not need to repeat it as a caveat.

**Signal**: a main clause followed by ", highlighting …", ", underscoring …", ", demonstrating …", ", showcasing …", ", reflecting …", ", emphasizing …", ", ensuring …".

**Fix**: delete the tail, or make it a separate sentence with evidence.

> Before: *Accuracy rose to 94%, highlighting the effectiveness of the proposed loss.*
> After: *Accuracy rose to 94%; removing the proposed loss lowers it to 89% (Table 4).*

### B4 Rule of three [manual]

**Signal**: lists padded to three items ("faster, simpler, and more robust") where one item has no support.

**Fix**: keep only the supported items.

### B5 "As can be seen from Fig. X" [script]

**Signal**: As can be seen from / As shown in Fig. X, it can be observed that / It can be seen that / We can observe that.

**Fix**: lead with the content; put the figure reference in parentheses.

> Before: *As can be seen from Fig. 4, it can be observed that error decreases with batch size.*
> After: *Error decreases with batch size (Fig. 4).*

### B6 Em-dash [script]

**Signal**: — or `---` in LaTeX used as a parenthetical or a "reveal".

**Fix**: recast with commas, a colon, parentheses, or two sentences. (Keep `--` en-dash for numeric ranges.)

### B7 Overlong, clause-stacked sentences [script: length]

**Signal**: more than ~30 words, or three or more subordinate clauses chained with which / that / while / with.

**Fix**: one idea per sentence.

### B8 Elegant variation [manual]

**Signal**: one referent cycled through synonyms (our method / the proposed framework / this approach / the model).

**Fix**: pick one name and use it consistently.

### B9 Rhetorical questions and reveal framing [script]

**Signal**: "But what does this mean?"; "The answer is simple:"; "Here's the key insight:".

**Fix**: plain declarative.

---

## C. Paragraph-level

### C1 Uniform paragraph template [manual]

Every paragraph is topic sentence → three supports → wrap-up line. Vary the structure; drop the wrap-up when it only restates.

### C2 Uniform rhythm [script: sentence-length CV]

Sentences of nearly identical length read as generated. Merge, split, and allow a short sentence.

### C3 Contribution-list clichés [manual]

> Before: *(1) a novel framework; (2) extensive experiments; (3) state-of-the-art results.*
> After: *(1) a sparse attention layer that cuts memory from O(n²) to O(n log n); (2) on Long Range Arena it matches dense attention within 0.4 points while using 6× less memory.*

### C4 Citation dumping [manual]

> Before: *Many methods have been proposed [3, 7, 9, 12, 15].*
> After: *The closest prior work, TabNet [7], encodes all features jointly; we condition on feature types instead.*

---

## D. Do not over-correct

- Keep "we": first-person plural is standard.
- Keep passive voice where the actor is irrelevant ("Samples were centrifuged at 4 °C").
- "significant" is correct when a statistical test is reported; "robust" is correct when robustness is tested.
- "demonstrates" is fine when a direct experimental test rules out the main alternative.
- Fixed terms stay: "significance level", "robust standard errors", "comprehensive metabolic panel".
- Semicolons and an occasional genuine three-item list are fine.
- Keep "rather than" when it contrasts a real alternative — e.g., distinguishing the paper's scope from a related line of work the reader might conflate it with.
- Keep "novel" when a specific technical distinction is stated in the same sentence.
- Quoted text, definitions, theorems, and equations stay verbatim.
- **Examples in the rule catalogs are not facts**: never import wording such as "three institutional settings" or "most relevant variation" into the user's text unless the draft already contains that evidence.
