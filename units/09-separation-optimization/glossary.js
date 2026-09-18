// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "optimization oracle",
"html": "Given \\(c\\), returns \\(\\arg\\max\\{c^\\top x : x \\in P\\}\\) or reports \\(P = \\emptyset\\). \"Solve the problem for any objective.\"",
"section": "The theorem",
"slide": "Two ways to be given a polytope",
"keys": [
"optimization oracle"
]
},
{
"term_html": "separation oracle",
"html": "Given \\(y\\), certifies \\(y \\in P\\) or returns an inequality valid for \\(P\\) that \\(y\\) violates. \"Find a violated constraint, if there is one.\"",
"section": "The theorem",
"slide": "Two ways to be given a polytope",
"keys": [
"separation oracle"
]
},
{
"term_html": "well-described polyhedron",
"html": "One whose facets have bounded encoding size \\(\\varphi\\), so running times can be polynomial in \\(\\varphi\\) and \\(n\\).",
"section": "The theorem",
"slide": "Two ways to be given a polytope",
"keys": [
"well-described polyhedron"
]
},
{
"term_html": "strong and weak oracles",
"html": "The exact versions above, and versions with an \\(\\varepsilon\\) tolerance used for general convex bodies.",
"section": "The theorem",
"slide": "Two ways to be given a polytope",
"keys": [
"strong and weak oracles"
]
},
{
"term_html": "affine hull",
"html": "The smallest affine space containing \\(P\\). A lower-dimensional polytope contains no ball, so it must be found first.",
"section": "The theorem",
"slide": "Two ways to be given a polytope",
"keys": [
"affine hull"
]
},
{
"term_html": "GLS theorem (separation ⇔ optimization)",
"html": "For a family of well-described polyhedra, optimization is polynomial if and only if separation is (Grötschel, Lovász &amp; Schrijver 1981).",
"section": "The theorem",
"slide": "Grötschel, Lovász & Schrijver (1981)",
"keys": [
"gls theorem (separation ⇔ optimization)",
"gls theorem",
"separation ⇔ optimization"
]
},
{
"term_html": "sliding objective",
"html": "In the ellipsoid method, cutting with the objective, as the constraint \\(c^\\top x \\ge \\gamma\\), when the centre is feasible, to push toward the optimum.",
"section": "The theorem",
"slide": "Grötschel, Lovász & Schrijver (1981)",
"keys": [
"sliding objective"
]
},
{
"term_html": "polar \\(P^\\circ\\)",
"html": "\\(\\{a : a^\\top x \\le 1\\ \\forall x \\in P\\}\\), with \\(0\\) in the interior of \\(P\\). Its vertices are \\(P\\)'s facets and vice versa, so optimizing over \\(P\\) is separating over \\(P^\\circ\\).",
"section": "The theorem",
"slide": "Grötschel, Lovász & Schrijver (1981)",
"keys": [
"polar p^\\circ"
]
},
{
"term_html": "NP-hardness of separation",
"html": "The contrapositive direction: if optimizing over a polytope is NP-hard, so is separating over it. Why TSP codes separate chosen families only.",
"section": "The theorem",
"slide": "Grötschel, Lovász & Schrijver (1981)",
"keys": [
"np-hardness of separation"
]
},
{
"term_html": "submodular function minimization",
"html": "First made polynomial through GLS, via separation over the base polytope (unit 13).",
"section": "The theorem",
"slide": "What it bought",
"keys": [
"submodular function minimization"
]
},
{
"term_html": "theta function",
"html": "Lovász's SDP bound, through which maximum stable set in perfect graphs is polynomial (unit 25). No combinatorial algorithm is known.",
"section": "The theorem",
"slide": "What it bought",
"keys": [
"theta function"
]
},
{
"term_html": "minimum odd cut",
"html": "The separation routine for matching's odd-set inequalities (Padberg &amp; Rao 1982), via Gomory–Hu trees.",
"section": "The theorem",
"slide": "What it bought",
"keys": [
"minimum odd cut"
]
},
{
"term_html": "subtour",
"html": "A cycle through only some of the cities. The degree constraints alone allow a solution made of several disjoint ones.",
"section": "Subtours",
"slide": "The subtour elimination LP",
"keys": [
"subtour"
]
},
{
"term_html": "\\(\\delta(v)\\), \\(\\delta(S)\\)",
"html": "The edges with exactly one endpoint at \\(v\\), or in \\(S\\): the cut around \\(S\\).",
"section": "Subtours",
"slide": "The subtour elimination LP",
"keys": [
"\\delta(v), \\delta(s)",
"\\delta(v)",
"\\delta(s)"
]
},
{
"term_html": "degree constraints",
"html": "\\(\\sum_{e \\in \\delta(v)} x_e = 2\\) for every city.",
"section": "Subtours",
"slide": "The subtour elimination LP",
"keys": [
"degree constraints"
]
},
{
"term_html": "subtour elimination constraint",
"html": "\\(\\sum_{e \\in \\delta(S)} x_e \\ge 2\\) for every proper nonempty \\(S\\): every set must be entered and left. There are \\(2^{n-1} - 1\\).",
"section": "Subtours",
"slide": "The subtour elimination LP",
"keys": [
"subtour elimination constraint"
]
},
{
"term_html": "DFJ formulation",
"html": "Dantzig, Fulkerson &amp; Johnson's 1954 TSP model: degree constraints plus all subtour constraints over edge variables. The first cutting-plane computation.",
"section": "Subtours",
"slide": "The subtour elimination LP",
"keys": [
"dfj formulation"
]
},
{
"term_html": "subtour polytope",
"html": "The LP relaxation of the DFJ formulation; strictly contains the TSP polytope.",
"section": "Subtours",
"slide": "The subtour elimination LP",
"keys": [
"subtour polytope"
]
},
{
"term_html": "support graph",
"html": "The graph of edges with \\(x^*_e &gt; 0\\), weighted by \\(x^*_e\\).",
"section": "Subtours",
"slide": "The subtour elimination LP",
"keys": [
"support graph"
]
},
{
"term_html": "global minimum cut",
"html": "The lightest \\(\\delta(S)\\) over all proper \\(S\\). \\(x^*\\) violates a subtour constraint iff this is below 2.",
"section": "Subtours",
"slide": "Separation is a minimum cut",
"keys": [
"global minimum cut"
]
},
{
"term_html": "connected components check",
"html": "For integer points, a solution of the degree constraints is a union of cycles, and each cycle's vertex set has cut weight 0. Components suffice.",
"section": "Subtours",
"slide": "Separation is a minimum cut",
"keys": [
"connected components check"
]
},
{
"term_html": "Stoer–Wagner algorithm",
"html": "Global minimum cut without flows: build a maximum-adjacency order, record the cut of the last vertex, merge the last two, repeat \\(n - 1\\) times. \\(O(nm + n^2 \\log n)\\).",
"section": "Subtours",
"slide": "Separation is a minimum cut",
"keys": [
"stoer–wagner algorithm"
]
},
{
"term_html": "maximum-adjacency order",
"html": "Repeatedly add the vertex most strongly attached to the vertices already added.",
"section": "Subtours",
"slide": "Separation is a minimum cut",
"keys": [
"maximum-adjacency order"
]
},
{
"term_html": "cut of the phase",
"html": "The last vertex's total attachment in a maximum-adjacency order: a minimum cut separating the last two vertices.",
"section": "Subtours",
"slide": "Separation is a minimum cut",
"keys": [
"cut of the phase"
]
},
{
"term_html": "Gomory–Hu tree",
"html": "A tree encoding all pairwise minimum cuts, built with \\(n - 1\\) max-flow computations (unit 14).",
"section": "Subtours",
"slide": "Separation is a minimum cut",
"keys": [
"gomory–hu tree"
]
},
{
"term_html": "lazy constraint",
"html": "A constraint checked on every candidate integer solution; a violated one rejects the solution and is added. Required for correctness.",
"section": "In practice",
"slide": "Lazy constraints and callbacks",
"keys": [
"lazy constraint"
]
},
{
"term_html": "user cut",
"html": "A constraint separated at fractional LP points to tighten the bound. Optional, for speed only.",
"section": "In practice",
"slide": "Lazy constraints and callbacks",
"keys": [
"user cut"
]
},
{
"term_html": "callback",
"html": "The solver hook where lazy constraints and user cuts are added (Gurobi's <code>cbLazy</code> and <code>cbCut</code>).",
"section": "In practice",
"slide": "Lazy constraints and callbacks",
"keys": [
"callback"
]
},
{
"term_html": "constraint handler",
"html": "SCIP's version, with <code>check</code>, <code>enforce</code> and <code>separate</code> methods.",
"section": "In practice",
"slide": "Lazy constraints and callbacks",
"keys": [
"constraint handler"
]
},
{
"term_html": "enforcement",
"html": "Checking a candidate integer solution against the implicit constraints. Subtour constraints only as user cuts can let a tour made of subtours through.",
"section": "In practice",
"slide": "Lazy constraints and callbacks",
"keys": [
"enforcement"
]
},
{
"term_html": "4/3 conjecture",
"html": "That the subtour LP's integrality gap for metric TSP is \\(\\tfrac43\\). Proved at most \\(\\tfrac32\\); open.",
"section": "In practice",
"slide": "How good is the bound, and how far has this gone?",
"keys": [
"4/3 conjecture"
]
},
{
"term_html": "Held–Karp bound",
"html": "The Lagrangian 1-tree bound, equal to the subtour LP bound (unit 11).",
"section": "In practice",
"slide": "How good is the bound, and how far has this gone?",
"keys": [
"held–karp bound"
]
},
{
"term_html": "comb inequality",
"html": "A family of TSP facets with no known exact polynomial separation, separated heuristically by Concorde.",
"section": "In practice",
"slide": "How good is the bound, and how far has this gone?",
"keys": [
"comb inequality"
]
},
{
"term_html": "Concorde",
"html": "The TSP branch-and-cut code of Applegate, Bixby, Chvátal &amp; Cook, which solved an 85 900-city instance to optimality.",
"section": "In practice",
"slide": "How good is the bound, and how far has this gone?",
"keys": [
"concorde"
]
}
];
