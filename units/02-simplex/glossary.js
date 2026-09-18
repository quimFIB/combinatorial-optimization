// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "slack variable",
"html": "\\(s_i = b_i - a_i x \\ge 0\\), turning each inequality into an equality so the system reads \\(Ax + s = b\\) over \\(n + m\\) variables with matrix \\([A \\mid I]\\).",
"section": "From vertices to bases",
"slide": "Bases and basic solutions",
"keys": [
"slack variable"
]
},
{
"term_html": "basis",
"html": "A set \\(B\\) of \\(m\\) linearly independent columns of \\([A \\mid I]\\).",
"section": "From vertices to bases",
"slide": "Bases and basic solutions",
"keys": [
"basis"
]
},
{
"term_html": "basic, nonbasic variables",
"html": "The variables whose columns are in \\(B\\), and the rest (\\(N\\)). Nonbasic variables sit at 0.",
"section": "From vertices to bases",
"slide": "Bases and basic solutions",
"keys": [
"basic, nonbasic variables",
"basic",
"nonbasic variables"
]
},
{
"term_html": "basic solution",
"html": "Setting the nonbasic variables to 0 and solving: \\(x_B = A_B^{-1} b\\). <em>Feasible</em> when \\(x_B \\ge 0\\).",
"section": "From vertices to bases",
"slide": "Bases and basic solutions",
"keys": [
"basic solution"
]
},
{
"term_html": "basic feasible solution (BFS)",
"html": "A feasible basic solution. Exactly the vertices of unit 01.",
"section": "From vertices to bases",
"slide": "Bases and basic solutions",
"keys": [
"basic feasible solution (bfs)",
"basic feasible solution",
"bfs"
]
},
{
"term_html": "degenerate vertex",
"html": "A vertex with fewer than \\(m\\) positive basic variables, so several bases describe it. Common in combinatorial LPs such as assignment and set cover.",
"section": "From vertices to bases",
"slide": "Bases and basic solutions",
"keys": [
"degenerate vertex"
]
},
{
"term_html": "slack basis",
"html": "The basis of all slack columns: \\(x = 0,\\ s = b\\). Feasible when \\(b \\ge 0\\), and the usual starting point.",
"section": "From vertices to bases",
"slide": "Bases and basic solutions",
"keys": [
"slack basis"
]
},
{
"term_html": "dictionary",
"html": "The LP rewritten for one basis: basic variables as constants minus combinations of nonbasic ones, and the objective as a constant plus reduced costs times nonbasic ones. Chvátal's term.",
"section": "From vertices to bases",
"slide": "Reduced costs: the optimality certificate",
"keys": [
"dictionary"
]
},
{
"term_html": "reduced cost",
"html": "\\(\\bar c_j = c_j - y^\\top a_j\\), the rate the objective changes as nonbasic \\(x_j\\) increases from 0.",
"section": "From vertices to bases",
"slide": "Reduced costs: the optimality certificate",
"keys": [
"reduced cost"
]
},
{
"term_html": "optimality criterion",
"html": "A feasible basis with every \\(\\bar c_j \\le 0\\) is optimal. Sufficient, not necessary: at a degenerate optimum some bases still show a positive reduced cost.",
"section": "From vertices to bases",
"slide": "Reduced costs: the optimality certificate",
"keys": [
"optimality criterion"
]
},
{
"term_html": "simplex multipliers",
"html": "\\(y^\\top = c_B^\\top A_B^{-1}\\). At an optimal basis they are an optimal dual solution (unit 03).",
"section": "From vertices to bases",
"slide": "Reduced costs: the optimality certificate",
"keys": [
"simplex multipliers"
]
},
{
"term_html": "entering variable",
"html": "A nonbasic \\(x_j\\) with \\(\\bar c_j &gt; 0\\), chosen to increase.",
"section": "From vertices to bases",
"slide": "Reduced costs: the optimality certificate",
"keys": [
"entering variable"
]
},
{
"term_html": "ratio test",
"html": "How far the entering variable can grow: \\(t^* = \\min_{i : d_i &gt; 0} \\bar b_i / d_i\\) with \\(\\bar b = A_B^{-1} b\\) and \\(d = A_B^{-1} a_j\\).",
"section": "From vertices to bases",
"slide": "The ratio test: how far to move",
"keys": [
"ratio test"
]
},
{
"term_html": "leaving variable",
"html": "The basic variable in the row attaining the ratio-test minimum. It hits 0 and becomes nonbasic.",
"section": "From vertices to bases",
"slide": "The ratio test: how far to move",
"keys": [
"leaving variable"
]
},
{
"term_html": "unbounded",
"html": "No \\(d_i &gt; 0\\), so the entering variable grows forever. The ray \\(x_B = \\bar b - td,\\ x_j = t\\) is the certificate.",
"section": "From vertices to bases",
"slide": "The ratio test: how far to move",
"keys": [
"unbounded"
]
},
{
"term_html": "degenerate pivot",
"html": "A pivot with \\(t^* = 0\\): the basis changes but the point does not move and the objective does not improve.",
"section": "From vertices to bases",
"slide": "The ratio test: how far to move",
"keys": [
"degenerate pivot"
]
},
{
"term_html": "pivot",
"html": "One basis change: an edge step between adjacent vertices, done algebraically as one Gauss–Jordan step.",
"section": "From vertices to bases",
"slide": "The ratio test: how far to move",
"keys": [
"pivot"
]
},
{
"term_html": "Dantzig's rule",
"html": "Enter the variable with the largest reduced cost.",
"section": "From vertices to bases",
"slide": "A walk on the example polygon",
"keys": [
"dantzig's rule"
]
},
{
"term_html": "shadow price",
"html": "How much the optimum rises per unit of loosening a constraint; the negated slack reduced costs at the optimum.",
"section": "From vertices to bases",
"slide": "A walk on the example polygon",
"keys": [
"shadow price"
]
},
{
"term_html": "tableau",
"html": "The dictionary as a matrix, \\(A_B^{-1}[A \\mid I]\\) with rhs \\(A_B^{-1} b\\). The lab's objective row stores \\(-\\bar c\\), so optimality means no negative entries there.",
"section": "From vertices to bases",
"slide": "The tableau: pivots as row operations",
"keys": [
"tableau"
]
},
{
"term_html": "pivot element",
"html": "The entry at the entering column and leaving row, turned into 1 with the rest of its column cleared.",
"section": "From vertices to bases",
"slide": "The tableau: pivots as row operations",
"keys": [
"pivot element"
]
},
{
"term_html": "dual values",
"html": "The slack columns of the final objective row. The bridge to unit 03.",
"section": "From vertices to bases",
"slide": "The tableau: pivots as row operations",
"keys": [
"dual values"
]
},
{
"term_html": "cycling",
"html": "A sequence of degenerate pivots that returns to an earlier basis and repeats forever.",
"section": "How the naive method fails",
"slide": "Degeneracy and cycling",
"keys": [
"cycling"
]
},
{
"term_html": "stalling",
"html": "A long run of degenerate pivots that does eventually end. The practical form of the cycling problem.",
"section": "How the naive method fails",
"slide": "Bland's rule",
"keys": [
"stalling"
]
},
{
"term_html": "Beale's example",
"html": "A 4-variable LP (1955) on which Dantzig's rule with lowest-row tie-breaking cycles after 6 degenerate pivots. Bland's rule leaves the cycle at pivot 5.",
"section": "How the naive method fails",
"slide": "Beale's cycle, pivot by pivot",
"keys": [
"beale's example"
]
},
{
"term_html": "Bland's rule",
"html": "Enter the lowest-index improving variable; break ratio-test ties by lowest index. Never cycles, and is usually slow.",
"section": "How the naive method fails",
"slide": "Bland's rule",
"keys": [
"bland's rule"
]
},
{
"term_html": "anti-cycling rule",
"html": "Any rule that guarantees termination: Bland's, the lexicographic ratio test, or perturbation.",
"section": "How the naive method fails",
"slide": "Bland's rule",
"keys": [
"anti-cycling rule"
]
},
{
"term_html": "lexicographic ratio test",
"html": "Breaking ratio-test ties by comparing rows lexicographically (Dantzig, Orden, Wolfe 1955).",
"section": "How the naive method fails",
"slide": "Bland's rule",
"keys": [
"lexicographic ratio test"
]
},
{
"term_html": "perturbation",
"html": "Adding tiny amounts to \\(b\\) (or to \\(c\\) in dual simplex) so ties essentially never occur, then removing them at the end.",
"section": "How the naive method fails",
"slide": "Bland's rule",
"keys": [
"perturbation"
]
},
{
"term_html": "Klee–Minty cube",
"html": "A squashed \\(n\\)-cube on which Dantzig's rule visits all \\(2^n\\) vertices, taking \\(2^n - 1\\) pivots.",
"section": "How the naive method fails",
"slide": "Klee–Minty: exponentially many pivots",
"keys": [
"klee–minty cube"
]
},
{
"term_html": "Hirsch conjecture",
"html": "That a polytope's vertex graph has diameter at most \\(m - n\\). Disproved by Santos (2012); whether the diameter is polynomial is still open.",
"section": "How the naive method fails",
"slide": "Klee–Minty: exponentially many pivots",
"keys": [
"hirsch conjecture"
]
},
{
"term_html": "average-case analysis",
"html": "Borgwardt (1982): polynomial expected pivots for the shadow-vertex rule on random LPs.",
"section": "How the naive method fails",
"slide": "So why is simplex the workhorse?",
"keys": [
"average-case analysis"
]
},
{
"term_html": "smoothed analysis",
"html": "Spielman &amp; Teng (2004): perturb any LP with small Gaussian noise, and shadow-vertex simplex takes polynomial expected time.",
"section": "How the naive method fails",
"slide": "So why is simplex the workhorse?",
"keys": [
"smoothed analysis"
]
},
{
"term_html": "warm start",
"html": "Re-solving a slightly changed LP from the previous optimal basis. Why simplex dominates inside branch-and-bound and cutting planes.",
"section": "How the naive method fails",
"slide": "So why is simplex the workhorse?",
"keys": [
"warm start"
]
},
{
"term_html": "phase 1",
"html": "Finding a feasible basis: add an artificial variable to each constraint with \\(b_i &lt; 0\\) and maximize \\(-\\sum a_i\\). Optimum below 0 means the LP is infeasible.",
"section": "Starting, and what real codes do",
"slide": "Getting started: two phases",
"keys": [
"phase 1"
]
},
{
"term_html": "artificial variable",
"html": "A variable added only to make a starting basis feasible; must be driven to 0 and removed.",
"section": "Starting, and what real codes do",
"slide": "Getting started: two phases",
"keys": [
"artificial variable"
]
},
{
"term_html": "phase 2",
"html": "Optimizing the real objective from the feasible basis phase 1 found.",
"section": "Starting, and what real codes do",
"slide": "Getting started: two phases",
"keys": [
"phase 2"
]
},
{
"term_html": "pricing out",
"html": "Making the objective row consistent with the current basis by subtracting basic rows, so basic variables have reduced cost 0. Forgetting it is the most common phase-1 bug.",
"section": "Starting, and what real codes do",
"slide": "Getting started: two phases",
"keys": [
"pricing out"
]
},
{
"term_html": "big-M method",
"html": "One phase with objective \\(c^\\top x - M \\sum a_i\\) for a huge \\(M\\). Simple and numerically poor.",
"section": "Starting, and what real codes do",
"slide": "Getting started: two phases",
"keys": [
"big-m method"
]
},
{
"term_html": "redundant row",
"html": "A constraint that is a combination of the others. Shows up as an artificial stuck in the basis at 0 with no nonzero real entries in its row.",
"section": "Starting, and what real codes do",
"slide": "Getting started: two phases",
"keys": [
"redundant row"
]
},
{
"term_html": "crash basis",
"html": "A heuristic starting basis with as many structural variables as possible, used by real codes instead of the slack basis.",
"section": "Starting, and what real codes do",
"slide": "Getting started: two phases",
"keys": [
"crash basis"
]
},
{
"term_html": "revised simplex method",
"html": "Simplex that stores a factorization of \\(A_B\\) instead of the full tableau, computing only the column and row a pivot needs.",
"section": "Starting, and what real codes do",
"slide": "The revised simplex method",
"keys": [
"revised simplex method"
]
},
{
"term_html": "BTRAN, FTRAN",
"html": "The two triangular solves per iteration: backward for \\(y^\\top = c_B^\\top A_B^{-1}\\), forward for \\(d = A_B^{-1} a_j\\).",
"section": "Starting, and what real codes do",
"slide": "The revised simplex method",
"keys": [
"btran, ftran",
"btran",
"ftran"
]
},
{
"term_html": "LU factorization",
"html": "\\(A_B\\) kept as sparse triangular factors (Markowitz ordering), updated each pivot (Forrest–Tomlin) and periodically <em>refactorized</em> to control fill-in and error.",
"section": "Starting, and what real codes do",
"slide": "The revised simplex method",
"keys": [
"lu factorization"
]
},
{
"term_html": "pricing",
"html": "Choosing the entering column. Can be <em>partial</em>: only some columns checked.",
"section": "Starting, and what real codes do",
"slide": "Pricing: which column enters",
"keys": [
"pricing"
]
},
{
"term_html": "steepest edge",
"html": "Enter the column with the largest improvement per unit of distance along the edge, \\(\\max_j \\bar c_j / \\|\\eta_j\\|\\). Far fewer pivots and insensitive to how variables are scaled.",
"section": "Starting, and what real codes do",
"slide": "Pricing: which column enters",
"keys": [
"steepest edge"
]
},
{
"term_html": "Devex",
"html": "A cheap approximation to steepest-edge norms (Harris 1973).",
"section": "Starting, and what real codes do",
"slide": "Pricing: which column enters",
"keys": [
"devex"
]
},
{
"term_html": "tolerance",
"html": "The threshold below which floating-point simplex treats a number as zero, such as \\(10^{-7}\\) for feasibility.",
"section": "Starting, and what real codes do",
"slide": "Tolerances, and what they hide",
"keys": [
"tolerance"
]
},
{
"term_html": "condition number",
"html": "How much a linear system amplifies input error. The Hilbert matrix's grows like \\(e^{3.5n}\\); at \\(n = 8\\) the solver's value looks right while the point is wrong by more than 1.",
"section": "Starting, and what real codes do",
"slide": "Tolerances, and what they hide",
"keys": [
"condition number"
]
},
{
"term_html": "exact rational LP solver",
"html": "A solver that verifies its basis in rational arithmetic, such as QSopt_ex or SoPlex in exact mode.",
"section": "Starting, and what real codes do",
"slide": "Tolerances, and what they hide",
"keys": [
"exact rational lp solver"
]
},
{
"term_html": "<code>LPResult</code>",
"html": "The result type, carrying status, solution, and the final <code>tableau</code> that unit 03 reads duals from.",
"section": "In the lab",
"slide": "",
"keys": [
"~lpresult~"
]
},
{
"term_html": "<code>Cycling</code>",
"html": "The exception the simplex loop raises when a basis repeats.",
"section": "In the lab",
"slide": "",
"keys": [
"~cycling~"
]
}
];
