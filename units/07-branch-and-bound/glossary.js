// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "branch and bound",
"html": "Split the feasible set, bound each piece with its LP relaxation, discard pieces that cannot beat the best solution found. Land &amp; Doig, 1960.",
"section": "The tree",
"slide": "LP-based branch and bound",
"keys": [
"branch and bound"
]
},
{
"term_html": "node",
"html": "One subproblem: the original MILP with some variable bounds tightened.",
"section": "The tree",
"slide": "LP-based branch and bound",
"keys": [
"node"
]
},
{
"term_html": "root",
"html": "The node with no added bounds; its LP is the MILP's LP relaxation.",
"section": "The tree",
"slide": "LP-based branch and bound",
"keys": [
"root"
]
},
{
"term_html": "branching",
"html": "Picking a fractional \\(x_j = v\\) and creating two children with \\(x_j \\le \\lfloor v \\rfloor\\) and \\(x_j \\ge \\lceil v \\rceil\\). The children partition the integer points and both cut off the fractional solution.",
"section": "The tree",
"slide": "LP-based branch and bound",
"keys": [
"branching"
]
},
{
"term_html": "open node",
"html": "A node created but not yet solved or branched on.",
"section": "The tree",
"slide": "LP-based branch and bound",
"keys": [
"open node"
]
},
{
"term_html": "prune by infeasibility",
"html": "Discard a node whose LP is infeasible.",
"section": "The tree",
"slide": "LP-based branch and bound",
"keys": [
"prune by infeasibility"
]
},
{
"term_html": "prune by integrality",
"html": "A node whose LP solution is integral becomes a candidate incumbent and needs no children.",
"section": "The tree",
"slide": "LP-based branch and bound",
"keys": [
"prune by integrality"
]
},
{
"term_html": "prune by bound",
"html": "Discard a node whose LP bound is at least the incumbent's value.",
"section": "The tree",
"slide": "LP-based branch and bound",
"keys": [
"prune by bound"
]
},
{
"term_html": "incumbent",
"html": "The best integer solution found so far.",
"section": "The tree",
"slide": "LP-based branch and bound",
"keys": [
"incumbent"
]
},
{
"term_html": "upper bound \\(U\\) (primal bound)",
"html": "The incumbent's value, or \\(+\\infty\\) before one exists.",
"section": "The tree",
"slide": "Two bounds, one gap",
"keys": [
"upper bound u (primal bound)",
"upper bound u",
"primal bound"
]
},
{
"term_html": "lower bound \\(L\\) (dual bound)",
"html": "The smallest LP bound among open nodes. Every unexplored integer point lies in some open node.",
"section": "The tree",
"slide": "Two bounds, one gap",
"keys": [
"lower bound l (dual bound)",
"lower bound l",
"dual bound"
]
},
{
"term_html": "gap",
"html": "\\((U - L) / |U|\\). The solver stops at 0 or below a tolerance.",
"section": "The tree",
"slide": "Two bounds, one gap",
"keys": [
"gap"
]
},
{
"term_html": "relative gap tolerance",
"html": "The stopping threshold: \\(10^{-4}\\) by default in HiGHS and Gurobi, 0 in SCIP. On an objective of \\(10^6\\) it allows 100 units of difference.",
"section": "The tree",
"slide": "Two bounds, one gap",
"keys": [
"relative gap tolerance"
]
},
{
"term_html": "node selection",
"html": "The rule for which open node to process next.",
"section": "Node selection",
"slide": "Depth-first against best-first",
"keys": [
"node selection"
]
},
{
"term_html": "depth-first search (DFS)",
"html": "Always a child of the last node. Finds incumbents early and uses little memory; can linger in a bad subtree.",
"section": "Node selection",
"slide": "Depth-first against best-first",
"keys": [
"depth-first search (dfs)",
"depth-first search",
"dfs"
]
},
{
"term_html": "best-first search",
"html": "Always the open node with the smallest bound. Raises \\(L\\) fastest and branches on the fewest nodes for a given branching rule; the frontier grows large and incumbents come late.",
"section": "Node selection",
"slide": "Depth-first against best-first",
"keys": [
"best-first search"
]
},
{
"term_html": "frontier",
"html": "The set of open nodes.",
"section": "Node selection",
"slide": "Depth-first against best-first",
"keys": [
"frontier"
]
},
{
"term_html": "best estimate selection",
"html": "Choosing nodes by an estimate of the best integer solution below them, not by bound alone.",
"section": "Node selection",
"slide": "Depth-first against best-first",
"keys": [
"best estimate selection"
]
},
{
"term_html": "plunging (diving)",
"html": "Following children depth-first from a promising node for a while before jumping back. What solvers ship, as a hybrid.",
"section": "Node selection",
"slide": "Depth-first against best-first",
"keys": [
"plunging (diving)",
"plunging",
"diving"
]
},
{
"term_html": "branching rule",
"html": "The rule for which fractional variable to split on. The biggest single influence on tree size.",
"section": "Branching",
"slide": "Most fractional, and why it's weak",
"keys": [
"branching rule"
]
},
{
"term_html": "most-fractional branching",
"html": "Pick the variable closest to 0.5. Measured to be about as good as random.",
"section": "Branching",
"slide": "Most fractional, and why it's weak",
"keys": [
"most-fractional branching"
]
},
{
"term_html": "fractionality",
"html": "How far \\(x_j\\) is from the nearest integer.",
"section": "Branching",
"slide": "Most fractional, and why it's weak",
"keys": [
"fractionality"
]
},
{
"term_html": "\\(\\Delta_j^-\\), \\(\\Delta_j^+\\)",
"html": "The bound improvement in the down and up child when branching on \\(x_j\\).",
"section": "Branching",
"slide": "Most fractional, and why it's weak",
"keys": [
"\\delta_j^-, \\delta_j^+",
"\\delta_j^-",
"\\delta_j^+"
]
},
{
"term_html": "product score",
"html": "\\(\\max(\\Delta_j^-, \\varepsilon) \\cdot \\max(\\Delta_j^+, \\varepsilon)\\). Rewards moving both children; \\(\\varepsilon\\) keeps a zero on one side from erasing the other.",
"section": "Branching",
"slide": "Most fractional, and why it's weak",
"keys": [
"product score"
]
},
{
"term_html": "strong branching",
"html": "Compute \\(\\Delta_j^\\pm\\) exactly by solving both child LPs for each candidate. Fewest nodes, most LP solves.",
"section": "Branching",
"slide": "Strong branching and pseudocosts",
"keys": [
"strong branching"
]
},
{
"term_html": "probe LP",
"html": "A child LP solved only to score a candidate during strong branching.",
"section": "Branching",
"slide": "Strong branching and pseudocosts",
"keys": [
"probe lp"
]
},
{
"term_html": "pseudocost",
"html": "The average bound gain per unit of fractionality observed when branching on \\(x_j\\) before. Pseudocost branching multiplies it by the current fractionality; costs nothing per node, but is uninformed at the top of the tree.",
"section": "Branching",
"slide": "Strong branching and pseudocosts",
"keys": [
"pseudocost"
]
},
{
"term_html": "pseudocost initialization",
"html": "What to assume for a variable never branched on. The whole weakness of pseudocosts.",
"section": "Branching",
"slide": "Strong branching and pseudocosts",
"keys": [
"pseudocost initialization"
]
},
{
"term_html": "reliability branching",
"html": "Strong branching on a variable until its pseudocosts have enough observations each way, then trusting them. SCIP's default.",
"section": "Branching",
"slide": "Strong branching and pseudocosts",
"keys": [
"reliability branching"
]
},
{
"term_html": "primal heuristic",
"html": "A method for finding good integer solutions quickly, so pruning by bound starts early.",
"section": "The other job, and the gap to SCIP",
"slide": "Primal heuristics",
"keys": [
"primal heuristic"
]
},
{
"term_html": "rounding heuristic",
"html": "Round the LP solution while keeping feasibility where possible (simple rounding, ZI rounding).",
"section": "The other job, and the gap to SCIP",
"slide": "Primal heuristics",
"keys": [
"rounding heuristic"
]
},
{
"term_html": "diving heuristic",
"html": "Fix a variable, re-solve, repeat down one branch without keeping a tree.",
"section": "The other job, and the gap to SCIP",
"slide": "Primal heuristics",
"keys": [
"diving heuristic"
]
},
{
"term_html": "RINS",
"html": "Relaxation-induced neighbourhood search: fix variables where incumbent and LP agree, solve the sub-MILP that remains. Large neighbourhood search with the MILP solver as repair (unit 19).",
"section": "The other job, and the gap to SCIP",
"slide": "Primal heuristics",
"keys": [
"rins"
]
},
{
"term_html": "feasibility pump",
"html": "Alternate between projecting onto the LP polytope and rounding to the nearest integer point, until the two meet.",
"section": "The other job, and the gap to SCIP",
"slide": "Primal heuristics",
"keys": [
"feasibility pump"
]
},
{
"term_html": "conflict analysis",
"html": "Learning a constraint from why a node was infeasible, as SAT solvers do (unit 20).",
"section": "The other job, and the gap to SCIP",
"slide": "Your factor of shame",
"keys": [
"conflict analysis"
]
},
{
"term_html": "factor of shame",
"html": "Your best node count divided by SCIP's on the same instance.",
"section": "The other job, and the gap to SCIP",
"slide": "Your factor of shame",
"keys": [
"factor of shame"
]
},
{
"term_html": "SCIP bare",
"html": "SCIP with presolve and cuts off. Separates the effect of branching and LP handling from that of cuts, presolve and heuristics.",
"section": "The other job, and the gap to SCIP",
"slide": "Your factor of shame",
"keys": [
"scip bare"
]
},
{
"term_html": "<code>solve_node(milp, lb, ub)</code>",
"html": "Solves one node's LP under the given bounds, returning a <code>NodeLP</code>.",
"section": "In the lab",
"slide": "",
"keys": [
"~solve_node(milp, lb, ub)~"
]
},
{
"term_html": "<code>INT_TOL</code>",
"html": "The tolerance within which a value counts as integral.",
"section": "In the lab",
"slide": "",
"keys": [
"~int_tol~"
]
},
{
"term_html": "<code>BBResult</code>",
"html": "The tree's result, including node and LP-solve counts.",
"section": "In the lab",
"slide": "",
"keys": [
"~bbresult~"
]
}
];
