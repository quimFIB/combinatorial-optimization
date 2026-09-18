// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "presolve",
"html": "The solver's rewriting of a model before search.",
"section": "Before branching",
"slide": "What presolve does, and what defeats it",
"keys": [
"presolve"
]
},
{
"term_html": "bound tightening",
"html": "Deriving a smaller variable bound from the constraints, such as \\(x \\le 12\\) from \\(x + 10y \\le 12\\).",
"section": "Before branching",
"slide": "What presolve does, and what defeats it",
"keys": [
"bound tightening"
]
},
{
"term_html": "coefficient tightening",
"html": "Shrinking a coefficient to what the bounds allow, such as \\(x \\le 1000y\\) with \\(x \\le 50\\) becoming \\(x \\le 50y\\).",
"section": "Before branching",
"slide": "What presolve does, and what defeats it",
"keys": [
"coefficient tightening"
]
},
{
"term_html": "dual fixing",
"html": "Fixing a variable at the bound its objective and constraints both favour.",
"section": "Before branching",
"slide": "What presolve does, and what defeats it",
"keys": [
"dual fixing"
]
},
{
"term_html": "aggregation (presolve)",
"html": "Substituting a variable away using an equality such as \\(x = y + z\\).",
"section": "Before branching",
"slide": "What presolve does, and what defeats it",
"keys": [
"aggregation (presolve)",
"aggregation",
"presolve"
]
},
{
"term_html": "probing",
"html": "Tentatively fixing a binary both ways and learning implications from what propagation deduces.",
"section": "Before branching",
"slide": "What presolve does, and what defeats it",
"keys": [
"probing"
]
},
{
"term_html": "clique detection",
"html": "Merging pairwise conflicts between binaries into one clique constraint.",
"section": "Before branching",
"slide": "What presolve does, and what defeats it",
"keys": [
"clique detection"
]
},
{
"term_html": "numerically wide coefficients",
"html": "Values like \\(10^{-6}\\) next to \\(10^6\\) in one model, where tolerances start to bite and cuts get rejected.",
"section": "Before branching",
"slide": "What presolve does, and what defeats it",
"keys": [
"numerically wide coefficients"
]
},
{
"term_html": "indicator constraint",
"html": "\\(y = 1 \\Rightarrow a^\\top x \\le b\\) given to the solver directly, which chooses a big-M reformulation, branching, or SOS1.",
"section": "Before branching",
"slide": "What presolve does, and what defeats it",
"keys": [
"indicator constraint"
]
},
{
"term_html": "SOS1",
"html": "A special ordered set of type 1: at most one variable in the set is nonzero.",
"section": "Before branching",
"slide": "What presolve does, and what defeats it",
"keys": [
"sos1"
]
},
{
"term_html": "symmetry (model)",
"html": "A permutation of variables, such as relabelling bins, that maps solutions to solutions of equal cost. With 17 bins, up to \\(17!\\) copies of every solution.",
"section": "Symmetry",
"slide": "Interchangeable objects cost k!",
"keys": [
"symmetry (model)",
"symmetry",
"model"
]
},
{
"term_html": "orbit",
"html": "The set of solutions (or variables) a symmetry group maps into each other.",
"section": "Symmetry",
"slide": "Interchangeable objects cost k!",
"keys": [
"orbit"
]
},
{
"term_html": "symmetry-breaking constraints",
"html": "Constraints that keep one representative per orbit, such as \\(y_b \\ge y_{b+1}\\) and item \\(i\\) only in bins \\(0..i\\).",
"section": "Symmetry",
"slide": "Interchangeable objects cost k!",
"keys": [
"symmetry-breaking constraints"
]
},
{
"term_html": "lex-leader constraints",
"html": "Symmetry breaking that keeps the lexicographically largest member of each orbit (Crawford et al. 1996).",
"section": "Symmetry",
"slide": "Interchangeable objects cost k!",
"keys": [
"lex-leader constraints"
]
},
{
"term_html": "orbitope",
"html": "The convex hull of lexicographically sorted 0/1 matrices, with a propagation algorithm (Kaibel &amp; Pfetsch 2008).",
"section": "Symmetry",
"slide": "Interchangeable objects cost k!",
"keys": [
"orbitope"
]
},
{
"term_html": "orbital branching and fixing",
"html": "Detecting the symmetry group, branching on orbits, and fixing variables in the same orbit (Ostrowski et al. 2011).",
"section": "Symmetry",
"slide": "Interchangeable objects cost k!",
"keys": [
"orbital branching and fixing"
]
},
{
"term_html": "first-fit decreasing (FFD)",
"html": "Sort items largest first and put each in the first bin it fits. At most \\(\\tfrac{11}{9}\\mathrm{OPT} + \\tfrac69\\) bins, so it caps the bins a model needs.",
"section": "Starts, bounds, reformulation",
"slide": "Bounds, starts, and a different model",
"keys": [
"first-fit decreasing (ffd)",
"first-fit decreasing",
"ffd"
]
},
{
"term_html": "Martello–Toth L2",
"html": "A bin-packing lower bound at least \\(\\lceil \\sum / C \\rceil\\). With symmetry broken, bins \\(0..L_2 - 1\\) can be fixed as used.",
"section": "Starts, bounds, reformulation",
"slide": "Bounds, starts, and a different model",
"keys": [
"martello–toth l2"
]
},
{
"term_html": "bounded model",
"html": "The assignment model restricted to the FFD bin count, with the first \\(L_2\\) bins fixed open.",
"section": "Starts, bounds, reformulation",
"slide": "Bounds, starts, and a different model",
"keys": [
"bounded model"
]
},
{
"term_html": "MIP start (warm start)",
"html": "A feasible solution handed to the solver before the first node, giving an incumbent for pruning and a seed for improvement heuristics.",
"section": "Starts, bounds, reformulation",
"slide": "Bounds, starts, and a different model",
"keys": [
"mip start (warm start)",
"mip start",
"warm start"
]
},
{
"term_html": "solution pool",
"html": "Several solutions kept by the solver instead of one.",
"section": "Starts, bounds, reformulation",
"slide": "Bounds, starts, and a different model",
"keys": [
"solution pool"
]
},
{
"term_html": "reformulation",
"html": "Changing the model itself rather than tuning it. The one intervention with a large, stable effect in the lab.",
"section": "Starts, bounds, reformulation",
"slide": "Bounds, starts, and a different model",
"keys": [
"reformulation"
]
},
{
"term_html": "arc-flow model",
"html": "One unit of flow per bin along a path through capacities \\(0..C\\), each arc an item size (Valério de Carvalho 1999). Pseudo-polynomial size, no bin identities, and the same LP as the pattern model of unit 10.",
"section": "Starts, bounds, reformulation",
"slide": "Bounds, starts, and a different model",
"keys": [
"arc-flow model"
]
},
{
"term_html": "round-up property",
"html": "For almost all practical bin-packing instances, the optimum is the pattern LP rounded up, so the root LP proves optimality.",
"section": "Starts, bounds, reformulation",
"slide": "Bounds, starts, and a different model",
"keys": [
"round-up property"
]
},
{
"term_html": "shifted geometric mean (SGM)",
"html": "\\(\\left(\\prod_i (t_i + s)\\right)^{1/n} - s\\): the geometric mean of times shifted by \\(s\\), so tiny times do not dominate (unit 28).",
"section": "Starts, bounds, reformulation",
"slide": "Bounds, starts, and a different model",
"keys": [
"shifted geometric mean (sgm)",
"shifted geometric mean",
"sgm"
]
},
{
"term_html": "statistics report",
"html": "SCIP's end-of-solve summary: presolvers, constraints, separators, primal heuristics, branching rules, B&amp;B tree, root node, solution.",
"section": "Logs and variability",
"slide": "Reading a SCIP statistics report",
"keys": [
"statistics report"
]
},
{
"term_html": "first LP value",
"html": "The root LP bound before cuts. Compared with the final dual bound, it shows what cuts bought.",
"section": "Logs and variability",
"slide": "Reading a SCIP statistics report",
"keys": [
"first lp value"
]
},
{
"term_html": "stuck dual bound",
"html": "A dual bound that never leaves the first LP value while nodes pile up: a weak relaxation.",
"section": "Logs and variability",
"slide": "Reading a SCIP statistics report",
"keys": [
"stuck dual bound"
]
},
{
"term_html": "performance variability",
"html": "Large changes in solve time from irrelevant changes such as the random seed or constraint order.",
"section": "Logs and variability",
"slide": "Performance variability: the same model, different seeds",
"keys": [
"performance variability"
]
},
{
"term_html": "random seed (solver)",
"html": "The number fixing a solver's internal random choices. Different seeds give different trees on the same model.",
"section": "Logs and variability",
"slide": "Performance variability: the same model, different seeds",
"keys": [
"random seed (solver)",
"random seed",
"solver"
]
},
{
"term_html": "chaotic behaviour (MIP)",
"html": "A tiny change alters early branching, and the tree grows differently from there (Lodi &amp; Tramontani 2013).",
"section": "Logs and variability",
"slide": "Performance variability: the same model, different seeds",
"keys": [
"chaotic behaviour (mip)",
"chaotic behaviour",
"mip"
]
},
{
"term_html": "within noise",
"html": "An effect no larger than the run-to-run variation across seeds; a legitimate row in a before/after table, with the seed runs as evidence.",
"section": "Logs and variability",
"slide": "Performance variability: the same model, different seeds",
"keys": [
"within noise"
]
},
{
"term_html": "MIPLIB 2017",
"html": "The standard MIP library: 1 065 instances with a 240-instance benchmark set (Gleixner et al. 2021).",
"section": "Logs and variability",
"slide": "Performance variability: the same model, different seeds",
"keys": [
"miplib 2017"
]
}
];
