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

### B3 Superficial "-ing" tails [script]

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
- Fixed terms stay: "significance level", "robust standard errors", "comprehensive metabolic panel".
- Semicolons and an occasional genuine three-item list are fine.
- Quoted text, definitions, theorems, and equations stay verbatim.
