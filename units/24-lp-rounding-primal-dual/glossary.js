// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "LP rounding",
"html": "Solving the LP relaxation and turning its fractional solution into an integral one whose cost is bounded against the LP.",
"section": "Rounding",
"slide": "",
"keys": [
"lp rounding"
]
},
{
"term_html": "threshold rounding",
"html": "Take \\(v\\) iff \\(x_v \\ge \\tfrac12\\) for vertex cover: feasible, and at most \\(2 \\cdot \\mathrm{LP}\\) (Hochbaum 1982).",
"section": "Rounding",
"slide": "Vertex cover at ½",
"keys": [
"threshold rounding"
]
},
{
"term_html": "half-integrality",
"html": "Every vertex of the vertex cover LP has all \\(x_v \\in \\{0, \\tfrac12, 1\\}\\) (Nemhauser &amp; Trotter 1975).",
"section": "Rounding",
"slide": "Vertex cover at ½",
"keys": [
"half-integrality"
]
},
{
"term_html": "persistence",
"html": "Some optimal integral cover contains every vertex at 1 and avoids every vertex at 0, so the LP settles part of the instance exactly.",
"section": "Rounding",
"slide": "Vertex cover at ½",
"keys": [
"persistence"
]
},
{
"term_html": "frequency \\(f\\)",
"html": "The largest number of sets any element belongs to. Threshold rounding at \\(1/f\\) is an \\(f\\)-approximation for set cover.",
"section": "Rounding",
"slide": "Vertex cover at ½",
"keys": [
"frequency f"
]
},
{
"term_html": "randomized rounding",
"html": "Pick each set independently with probability \\(x_j\\), repeat \\(t\\) times, take the union (Raghavan &amp; Thompson 1987).",
"section": "Rounding",
"slide": "Randomized rounding for set cover",
"keys": [
"randomized rounding"
]
},
{
"term_html": "miss probability",
"html": "The chance an element is uncovered in one round: \\(\\prod_{j \\ni e}(1 - x_j) \\le e^{-1}\\), using \\(1 - x \\le e^{-x}\\).",
"section": "Rounding",
"slide": "Randomized rounding for set cover",
"keys": [
"miss probability"
]
},
{
"term_html": "union bound",
"html": "\\(\\Pr[\\text{some bad event}] \\le \\sum \\Pr[\\text{each}]\\); here \\(\\Pr[\\text{not a cover}] \\le n e^{-t}\\).",
"section": "Rounding",
"slide": "Randomized rounding for set cover",
"keys": [
"union bound"
]
},
{
"term_html": "linearity of expectation",
"html": "\\(\\mathbb{E}[\\text{cost}] \\le t \\cdot \\mathrm{LP}\\), whatever the dependence between rounds.",
"section": "Rounding",
"slide": "Randomized rounding for set cover",
"keys": [
"linearity of expectation"
]
},
{
"term_html": "Markov's inequality",
"html": "\\(\\Pr[X \\ge a] \\le \\mathbb{E}[X]/a\\) for nonnegative \\(X\\); bounds the chance the cost is too high.",
"section": "Rounding",
"slide": "Randomized rounding for set cover",
"keys": [
"markov's inequality"
]
},
{
"term_html": "Chernoff bound",
"html": "A tail bound for sums of independent variables; needed when rounding under packing constraints, not for set cover.",
"section": "Rounding",
"slide": "Randomized rounding for set cover",
"keys": [
"chernoff bound"
]
},
{
"term_html": "derandomization",
"html": "Turning a randomized algorithm deterministic, here by conditional expectations with a pessimistic estimator.",
"section": "Rounding",
"slide": "Randomized rounding for set cover",
"keys": [
"derandomization"
]
},
{
"term_html": "primal–dual method (approximation)",
"html": "Grow a feasible dual solution, set a primal variable when its dual constraint goes tight, stop when the primal is feasible, and bound how often each dual is charged. Never solves an LP.",
"section": "Primal–dual",
"slide": "The schema, on set cover",
"keys": [
"primal–dual method (approximation)",
"primal–dual method",
"approximation"
]
},
{
"term_html": "tight (dual constraint)",
"html": "Holding with equality: the elements in a set have paid its full cost.",
"section": "Primal–dual",
"slide": "The schema, on set cover",
"keys": [
"tight (dual constraint)",
"tight",
"dual constraint"
]
},
{
"term_html": "primal–dual set cover",
"html": "For each uncovered element, raise its dual until some set containing it is tight; buy every tight set. An \\(f\\)-approximation (Bar-Yehuda &amp; Even 1981).",
"section": "Primal–dual",
"slide": "The schema, on set cover",
"keys": [
"primal–dual set cover"
]
},
{
"term_html": "relaxed complementary slackness",
"html": "Primal CS holds exactly (bought sets are tight), dual CS only up to a factor (an element with positive dual is covered at most \\(f\\) times). The ratio is that factor.",
"section": "Primal–dual",
"slide": "The schema, on set cover",
"keys": [
"relaxed complementary slackness"
]
},
{
"term_html": "facility location LP dual",
"html": "\\(\\max \\sum_j \\alpha_j\\) subject to \\(\\sum_j \\beta_{ij} \\le f_i\\), \\(\\alpha_j - \\beta_{ij} \\le d_{ij}\\), \\(\\beta \\ge 0\\). \\(\\alpha_j\\) is what client \\(j\\) pays.",
"section": "Primal–dual",
"slide": "Facility location: Jain & Vazirani (2001)",
"keys": [
"facility location lp dual"
]
},
{
"term_html": "Jain–Vazirani algorithm",
"html": "Phase 1: all \\(\\alpha_j\\) grow; clients pay toward facilities within reach; fully paid facilities open temporarily and freeze their clients. Phase 2: keep a maximal non-conflicting set of opened facilities and assign clients to the nearest. A 3-approximation for metric facility location.",
"section": "Primal–dual",
"slide": "Facility location: Jain & Vazirani (2001)",
"keys": [
"jain–vazirani algorithm"
]
},
{
"term_html": "temporarily open",
"html": "A facility whose cost has been fully paid in phase 1, before conflicts are resolved.",
"section": "Primal–dual",
"slide": "Facility location: Jain & Vazirani (2001)",
"keys": [
"temporarily open"
]
},
{
"term_html": "conflicting facilities",
"html": "Two temporarily open facilities that one client pays toward.",
"section": "Primal–dual",
"slide": "Facility location: Jain & Vazirani (2001)",
"keys": [
"conflicting facilities"
]
},
{
"term_html": "freeze",
"html": "A client stops raising \\(\\alpha_j\\) once it is tight with an open facility, at time \\(\\min_i \\max(t_i, d_{ij})\\).",
"section": "Primal–dual",
"slide": "Facility location: Jain & Vazirani (2001)",
"keys": [
"freeze"
]
},
{
"term_html": "Lagrangian-multiplier-preserving (LMP)",
"html": "A guarantee where facility cost is paid exactly from the duals: \\(\\text{connection} + 3 \\cdot \\text{facility} \\le 3 \\sum \\alpha\\). What lets JV give a \\(k\\)-median algorithm.",
"section": "Primal–dual",
"slide": "Facility location: Jain & Vazirani (2001)",
"keys": [
"lagrangian-multiplier-preserving (lmp)",
"lagrangian-multiplier-preserving",
"lmp"
]
},
{
"term_html": "Steiner forest",
"html": "The cheapest edge set connecting every given pair \\((s_i, t_i)\\).",
"section": "Primal–dual",
"slide": "Steiner forest, and iterative rounding",
"keys": [
"steiner forest"
]
},
{
"term_html": "active component",
"html": "A component still separating some pair, whose dual keeps growing.",
"section": "Primal–dual",
"slide": "Steiner forest, and iterative rounding",
"keys": [
"active component"
]
},
{
"term_html": "reverse delete",
"html": "After the primal–dual growth, removing unnecessary bought edges in reverse order. What makes Steiner forest's factor 2 work.",
"section": "Primal–dual",
"slide": "Steiner forest, and iterative rounding",
"keys": [
"reverse delete"
]
},
{
"term_html": "iterative rounding",
"html": "Solve the LP, fix a variable with a large value, update, re-solve (Jain 2001).",
"section": "Primal–dual",
"slide": "Steiner forest, and iterative rounding",
"keys": [
"iterative rounding"
]
},
{
"term_html": "laminar family",
"html": "Sets any two of which are disjoint or nested; the structure of tight constraints in iterative rounding proofs.",
"section": "Primal–dual",
"slide": "Steiner forest, and iterative rounding",
"keys": [
"laminar family"
]
},
{
"term_html": "integrality gap (of an LP)",
"html": "\\(\\sup_I \\mathrm{OPT}(I) / \\mathrm{LP}(I)\\) for minimization. No proof of the form \\(\\mathrm{ALG} \\le \\rho \\cdot \\mathrm{LP}\\) can give \\(\\rho\\) below it.",
"section": "Integrality gaps",
"slide": "Instances that realise the gap",
"keys": [
"integrality gap (of an lp)",
"integrality gap",
"of an lp"
]
},
{
"term_html": "gap instance",
"html": "An instance realising the gap. For vertex cover, \\(K_n\\): LP \\(n/2\\), OPT \\(n - 1\\).",
"section": "Integrality gaps",
"slide": "Instances that realise the gap",
"keys": [
"gap instance"
]
},
{
"term_html": "GF(2)^k family",
"html": "Elements and sets are nonzero vectors of \\(\\mathrm{GF}(2)^k\\); set \\(v\\) holds \\(\\{u : u \\cdot v = 1\\}\\). LP below 2, OPT \\(k\\): a logarithmic gap on which greedy is still optimal.",
"section": "Integrality gaps",
"slide": "Instances that realise the gap",
"keys": [
"gf(2)^k family"
]
},
{
"term_html": "GF(2)",
"html": "The field with two elements, arithmetic modulo 2.",
"section": "Integrality gaps",
"slide": "Instances that realise the gap",
"keys": [
"gf(2)",
"gf",
"2"
]
},
{
"term_html": "limit on proofs, not algorithms",
"html": "A gap instance shows an LP cannot certify a better ratio; it says nothing about how hard the instance is to solve.",
"section": "Integrality gaps",
"slide": "Instances that realise the gap",
"keys": [
"limit on proofs, not algorithms",
"limit on proofs",
"not algorithms"
]
},
{
"term_html": "Sherali–Adams, Lasserre",
"html": "Hierarchies of increasingly strong LP and SDP relaxations obtained by lifting.",
"section": "Integrality gaps",
"slide": "Instances that realise the gap",
"keys": [
"sherali–adams, lasserre",
"sherali–adams",
"lasserre"
]
}
];
