// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "valid inequality",
"html": "\\(a^\\top x \\le \\beta\\) satisfied by every \\(x \\in S\\).",
"section": "General cuts",
"slide": "Valid inequalities and separation",
"keys": [
"valid inequality"
]
},
{
"term_html": "cut (cutting plane)",
"html": "A valid inequality violated by the current LP point \\(x^*\\): \\(a^\\top x^* &gt; \\beta\\).",
"section": "General cuts",
"slide": "Valid inequalities and separation",
"keys": [
"cut (cutting plane)",
"cut",
"cutting plane"
]
},
{
"term_html": "facet of \\(\\mathrm{conv}(S)\\)",
"html": "The strongest kind of valid inequality; the hull is exactly the intersection of its facets.",
"section": "General cuts",
"slide": "Valid inequalities and separation",
"keys": [
"facet of \\mathrm{conv}(s)"
]
},
{
"term_html": "separation problem",
"html": "Given \\(x^*\\) and a family of valid inequalities, find a member violated by \\(x^*\\) or prove none exists. A family with hard separation is useless in practice.",
"section": "General cuts",
"slide": "Valid inequalities and separation",
"keys": [
"separation problem"
]
},
{
"term_html": "cutting-plane method",
"html": "Solve the LP, separate, add the cut, re-solve with the dual simplex; branch when no cut is found.",
"section": "General cuts",
"slide": "Valid inequalities and separation",
"keys": [
"cutting-plane method"
]
},
{
"term_html": "Chvátal–Gomory (CG) cut",
"html": "For \\(Ax \\le b\\), \\(x \\ge 0\\) integer and any \\(u \\ge 0\\): \\(\\lfloor u^\\top A \\rfloor x \\le \\lfloor u^\\top b \\rfloor\\). Farkas' combination plus one rounding step.",
"section": "General cuts",
"slide": "Chvátal–Gomory rounding",
"keys": [
"chvátal–gomory (cg) cut"
]
},
{
"term_html": "CG closure",
"html": "The polyhedron obtained by adding every CG cut at once. Repeating finitely often reaches \\(\\mathrm{conv}(S)\\) for bounded pure IPs.",
"section": "General cuts",
"slide": "Chvátal–Gomory rounding",
"keys": [
"cg closure"
]
},
{
"term_html": "CG rank",
"html": "How many rounds of closure an inequality needs. Edmonds' odd-set inequalities have rank 1; some TSP inequalities have rank growing with \\(n\\).",
"section": "General cuts",
"slide": "Chvátal–Gomory rounding",
"keys": [
"cg rank"
]
},
{
"term_html": "cutting-plane proof",
"html": "A CG derivation viewed as a proof system for integer infeasibility.",
"section": "General cuts",
"slide": "Chvátal–Gomory rounding",
"keys": [
"cutting-plane proof"
]
},
{
"term_html": "fractional part \\(f(v)\\)",
"html": "\\(v - \\lfloor v \\rfloor\\).",
"section": "General cuts",
"slide": "Gomory's cut, read off the tableau",
"keys": [
"fractional part f(v)"
]
},
{
"term_html": "Gomory fractional cut",
"html": "From a tableau row \\(x_i + \\sum_{j \\in N} \\bar a_{ij} z_j = \\bar b_i\\) with \\(\\bar b_i\\) fractional: \\(\\sum_{j \\in N} f(\\bar a_{ij}) z_j \\ge f(\\bar b_i)\\). A CG cut with multipliers from row \\(i\\) of \\(A_B^{-1}\\). Needs every variable, slacks included, integral.",
"section": "General cuts",
"slide": "Gomory's cut, read off the tableau",
"keys": [
"gomory fractional cut"
]
},
{
"term_html": "Gomory mixed-integer (GMI) cut",
"html": "The version for MILPs, with a different coefficient formula for continuous variables. Among the most effective cuts in modern solvers.",
"section": "General cuts",
"slide": "Gomory's cut, read off the tableau",
"keys": [
"gomory mixed-integer (gmi) cut"
]
},
{
"term_html": "stalling",
"html": "Successive cut rounds improving the bound less and less while coefficients and density grow.",
"section": "General cuts",
"slide": "Convergence in theory, stalling in practice",
"keys": [
"stalling"
]
},
{
"term_html": "coefficient growth",
"html": "The number of digits in cut coefficients rising round after round; in floating point it makes cuts invalid.",
"section": "General cuts",
"slide": "Convergence in theory, stalling in practice",
"keys": [
"coefficient growth"
]
},
{
"term_html": "dynamism",
"html": "The ratio of largest to smallest coefficient in a constraint; solvers discard cuts where it is too high.",
"section": "General cuts",
"slide": "Convergence in theory, stalling in practice",
"keys": [
"dynamism"
]
},
{
"term_html": "cover",
"html": "For a knapsack constraint \\(\\sum_j w_j x_j \\le c\\), a set \\(C\\) with \\(\\sum_{j \\in C} w_j &gt; c\\): not all of it fits.",
"section": "Structural cuts",
"slide": "Knapsack cover inequalities",
"keys": [
"cover"
]
},
{
"term_html": "cover inequality",
"html": "\\(\\sum_{j \\in C} x_j \\le |C| - 1\\).",
"section": "Structural cuts",
"slide": "Knapsack cover inequalities",
"keys": [
"cover inequality"
]
},
{
"term_html": "minimal cover",
"html": "A cover from which removing any item makes it fit.",
"section": "Structural cuts",
"slide": "Knapsack cover inequalities",
"keys": [
"minimal cover"
]
},
{
"term_html": "cover separation",
"html": "\\(x^*\\) violates the cover inequality for \\(C\\) iff \\(\\sum_{j \\in C} (1 - x_j^*) &lt; 1\\), so separation is a knapsack problem: minimize that sum over covers. Exact by DP over integer weights (lab step 3); solvers usually do it greedily.",
"section": "Structural cuts",
"slide": "Knapsack cover inequalities",
"keys": [
"cover separation"
]
},
{
"term_html": "lifting",
"html": "Strengthening a valid inequality for a restriction (some variables fixed to 0) by bringing the variables back one at a time, each with the largest coefficient that keeps it valid.",
"section": "Structural cuts",
"slide": "Lifting: strengthening a cut variable by variable",
"keys": [
"lifting"
]
},
{
"term_html": "sequential up-lifting",
"html": "\\(\\alpha_j = r - \\max\\{\\sum_{\\text{lifted}} \\alpha_i x_i : \\sum w_i x_i \\le c - w_j\\}\\) for the next \\(j \\notin C\\), where \\(r\\) is the right-hand side.",
"section": "Structural cuts",
"slide": "Lifting: strengthening a cut variable by variable",
"keys": [
"sequential up-lifting"
]
},
{
"term_html": "lifted cover inequality",
"html": "A minimal cover inequality after sequential lifting. Always a facet of the knapsack polytope; the lifting order can change which.",
"section": "Structural cuts",
"slide": "Lifting: strengthening a cut variable by variable",
"keys": [
"lifted cover inequality"
]
},
{
"term_html": "mixed-integer rounding (MIR) cut",
"html": "A rounding formula applied to an aggregation of constraints.",
"section": "Structural cuts",
"slide": "The families solvers actually run",
"keys": [
"mixed-integer rounding (mir) cut"
]
},
{
"term_html": "aggregation",
"html": "A combination of several constraints into one, used as the base for MIR cuts. Sees structure no single constraint shows.",
"section": "Structural cuts",
"slide": "The families solvers actually run",
"keys": [
"aggregation"
]
},
{
"term_html": "flow cover cut",
"html": "A cut from fixed-charge flow constraints \\(x \\le uy\\).",
"section": "Structural cuts",
"slide": "The families solvers actually run",
"keys": [
"flow cover cut"
]
},
{
"term_html": "conflict graph",
"html": "A graph on binaries (and their complements) with an edge wherever two cannot both be 1.",
"section": "Structural cuts",
"slide": "The families solvers actually run",
"keys": [
"conflict graph"
]
},
{
"term_html": "clique cut",
"html": "\\(\\sum_{j \\in K} x_j \\le 1\\) for a clique \\(K\\) of the conflict graph.",
"section": "Structural cuts",
"slide": "The families solvers actually run",
"keys": [
"clique cut"
]
},
{
"term_html": "odd cycle cut",
"html": "A cut from an odd cycle in the conflict graph.",
"section": "Structural cuts",
"slide": "The families solvers actually run",
"keys": [
"odd cycle cut"
]
},
{
"term_html": "zero-half cut",
"html": "A CG cut with every \\(u_i \\in \\{0, \\tfrac12\\}\\), separated as a parity problem.",
"section": "Structural cuts",
"slide": "The families solvers actually run",
"keys": [
"zero-half cut"
]
},
{
"term_html": "implied bound cut",
"html": "A cut from bounds and implications, such as recovering \\(x \\le uy\\).",
"section": "Structural cuts",
"slide": "The families solvers actually run",
"keys": [
"implied bound cut"
]
},
{
"term_html": "branch-and-cut",
"html": "Branch and bound with cutting planes added at the root and at nodes.",
"section": "Branch-and-cut",
"slide": "Cut loops and cut management",
"keys": [
"branch-and-cut"
]
},
{
"term_html": "root cut loop",
"html": "Rounds of solve, separate, select and add at the root, until the bound stops moving enough.",
"section": "Branch-and-cut",
"slide": "Cut loops and cut management",
"keys": [
"root cut loop"
]
},
{
"term_html": "efficacy",
"html": "How far a cut moves \\(x^*\\): \\((a^\\top x^* - \\beta) / \\|a\\|\\).",
"section": "Branch-and-cut",
"slide": "Cut loops and cut management",
"keys": [
"efficacy"
]
},
{
"term_html": "parallelism filter",
"html": "Skipping a cut nearly parallel to one already chosen.",
"section": "Branch-and-cut",
"slide": "Cut loops and cut management",
"keys": [
"parallelism filter"
]
},
{
"term_html": "cut pool",
"html": "Where cuts that have been slack for several rounds are kept after removal from the LP, ready to be re-added if violated again.",
"section": "Branch-and-cut",
"slide": "Cut loops and cut management",
"keys": [
"cut pool"
]
},
{
"term_html": "aging",
"html": "Counting how many consecutive rounds a cut has been slack, and dropping it once that exceeds a limit. The lab's <code>age_pool</code>: a binding cut resets to age 0, a slack one ages by 1.",
"section": "Branch-and-cut",
"slide": "Cut loops and cut management",
"keys": [
"aging"
]
},
{
"term_html": "local cut",
"html": "A cut derived at a node and valid only in its subtree, because it uses that node's bound changes.",
"section": "Branch-and-cut",
"slide": "Cut loops and cut management",
"keys": [
"local cut"
]
},
{
"term_html": "global cut",
"html": "A cut valid everywhere in the tree.",
"section": "Branch-and-cut",
"slide": "Cut loops and cut management",
"keys": [
"global cut"
]
},
{
"term_html": "root gap closed",
"html": "The share of the root integrality gap the cuts removed.",
"section": "Branch-and-cut",
"slide": "What your cuts were worth, and SCIP's",
"keys": [
"root gap closed"
]
}
];
