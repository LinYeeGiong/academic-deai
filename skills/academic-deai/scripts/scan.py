#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan academic prose for AI-tell and defensive-hedging patterns (zh + en).

Usage:
    python scan.py <file> [--lang auto|zh|en] [--lines 120-260] [--format md|text]

Hits are CANDIDATES only. Judge each one in context before editing:
"significant" next to a reported p-value is correct, not a defect.
"""

from __future__ import annotations

import argparse
import re
import statistics
import sys
from pathlib import Path

CJK = r"一-鿿"
CJK_RE = re.compile(f"[{CJK}]")

# Each entry: (code, category, regex, hint)
ZH_PATTERNS: list[tuple[str, str, str, str]] = [
    ("A1", "空泛强调",
     r"值得注意的是|值得一提的是|需要指出的是|需要强调的是|不难发现|不难看出"
     r"|显而易见|毋庸置疑|不可否认|众所周知",
     "删除；若内容重要，陈述本身即可体现"),
    ("A2", "拔高夸大",
     r"至关重要|举足轻重|具有重要(的)?意义|意义重大|里程碑|革命性|颠覆性|开创性"
     r"|前所未有|全方位|深度赋能|注入新动能|开辟(了)?新(路径|途径)"
     r"|提供(了)?新思路|奠定(了)?坚实基础|具有广阔的应用前景|有着广阔的前景",
     "改为具体影响对象与幅度，说不出则删"),
    ("A3", "程度词无量化",
     r"显著|大幅|明显(地|提[高升])?|极大(地)?|有效(地)?(提[高升]|改善|降低)"
     r"|充分(说明|证明|体现|验证)|良好的?(性能|效果)|较好的?(性能|效果)"
     r"|优异|卓越|出色",
     "补原文已有数值与比较对象，或删程度词；“显著”仅在有统计检验时保留"),
    ("A4", "虚化动词",
     r"进行(了)?[^，。；\s]{0,6}(分析|优化|验证|训练|测试|研究|处理|探讨|对比|评估|建模)"
     r"|实现(了)?[^，。；]{0,12}的?(提[升高]|优化|改善)"
     r"|起到(了)?[^，。；]{0,12}作用|发挥(着|了)?[^，。；]{0,12}作用"
     r"|对[^，。；]{1,14}加以|做出(了)?[^，。；]{0,12}贡献|展开(了)?研究",
     "还原为实义动词"),
    ("A5", "模板化开头",
     r"随着[^，。；]{2,24}的?(快速|迅速|不断)?(发展|进步|普及)"
     r"|近年来[^。；]{0,34}(受到|引起|获得)[^。；]{0,12}(广泛|越来越多的)?关注"
     r"|在当今(社会|时代)|当今社会|在[^，。；]{2,14}(背景|大背景)下|随着时代的",
     "从具体问题或矛盾开头"),
    ("A6", "模板化收尾",
     r"综上所述|总而言之|总的来说|由此可见|这(充分|进一步)?(说明|证明|体现|验证|印证)了"
     r"|证明(了)?本文(所提)?方法的(有效性|优越性)|体现(了)?本文方法的",
     "只重复前文则删；有新推论则保留推论、删套话"),
]
ZH_PATTERNS += [
    ("A8", "四字格堆砌",
     f"[{CJK}]{{4}}[、，]\\s*[{CJK}]{{4}}[、，]\\s*[{CJK}]{{4}}",
     "保留一个有实指的词，其余换成具体描述"),
    ("A9", "AI 中文高频词",
     r"赋能|抓手|底层逻辑|深度融合|协同发力|全链条|助力|织就|画卷"
     r"|(重要|坚实)的?基石|(增长|创新)引擎|多维度(地)?|打造(了)?一个?",
     "换成平实动词或具体名词"),
    ("B1", "不是…而是…",
     r"(不是|并非|不只是|不仅仅是)[^，。；]{1,28}(，|，\s*)?(而是|而更是|更是)"
     r"|与其说[^，。；]{1,28}不如说",
     "若被否定的说法无人主张，直接陈述后半句"),
    ("B4", "从图中可以看出",
     r"(从|由|如)?(图|表|式)\s*[\d０-９\.\-]{0,8}\s*(中)?(可以|可)?(看出|得出|得知|知|发现)"
     r"|通过观察(可以)?(发现|看出)|可以(清楚地)?(看出|观察到)",
     "以图表内容为主语直陈，编号入括号"),
    ("D1", "叠加式限定",
     r"可能在一定程度上|或许可以在某种|似乎可能|可能会在一定|有望在一定"
     r"|(可能|或许|似乎)[^，。；]{0,10}(在一定程度上|在某种意义上|某种程度上)",
     "最多保留一个限定词，选与证据强度相称的"),
    ("D1b", "单个模糊限定",
     r"在一定程度上|某种程度上|在某种意义上|或多或少|多少有些",
     "能量化就量化；对应真实不确定性才保留，且只说一次"),
    ("D2", "预先自我辩护",
     r"需要(说明|指出)的是[^。；]{0,20}(本文|我们)(并非|并不|无意)"
     r"|本文(并非|无意于?)[^。；]{0,24}(试图|旨在|声称)"
     r"|(我们|本文)(并不|不)声称|这并不意味着|应当承认[^。；]{0,24}但",
     "若无人提出该观点则删；需划定范围则改为一句正面范围陈述"),
    ("D3", "免责声明后缀",
     r"(仍|还)(有)?待(进一步|更多)[^。；]{0,10}(验证|证实|研究|探索)"
     r"|仍需(进一步|更多)[^。；]{0,10}(验证|证实|研究|工作)"
     r"|(当然|不过)，?这一(结论|结果)[^。；]{0,16}(验证|证实)",
     "泛泛的“仍需进一步研究”删除；具体局限集中写入局限性一节"),
    ("D4", "让步转折套话",
     r"尽管[^。；]{0,30}(存在一定|仍有)(局限|不足)[^。；]{0,8}但"
     r"|虽然[^。；]{0,30}(仍有|存在)(不足|局限)[^。；]{0,8}但(总体而言)?"
     r"|诚然[^。；]{1,30}然而",
     "局限性未写清则删让步从句；写清则单独成句，不用于铺垫自夸"),
    ("D5", "过度谦辞",
     r"仅(做|作)(了)?(一些)?初步(探索|尝试)|限于(笔者|作者)水平"
     r"|还(很|较为)?粗浅|抛砖引玉|不足之处在所难免",
     "删除；范围由内容与局限性说明（学位论文致谢除外）"),
    ("D8", "无引用的转述",
     r"(有|一些)学者认为|(一般|普遍|通常)认为|业内人士指出|研究表明(?![^。；]{0,20}\\\\cite)",
     "补原文已有引用；无引用则改为作者自述或列入需确认"),
]

EN_PATTERNS: list[tuple[str, str, str, str]] = [
    ("A1", "AI vocabulary",
     r"\b(delv(e|es|ing|ed)|underscor(e|es|ing|ed)|showcas(e|es|ing|ed)|pivotal"
     r"|intricate|tapestry|testament|realm|seamless(ly)?|foster(s|ing|ed)?"
     r"|harness(es|ing|ed)?|unlock(s|ing|ed)?|unveil(s|ing|ed)?|embark(s|ing|ed)?"
     r"|multifaceted|holistic|cutting-edge|game-chang(er|ing)|synergy"
     r"|paradigm shift|meticulous(ly)?|commendable|noteworthy|invaluable)\b",
     "plain verb or concrete noun; delete if nothing remains"),
    ("A2", "Boilerplate emphasis",
     r"\b(it is worth (noting|mentioning)|it should be noted|it is important to note"
     r"|notably|importantly|interestingly|crucially|needless to say)\b",
     "delete; if it matters, the content shows it"),
    ("A3", "Significance hype",
     r"\b(paves? the way|opens? (up )?new avenues|sheds? light on|bridges? the gap"
     r"|a (crucial|pivotal|critical) step toward|of paramount importance"
     r"|has the potential to revolutioni[sz]e|plays? an? (vital|crucial|key|critical) role"
     r"|lays? a solid foundation)\b",
     "state the specific consequence, or cut"),
    ("A4", "Empty intensifier",
     r"\b(significantly|substantially|dramatically|remarkably|considerably|greatly"
     r"|(extensive|comprehensive|thorough) experiments|a wide range of|numerous"
     r"|superior performance|excellent results)\b",
     "number + comparison target, or drop; 'significantly' only with a test"),
    ("A5", "Nominalization",
     r"\b(perform(s|ed|ing)? an? (analysis|evaluation|comparison|investigation)"
     r"|conduct(s|ed|ing)? an? (analysis|investigation|study) (of|into)"
     r"|achiev(e|es|ed|ing) an? improvement|mak(e|es|ing) a comparison"
     r"|provid(e|es|ing) a description|in order to|with the aim of|for the purpose of)\b",
     "use the verb; 'in order to' -> 'to'"),
    ("A6", "Copula avoidance",
     r"\b(serves? as|stands? as|acts? as|boasts?)\b",
     "'is' usually suffices"),
    ("A7", "Formulaic opener",
     r"\b(in recent years|with the rapid (development|growth|advancement)"
     r"|in today's world|in the era of|despite recent advances"
     r"|has emerged as a promising|has attracted (increasing|growing|widespread) attention)\b",
     "open with the concrete problem or tension"),
    ("A8", "Formulaic closer",
     r"\b(in conclusion|in summary|overall, these results (demonstrate|show)"
     r"|this further (validates|confirms)|this highlights the importance"
     r"|demonstrat(e|es|ing) the effectiveness of (our|the proposed))\b",
     "delete pure restatement; keep genuinely new inference"),
    ("B2", "Negative parallelism",
     r"\bnot (only|just|merely|simply) [^.;]{1,40}\bbut (also )?"
     r"|\brather than (merely|simply)\b|\bis not about [^.;]{1,30}\bit is about\b",
     "state the positive claim directly unless X is a real position"),
    ("B3", "Superficial -ing tail",
     r",\s*(highlight|underscor|demonstrat|showcas|reflect|emphasi[sz]|ensur|illustrat"
     r"|signif|suggest|indicat)(ing)\b",
     "delete the tail, or make it a sentence with evidence"),
    ("B5", "'As can be seen'",
     r"\b(as can be seen|it can be (seen|observed|noted)|we can (see|observe)"
     r"|as (is )?shown in [^,.;]{1,18},? (it|we) can)\b",
     "lead with content; figure reference in parentheses"),
    ("B6", "Em-dash",
     r"—|(?<!-)---(?!-)",
     "recast with commas, colon, parentheses, or two sentences"),
    ("B9", "Reveal framing",
     r"\b(the answer is|here's the (key )?insight|but what does this mean"
     r"|the reason is simple)\b",
     "plain declarative"),
    ("D1", "Hedge stacking",
     r"\b(may|might|could) (potentially|possibly|perhaps|arguably)\b"
     r"|\b(may|might|could) suggest that [^.;]{0,40}\b(may|might|could)\b"
     r"|\bappears? to possibly\b|\bseems? to potentially\b",
     "keep at most one hedge, matched to evidence strength"),
    ("A10", "Novelty/priority claim",
     r"\b(to (the best of )?our knowledge|to our best knowledge"
     r"|for the first time|the first (study|work|method|paper|approach|framework|model|system|analysis) to\b"
     r"|first (attempt|effort|investigation|characterization|demonstration) (to|of)\b"
     r"|a? novel (method|approach|framework|model|system|algorithm|architecture|technique)"
     r"|novel and|uniquely|we (are|were) the first)\b",
     "state what specifically distinguishes the work; avoid unverifiable priority claims"),
    ("A11", "Over-claiming verb",
     r"\b(proves?|prove[sd]|demonstrat(e|es|ed|ing) (that|the)|confirm(s|ed|ing) (that|the)"
     r"|validat(e|es|ed|ing) (that|the)|establish(es|ed|ing) (that|the))\b",
     "'shows', 'indicates', 'suggests' matched to evidence strength; 'demonstrates' needs a direct test"),
    ("B10", "Reflexive rather-than contrast",
     r"\brather than (?!just|than|having|be\b)[^.;,]{2,50}(?=[,;.]|\b(we|this|the|our|it|these)\b)"
     r"|\binstead of [^.;]{1,40}\b(we|this|the)\b",
     "state the positive claim; keep only if X is a real alternative the reader might assume"),
    ("D1b", "Vague hedge",
     r"\b(to some extent|somewhat|relatively|fairly)\b|\bto a certain degree\b",
     "quantify or cut; keep only for a real uncertainty, stated once"),
    ("D2", "Pre-emptive defence",
     r"\bwe do not claim\b|\bthis is not to say\b|\bwe make no claim\b"
     r"|\bit should be noted that this does not imply\b|\bwhile we (recognize|acknowledge)\b",
     "delete if nobody made that claim; else one positive scope sentence"),
    ("D3", "Disclaimer suffix",
     r"\b(although|though|while) further (research|work|study) is needed"
     r"|\bmore (work|research) is (needed|required) to confirm"
     r"|\bfurther (research|work|studies) (is|are) (needed|warranted|required)\b",
     "delete generic ones; put specific limits in the limitations section"),
    ("D4", "Concessive boilerplate",
     r"\balthough (our|the proposed) (method|approach|work) has (certain|some) limitations"
     r"|\bdespite (some|certain) (shortcomings|limitations),? overall\b|\badmittedly\b",
     "drop the concession unless the limitation is specific"),
    ("D5", "Excessive modesty",
     r"\b(our humble attempt|we merely|this preliminary (work|study) (only|merely))\b",
     "delete; scope belongs in the limitations section"),
    ("D8", "Unattributed attribution",
     r"\b(it is (widely|generally) (believed|accepted|assumed)|experts (argue|believe|say)"
     r"|some researchers (suggest|argue)|studies have shown)\b(?![^.;]{0,30}(\\cite|\[))",
     "add the citation already present in the source, or restate as your own claim"),
]
ZH_CONNECTIVES = ("此外", "另外", "同时", "与此同时", "进一步地", "更重要的是",
                  "不仅如此", "除此之外", "值得注意的是", "首先", "其次", "最后",
                  "总之", "因此", "所以", "然而", "但是")
EN_CONNECTIVES = ("moreover", "furthermore", "additionally", "in addition", "also",
                  "in particular", "consequently", "therefore", "thus", "however",
                  "nevertheless", "nonetheless", "overall", "notably", "importantly")

# Lines/blocks to skip entirely when scanning LaTeX.
TEX_SKIP_ENV = re.compile(
    r"\\begin\{(equation|align|gather|multline|eqnarray|array|matrix|tabular|table"
    r"|figure|lstlisting|verbatim|tikzpicture|algorithm|algorithmic)\*?\}")
TEX_END_ENV = re.compile(
    r"\\end\{(equation|align|gather|multline|eqnarray|array|matrix|tabular|table"
    r"|figure|lstlisting|verbatim|tikzpicture|algorithm|algorithmic)\*?\}")


def strip_tex(line: str) -> str:
    """Blank out TeX comments, math, command names and cite/ref keys."""
    line = re.sub(r"(?<!\\)%.*$", "", line)
    line = re.sub(r"\$\$.*?\$\$", " ", line)
    line = re.sub(r"(?<!\\)\$[^$]*\$", " ", line)
    line = re.sub(r"\\\[[^\]]*\\\]|\\\([^)]*\\\)", " ", line)
    # citation / reference / label keys carry no prose
    line = re.sub(r"\\(cite[a-zA-Z]*|ref|eqref|label|autoref|url|bibliography"
                  r"|includegraphics|input|include)\s*(\[[^\]]*\])?\{[^}]*\}", " ", line)
    # remaining command names: keep braces content, drop the backslash token
    line = re.sub(r"\\[a-zA-Z@]+\*?", " ", line)
    return line


def split_sentences(text: str, lang: str) -> list[str]:
    if lang == "zh":
        parts = re.split(r"(?<=[。！？；!?])\s*", text)
    else:
        parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\[])", text)
    return [p.strip() for p in parts if p.strip()]


def sent_len(sentence: str, lang: str) -> int:
    if lang == "zh":
        return len(CJK_RE.findall(sentence)) or len(sentence)
    return len(re.findall(r"[A-Za-z][A-Za-z'\-]*", sentence))


def detect_lang(text: str) -> str:
    cjk = len(CJK_RE.findall(text))
    latin = len(re.findall(r"[A-Za-z]", text))
    return "zh" if cjk * 3 >= latin else "en"


def parse_range(spec: str | None, total: int) -> tuple[int, int]:
    if not spec:
        return 1, total
    m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", spec.strip())
    if not m:
        sys.exit("--lines expects START-END, e.g. 120-260")
    lo, hi = int(m.group(1)), int(m.group(2))
    return max(1, lo), min(total, hi)
def compile_patterns(lang: str):
    sets = []
    if lang in ("zh", "both"):
        sets += [(c, "zh", cat, re.compile(p), h) for c, cat, p, h in ZH_PATTERNS]
    if lang in ("en", "both"):
        sets += [(c, "en", cat, re.compile(p, re.IGNORECASE), h) for c, cat, p, h in EN_PATTERNS]
    return sets


def scan_lines(lines: list[str], lang: str, is_tex: bool, lo: int, hi: int):
    """Return (hits, prose_text). hits: list of dicts."""
    patterns = compile_patterns(lang)
    hits: list[dict] = []
    prose: list[str] = []
    in_skip = False

    for idx, raw in enumerate(lines, start=1):
        if is_tex:
            if in_skip:
                if TEX_END_ENV.search(raw):
                    in_skip = False
                continue
            if TEX_SKIP_ENV.search(raw):
                in_skip = not bool(TEX_END_ENV.search(raw))
                continue
            text = strip_tex(raw)
        else:
            text = raw

        if not (lo <= idx <= hi):
            continue
        if not text.strip():
            continue
        prose.append(text.strip())

        for code, plang, cat, rx, hint in patterns:
            for m in rx.finditer(text):
                frag = m.group(0).strip()
                if not frag:
                    continue
                start = max(0, m.start() - 24)
                end = min(len(text), m.end() + 24)
                hits.append({
                    "line": idx, "code": code, "lang": plang, "cat": cat,
                    "match": frag, "context": text[start:end].strip(), "hint": hint,
                })
    return hits, "\n".join(prose)


def split_by_language(prose: str) -> dict[str, str]:
    """Partition prose lines into zh / en buckets so stats use the right rules."""
    buckets: dict[str, list[str]] = {"zh": [], "en": []}
    for line in prose.splitlines():
        if not line.strip():
            continue
        buckets[detect_lang(line)].append(line)
    return {k: "\n".join(v) for k, v in buckets.items() if v}


def sentence_stats(prose: str, lang: str) -> dict:
    sentences = split_sentences(prose, lang)
    lengths = [sent_len(s, lang) for s in sentences]
    lengths = [n for n in lengths if n > 0]
    long_limit = 60 if lang == "zh" else 30
    stats = {
        "n_sent": len(lengths),
        "long_limit": long_limit,
        "long": [(s, n) for s, n in zip(sentences, lengths) if n > long_limit],
        "mean": round(statistics.mean(lengths), 1) if lengths else 0.0,
        "cv": 0.0,
    }
    if len(lengths) > 1 and stats["mean"]:
        stats["cv"] = round(statistics.pstdev(lengths) / stats["mean"], 2)

    connectives = ZH_CONNECTIVES if lang == "zh" else EN_CONNECTIVES
    runs, cur = [], 0
    for s in sentences:
        head = s.lstrip("“\"'（([")
        if lang == "zh":
            opened = head.startswith(connectives)
        else:
            opened = head.lower().startswith(connectives)
        if opened:
            cur += 1
        else:
            if cur >= 2:
                runs.append(cur)
            cur = 0
    if cur >= 2:
        runs.append(cur)
    stats["connective_runs"] = runs
    stats["connective_rate"] = (
        round(sum(1 for s in sentences
                  if (s.lstrip("“\"'（([").lower() if lang == "en"
                      else s.lstrip("“\"'（([")).startswith(
                      tuple(c.lower() for c in connectives) if lang == "en" else connectives)
                  ) / len(sentences), 2) if sentences else 0.0)
    return stats
def group_by_code(hits: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for h in hits:
        out.setdefault(f"{h['lang']}/{h['code']} {h['cat']}", []).append(h)
    return dict(sorted(out.items(), key=lambda kv: (-len(kv[1]), kv[0])))


def truncate(s: str, n: int = 70) -> str:
    s = re.sub(r"\s+", " ", s)
    return s if len(s) <= n else s[: n - 1] + "…"


def report_md(path: Path, hits: list[dict], stats_by_lang: dict[str, dict], lang: str) -> str:
    out = [f"# 扫描报告 / Scan report: `{path.name}`", ""]
    out.append(f"- 语言 / language: **{lang}**")
    out.append(f"- 命中总数 / total hits: **{len(hits)}**")
    for lg, st in stats_by_lang.items():
        out.append(f"- [{lg}] 句数 / sentences: {st['n_sent']}，平均句长 / mean: {st['mean']}，"
                   f"句长变异系数 / CV: {st['cv']}（< 0.35 偏均匀，考虑拆分与合并），"
                   f"句首连接词比例 / connectives: {st['connective_rate']}"
                   + (f"，连续段 / runs: {st['connective_runs']}" if st["connective_runs"] else ""))
    out.append("")

    if not hits:
        out.append("未命中词句类模式。仍需人工检查段落结构、论断—证据匹配和同指异名。")
        out.append("No lexical hits. Still check paragraph templating, claim-evidence match, and elegant variation manually.")
    else:
        out.append("## 按类别 / By category")
        out.append("")
        out.append("| 类别 Category | 次数 n | 处理建议 Hint |")
        out.append("|---|---|---|")
        for key, group in group_by_code(hits).items():
            out.append(f"| {key} | {len(group)} | {group[0]['hint']} |")
        out.append("")
        out.append("## 逐条 / Line by line")
        out.append("")
        out.append("| 行 Line | 类别 | 命中 Match | 上下文 Context |")
        out.append("|---|---|---|---|")
        for h in sorted(hits, key=lambda x: (x["line"], x["code"])):
            out.append(f"| {h['line']} | {h['lang']}/{h['code']} {h['cat']} | "
                       f"`{truncate(h['match'], 36)}` | {truncate(h['context'])} |")
        out.append("")

    long_all = [(lg, s, n) for lg, st in stats_by_lang.items() for s, n in st["long"]]
    if long_all:
        limits = "，".join(f"{lg} > {st['long_limit']}" for lg, st in stats_by_lang.items())
        out.append(f"## 过长句 / Long sentences ({limits})")
        out.append("")
        for lg, s, n in long_all[:25]:
            out.append(f"- [{lg}] ({n}) {truncate(s, 110)}")
        if len(long_all) > 25:
            out.append(f"- …其余 {len(long_all) - 25} 句 / {len(long_all) - 25} more")
        out.append("")

    out.append("---")
    out.append("命中均为**候选项**，须结合上下文判断：带统计检验的 “显著”/\"significant\"、"
               "表达真实不确定性的 “可能”/\"may\" 都应保留。")
    out.append("Hits are **candidates**. Keep \"significant\" when a test is reported and "
               "\"may\" when the uncertainty is real.")
    return "\n".join(out)


def report_text(path: Path, hits: list[dict], stats_by_lang: dict[str, dict], lang: str) -> str:
    out = [f"{path.name}  lang={lang}  hits={len(hits)}"]
    for lg, st in stats_by_lang.items():
        out.append(f"  [{lg}] sent={st['n_sent']} mean={st['mean']} cv={st['cv']} "
                   f"conn={st['connective_rate']} runs={st['connective_runs']}")
    for h in sorted(hits, key=lambda x: (x["line"], x["code"])):
        out.append(f"{h['line']:>5}  {h['lang']}/{h['code']:<4} {h['cat']:<12} "
                   f"{truncate(h['match'], 34):<36} | {truncate(h['context'], 60)}")
    for lg, st in stats_by_lang.items():
        for s, n in st["long"]:
            out.append(f"{'':>5}  LONG[{lg}]({n}) {truncate(s, 100)}")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Scan academic prose for AI-tell and defensive-hedging patterns (zh+en).")
    ap.add_argument("file", type=Path)
    ap.add_argument("--lang", choices=["auto", "zh", "en", "both"], default="auto")
    ap.add_argument("--lines", help="limit to a line range, e.g. 120-260")
    ap.add_argument("--format", choices=["md", "text"], default="md")
    args = ap.parse_args()

    # Windows consoles default to a legacy code page; force UTF-8 so Chinese
    # patterns and hints are readable.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    if not args.file.is_file():
        sys.exit(f"not a file: {args.file}")
    raw = args.file.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()
    lo, hi = parse_range(args.lines, len(lines))

    lang = detect_lang(raw) if args.lang == "auto" else args.lang
    is_tex = args.file.suffix.lower() in (".tex", ".sty", ".cls")

    # Always run both pattern sets: mixed-language manuscripts are common.
    hits, prose = scan_lines(lines, "both", is_tex, lo, hi)
    stats_by_lang = {lg: sentence_stats(text, lg)
                     for lg, text in split_by_language(prose).items()}
    if not stats_by_lang:
        stats_by_lang = {lang: sentence_stats("", lang)}

    render = report_md if args.format == "md" else report_text
    sys.stdout.write(render(args.file, hits, stats_by_lang, lang) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
