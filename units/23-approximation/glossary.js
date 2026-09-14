// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "approximation algorithm",
"html": "A polynomial algorithm with a proved worst-case ratio \\(\\rho\\) to the optimum.",
"section": "The shape of a guarantee",
"slide": "",
"keys": [
"approximation algorithm"
]
},
{
"term_html": "\\(\\rho\\)-approximation",
"html": "For minimization, \\(\\mathrm{ALG} \\le \\rho \\cdot \\mathrm{OPT}\\) on every instance, with \\(\\rho \\ge 1\\). For maximization written as a fraction of OPT, like 0.878.",
"section": "The shape of a guarantee",
"slide": "",
"keys": [
"\\rho-approximation"
]
},
{
"term_html": "lower bound LB",
"html": "A computable quantity with \\(\\mathrm{LB} \\le \\mathrm{OPT}\\). Every proof here shows \\(\\mathrm{ALG} \\le \\rho \\cdot \\mathrm{LB}\\).",
"section": "The shape of a guarantee",
"slide": "Every proof in this unit has one shape",
"keys": [
"lower bound lb"
]
},
{
"term_html": "limit of a lower bound",
"html": "If some instance has \\(\\mathrm{OPT}/\\mathrm{LB} = r\\), no analysis against that bound proves a ratio below \\(r\\): an integrality gap for bounds that are not LPs.",
"section": "The shape of a guarantee",
"slide": "Every proof in this unit has one shape",
"keys": [
"limit of a lower bound"
]
},
{
"term_html": "tight family",
"html": "Instances on which the algorithm attains its guarantee exactly, showing the analysis cannot be improved.",
"section": "The shape of a guarantee",
"slide": "Every proof in this unit has one shape",
"keys": [
"tight family"
]
},
{
"term_html": "price (set cover)",
"html": "The cost per newly covered element of the set greedy buys, charged to each element it covers.",
"section": "The shape of a guarantee",
"slide": "Greedy set cover and its prices",
"keys": [
"price (set cover)",
"price",
"set cover"
]
},
{
"term_html": "greedy set cover",
"html": "Repeatedly buy the set with the least cost per newly covered element.",
"section": "The shape of a guarantee",
"slide": "Greedy set cover and its prices",
"keys": [
"greedy set cover"
]
},
{
"term_html": "price lemma",
"html": "For every set \\(S\\), \\(\\sum_{e \\in S} \\mathrm{price}_e \\le H_{|S|} c_S\\). Applied to an optimal cover it gives \\(\\mathrm{ALG} \\le H_d \\cdot \\mathrm{OPT}\\), with \\(d\\) the largest set size.",
"section": "The shape of a guarantee",
"slide": "Greedy set cover and its prices",
"keys": [
"price lemma"
]
},
{
"term_html": "dual fitting",
"html": "Scaling a primal algorithm's charges into a feasible LP dual, so the guarantee holds against the LP. What the price lemma really is.",
"section": "The shape of a guarantee",
"slide": "Greedy set cover and its prices",
"keys": [
"dual fitting"
]
},
{
"term_html": "maximal matching",
"html": "A matching no edge can be added to; built by scanning edges and keeping those with both ends free.",
"section": "Packings",
"slide": "Vertex cover by matching; k-center by farthest-first",
"keys": [
"maximal matching"
]
},
{
"term_html": "matching-based vertex cover",
"html": "Take both endpoints of every edge in a maximal matching. A 2-approximation, tight on \\(K_{n,n}\\).",
"section": "Packings",
"slide": "Vertex cover by matching; k-center by farthest-first",
"keys": [
"matching-based vertex cover"
]
},
{
"term_html": "\\(k\\)-center",
"html": "Choose \\(k\\) centres to minimize the largest distance from any point to its nearest centre.",
"section": "Packings",
"slide": "Vertex cover by matching; k-center by farthest-first",
"keys": [
"k-center"
]
},
{
"term_html": "farthest-first traversal",
"html": "Start anywhere, repeatedly add the point farthest from the chosen centres. A 2-approximation for \\(k\\)-center (Gonzalez 1985).",
"section": "Packings",
"slide": "Vertex cover by matching; k-center by farthest-first",
"keys": [
"farthest-first traversal"
]
},
{
"term_html": "packing witness",
"html": "\\(k + 1\\) points pairwise at least \\(r\\) apart; two share an optimal centre, so \\(r \\le 2 \\cdot \\mathrm{OPT}\\).",
"section": "Packings",
"slide": "Vertex cover by matching; k-center by farthest-first",
"keys": [
"packing witness"
]
},
{
"term_html": "metric TSP",
"html": "TSP whose distances satisfy the triangle inequality.",
"section": "Metric TSP",
"slide": "The double tree: 2",
"keys": [
"metric tsp"
]
},
{
"term_html": "triangle inequality",
"html": "\\(d(a, c) \\le d(a, b) + d(b, c)\\). Makes every shortcut no longer.",
"section": "Metric TSP",
"slide": "The double tree: 2",
"keys": [
"triangle inequality"
]
},
{
"term_html": "metric closure",
"html": "Replacing each distance by the shortest-path distance, which forces the triangle inequality.",
"section": "Metric TSP",
"slide": "The double tree: 2",
"keys": [
"metric closure"
]
},
{
"term_html": "minimum spanning tree (MST)",
"html": "A lower bound on OPT: removing one edge of the optimal tour leaves a spanning path.",
"section": "Metric TSP",
"slide": "The double tree: 2",
"keys": [
"minimum spanning tree (mst)",
"minimum spanning tree",
"mst"
]
},
{
"term_html": "Prim's algorithm",
"html": "Grow a spanning tree from one vertex by repeatedly adding the cheapest edge leaving it.",
"section": "Metric TSP",
"slide": "The double tree: 2",
"keys": [
"prim's algorithm"
]
},
{
"term_html": "shortcutting",
"html": "Skipping already-visited vertices in a walk, replacing a path by one direct edge.",
"section": "Metric TSP",
"slide": "The double tree: 2",
"keys": [
"shortcutting"
]
},
{
"term_html": "double-tree algorithm",
"html": "Walk around the MST using every edge twice, then shortcut (a preorder of the tree). A 2-approximation.",
"section": "Metric TSP",
"slide": "The double tree: 2",
"keys": [
"double-tree algorithm"
]
},
{
"term_html": "odd vertices",
"html": "The odd-degree vertices of the MST; always an even number, by the handshake lemma.",
"section": "Metric TSP",
"slide": "Christofides: 3/2",
"keys": [
"odd vertices"
]
},
{
"term_html": "handshake lemma",
"html": "The sum of degrees is twice the number of edges, so the number of odd-degree vertices is even.",
"section": "Metric TSP",
"slide": "Christofides: 3/2",
"keys": [
"handshake lemma"
]
},
{
"term_html": "minimum-weight perfect matching",
"html": "A perfect matching of least total weight; on the odd vertices it costs at most \\(\\mathrm{OPT}/2\\).",
"section": "Metric TSP",
"slide": "Christofides: 3/2",
"keys": [
"minimum-weight perfect matching"
]
},
{
"term_html": "Euler circuit",
"html": "A closed walk using every edge exactly once; exists when every degree is even.",
"section": "Metric TSP",
"slide": "Christofides: 3/2",
"keys": [
"euler circuit"
]
},
{
"term_html": "Hierholzer's algorithm",
"html": "Builds an Euler circuit by splicing together closed walks.",
"section": "Metric TSP",
"slide": "Christofides: 3/2",
"keys": [
"hierholzer's algorithm"
]
},
{
"term_html": "Christofides' algorithm",
"html": "MST, plus a minimum-weight perfect matching on its odd vertices, then an Euler circuit, shortcut. A \\(3/2\\)-approximation (Christofides 1976; Serdyukov 1978).",
"section": "Metric TSP",
"slide": "Christofides: 3/2",
"keys": [
"christofides' algorithm"
]
},
{
"term_html": "Karlin–Klein–Oveis Gharan",
"html": "A \\(3/2 - 10^{-36}\\) approximation for metric TSP (2021), from a max-entropy random spanning tree fitted to the Held–Karp LP.",
"section": "Metric TSP",
"slide": "Christofides: 3/2",
"keys": [
"karlin–klein–oveis gharan"
]
},
{
"term_html": "identical machines makespan",
"html": "Assign \\(n\\) jobs with times \\(p_j\\) to \\(m\\) identical machines, minimizing the largest total load.",
"section": "Scheduling",
"slide": "List scheduling and LPT (Graham 1966, 1969)",
"keys": [
"identical machines makespan"
]
},
{
"term_html": "makespan lower bounds",
"html": "\\(\\mathrm{OPT} \\ge \\sum_j p_j / m\\) and \\(\\mathrm{OPT} \\ge \\max_j p_j\\).",
"section": "Scheduling",
"slide": "List scheduling and LPT (Graham 1966, 1969)",
"keys": [
"makespan lower bounds"
]
},
{
"term_html": "list scheduling",
"html": "Assign each job, in the given order, to the least-loaded machine. \\((2 - 1/m)\\)-approximation.",
"section": "Scheduling",
"slide": "List scheduling and LPT (Graham 1966, 1969)",
"keys": [
"list scheduling"
]
},
{
"term_html": "LPT (longest processing time first)",
"html": "Sort jobs longest first, then list schedule. \\((4/3 - 1/(3m))\\)-approximation.",
"section": "Scheduling",
"slide": "List scheduling and LPT (Graham 1966, 1969)",
"keys": [
"lpt (longest processing time first)",
"lpt",
"longest processing time first"
]
},
{
"term_html": "\\(k\\)-median",
"html": "Open \\(k\\) facilities minimizing the sum of distances from clients to their nearest open one.",
"section": "Scheduling",
"slide": "Local search as an approximation algorithm: k-median",
"keys": [
"k-median"
]
},
{
"term_html": "local search with a guarantee",
"html": "Swapping up to \\(p\\) facilities until no swap improves gives a \\((3 + 2/p)\\)-approximation for \\(k\\)-median (Arya et al. 2004).",
"section": "Scheduling",
"slide": "Local search as an approximation algorithm: k-median",
"keys": [
"local search with a guarantee"
]
},
{
"term_html": "local optimum",
"html": "A solution no move in the neighbourhood improves.",
"section": "Scheduling",
"slide": "Local search as an approximation algorithm: k-median",
"keys": [
"local optimum"
]
}
];
