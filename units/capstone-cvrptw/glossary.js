// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "VRPTW",
"html": "Vehicle routing with time windows: serve every customer once from a depot with identical vehicles of capacity \\(Q\\), starting each service inside its window, minimizing total distance.",
"section": "The problem",
"slide": "VRPTW",
"keys": [
"vrptw"
]
},
{
"term_html": "time window \\([a_i, b_i]\\)",
"html": "The interval in which service at customer \\(i\\) must start. Arriving early means waiting, which is free.",
"section": "The problem",
"slide": "VRPTW",
"keys": [
"time window [a_i, b_i]"
]
},
{
"term_html": "service time \\(s_i\\)",
"html": "How long service at customer \\(i\\) takes.",
"section": "The problem",
"slide": "VRPTW",
"keys": [
"service time s_i"
]
},
{
"term_html": "horizon",
"html": "The depot's window \\([a_0, b_0]\\): vehicles leave no earlier than \\(a_0\\) and return by \\(b_0\\).",
"section": "The problem",
"slide": "VRPTW",
"keys": [
"horizon"
]
},
{
"term_html": "start-time recurrence",
"html": "\\(t_j = \\max(a_j,\\ t_i + s_i + d_{ij}) \\le b_j\\) along a route; the entire time-window model.",
"section": "The problem",
"slide": "VRPTW",
"keys": [
"start-time recurrence"
]
},
{
"term_html": "Solomon instances",
"html": "The standard VRPTW benchmark (1987): 56 instances of 100 customers in series C (clustered), R (random) and RC (mixed); series 1 has short horizons and tight windows, series 2 long horizons and wide windows.",
"section": "The problem",
"slide": "VRPTW",
"keys": [
"solomon instances"
]
},
{
"term_html": "R101.25",
"html": "Naming convention: instance R101 truncated to its first 25 customers.",
"section": "The problem",
"slide": "VRPTW",
"keys": [
"r101.25"
]
},
{
"term_html": "hierarchical objective",
"html": "Minimize vehicles first, then distance; the convention of the heuristic best-known tables.",
"section": "The problem",
"slide": "Two objectives, and why the numbers are in tenths",
"keys": [
"hierarchical objective"
]
},
{
"term_html": "distance-only objective",
"html": "Minimize distance alone, with distances truncated to one decimal and stored as integer tenths. The exact literature's convention, and the lab's. Not comparable with hierarchical results.",
"section": "The problem",
"slide": "Two objectives, and why the numbers are in tenths",
"keys": [
"distance-only objective"
]
},
{
"term_html": "arc MIP",
"html": "Binary arc variables, start-time variables, and big-M time constraints \\(t_j \\ge t_i + s_i + d_{ij} - M_{ij}(1 - x_{ij})\\) with the smallest valid \\(M_{ij}\\). The time constraints rule out subtours but not overloads.",
"section": "Four models of one problem",
"slide": "A compact model whose capacity lives in your cuts",
"keys": [
"arc mip"
]
},
{
"term_html": "\\(\\delta^+(i)\\), \\(\\delta^-(i)\\)",
"html": "The arcs leaving and entering \\(i\\) or a set.",
"section": "Four models of one problem",
"slide": "A compact model whose capacity lives in your cuts",
"keys": [
"\\delta^+(i), \\delta^-(i)",
"\\delta^+(i)",
"\\delta^-(i)"
]
},
{
"term_html": "rounded capacity inequality",
"html": "\\(x(\\delta^-(S)) \\ge \\lceil q(S)/Q \\rceil\\) for every customer set \\(S\\): at least that many vehicles must enter it. With the right side 1 it is unit 09's subtour constraint.",
"section": "Four models of one problem",
"slide": "A compact model whose capacity lives in your cuts",
"keys": [
"rounded capacity inequality"
]
},
{
"term_html": "connected-components separation",
"html": "Checking each component of the support graph as a candidate \\(S\\). Exact on integer points, heuristic on fractional ones.",
"section": "Four models of one problem",
"slide": "A compact model whose capacity lives in your cuts",
"keys": [
"connected-components separation"
]
},
{
"term_html": "CVRPSEP",
"html": "The standard code for separating capacity cuts heuristically.",
"section": "Four models of one problem",
"slide": "A compact model whose capacity lives in your cuts",
"keys": [
"cvrpsep"
]
},
{
"term_html": "constraint handler",
"html": "SCIP's plugin for lazy constraints; the lab supplies <code>separate(values)</code> and <code>colib.vrptw.lazy_cut_handler</code> the plumbing.",
"section": "Four models of one problem",
"slide": "A compact model whose capacity lives in your cuts",
"keys": [
"constraint handler"
]
},
{
"term_html": "route set partitioning",
"html": "\\(\\min \\sum_r c_r \\lambda_r\\) with every customer covered exactly once; \\(= 1\\), not \\(\\ge 1\\), because truncated distances can break the triangle inequality.",
"section": "Four models of one problem",
"slide": "Routes as columns, found by labelling",
"keys": [
"route set partitioning"
]
},
{
"term_html": "label",
"html": "A partial route at a vertex: reduced cost, load, start time, unreachable set, route.",
"section": "Four models of one problem",
"slide": "Routes as columns, found by labelling",
"keys": [
"label"
]
},
{
"term_html": "unreachable set (Feillet)",
"html": "Customers already visited or no longer reachable within the windows, counted together so dominance fires more often (Feillet et al. 2004).",
"section": "Four models of one problem",
"slide": "Routes as columns, found by labelling",
"keys": [
"unreachable set (feillet)",
"unreachable set",
"feillet"
]
},
{
"term_html": "dominance (VRPTW labels)",
"html": "\\(L\\) dominates \\(L'\\) if it is no worse in cost, load and time and its unreachable set is a subset of \\(L'\\)'s.",
"section": "Four models of one problem",
"slide": "Routes as columns, found by labelling",
"keys": [
"dominance (vrptw labels)",
"dominance",
"vrptw labels"
]
},
{
"term_html": "heuristic pricing pass",
"html": "Labelling with a cap on labels per vertex, used until it fails; only the final pass must be exact.",
"section": "Four models of one problem",
"slide": "Routes as columns, found by labelling",
"keys": [
"heuristic pricing pass"
]
},
{
"term_html": "arc branching",
"html": "Branching on an arc's total flow \\(\\sum_r [ij \\in r] \\lambda_r\\): forbid the arc, or force it by forbidding its alternatives.",
"section": "Four models of one problem",
"slide": "Routes as columns, found by labelling",
"keys": [
"arc branching"
]
},
{
"term_html": "multiple-circuit constraint",
"html": "CP-SAT's constraint that arc literals form circuits through a depot visited by many and every other vertex on exactly one. Replaces degree constraints and subtour elimination.",
"section": "Four models of one problem",
"slide": "A circuit constraint, enforced implications, and a strategy",
"keys": [
"multiple-circuit constraint"
]
},
{
"term_html": "enforced implication",
"html": "A constraint active only when a literal is true (<code>only_enforce_if</code>), propagated directly instead of through big-M.",
"section": "Four models of one problem",
"slide": "A circuit constraint, enforced implications, and a strategy",
"keys": [
"enforced implication"
]
},
{
"term_html": "decision strategy",
"html": "A branching order given to CP-SAT, such as short arcs first; followed with one worker only under <code>FIXED_SEARCH</code>.",
"section": "Four models of one problem",
"slide": "A circuit constraint, enforced implications, and a strategy",
"keys": [
"decision strategy"
]
},
{
"term_html": "latest start \\(\\ell_k\\)",
"html": "\\(\\min(b_k,\\ \\ell_{k+1} - s_k - d_{k,k+1})\\), the latest service start at \\(k\\) that keeps the rest of the route feasible.",
"section": "Four models of one problem",
"slide": "Feasible insertion in constant time",
"keys": [
"latest start \\ell_k"
]
},
{
"term_html": "constant-time feasible insertion",
"html": "Checking that inserting \\(c\\) between \\(p\\) and \\(q\\) meets \\(c\\)'s window and starts \\(q\\) by \\(\\ell_q\\), plus load, without rescheduling the rest (Savelsbergh 1992).",
"section": "Four models of one problem",
"slide": "Feasible insertion in constant time",
"keys": [
"constant-time feasible insertion"
]
},
{
"term_html": "Shaw removal",
"html": "Destroying customers related in space, time and demand.",
"section": "Four models of one problem",
"slide": "Feasible insertion in constant time",
"keys": [
"shaw removal"
]
},
{
"term_html": "regret-\\(k\\) repair",
"html": "Inserting first the customer with most to lose, \\(\\sum_{h=2}^{k}(\\text{cost}_h - \\text{cost}_1)\\) over its best positions.",
"section": "Four models of one problem",
"slide": "Feasible insertion in constant time",
"keys": [
"regret-k repair"
]
},
{
"term_html": "new-route option",
"html": "Allowing repair to open a route; without it ALNS cannot increase the route count and gets stuck.",
"section": "Four models of one problem",
"slide": "Feasible insertion in constant time",
"keys": [
"new-route option"
]
},
{
"term_html": "referee",
"html": "The harness that re-checks every solution, recomputes every cost and compares methods fairly.",
"section": "Refereeing",
"slide": "What the harness holds fixed, and what it measures",
"keys": [
"referee"
]
},
{
"term_html": "violation checker",
"html": "Step 1's function that finds every broken window, capacity or coverage requirement in a claimed solution.",
"section": "Refereeing",
"slide": "What the harness holds fixed, and what it measures",
"keys": [
"violation checker"
]
},
{
"term_html": "primal gap",
"html": "\\(\\gamma(v, v^*) = |v - v^*| / \\max(|v|, |v^*|)\\), or 1 with no solution, where \\(v^*\\) is the best value any method found (Berthold 2013).",
"section": "Refereeing",
"slide": "What the harness holds fixed, and what it measures",
"keys": [
"primal gap"
]
},
{
"term_html": "PAR1",
"html": "Penalized average runtime with timeouts counted at the limit; the time-to-proof metric for the exact methods.",
"section": "Refereeing",
"slide": "What the harness holds fixed, and what it measures",
"keys": [
"par1"
]
},
{
"term_html": "refuted claim",
"html": "A method's \"optimal\" contradicted by a better solution from another method, or two different proven optima.",
"section": "Refereeing",
"slide": "What the harness holds fixed, and what it measures",
"keys": [
"refuted claim"
]
},
{
"term_html": "head-to-head verdict",
"html": "A paired Wilcoxon test with Holm's correction over all pairs, reporting a winner or \"indistinguishable\".",
"section": "Refereeing",
"slide": "What the harness holds fixed, and what it measures",
"keys": [
"head-to-head verdict"
]
},
{
"term_html": "primal integral",
"html": "The area under a method's gap-versus-time curve, capturing when it found good solutions, not just where it ended.",
"section": "Refereeing",
"slide": "What the harness holds fixed, and what it measures",
"keys": [
"primal integral"
]
},
{
"term_html": "window / horizon ratio",
"html": "Mean window width over the depot's horizon; the crude instance characteristic used to explain which method wins.",
"section": "Refereeing",
"slide": "Which characteristics favour which method",
"keys": [
"window / horizon ratio"
]
}
];
