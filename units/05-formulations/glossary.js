// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "MILP",
"html": "A mixed-integer linear program, \\(\\min\\{c^\\top x : Ax \\le b,\\ x_j \\in \\mathbb{Z} \\text{ for } j \\in I\\}\\).",
"section": "Formulations and relaxations",
"slide": "Integer programs and their LP relaxation",
"keys": [
"milp"
]
},
{
"term_html": "IP",
"html": "A MILP in which every variable is integer.",
"section": "Formulations and relaxations",
"slide": "Integer programs and their LP relaxation",
"keys": [
"ip"
]
},
{
"term_html": "LP relaxation",
"html": "The MILP with integrality dropped. Its optimum \\(z_{LP}\\) is a lower bound: \\(z_{LP} \\le z_{IP}\\).",
"section": "Formulations and relaxations",
"slide": "Integer programs and their LP relaxation",
"keys": [
"lp relaxation"
]
},
{
"term_html": "integrality gap",
"html": "Of an instance, \\(z_{IP} - z_{LP}\\) or the ratio \\(z_{IP} / z_{LP}\\). Of a formulation for a problem class, the worst ratio over all instances (unit 24).",
"section": "Formulations and relaxations",
"slide": "Integer programs and their LP relaxation",
"keys": [
"integrality gap"
]
},
{
"term_html": "pruning",
"html": "Discarding a branch whose LP bound is no better than the best known solution (unit 07).",
"section": "Formulations and relaxations",
"slide": "Integer programs and their LP relaxation",
"keys": [
"pruning"
]
},
{
"term_html": "incumbent",
"html": "The best integer solution found so far.",
"section": "Formulations and relaxations",
"slide": "Integer programs and their LP relaxation",
"keys": [
"incumbent"
]
},
{
"term_html": "global bound",
"html": "The best lower bound proved so far. Optimality is proved when it meets the incumbent.",
"section": "Formulations and relaxations",
"slide": "Integer programs and their LP relaxation",
"keys": [
"global bound"
]
},
{
"term_html": "formulation",
"html": "A polyhedron \\(P\\) whose integer points are exactly the solutions, \\(P \\cap \\mathbb{Z}^n = S\\).",
"section": "Formulations and relaxations",
"slide": "Formulations are polyhedra, and some are better",
"keys": [
"formulation"
]
},
{
"term_html": "stronger formulation",
"html": "\\(P_2\\) is at least as strong as \\(P_1\\) if \\(P_2 \\subseteq P_1\\). Its bound is then at least as good for every objective. Two formulations can also be incomparable.",
"section": "Formulations and relaxations",
"slide": "Formulations are polyhedra, and some are better",
"keys": [
"stronger formulation"
]
},
{
"term_html": "ideal formulation",
"html": "\\(\\mathrm{conv}(S)\\), the convex hull of the solutions. Over it the LP optimum is integral, so the MILP is an LP. Usually exponentially large and as hard to find as the problem.",
"section": "Formulations and relaxations",
"slide": "Formulations are polyhedra, and some are better",
"keys": [
"ideal formulation"
]
},
{
"term_html": "Meyer's theorem",
"html": "For rational data, \\(\\mathrm{conv}(S)\\) is a polyhedron (1974). With irrational data it need not be.",
"section": "Formulations and relaxations",
"slide": "Formulations are polyhedra, and some are better",
"keys": [
"meyer's theorem"
]
},
{
"term_html": "big-M constraint",
"html": "\\(x \\le My,\\ y \\in \\{0,1\\}\\), switching a continuous quantity off with a binary.",
"section": "Strength",
"slide": "Big-M, and why the M matters",
"keys": [
"big-m constraint"
]
},
{
"term_html": "valid M",
"html": "Any \\(M\\) at least the true upper bound \\(u\\) on \\(x\\).",
"section": "Strength",
"slide": "Big-M, and why the M matters",
"keys": [
"valid m"
]
},
{
"term_html": "tightest valid M",
"html": "The best upper bound on \\(x\\) you can prove. A larger \\(M\\) lets the LP set \\(y = x/M\\), opening a facility \"a little\" and weakening the bound; it also mixes magnitudes in one constraint, inviting unit 02's tolerance problems.",
"section": "Strength",
"slide": "Big-M, and why the M matters",
"keys": [
"tightest valid m"
]
},
{
"term_html": "indicator constraint",
"html": "\\(y = 1 \\Rightarrow a^\\top x \\le b\\), given to the solver directly so it handles the switch by branching or by choosing \\(M\\) itself.",
"section": "Strength",
"slide": "Big-M, and why the M matters",
"keys": [
"indicator constraint"
]
},
{
"term_html": "disjunctive formulation",
"html": "The convex hull of a union of polyhedra, obtained by copying variables (Balas 1979).",
"section": "Strength",
"slide": "Big-M, and why the M matters",
"keys": [
"disjunctive formulation"
]
},
{
"term_html": "UFL",
"html": "Uncapacitated facility location: choose facilities to open and assign every customer, minimizing opening plus service cost.",
"section": "Strength",
"slide": "Big-M, and why the M matters",
"keys": [
"ufl"
]
},
{
"term_html": "aggregated formulation",
"html": "One linking constraint per facility, \\(\\sum_j x_{ij} \\le C y_i\\).",
"section": "Strength",
"slide": "Aggregated against disaggregated",
"keys": [
"aggregated formulation"
]
},
{
"term_html": "disaggregated formulation",
"html": "One linking constraint per facility–customer pair, \\(x_{ij} \\le y_i\\). Strictly stronger: its constraints sum to the aggregated ones, and it forbids \\(y_i = 1/C\\) for a facility serving one customer.",
"section": "Strength",
"slide": "Aggregated against disaggregated",
"keys": [
"disaggregated formulation"
]
},
{
"term_html": "capacitated facility location (CFL)",
"html": "UFL with capacities, \\(\\sum_j d_j x_{ij} \\le u_i y_i\\).",
"section": "Strength",
"slide": "When a constraint is implied, and still helps",
"keys": [
"capacitated facility location (cfl)",
"capacitated facility location",
"cfl"
]
},
{
"term_html": "linking constraint",
"html": "\\(x_{ij} \\le y_i\\) added to CFL. Removes no integer solution but cuts off fractional ones.",
"section": "Strength",
"slide": "When a constraint is implied, and still helps",
"keys": [
"linking constraint"
]
},
{
"term_html": "cover constraint",
"html": "\\(\\sum_i u_i y_i \\ge \\sum_j d_j\\): open capacity must cover total demand. Valid, and it tightens the relaxation.",
"section": "Strength",
"slide": "When a constraint is implied, and still helps",
"keys": [
"cover constraint"
]
},
{
"term_html": "valid inequality",
"html": "One satisfied by every integer solution. Adding it never changes the MILP and may tighten its relaxation. All of unit 08 in one sentence.",
"section": "Strength",
"slide": "When a constraint is implied, and still helps",
"keys": [
"valid inequality"
]
},
{
"term_html": "extended formulation",
"html": "A description in extra variables whose projection is the polytope you want. Can replace exponentially many facets with polynomially many constraints.",
"section": "Strength",
"slide": "Extended formulations: add variables, lose facets",
"keys": [
"extended formulation"
]
},
{
"term_html": "permutahedron",
"html": "The convex hull of all permutations of \\((1, \\dots, n)\\). \\(2^n - 2\\) facets, but an \\(O(n \\log n)\\) extended formulation via a sorting network.",
"section": "Strength",
"slide": "Extended formulations: add variables, lose facets",
"keys": [
"permutahedron"
]
},
{
"term_html": "extension complexity limits",
"html": "The TSP, cut and stable-set polytopes have no polynomial-size extended formulation (Fiorini et al. 2012), nor does the perfect matching polytope (Rothvoss 2014), though matching is polynomial.",
"section": "Strength",
"slide": "Extended formulations: add variables, lose facets",
"keys": [
"extension complexity limits"
]
},
{
"term_html": "nonnegative rank",
"html": "The rank measure of the slack matrix that equals the size of the smallest extended formulation. <em>Slide notes.</em>",
"section": "Strength",
"slide": "Extended formulations: add variables, lose facets",
"keys": [
"nonnegative rank"
]
},
{
"term_html": "symmetry (formulation defect)",
"html": "A model in which every solution appears many times under relabelling, such as \\(K!\\) copies of each bin packing. Branch and bound proves the same thing once per copy.",
"section": "Strength",
"slide": "Symmetry is a formulation defect",
"keys": [
"symmetry (formulation defect)",
"symmetry",
"formulation defect"
]
},
{
"term_html": "symmetry-breaking constraints",
"html": "Constraints that pick one representative, such as \\(y_1 \\ge y_2 \\ge \\dots\\), or item \\(i\\) only in bins \\(\\le i\\).",
"section": "Strength",
"slide": "Symmetry is a formulation defect",
"keys": [
"symmetry-breaking constraints"
]
},
{
"term_html": "orbital fixing",
"html": "A solver technique that fixes variables using the symmetry group it detects in the model.",
"section": "Strength",
"slide": "Symmetry is a formulation defect",
"keys": [
"orbital fixing"
]
},
{
"term_html": "presolve",
"html": "The solver's rewriting of the model before solving: removing, tightening and substituting.",
"section": "What solvers do with your model",
"slide": "Presolve and cuts repair weak models",
"keys": [
"presolve"
]
},
{
"term_html": "bound tightening",
"html": "A presolve reduction that shrinks variable bounds, and so \\(M\\), to what is provable.",
"section": "What solvers do with your model",
"slide": "Presolve and cuts repair weak models",
"keys": [
"bound tightening"
]
},
{
"term_html": "implied bound cut",
"html": "A cut that recovers \\(x_{ij} \\le y_i\\) from bounds and linking constraints.",
"section": "What solvers do with your model",
"slide": "Presolve and cuts repair weak models",
"keys": [
"implied bound cut"
]
},
{
"term_html": "knapsack cover cut, flow cover cut",
"html": "Cut families that recover capacity structure (unit 08).",
"section": "What solvers do with your model",
"slide": "Presolve and cuts repair weak models",
"keys": [
"knapsack cover cut, flow cover cut",
"knapsack cover cut",
"flow cover cut"
]
},
{
"term_html": "node count",
"html": "The number of branch-and-bound nodes solved. Within one solver, a good measure of formulation strength; not comparable across solvers.",
"section": "What solvers do with your model",
"slide": "Presolve and cuts repair weak models",
"keys": [
"node count"
]
},
{
"term_html": "robust vs fragile model",
"html": "Strong before the solver touches it, versus strong only because presolve quietly repaired it.",
"section": "What solvers do with your model",
"slide": "Presolve and cuts repair weak models",
"keys": [
"robust vs fragile model"
]
},
{
"term_html": "MIPLIB",
"html": "The standard library of MIP instances with known optima, used to test solvers.",
"section": "What solvers do with your model",
"slide": "A caught bug, and why brute force stays in the course",
"keys": [
"miplib"
]
},
{
"term_html": "<code>MILP</code>",
"html": "A min problem as plain tuples, in <code>colib.mip</code>.",
"section": "In the lab",
"slide": "",
"keys": [
"~milp~"
]
},
{
"term_html": "gap closed",
"html": "\\((z_{\\text{strong}} - z_{\\text{weak}}) / (z_{IP} - z_{\\text{weak}})\\): the fraction of the weak formulation's gap that the strong one closes. Lab step 5.",
"section": "In the lab",
"slide": "",
"keys": [
"gap closed"
]
}
];
