// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "matching",
"html": "A set of edges no two of which share a vertex.",
"section": "Bipartite cardinality",
"slide": "",
"keys": [
"matching"
]
},
{
"term_html": "free (exposed) vertex",
"html": "A vertex no matching edge touches.",
"section": "Bipartite cardinality",
"slide": "Augmenting paths: Berge's theorem",
"keys": [
"free (exposed) vertex"
]
},
{
"term_html": "alternating path",
"html": "A path whose edges alternate between outside and inside the matching.",
"section": "Bipartite cardinality",
"slide": "Augmenting paths: Berge's theorem",
"keys": [
"alternating path"
]
},
{
"term_html": "augmenting path",
"html": "An alternating path with both ends free. Flipping it, \\(M \\mathbin{\\triangle} P\\), gives a matching with one more edge.",
"section": "Bipartite cardinality",
"slide": "Augmenting paths: Berge's theorem",
"keys": [
"augmenting path"
]
},
{
"term_html": "symmetric difference \\(\\triangle\\)",
"html": "The edges in exactly one of two sets.",
"section": "Bipartite cardinality",
"slide": "Augmenting paths: Berge's theorem",
"keys": [
"symmetric difference \\triangle"
]
},
{
"term_html": "Berge's theorem",
"html": "A matching is maximum iff it has no augmenting path. Holds in every graph.",
"section": "Bipartite cardinality",
"slide": "Augmenting paths: Berge's theorem",
"keys": [
"berge's theorem"
]
},
{
"term_html": "maximum vs maximal matching",
"html": "Largest possible, versus one no edge can be added to.",
"section": "Bipartite cardinality",
"slide": "Augmenting paths: Berge's theorem",
"keys": [
"maximum vs maximal matching"
]
},
{
"term_html": "König's theorem",
"html": "In a bipartite graph, maximum matching size equals minimum vertex cover size (1931).",
"section": "Bipartite cardinality",
"slide": "König and Hall: min–max theorems",
"keys": [
"könig's theorem"
]
},
{
"term_html": "König's cover construction",
"html": "From a maximum matching, let \\(Z\\) be the vertices reachable from free left vertices by alternating paths; the cover is \\((L \\setminus Z) \\cup (R \\cap Z)\\). Lab step 2.",
"section": "Bipartite cardinality",
"slide": "König and Hall: min–max theorems",
"keys": [
"könig's cover construction"
]
},
{
"term_html": "neighbourhood \\(N(S)\\)",
"html": "The vertices adjacent to some vertex of \\(S\\).",
"section": "Bipartite cardinality",
"slide": "König and Hall: min–max theorems",
"keys": [
"neighbourhood n(s)"
]
},
{
"term_html": "Hall's theorem",
"html": "A matching saturating the left side exists iff \\(|N(S)| \\ge |S|\\) for every left set \\(S\\) (1935). A set with too few neighbours is the certificate of impossibility.",
"section": "Bipartite cardinality",
"slide": "König and Hall: min–max theorems",
"keys": [
"hall's theorem"
]
},
{
"term_html": "saturate",
"html": "To match every vertex of a set.",
"section": "Bipartite cardinality",
"slide": "König and Hall: min–max theorems",
"keys": [
"saturate"
]
},
{
"term_html": "perfect matching",
"html": "One that saturates every vertex.",
"section": "Bipartite cardinality",
"slide": "König and Hall: min–max theorems",
"keys": [
"perfect matching"
]
},
{
"term_html": "Hopcroft–Karp",
"html": "Phases of BFS layering from all free left vertices, then a DFS taking a maximal set of vertex-disjoint shortest augmenting paths. \\(O(\\sqrt V)\\) phases, \\(O(E \\sqrt V)\\) total; Dinic on the unit-capacity network.",
"section": "Bipartite cardinality",
"slide": "Hopcroft–Karp: many shortest paths per phase",
"keys": [
"hopcroft–karp"
]
},
{
"term_html": "assignment problem",
"html": "Match \\(n\\) rows to \\(n\\) columns at minimum total cost.",
"section": "Assignment",
"slide": "The assignment LP and its dual",
"keys": [
"assignment problem"
]
},
{
"term_html": "assignment dual",
"html": "\\(\\max \\sum_i u_i + \\sum_j v_j\\) subject to \\(u_i + v_j \\le c_{ij}\\).",
"section": "Assignment",
"slide": "The assignment LP and its dual",
"keys": [
"assignment dual"
]
},
{
"term_html": "dual potentials \\((u, v)\\)",
"html": "The dual variables, one per row and column.",
"section": "Assignment",
"slide": "The assignment LP and its dual",
"keys": [
"dual potentials (u, v)"
]
},
{
"term_html": "reduced cost (assignment)",
"html": "\\(c_{ij} - u_i - v_j\\). Dual feasibility means all are nonnegative.",
"section": "Assignment",
"slide": "The assignment LP and its dual",
"keys": [
"reduced cost (assignment)",
"reduced cost",
"assignment"
]
},
{
"term_html": "doubly stochastic matrix",
"html": "A nonnegative matrix with every row and column summing to 1.",
"section": "Assignment",
"slide": "The assignment LP and its dual",
"keys": [
"doubly stochastic matrix"
]
},
{
"term_html": "Birkhoff–von Neumann theorem",
"html": "The doubly stochastic matrices are the convex hull of the permutation matrices, so the assignment LP has integral vertices.",
"section": "Assignment",
"slide": "The assignment LP and its dual",
"keys": [
"birkhoff–von neumann theorem"
]
},
{
"term_html": "optimality certificate (assignment)",
"html": "A permutation \\(\\sigma\\) plus dual-feasible \\((u, v)\\) with \\(u_i + v_{\\sigma(i)} = c_{i\\sigma(i)}\\) for every \\(i\\). Checked in \\(O(n^2)\\) without a solver. Lab step 4.",
"section": "Assignment",
"slide": "The assignment LP and its dual",
"keys": [
"optimality certificate (assignment)",
"optimality certificate",
"assignment"
]
},
{
"term_html": "tight edge",
"html": "One with zero reduced cost, \\(c_{ij} = u_i + v_j\\).",
"section": "Assignment",
"slide": "The Hungarian method is primal–dual",
"keys": [
"tight edge"
]
},
{
"term_html": "Hungarian method",
"html": "Keep dual-feasible potentials and a partial assignment on tight edges; grow an alternating tree, and when stuck, shift the duals by the smallest reduced cost \\(\\delta\\) to make a new edge tight. \\(O(n^3)\\).",
"section": "Assignment",
"slide": "The Hungarian method is primal–dual",
"keys": [
"hungarian method"
]
},
{
"term_html": "primal–dual method",
"html": "An algorithm that maintains a dual solution explicitly and uses it to steer the primal; the pattern of units 11 and 24.",
"section": "Assignment",
"slide": "The Hungarian method is primal–dual",
"keys": [
"primal–dual method"
]
},
{
"term_html": "\\(\\mathrm{minv}\\)",
"html": "The smallest reduced cost into each column from the tree; it makes each dual step \\(O(n)\\). Dijkstra's tentative distance in disguise.",
"section": "Assignment",
"slide": "The Hungarian method is primal–dual",
"keys": [
"\\mathrm{minv}"
]
},
{
"term_html": "virtual column 0",
"html": "The lab's trick of pretending the new row is matched to a dummy column, so every row enters through the same loop.",
"section": "Assignment",
"slide": "The Hungarian method is primal–dual",
"keys": [
"virtual column 0"
]
},
{
"term_html": "cost scaling",
"html": "The push–relabel family OR-Tools uses for assignment, suited to large sparse graphs.",
"section": "Assignment",
"slide": "How much faster is production code?",
"keys": [
"cost scaling"
]
},
{
"term_html": "odd component",
"html": "A connected component with an odd number of vertices.",
"section": "General graphs",
"slide": "Tutte's theorem, and why the bipartite search fails",
"keys": [
"odd component"
]
},
{
"term_html": "Tutte's theorem",
"html": "\\(G\\) has a perfect matching iff \\(\\mathrm{odd}(G - U) \\le |U|\\) for every vertex set \\(U\\) (1947).",
"section": "General graphs",
"slide": "Tutte's theorem, and why the bipartite search fails",
"keys": [
"tutte's theorem"
]
},
{
"term_html": "Tutte–Berge formula",
"html": "\\(\\nu(G) = \\min_U \\tfrac12 (|V| + |U| - \\mathrm{odd}(G - U))\\).",
"section": "General graphs",
"slide": "Tutte's theorem, and why the bipartite search fails",
"keys": [
"tutte–berge formula"
]
},
{
"term_html": "Tutte set",
"html": "The \\(U\\) attaining the formula: the general-graph certificate that no larger matching exists.",
"section": "General graphs",
"slide": "Tutte's theorem, and why the bipartite search fails",
"keys": [
"tutte set"
]
},
{
"term_html": "blossom",
"html": "An odd alternating cycle reached at its base.",
"section": "General graphs",
"slide": "Edmonds 1965: shrink the blossom",
"keys": [
"blossom"
]
},
{
"term_html": "base",
"html": "The blossom vertex where the alternating path enters the cycle.",
"section": "General graphs",
"slide": "Edmonds 1965: shrink the blossom",
"keys": [
"base"
]
},
{
"term_html": "even (outer) and odd (inner) vertices",
"html": "Vertices at even or odd distance from a free root in an alternating tree.",
"section": "General graphs",
"slide": "Edmonds 1965: shrink the blossom",
"keys": [
"even (outer) and odd (inner) vertices"
]
},
{
"term_html": "contraction \\(G / B\\)",
"html": "Shrinking a blossom to one vertex. \\(M\\) has an augmenting path in \\(G\\) iff \\(M/B\\) has one in \\(G/B\\).",
"section": "General graphs",
"slide": "Edmonds 1965: shrink the blossom",
"keys": [
"contraction g / b"
]
},
{
"term_html": "blossom algorithm",
"html": "Grow alternating trees; contract a blossom when two even vertices of the same tree meet; augment when a free vertex is reached, expanding blossoms along the path. \\(O(V^3)\\); \\(O(E \\sqrt V)\\) by Micali–Vazirani.",
"section": "General graphs",
"slide": "Edmonds 1965: shrink the blossom",
"keys": [
"blossom algorithm"
]
},
{
"term_html": "<code>base[v]</code> relabelling",
"html": "The lab's contraction: each vertex records the base of its outermost blossom, instead of building \\(G / B\\).",
"section": "General graphs",
"slide": "Edmonds 1965: shrink the blossom",
"keys": [
"~base[v]~ relabelling"
]
},
{
"term_html": "Edmonds–Cobham thesis",
"html": "Polynomial running time is the right formal notion of a good algorithm (1965). Why P is the dividing line of unit 22.",
"section": "General graphs",
"slide": "Edmonds 1965: shrink the blossom",
"keys": [
"edmonds–cobham thesis"
]
},
{
"term_html": "matching polytope",
"html": "Degree constraints plus odd-set inequalities \\(x(E[S]) \\le (|S| - 1)/2\\) for odd \\(S\\). The convex hull of matchings (Edmonds 1965).",
"section": "General graphs",
"slide": "The matching polytope",
"keys": [
"matching polytope"
]
},
{
"term_html": "\\(E[S]\\)",
"html": "The edges with both endpoints in \\(S\\).",
"section": "General graphs",
"slide": "The matching polytope",
"keys": [
"e[s]"
]
},
{
"term_html": "Padberg–Rao separation",
"html": "Finding a violated odd-set inequality with a minimum odd cut via a Gomory–Hu tree.",
"section": "General graphs",
"slide": "The matching polytope",
"keys": [
"padberg–rao separation"
]
},
{
"term_html": "weighted blossom algorithm",
"html": "The primal–dual method on the matching polytope, with a dual variable on every odd set. Not built in the lab.",
"section": "General graphs",
"slide": "The matching polytope",
"keys": [
"weighted blossom algorithm"
]
},
{
"term_html": "double cover",
"html": "The bipartite graph with two copies of every vertex, used in the lab to compute the degree-constraint LP's optimum.",
"section": "General graphs",
"slide": "The matching polytope",
"keys": [
"double cover"
]
},
{
"term_html": "stable matching",
"html": "A perfect matching with no blocking pair.",
"section": "Stable matching",
"slide": "Gale–Shapley",
"keys": [
"stable matching"
]
},
{
"term_html": "blocking pair",
"html": "A proposer and receiver who both prefer each other to their partners.",
"section": "Stable matching",
"slide": "Gale–Shapley",
"keys": [
"blocking pair"
]
},
{
"term_html": "Gale–Shapley algorithm",
"html": "Free proposers propose down their lists; receivers keep the best offer so far. At most \\(n^2\\) proposals.",
"section": "Stable matching",
"slide": "Gale–Shapley",
"keys": [
"gale–shapley algorithm"
]
},
{
"term_html": "proposer-optimal",
"html": "Every proposer gets their best stable partner, and every receiver their worst.",
"section": "Stable matching",
"slide": "Gale–Shapley",
"keys": [
"proposer-optimal"
]
},
{
"term_html": "strategy-proof (for proposers)",
"html": "Truthful ranking is a dominant strategy for proposers, but not for receivers.",
"section": "Stable matching",
"slide": "Gale–Shapley",
"keys": [
"strategy-proof (for proposers)",
"strategy-proof",
"for proposers"
]
}
];
