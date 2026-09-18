// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "bit size \\(L\\)",
"html": "The number of bits needed to write \\(A, b, c\\) as integers. \"Polynomial\" for LP means polynomial in \\(L\\).",
"section": "Is LP in P?",
"slide": "What was known, and what wasn't",
"keys": [
"bit size l"
]
},
{
"term_html": "strongly polynomial",
"html": "Polynomial in \\(m\\) and \\(n\\) alone, independent of the numbers. Known for network flows; open for general LP (one of Smale's problems).",
"section": "Is LP in P?",
"slide": "What was known, and what wasn't",
"keys": [
"strongly polynomial"
]
},
{
"term_html": "NP ∩ coNP",
"html": "Where LP was known to sit before 1979: short certificates both ways (units 01, 03), but no polynomial algorithm.",
"section": "Is LP in P?",
"slide": "What was known, and what wasn't",
"keys": [
"np ∩ conp"
]
},
{
"term_html": "Karmarkar's algorithm",
"html": "The 1984 polynomial interior-point method that also looked practical.",
"section": "Is LP in P?",
"slide": "What was known, and what wasn't",
"keys": [
"karmarkar's algorithm"
]
},
{
"term_html": "ellipsoid",
"html": "\\(E = \\{z : (z - x)^\\top P^{-1} (z - x) \\le 1\\}\\), described by a centre \\(x\\) and a positive definite matrix \\(P\\).",
"section": "The ellipsoid method",
"slide": "The update, and why the volume shrinks",
"keys": [
"ellipsoid"
]
},
{
"term_html": "ellipsoid method",
"html": "Start with a ball containing the feasible set. If the centre is infeasible, keep the half on the feasible side of a violated constraint, wrap it in the smallest ellipsoid, repeat. Stop when the centre is feasible or the ellipsoid is too small to hold the set.",
"section": "The ellipsoid method",
"slide": "The idea",
"keys": [
"ellipsoid method"
]
},
{
"term_html": "central cut",
"html": "A cut through the current centre, \\(\\{a^\\top z \\le a^\\top x\\}\\), keeping exactly half the ellipsoid.",
"section": "The ellipsoid method",
"slide": "The idea",
"keys": [
"central cut"
]
},
{
"term_html": "ellipsoid update",
"html": "\\(g = Pa / \\sqrt{a^\\top P a}\\), \\(x' = x - g/(n+1)\\), \\(P' = \\frac{n^2}{n^2 - 1}(P - \\frac{2}{n+1} g g^\\top)\\).",
"section": "The ellipsoid method",
"slide": "The idea",
"keys": [
"ellipsoid update"
]
},
{
"term_html": "volume ratio",
"html": "Each step shrinks volume by a factor below \\(e^{-1/(2(n+1))}\\), whatever the cut.",
"section": "The ellipsoid method",
"slide": "The idea",
"keys": [
"volume ratio"
]
},
{
"term_html": "iteration bound",
"html": "If a nonempty feasible set contains a ball of radius \\(r\\) inside the starting ball of radius \\(R\\), then \\(k \\ge 2n(n+1) \\ln(R/r)\\) steps suffice. Lab step 5.",
"section": "The ellipsoid method",
"slide": "The idea",
"keys": [
"iteration bound"
]
},
{
"term_html": "\\(R\\) and \\(r\\) from the data",
"html": "Cramer's rule bounds a solution's size by \\(2^{O(L)}\\); relaxing each \\(b_i\\) by \\(2^{-O(L)}\\) gives a flat polytope a ball of radius \\(2^{-O(L)}\\) without changing feasibility.",
"section": "The ellipsoid method",
"slide": "From feasibility to polynomial-time LP",
"keys": [
"r and r from the data"
]
},
{
"term_html": "sliding objective",
"html": "Turning the feasibility method into optimization by adding \\(c^\\top x \\ge \\gamma\\) and raising \\(\\gamma\\).",
"section": "The ellipsoid method",
"slide": "From feasibility to polynomial-time LP",
"keys": [
"sliding objective"
]
},
{
"term_html": "Khachiyan's theorem",
"html": "LP feasibility is decided in \\(O(n^2 L)\\) ellipsoid iterations with polynomial precision, so LP is in P (1979).",
"section": "The ellipsoid method",
"slide": "From feasibility to polynomial-time LP",
"keys": [
"khachiyan's theorem"
]
},
{
"term_html": "separation oracle",
"html": "A procedure that, given a point, says it is feasible or returns a violated inequality. All the ellipsoid method needs, even for exponentially many constraints (unit 09).",
"section": "The ellipsoid method",
"slide": "Useless in practice, indispensable in theory",
"keys": [
"separation oracle"
]
},
{
"term_html": "log barrier",
"html": "\\(-\\sum_i \\log(b_i - a_i^\\top x)\\), a penalty that is finite inside the polyhedron and infinite on its boundary.",
"section": "Interior-point methods",
"slide": "The log barrier and the central path",
"keys": [
"log barrier"
]
},
{
"term_html": "barrier function \\(f_t\\)",
"html": "\\(f_t(x) = -t\\, c^\\top x - \\sum_i \\log(b_i - a_i^\\top x)\\). The parameter \\(t\\) weighs the objective against the barrier.",
"section": "Interior-point methods",
"slide": "The log barrier and the central path",
"keys": [
"barrier function f_t"
]
},
{
"term_html": "analytic centre",
"html": "The minimizer of the barrier alone (\\(t \\to 0\\)). Depends on the description, not just the shape: a redundant constraint moves it.",
"section": "Interior-point methods",
"slide": "The log barrier and the central path",
"keys": [
"analytic centre"
]
},
{
"term_html": "central path",
"html": "The curve of minimizers \\(x^*(t)\\) as \\(t\\) grows, running from the analytic centre to an optimal point.",
"section": "Interior-point methods",
"slide": "The log barrier and the central path",
"keys": [
"central path"
]
},
{
"term_html": "Newton's method",
"html": "Minimizing \\(f_t\\) by repeatedly solving with its Hessian \\(A^\\top \\mathrm{diag}(1/s^2) A\\). Converges quadratically near the minimizer.",
"section": "Interior-point methods",
"slide": "The log barrier and the central path",
"keys": [
"newton's method"
]
},
{
"term_html": "centering",
"html": "Minimizing \\(f_t\\) for one fixed \\(t\\).",
"section": "Interior-point methods",
"slide": "The log barrier and the central path",
"keys": [
"centering"
]
},
{
"term_html": "backtracking line search",
"html": "Shrinking the Newton step until it both decreases \\(f_t\\) enough and stays strictly inside the polyhedron. Lab step 2.",
"section": "Interior-point methods",
"slide": "The log barrier and the central path",
"keys": [
"backtracking line search"
]
},
{
"term_html": "Newton decrement",
"html": "The predicted decrease from a Newton step, used as the stopping test for centering.",
"section": "Interior-point methods",
"slide": "The log barrier and the central path",
"keys": [
"newton decrement"
]
},
{
"term_html": "dual point on the path",
"html": "At \\(x^*(t)\\), \\(y = 1/(t s)\\) is dual feasible: \\(A^\\top y = c,\\ y &gt; 0\\).",
"section": "Interior-point methods",
"slide": "Duality comes for free on the path",
"keys": [
"dual point on the path"
]
},
{
"term_html": "duality gap on the path",
"html": "Exactly \\(m/t\\). To reach accuracy \\(\\varepsilon\\), run until \\(t \\ge m/\\varepsilon\\).",
"section": "Interior-point methods",
"slide": "Duality comes for free on the path",
"keys": [
"duality gap on the path"
]
},
{
"term_html": "approximate complementary slackness",
"html": "\\(y_i s_i = 1/t\\) for every constraint, instead of unit 03's \\(y_i s_i = 0\\).",
"section": "Interior-point methods",
"slide": "Duality comes for free on the path",
"keys": [
"approximate complementary slackness"
]
},
{
"term_html": "path following",
"html": "Centre at \\(t\\), multiply \\(t\\) by \\(\\mu\\), re-centre from the previous point. With \\(\\mu = 1 + 1/\\sqrt m\\) the total is \\(O(\\sqrt m \\log(m/\\varepsilon))\\) Newton steps.",
"section": "Interior-point methods",
"slide": "Duality comes for free on the path",
"keys": [
"path following"
]
},
{
"term_html": "primal–dual interior-point method",
"html": "Newton's method on the perturbed KKT system \\(Ax + s = b,\\ A^\\top y = c,\\ y_i s_i = \\mu\\) in \\((x, y, s)\\) together, driving \\(\\mu \\to 0\\). What production solvers run.",
"section": "Interior-point methods",
"slide": "Duality comes for free on the path",
"keys": [
"primal–dual interior-point method"
]
},
{
"term_html": "predictor–corrector",
"html": "Mehrotra's (1992) long-step scheme; 20–60 iterations almost regardless of size.",
"section": "Interior-point methods",
"slide": "Duality comes for free on the path",
"keys": [
"predictor–corrector"
]
},
{
"term_html": "self-concordance",
"html": "The property of the log barrier behind the \\(O(\\sqrt m)\\) iteration bound (Nesterov &amp; Nemirovski, 1994).",
"section": "Interior-point methods",
"slide": "Duality comes for free on the path",
"keys": [
"self-concordance"
]
},
{
"term_html": "floating-point breakdown",
"html": "Past \\(t \\approx 10^6\\), slacks near \\(10^{-7}\\) push the Hessian's condition number beyond \\(10^{14}\\) and the Newton direction becomes noise.",
"section": "Interior-point methods",
"slide": "Where floating point ends the pure barrier method",
"keys": [
"floating-point breakdown"
]
},
{
"term_html": "crossover",
"html": "Moving an interior-point solution to a vertex of equal value with simplex-like steps, so branch-and-bound and sensitivity analysis get a basis (Megiddo 1991).",
"section": "Interior-point methods",
"slide": "Where floating point ends the pure barrier method",
"keys": [
"crossover"
]
},
{
"term_html": "relative interior of the optimal face",
"html": "Where an IPM's answer lies when the optimum is not unique: strictly inside the set of optimal points, not at a vertex.",
"section": "Interior-point methods",
"slide": "Where floating point ends the pure barrier method",
"keys": [
"relative interior of the optimal face"
]
},
{
"term_html": "cold solve",
"html": "Solving from scratch. IPM iterations barely grow with size, each one a sparse Cholesky factorization.",
"section": "Choosing between them",
"slide": "Cold solves: IPM iterations barely grow",
"keys": [
"cold solve"
]
},
{
"term_html": "normal-equations matrix",
"html": "\\(A\\,\\mathrm{diag}(y/s)\\,A^\\top\\), the matrix each IPM iteration factorizes. A few dense columns make it dense.",
"section": "Choosing between them",
"slide": "Cold solves: IPM iterations barely grow",
"keys": [
"normal-equations matrix"
]
},
{
"term_html": "fill-in",
"html": "Nonzeros a factorization creates where the matrix had zeros.",
"section": "Choosing between them",
"slide": "Cold solves: IPM iterations barely grow",
"keys": [
"fill-in"
]
},
{
"term_html": "concurrent solving",
"html": "Running simplex and IPM in parallel and taking the first answer, because no rule predicts the winner.",
"section": "Choosing between them",
"slide": "Cold solves: IPM iterations barely grow",
"keys": [
"concurrent solving"
]
},
{
"term_html": "warm solve",
"html": "Re-solving after a small change. Simplex re-solves 25× faster than cold; IPM gains nothing, because the old optimum is on the boundary, the worst place to start a barrier method.",
"section": "Choosing between them",
"slide": "Warm solves: why branch-and-bound wants simplex",
"keys": [
"warm solve"
]
}
];
