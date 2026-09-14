// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "arithmetic mean (of times)",
"html": "Dominated by the slowest instance; one instance's number.",
"section": "Summaries",
"slide": "Arithmetic, geometric, shifted geometric",
"keys": [
"arithmetic mean (of times)",
"arithmetic mean",
"of times"
]
},
{
"term_html": "geometric mean",
"html": "\\(\\exp(\\frac1n \\sum_i \\log t_i)\\). Treats equal ratios equally, which is what comparisons are about.",
"section": "Summaries",
"slide": "Arithmetic, geometric, shifted geometric",
"keys": [
"geometric mean"
]
},
{
"term_html": "shifted geometric mean (SGM)",
"html": "\\(\\mathrm{SGM}_s(t) = \\exp(\\frac1n \\sum_i \\log(t_i + s)) - s\\). The shift \\(s\\) keeps trivial instances from dominating; 10 s is the MIP convention, and the shift should match the scale of the runs.",
"section": "Summaries",
"slide": "Arithmetic, geometric, shifted geometric",
"keys": [
"shifted geometric mean (sgm)",
"shifted geometric mean",
"sgm"
]
},
{
"term_html": "timeout (censored run)",
"html": "An unsolved run, whose time is only a lower bound.",
"section": "Summaries",
"slide": "Arithmetic, geometric, shifted geometric",
"keys": [
"timeout (censored run)",
"timeout",
"censored run"
]
},
{
"term_html": "censoring",
"html": "Observations cut off at a limit. A mean of capped counts describes the cap as much as the solver.",
"section": "Summaries",
"slide": "Arithmetic, geometric, shifted geometric",
"keys": [
"censoring"
]
},
{
"term_html": "PAR-\\(k\\)",
"html": "Penalized average runtime: count each timeout as \\(k\\) times the limit. Depends on the limit and \\(k\\); report both, and the solved count separately.",
"section": "Summaries",
"slide": "Arithmetic, geometric, shifted geometric",
"keys": [
"par-k"
]
},
{
"term_html": "run store",
"html": "Storing every individual run (solver, instance, seed, time, status) rather than summaries, so analysis can be redone without re-solving. The lab uses SQLite.",
"section": "Summaries",
"slide": "Arithmetic, geometric, shifted geometric",
"keys": [
"run store"
]
},
{
"term_html": "resumable runner",
"html": "A benchmark runner that skips runs already stored and records timeouts as such.",
"section": "Summaries",
"slide": "Arithmetic, geometric, shifted geometric",
"keys": [
"resumable runner"
]
},
{
"term_html": "performance ratio \\(r_{p,s}\\)",
"html": "\\(t_{p,s} / \\min_{s'} t_{p,s'}\\) for problem \\(p\\) and solver \\(s\\), or \\(\\infty\\) if \\(s\\) failed.",
"section": "Pictures",
"slide": "Performance profiles (Dolan & Moré 2002)",
"keys": [
"performance ratio r_{p,s}"
]
},
{
"term_html": "performance profile",
"html": "\\(\\rho_s(\\tau)\\), the fraction of problems on which solver \\(s\\) is within a factor \\(\\tau\\) of the best. \\(\\rho_s(1)\\) is its win share; large \\(\\tau\\) gives its solved share.",
"section": "Pictures",
"slide": "Performance profiles (Dolan & Moré 2002)",
"keys": [
"performance profile"
]
},
{
"term_html": "profile reordering trap",
"html": "Ratios are to the best solver present, so adding or removing a solver can reorder the others (Gould &amp; Scott 2016). Compare two at a time for two-way claims.",
"section": "Pictures",
"slide": "Performance profiles (Dolan & Moré 2002)",
"keys": [
"profile reordering trap"
]
},
{
"term_html": "virtual best solver (VBS)",
"html": "Per problem, the fastest solver's time. The ceiling for any portfolio of those solvers.",
"section": "Pictures",
"slide": "Performance profiles (Dolan & Moré 2002)",
"keys": [
"virtual best solver (vbs)",
"virtual best solver",
"vbs"
]
},
{
"term_html": "time-to-target plot",
"html": "The per-instance, over-seeds counterpart of a profile (unit 26).",
"section": "Pictures",
"slide": "Performance profiles (Dolan & Moré 2002)",
"keys": [
"time-to-target plot"
]
},
{
"term_html": "unit of observation",
"html": "What one data point is; here an (instance, seed) pair.",
"section": "Inference",
"slide": "Seeds, pairing, intervals, and many tests",
"keys": [
"unit of observation"
]
},
{
"term_html": "paired comparison",
"html": "Analysing per-instance log ratios of two solvers on the same instances, removing the large between-instance variance.",
"section": "Inference",
"slide": "Seeds, pairing, intervals, and many tests",
"keys": [
"paired comparison"
]
},
{
"term_html": "paired geometric ratio",
"html": "\\(\\exp(\\frac1n \\sum_i \\log \\frac{a_i + s}{b_i + s})\\), the typical factor by which solver \\(a\\) differs from \\(b\\).",
"section": "Inference",
"slide": "Seeds, pairing, intervals, and many tests",
"keys": [
"paired geometric ratio"
]
},
{
"term_html": "bootstrap",
"html": "Resampling the observations with replacement and recomputing the summary each time, to see how much it would move.",
"section": "Inference",
"slide": "Seeds, pairing, intervals, and many tests",
"keys": [
"bootstrap"
]
},
{
"term_html": "percentile bootstrap interval",
"html": "The middle 95% of the bootstrap summaries: an interval with no normality assumption.",
"section": "Inference",
"slide": "Seeds, pairing, intervals, and many tests",
"keys": [
"percentile bootstrap interval"
]
},
{
"term_html": "confidence interval",
"html": "A range for an effect size; answers \"how big\".",
"section": "Inference",
"slide": "Seeds, pairing, intervals, and many tests",
"keys": [
"confidence interval"
]
},
{
"term_html": "effect size",
"html": "How large a difference is, as opposed to whether one exists.",
"section": "Inference",
"slide": "Seeds, pairing, intervals, and many tests",
"keys": [
"effect size"
]
},
{
"term_html": "Wilcoxon signed-rank test",
"html": "A paired, rank-based test of whether differences tend to be positive; answers \"is there a difference\".",
"section": "Inference",
"slide": "Seeds, pairing, intervals, and many tests",
"keys": [
"wilcoxon signed-rank test"
]
},
{
"term_html": "p-value",
"html": "The probability of data at least this extreme if there were no difference.",
"section": "Inference",
"slide": "Seeds, pairing, intervals, and many tests",
"keys": [
"p-value"
]
},
{
"term_html": "multiple comparisons problem",
"html": "Each extra test adds a chance of a false positive: three at \\(\\alpha = 0.05\\) give about 14%.",
"section": "Inference",
"slide": "Seeds, pairing, intervals, and many tests",
"keys": [
"multiple comparisons problem"
]
},
{
"term_html": "Holm–Bonferroni correction",
"html": "Sort the \\(m\\) p-values, multiply the \\(k\\)-th smallest by \\(m - k + 1\\), and keep the adjusted values monotone. Uniformly more powerful than Bonferroni.",
"section": "Inference",
"slide": "Seeds, pairing, intervals, and many tests",
"keys": [
"holm–bonferroni correction"
]
},
{
"term_html": "Bonferroni correction",
"html": "Multiply every p-value by the number of tests.",
"section": "Inference",
"slide": "Seeds, pairing, intervals, and many tests",
"keys": [
"bonferroni correction"
]
},
{
"term_html": "instance selection bias",
"html": "Choosing or dropping instances after seeing results, or letting one family stand for a problem. Fix the set before running.",
"section": "Inference",
"slide": "Instance selection, per-instance claims, negative results",
"keys": [
"instance selection bias"
]
},
{
"term_html": "aggregate vs per-instance claim",
"html": "\"Faster on average\" versus \"faster on most instances\"; different claims, and both can be reported.",
"section": "Inference",
"slide": "Instance selection, per-instance claims, negative results",
"keys": [
"aggregate vs per-instance claim"
]
},
{
"term_html": "negative result",
"html": "A stated hypothesis, instances, budget and effect size with its interval, showing what was ruled out.",
"section": "Inference",
"slide": "Instance selection, per-instance claims, negative results",
"keys": [
"negative result"
]
},
{
"term_html": "audit",
"html": "Re-running an earlier conclusion with stored runs, more instances, intervals and corrected tests.",
"section": "The audit",
"slide": "Unit 07: branching rules, from 3 instances to 24",
"keys": [
"audit"
]
},
{
"term_html": "regenerable claim",
"html": "A performance claim that one command reproduces from stored runs. The checkpoint.",
"section": "The audit",
"slide": "Unit 07: branching rules, from 3 instances to 24",
"keys": [
"regenerable claim"
]
},
{
"term_html": "withdrawn claim",
"html": "A conclusion that did not survive, corrected in place: unit 19's \"restarts make the median worse\".",
"section": "The audit",
"slide": "Unit 19: restarts, with intervals and eight more instances",
"keys": [
"withdrawn claim"
]
}
];
