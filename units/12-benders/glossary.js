// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "Benders decomposition",
"html": "Fix the complicating variables in a master problem, solve the rest as an LP, and turn its duals into an inequality on the master. Row generation; Benders 1962.",
"section": "Splitting",
"slide": "",
"keys": [
"benders decomposition"
]
},
{
"term_html": "complicating variables",
"html": "\\(y\\): few, often integer, and once fixed they leave an easy LP.",
"section": "Splitting",
"slide": "The value function of the easy part",
"keys": [
"complicating variables"
]
},
{
"term_html": "recourse (subproblem)",
"html": "The LP in \\(x\\) solved after \\(y\\) is fixed.",
"section": "Splitting",
"slide": "The value function of the easy part",
"keys": [
"recourse (subproblem)",
"recourse",
"subproblem"
]
},
{
"term_html": "value function \\(Q(y)\\)",
"html": "The recourse optimum as a function of \\(y\\). By LP duality, \\(\\max_{\\pi \\in \\Pi} \\pi^\\top (h - Ty)\\): convex and piecewise linear.",
"section": "Splitting",
"slide": "The value function of the easy part",
"keys": [
"value function q(y)"
]
},
{
"term_html": "dual polyhedron \\(\\Pi\\)",
"html": "\\(\\{\\pi \\ge 0 : W^\\top \\pi \\le c\\}\\). It does not depend on \\(y\\), so a dual solution found at one \\(y\\) is valid at all of them. The fact the whole method rests on.",
"section": "Splitting",
"slide": "The value function of the easy part",
"keys": [
"dual polyhedron \\pi"
]
},
{
"term_html": "optimality cut",
"html": "\\(\\theta \\ge \\bar\\pi^\\top (h - Ty)\\) from an optimal dual \\(\\bar\\pi\\) at \\(\\bar y\\). Tight at \\(\\bar y\\), valid everywhere by weak duality.",
"section": "Splitting",
"slide": "Optimality and feasibility cuts",
"keys": [
"optimality cut"
]
},
{
"term_html": "feasibility cut",
"html": "\\(\\bar r^\\top (h - Ty) \\le 0\\) from a ray \\(\\bar r\\) of \\(\\Pi\\) when the subproblem at \\(\\bar y\\) is infeasible. Excludes \\(\\bar y\\) and keeps every \\(y\\) that is feasible.",
"section": "Splitting",
"slide": "Optimality and feasibility cuts",
"keys": [
"feasibility cut"
]
},
{
"term_html": "phase-one LP",
"html": "\\(\\min \\sum z\\) with slack variables, always feasible and bounded; its duals give the feasibility cut without asking the solver for a ray.",
"section": "Splitting",
"slide": "Optimality and feasibility cuts",
"keys": [
"phase-one lp"
]
},
{
"term_html": "complete recourse",
"html": "Every \\(y\\) leaves a feasible subproblem, for example via a penalty on unmet demand. Feasibility cuts then never occur.",
"section": "Splitting",
"slide": "Optimality and feasibility cuts",
"keys": [
"complete recourse"
]
},
{
"term_html": "master problem",
"html": "\\(\\min f^\\top y + \\theta\\) subject to the cuts so far and \\(y \\in Y\\). A MIP that gains cuts every iteration.",
"section": "Splitting",
"slide": "The loop, and why it ends",
"keys": [
"master problem"
]
},
{
"term_html": "\\(\\theta\\)",
"html": "The master's estimate of \\(Q(y)\\), built from below by the cuts. Needs a starting lower bound, such as \\(\\theta \\ge 0\\).",
"section": "Splitting",
"slide": "The loop, and why it ends",
"keys": [
"\\theta"
]
},
{
"term_html": "Benders bounds",
"html": "LB is the master value, rising as cuts are added; UB is the best \\(f^\\top \\bar y + Q(\\bar y)\\) seen. Stop when they meet.",
"section": "Splitting",
"slide": "The loop, and why it ends",
"keys": [
"benders bounds"
]
},
{
"term_html": "finite convergence",
"html": "\\(\\Pi\\) has finitely many vertices and rays, so only finitely many cuts exist.",
"section": "Splitting",
"slide": "The loop, and why it ends",
"keys": [
"finite convergence"
]
},
{
"term_html": "linking variables vs linking constraints",
"html": "Benders splits a problem whose blocks share variables; Dantzig–Wolfe one whose blocks share constraints.",
"section": "The mirror of unit 10",
"slide": "Benders and Dantzig–Wolfe on one page",
"keys": [
"linking variables vs linking constraints"
]
},
{
"term_html": "Benders–DW duality",
"html": "For an LP, Benders on the primal is Dantzig–Wolfe on its dual: the transposed matrix swaps linking variables for linking constraints and generated rows for generated columns.",
"section": "The mirror of unit 10",
"slide": "Benders and Dantzig–Wolfe on one page",
"keys": [
"benders–dw duality"
]
},
{
"term_html": "relaxed master vs restricted master",
"html": "Benders' master lacks rows, so it gives a lower bound; DW's lacks columns, so it gives an upper bound. The row most often drawn backwards.",
"section": "The mirror of unit 10",
"slide": "Benders and Dantzig–Wolfe on one page",
"keys": [
"relaxed master vs restricted master"
]
},
{
"term_html": "two-stage stochastic program",
"html": "Decide \\(y\\) now, observe a scenario, then take recourse; minimize \\(f^\\top y + \\sum_s p_s Q_s(y)\\).",
"section": "Stochastic programming",
"slide": "Two-stage recourse and the L-shaped method",
"keys": [
"two-stage stochastic program"
]
},
{
"term_html": "scenario",
"html": "One possible realization of the uncertain data, with probability \\(p_s\\).",
"section": "Stochastic programming",
"slide": "Two-stage recourse and the L-shaped method",
"keys": [
"scenario"
]
},
{
"term_html": "deterministic equivalent (extensive form)",
"html": "One MIP with a copy of the second-stage variables per scenario.",
"section": "Stochastic programming",
"slide": "Two-stage recourse and the L-shaped method",
"keys": [
"deterministic equivalent (extensive form)",
"deterministic equivalent",
"extensive form"
]
},
{
"term_html": "L-shaped method",
"html": "Benders with one aggregated cut per iteration, \\(\\theta \\ge \\sum_s p_s(\\cdot)\\) (Van Slyke &amp; Wets 1969). Also called <em>single-cut</em>.",
"section": "Stochastic programming",
"slide": "Two-stage recourse and the L-shaped method",
"keys": [
"l-shaped method"
]
},
{
"term_html": "multi-cut",
"html": "One \\(\\theta_s\\) and one cut per scenario (Birge &amp; Louveaux 1988). Fewer iterations, bigger master.",
"section": "Stochastic programming",
"slide": "Two-stage recourse and the L-shaped method",
"keys": [
"multi-cut"
]
},
{
"term_html": "embarrassingly parallel",
"html": "Given \\(y\\), the scenario LPs are independent and can run at once.",
"section": "Stochastic programming",
"slide": "Two-stage recourse and the L-shaped method",
"keys": [
"embarrassingly parallel"
]
},
{
"term_html": "sample average approximation (SAA)",
"html": "Draw \\(S\\) scenarios, solve, repeat with fresh samples to estimate the optimality gap statistically.",
"section": "Stochastic programming",
"slide": "Two-stage recourse and the L-shaped method",
"keys": [
"sample average approximation (saa)",
"sample average approximation",
"saa"
]
},
{
"term_html": "EVPI",
"html": "The expected value of perfect information: what knowing the scenario in advance would save.",
"section": "Stochastic programming",
"slide": "Two-stage recourse and the L-shaped method",
"keys": [
"evpi"
]
},
{
"term_html": "VSS",
"html": "The value of the stochastic solution: what solving the stochastic model saves over planning for the average scenario.",
"section": "Stochastic programming",
"slide": "Two-stage recourse and the L-shaped method",
"keys": [
"vss"
]
},
{
"term_html": "crossover (Benders vs extensive form)",
"html": "The scenario count at which decomposition starts to win. Depends on iterations times cost per iteration, and the instance family controls the iterations.",
"section": "Stochastic programming",
"slide": "The crossover, measured",
"keys": [
"crossover (benders vs extensive form)",
"crossover",
"benders vs extensive form"
]
},
{
"term_html": "branch-and-Benders-cut",
"html": "Solving the master once, adding Benders cuts as lazy constraints from a callback whenever branch and bound finds a candidate.",
"section": "Modern Benders",
"slide": "One tree, and better cuts",
"keys": [
"branch-and-benders-cut"
]
},
{
"term_html": "LP-first",
"html": "Generating cuts at the master's LP relaxation before any integer solves (McDaniel &amp; Devine 1977).",
"section": "Modern Benders",
"slide": "One tree, and better cuts",
"keys": [
"lp-first"
]
},
{
"term_html": "dual degeneracy (Benders)",
"html": "Many optimal duals at \\(\\bar y\\), so many different cuts are tight there.",
"section": "Modern Benders",
"slide": "One tree, and better cuts",
"keys": [
"dual degeneracy (benders)",
"dual degeneracy",
"benders"
]
},
{
"term_html": "core point \\(y^0\\)",
"html": "A point in the relative interior of \\(\\mathrm{conv}(Y)\\), used to rank tight cuts.",
"section": "Modern Benders",
"slide": "One tree, and better cuts",
"keys": [
"core point y^0"
]
},
{
"term_html": "Pareto-optimal cut",
"html": "Among the cuts tight at \\(\\bar y\\), one highest at the core point (Magnanti &amp; Wong 1981). Needs one extra LP.",
"section": "Modern Benders",
"slide": "One tree, and better cuts",
"keys": [
"pareto-optimal cut"
]
},
{
"term_html": "combinatorial Benders",
"html": "No-good cuts from infeasible subsets (Codato &amp; Fischetti 2006).",
"section": "Modern Benders",
"slide": "One tree, and better cuts",
"keys": [
"combinatorial benders"
]
},
{
"term_html": "no-good cut",
"html": "A constraint that forbids one specific assignment of the master variables, or a subset of it.",
"section": "Modern Benders",
"slide": "One tree, and better cuts",
"keys": [
"no-good cut"
]
},
{
"term_html": "logic-based Benders",
"html": "Any subproblem, CP or SAT included, that returns an inference about the master's choice (Hooker &amp; Ottosson 2003; unit 21).",
"section": "Modern Benders",
"slide": "One tree, and better cuts",
"keys": [
"logic-based benders"
]
},
{
"term_html": "in-out separation",
"html": "Separating at a point between the master solution and a core point, to stabilise the cuts.",
"section": "Modern Benders",
"slide": "One tree, and better cuts",
"keys": [
"in-out separation"
]
}
];
