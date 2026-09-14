// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "variable ordering",
"html": "The rule for which variable to branch on next.",
"section": "Heuristics",
"slide": "Variable and value ordering",
"keys": [
"variable ordering"
]
},
{
"term_html": "value ordering",
"html": "The rule for which value to try first. Matters only in satisfiable subtrees; for a proof every value is tried.",
"section": "Heuristics",
"slide": "Variable and value ordering",
"keys": [
"value ordering"
]
},
{
"term_html": "fail first",
"html": "Branch where a dead end is most likely, so it is found near the root (Haralick &amp; Elliott 1980).",
"section": "Heuristics",
"slide": "Variable and value ordering",
"keys": [
"fail first"
]
},
{
"term_html": "succeed first",
"html": "Try the value most likely to lead to a solution.",
"section": "Heuristics",
"slide": "Variable and value ordering",
"keys": [
"succeed first"
]
},
{
"term_html": "first-fail",
"html": "Smallest domain first.",
"section": "Heuristics",
"slide": "Variable and value ordering",
"keys": [
"first-fail"
]
},
{
"term_html": "randomised first-fail",
"html": "First-fail with ties broken at random; the source of run-to-run variation in the lab.",
"section": "Heuristics",
"slide": "Variable and value ordering",
"keys": [
"randomised first-fail"
]
},
{
"term_html": "dom/deg",
"html": "Domain size divided by the variable's number of constraints.",
"section": "Heuristics",
"slide": "Variable and value ordering",
"keys": [
"dom/deg"
]
},
{
"term_html": "dom/wdeg",
"html": "Domain size divided by weighted degree, where each constraint's weight counts how often it failed. Draws search to the hard core (Boussemart et al. 2004).",
"section": "Heuristics",
"slide": "Variable and value ordering",
"keys": [
"dom/wdeg"
]
},
{
"term_html": "hard core",
"html": "The small part of a problem responsible for its difficulty, such as the \\(\\ne\\) clique hidden in the lab's chain instance.",
"section": "Heuristics",
"slide": "Variable and value ordering",
"keys": [
"hard core"
]
},
{
"term_html": "impact-based search",
"html": "Prefer variables whose assignments shrank the search space most in the past (Refalo 2004).",
"section": "Heuristics",
"slide": "Variable and value ordering",
"keys": [
"impact-based search"
]
},
{
"term_html": "activity-based search",
"html": "Prefer variables whose domains change most often; a VSIDS-like count (Michel &amp; Van Hentenryck 2012).",
"section": "Heuristics",
"slide": "Variable and value ordering",
"keys": [
"activity-based search"
]
},
{
"term_html": "symmetry breaking during search (SBDS, SBDD)",
"html": "After a failed branch, excluding its symmetric images, instead of adding ordering constraints to the model.",
"section": "Heuristics",
"slide": "Variable and value ordering",
"keys": [
"symmetry breaking during search (sbds, sbdd)",
"symmetry breaking during search",
"sbds, sbdd"
]
},
{
"term_html": "heuristics as bets",
"html": "A heuristic wins on some instance families and loses on others: dom/wdeg beats first-fail on a hidden core and loses on QCP.",
"section": "Heuristics",
"slide": "Variable and value ordering",
"keys": [
"heuristics as bets"
]
},
{
"term_html": "quasigroup completion (QCP)",
"html": "Filling a partial Latin square so each row and column has every symbol once. The lab's benchmark.",
"section": "Heavy tails",
"slide": "The runtime distribution of one instance",
"keys": [
"quasigroup completion (qcp)",
"quasigroup completion",
"qcp"
]
},
{
"term_html": "runtime distribution",
"html": "The distribution of search effort on one instance across random seeds.",
"section": "Heavy tails",
"slide": "The runtime distribution of one instance",
"keys": [
"runtime distribution"
]
},
{
"term_html": "heavy tail",
"html": "\\(P(T &gt; t) \\sim C t^{-\\alpha}\\): a Pareto-like tail. With \\(\\alpha &lt; 1\\) the mean is infinite in the limit (Gomes et al. 2000).",
"section": "Heavy tails",
"slide": "The runtime distribution of one instance",
"keys": [
"heavy tail"
]
},
{
"term_html": "Pareto (power-law) tail",
"html": "A straight line of slope \\(-\\alpha\\) on a log–log plot of \\(P(T &gt; t)\\), unlike an exponential tail, which curves down.",
"section": "Heavy tails",
"slide": "The runtime distribution of one instance",
"keys": [
"pareto (power-law) tail"
]
},
{
"term_html": "early mistake",
"html": "A wrong decision near the root that leaves an exponentially large solution-free subtree to exhaust. The cause of heavy tails.",
"section": "Heavy tails",
"slide": "The runtime distribution of one instance",
"keys": [
"early mistake"
]
},
{
"term_html": "median, p90",
"html": "The 50th and 90th percentiles of a runtime sample: robust summaries where the mean is not.",
"section": "Heavy tails",
"slide": "The runtime distribution of one instance",
"keys": [
"median, p90",
"median",
"p90"
]
},
{
"term_html": "restart",
"html": "Abandoning the current search tree and starting again, keeping some learned state.",
"section": "Restarts and nogoods",
"slide": "Luby's universal schedule",
"keys": [
"restart"
]
},
{
"term_html": "cutoff",
"html": "The node budget after which a run restarts.",
"section": "Restarts and nogoods",
"slide": "Luby's universal schedule",
"keys": [
"cutoff"
]
},
{
"term_html": "Las Vegas algorithm",
"html": "A randomized algorithm that is always correct but has a random running time.",
"section": "Restarts and nogoods",
"slide": "Luby's universal schedule",
"keys": [
"las vegas algorithm"
]
},
{
"term_html": "Luby sequence",
"html": "\\(1, 1, 2, 1, 1, 2, 4, 1, 1, 2, \\dots\\). Cutoffs \\(c \\cdot \\text{luby}(i)\\) are within a log factor of the best fixed cutoff for any unknown distribution (Luby, Sinclair &amp; Zuckerman 1993).",
"section": "Restarts and nogoods",
"slide": "Luby's universal schedule",
"keys": [
"luby sequence"
]
},
{
"term_html": "geometric restarts",
"html": "Cutoffs \\(c \\cdot r^i\\).",
"section": "Restarts and nogoods",
"slide": "Luby's universal schedule",
"keys": [
"geometric restarts"
]
},
{
"term_html": "adaptive restarts",
"html": "Restarting when recent conflicts look worse than average (Audemard &amp; Simon 2012).",
"section": "Restarts and nogoods",
"slide": "Luby's universal schedule",
"keys": [
"adaptive restarts"
]
},
{
"term_html": "restarts hurt without a tail",
"html": "On an instance whose runtimes cluster, restarting only throws away progress; the lab's light instance doubled its mean.",
"section": "Restarts and nogoods",
"slide": "Luby's universal schedule",
"keys": [
"restarts hurt without a tail"
]
},
{
"term_html": "nogood",
"html": "A set of decisions proved to have no solution below it, recorded as a constraint so search never re-enters it.",
"section": "Restarts and nogoods",
"slide": "What to remember across restarts",
"keys": [
"nogood"
]
},
{
"term_html": "decision nogood",
"html": "A nogood naming only decisions. Weak compared with one that records the reasons for failure: clause learning (unit 20).",
"section": "Restarts and nogoods",
"slide": "What to remember across restarts",
"keys": [
"decision nogood"
]
},
{
"term_html": "nogoods from restarts",
"html": "Nogoods extracted from the refuted branches of the tree at each restart (Lecoutre et al. 2007).",
"section": "Restarts and nogoods",
"slide": "What to remember across restarts",
"keys": [
"nogoods from restarts"
]
},
{
"term_html": "large neighbourhood search (LNS)",
"html": "Repeatedly destroy part of a solution and repair it with an exact search engine under a small budget, keeping improvements (Shaw 1998).",
"section": "Large neighbourhood search",
"slide": "Destroy and repair",
"keys": [
"large neighbourhood search (lns)",
"large neighbourhood search",
"lns"
]
},
{
"term_html": "destroy operator",
"html": "The rule for which part to free, such as a random 30% of the jobs.",
"section": "Large neighbourhood search",
"slide": "Destroy and repair",
"keys": [
"destroy operator"
]
},
{
"term_html": "repair",
"html": "Searching the freed part with full propagation and \"objective &lt; best\".",
"section": "Large neighbourhood search",
"slide": "Destroy and repair",
"keys": [
"repair"
]
},
{
"term_html": "neighbourhood",
"html": "The set of solutions reachable by one destroy-and-repair step. Exponentially large, but explored by propagation rather than enumeration.",
"section": "Large neighbourhood search",
"slide": "Destroy and repair",
"keys": [
"neighbourhood"
]
},
{
"term_html": "related destroy",
"html": "Freeing parts that interact, such as jobs sharing machines near the critical path. Usually beats random destroy.",
"section": "Large neighbourhood search",
"slide": "Destroy and repair",
"keys": [
"related destroy"
]
},
{
"term_html": "ALNS",
"html": "Adaptive LNS, choosing among destroy operators by their past success (Ropke &amp; Pisinger 2006).",
"section": "Large neighbourhood search",
"slide": "Destroy and repair",
"keys": [
"alns"
]
},
{
"term_html": "greedy dispatch",
"html": "The lab's starting schedule: place operations one at a time by a simple rule.",
"section": "Large neighbourhood search",
"slide": "Destroy and repair",
"keys": [
"greedy dispatch"
]
},
{
"term_html": "makespan",
"html": "The finishing time of the last operation in a schedule.",
"section": "Large neighbourhood search",
"slide": "Destroy and repair",
"keys": [
"makespan"
]
},
{
"term_html": "critical path",
"html": "The chain of operations that determines the makespan.",
"section": "Large neighbourhood search",
"slide": "Destroy and repair",
"keys": [
"critical path"
]
},
{
"term_html": "portfolio",
"html": "Several workers with different strategies running in parallel and sharing one incumbent, as CP-SAT does.",
"section": "Large neighbourhood search",
"slide": "In the tools",
"keys": [
"portfolio"
]
},
{
"term_html": "guided local search",
"html": "OR-Tools routing's metaheuristic: local search that penalizes features of local optima to escape them.",
"section": "Large neighbourhood search",
"slide": "In the tools",
"keys": [
"guided local search"
]
}
];
