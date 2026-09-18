// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "primal",
"html": "The LP you started with. Here \\(\\max\\{c^\\top x : Ax \\le b,\\ x \\ge 0\\}\\).",
"section": "The dual as a bound",
"slide": "",
"keys": [
"primal"
]
},
{
"term_html": "dual",
"html": "The LP whose solutions are the multipliers \\(y\\) giving an upper bound on the primal, minimized: \\(\\min\\{b^\\top y : A^\\top y \\ge c,\\ y \\ge 0\\}\\).",
"section": "The dual as a bound",
"slide": "Where the dual comes from",
"keys": [
"dual"
]
},
{
"term_html": "dual variable (multiplier)",
"html": "\\(y_i\\), the weight put on primal constraint \\(i\\) when combining constraints into a bound.",
"section": "The dual as a bound",
"slide": "Where the dual comes from",
"keys": [
"dual variable (multiplier)",
"dual variable",
"multiplier"
]
},
{
"term_html": "dualization rules",
"html": "\\(\\le\\) constraints get \\(y_i \\ge 0\\), \\(\\ge\\) constraints get \\(y_i \\le 0\\), equality constraints get free \\(y_i\\); \\(x_j \\ge 0\\) gives a \\(\\ge c_j\\) dual constraint, \\(x_j \\le 0\\) a \\(\\le\\) one, free \\(x_j\\) an equality. Rebuild them from the bounding argument rather than memorizing.",
"section": "The dual as a bound",
"slide": "The rules, once",
"keys": [
"dualization rules"
]
},
{
"term_html": "involution",
"html": "The dual of the dual is the primal, exactly. Lab step 1 tests it.",
"section": "The dual as a bound",
"slide": "The rules, once",
"keys": [
"involution"
]
},
{
"term_html": "weak duality",
"html": "Every feasible \\(x\\) and \\(y\\) have \\(c^\\top x \\le b^\\top y\\). One line of algebra.",
"section": "The dual as a bound",
"slide": "Weak and strong duality",
"keys": [
"weak duality"
]
},
{
"term_html": "strong duality",
"html": "If the primal has an optimum, so does the dual, with equal value. Proved from Farkas' lemma, or from simplex termination.",
"section": "The dual as a bound",
"slide": "Weak and strong duality",
"keys": [
"strong duality"
]
},
{
"term_html": "duality gap",
"html": "\\(b^\\top y - c^\\top x\\) for a feasible pair. Zero exactly when both are optimal.",
"section": "The dual as a bound",
"slide": "Weak and strong duality",
"keys": [
"duality gap"
]
},
{
"term_html": "outcome table",
"html": "Primal and dual are both optimal with equal values, or one is unbounded and the other infeasible, or both are infeasible. No other pairing happens.",
"section": "The dual as a bound",
"slide": "Four possible outcomes, not nine",
"keys": [
"outcome table"
]
},
{
"term_html": "infeasible or unbounded",
"html": "What presolve reports when it sees the dual is infeasible, which leaves both possibilities open for the primal.",
"section": "The dual as a bound",
"slide": "Four possible outcomes, not nine",
"keys": [
"infeasible or unbounded"
]
},
{
"term_html": "complementary slackness",
"html": "Feasible \\(x, y\\) are both optimal if and only if \\(y_i (b_i - a_i x) = 0\\) for every constraint and \\(x_j ((A^\\top y)_j - c_j) = 0\\) for every variable. In words: a constraint with slack has price 0, and a used variable has zero reduced cost.",
"section": "The dual as a certificate",
"slide": "Complementary slackness",
"keys": [
"complementary slackness"
]
},
{
"term_html": "optimality certificate",
"html": "A primal–dual pair checked for feasibility of both and a zero gap, in exact arithmetic. Lab step 3.",
"section": "The dual as a certificate",
"slide": "Complementary slackness",
"keys": [
"optimality certificate"
]
},
{
"term_html": "binding constraint",
"html": "One with no slack at the optimum, \\(a_i x = b_i\\). Only binding constraints can have a nonzero price.",
"section": "The dual as a certificate",
"slide": "Complementary slackness",
"keys": [
"binding constraint"
]
},
{
"term_html": "dual feasibility",
"html": "\\(A^\\top y \\ge c,\\ y \\ge 0\\). In the tableau: no negative entries in the objective row, the same test as unit 02's optimality criterion.",
"section": "The dual as a certificate",
"slide": "Reading the dual off the final tableau",
"keys": [
"dual feasibility"
]
},
{
"term_html": "reading duals off the tableau",
"html": "The optimal \\(y\\) is the slack columns of the final objective row, since a slack's reduced cost is \\(-y_i\\).",
"section": "The dual as a certificate",
"slide": "Reading the dual off the final tableau",
"keys": [
"reading duals off the tableau"
]
},
{
"term_html": "shadow price",
"html": "\\(y_i\\), the rate the optimum changes per unit of \\(b_i\\): \\(\\partial z^* / \\partial b_i = y_i\\) at a nondegenerate optimum. What one more unit of a resource is worth.",
"section": "The dual as prices",
"slide": "Shadow prices",
"keys": [
"shadow price"
]
},
{
"term_html": "value function \\(z^*(b)\\)",
"html": "The optimum as a function of the right-hand side. Concave and piecewise linear, one piece per optimal basis.",
"section": "The dual as prices",
"slide": "Shadow prices",
"keys": [
"value function z^*(b)"
]
},
{
"term_html": "supergradient",
"html": "A vector \\(y\\) with \\(z^*(b') \\le z^*(b) + y^\\top (b' - b)\\) for all \\(b'\\): the concave counterpart of a gradient, and what \\(y\\) is where \\(z^*\\) has a kink.",
"section": "The dual as prices",
"slide": "Shadow prices",
"keys": [
"supergradient"
]
},
{
"term_html": "ranging (sensitivity analysis)",
"html": "The interval of \\(\\delta\\) over which changing \\(b_i\\) to \\(b_i + \\delta\\) keeps the current basis optimal, and so keeps the shadow price valid. Computed from slack column \\(i\\) of the final tableau with a ratio test.",
"section": "The dual as prices",
"slide": "Ranging: how long the price holds",
"keys": [
"ranging (sensitivity analysis)",
"ranging",
"sensitivity analysis"
]
},
{
"term_html": "cost ranging",
"html": "The same analysis for an objective coefficient \\(c_j\\): the basis stays optimal while the objective row stays nonnegative.",
"section": "The dual as prices",
"slide": "Ranging: how long the price holds",
"keys": [
"cost ranging"
]
},
{
"term_html": "sign convention",
"html": "A reported dual is \\(\\partial(\\text{objective}) / \\partial(\\text{rhs})\\) in the solver's own objective sense, so the same LP written as a min reports negated duals.",
"section": "The dual as prices",
"slide": "Sign conventions: an afternoon, as promised",
"keys": [
"sign convention"
]
},
{
"term_html": "dual simplex method",
"html": "Simplex that keeps the objective row nonnegative (dual feasible) and pivots to remove negative right-hand sides (primal infeasibility). The primal simplex applied to the dual, on the same tableau.",
"section": "The dual as an algorithm",
"slide": "The dual simplex method",
"keys": [
"dual simplex method"
]
},
{
"term_html": "dual ratio test",
"html": "With leaving row \\(r\\), enter the column minimizing \\(T_{mj} / (-T_{rj})\\) over \\(T_{rj} &lt; 0\\). Keeps the objective row nonnegative.",
"section": "The dual as an algorithm",
"slide": "The dual simplex method",
"keys": [
"dual ratio test"
]
},
{
"term_html": "primal feasibility",
"html": "Every basic variable nonnegative, \\(\\bar b \\ge 0\\).",
"section": "The dual as an algorithm",
"slide": "The dual simplex method",
"keys": [
"primal feasibility"
]
},
{
"term_html": "infeasible row",
"html": "In the dual simplex, a leaving row with no negative entry reads \"nonnegative combination = negative\", so the LP is infeasible, and the row's multipliers are a Farkas vector.",
"section": "The dual as an algorithm",
"slide": "The dual simplex method",
"keys": [
"infeasible row"
]
},
{
"term_html": "warm start",
"html": "Re-optimizing from the previous optimal basis after adding a cut or tightening a bound. The basis stays dual feasible, so the dual simplex needs only a few pivots.",
"section": "The dual as an algorithm",
"slide": "Why branch-and-cut lives on it",
"keys": [
"warm start"
]
},
{
"term_html": "cold start",
"html": "Solving from scratch.",
"section": "The dual as an algorithm",
"slide": "Why branch-and-cut lives on it",
"keys": [
"cold start"
]
},
{
"term_html": "the seven hats",
"html": "Cutting planes, column generation, Lagrangian relaxation, Benders, the Hungarian algorithm, primal–dual approximation and KKT, each duality in a different setting.",
"section": "The dual as an algorithm",
"slide": "This unit, wearing seven hats",
"keys": [
"the seven hats"
]
},
{
"term_html": "<code>GeneralLP</code>",
"html": "An LP with \\(\\le\\), \\(\\ge\\) and \\(=\\) constraints and variables that are \\(\\ge 0\\), \\(\\le 0\\) or free: the input the dual transformer handles.",
"section": "In the lab",
"slide": "",
"keys": [
"~generallp~"
]
},
{
"term_html": "<code>CO_MINE=02</code>",
"html": "Runs this unit's tests on top of your own unit 02 simplex instead of the reference one.",
"section": "In the lab",
"slide": "",
"keys": [
"~co_mine=02~"
]
}
];
