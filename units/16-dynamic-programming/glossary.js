// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "dynamic programming (DP)",
"html": "Searching a DAG of states in topological order, merging partial solutions that reach the same state.",
"section": "States",
"slide": "DP is a shortest path in a DAG of states",
"keys": [
"dynamic programming (dp)",
"dynamic programming",
"dp"
]
},
{
"term_html": "state",
"html": "A summary of a partial solution holding exactly what the future needs to know. The \"same future\" test.",
"section": "States",
"slide": "DP is a shortest path in a DAG of states",
"keys": [
"state"
]
},
{
"term_html": "transition",
"html": "One decision extending a state, with a cost.",
"section": "States",
"slide": "DP is a shortest path in a DAG of states",
"keys": [
"transition"
]
},
{
"term_html": "DAG",
"html": "A directed acyclic graph; the states and transitions form one.",
"section": "States",
"slide": "DP is a shortest path in a DAG of states",
"keys": [
"dag"
]
},
{
"term_html": "topological order",
"html": "An order of the DAG's nodes with every arc pointing forward.",
"section": "States",
"slide": "DP is a shortest path in a DAG of states",
"keys": [
"topological order"
]
},
{
"term_html": "optimal substructure",
"html": "An optimal path's prefixes are optimal paths to their states. What makes DP correct.",
"section": "States",
"slide": "DP is a shortest path in a DAG of states",
"keys": [
"optimal substructure"
]
},
{
"term_html": "DP running time",
"html": "Number of states times transitions per state.",
"section": "States",
"slide": "DP is a shortest path in a DAG of states",
"keys": [
"dp running time"
]
},
{
"term_html": "reconstruction",
"html": "Recovering the optimal solution, not just its value, by walking the table back.",
"section": "States",
"slide": "DP is a shortest path in a DAG of states",
"keys": [
"reconstruction"
]
},
{
"term_html": "0/1 knapsack DP",
"html": "\\(B_i(c) = \\max(B_{i-1}(c),\\ B_{i-1}(c - w_i) + v_i)\\). \\(O(nC)\\).",
"section": "States",
"slide": "Knapsack in O(nC) — and why that is not P = NP",
"keys": [
"0/1 knapsack dp"
]
},
{
"term_html": "unbounded knapsack",
"html": "Each item may be used any number of times; unit 10's pricing problem.",
"section": "States",
"slide": "Knapsack in O(nC) — and why that is not P = NP",
"keys": [
"unbounded knapsack"
]
},
{
"term_html": "pseudo-polynomial",
"html": "Polynomial in the numeric value \\(C\\) but exponential in its \\(\\log C\\) bits of input. Why \\(O(nC)\\) does not show P = NP.",
"section": "States",
"slide": "Knapsack in O(nC) — and why that is not P = NP",
"keys": [
"pseudo-polynomial"
]
},
{
"term_html": "weakly NP-hard",
"html": "Hard only when the numbers are huge, like knapsack.",
"section": "States",
"slide": "Knapsack in O(nC) — and why that is not P = NP",
"keys": [
"weakly np-hard"
]
},
{
"term_html": "strongly NP-hard",
"html": "Hard even with numbers polynomial in \\(n\\), like bin packing and TSP. No pseudo-polynomial algorithm unless P = NP.",
"section": "States",
"slide": "Knapsack in O(nC) — and why that is not P = NP",
"keys": [
"strongly np-hard"
]
},
{
"term_html": "value-indexed knapsack",
"html": "\\(W_i(p)\\), the least weight achieving value \\(p\\). Rounding the values gives unit 22's FPTAS.",
"section": "States",
"slide": "Knapsack in O(nC) — and why that is not P = NP",
"keys": [
"value-indexed knapsack"
]
},
{
"term_html": "bitmask DP",
"html": "DP whose state includes a subset stored as a bitmask. Masks in increasing order are topologically sorted.",
"section": "Subsets",
"slide": "",
"keys": [
"bitmask dp"
]
},
{
"term_html": "Held–Karp DP",
"html": "\\(D(S, k) = \\min_{j \\in S \\setminus \\{k\\}} D(S \\setminus \\{k\\}, j) + d_{jk}\\): shortest path from city 0 through set \\(S\\) ending at \\(k\\). \\(O(n^2 2^n)\\) time, \\(O(n 2^n)\\) space; works for asymmetric distances.",
"section": "Subsets",
"slide": "Held–Karp (and Bellman), 1962",
"keys": [
"held–karp dp"
]
},
{
"term_html": "MTZ formulation",
"html": "The Miller–Tucker–Zemlin TSP model with ordering variables: compact and very weak.",
"section": "Subsets",
"slide": "Held–Karp (and Bellman), 1962",
"keys": [
"mtz formulation"
]
},
{
"term_html": "tree DP for vertex cover",
"html": "\\(\\mathrm{in}(v) = w_v + \\sum_c \\min(\\mathrm{in}(c), \\mathrm{out}(c))\\), \\(\\mathrm{out}(v) = \\sum_c \\mathrm{in}(c)\\). \\(O(n)\\), because a subtree talks to the rest only through its root.",
"section": "Treewidth",
"slide": "On trees, NP-hard problems become easy",
"keys": [
"tree dp for vertex cover"
]
},
{
"term_html": "separator",
"html": "A vertex set whose removal splits a graph into independent parts.",
"section": "Treewidth",
"slide": "On trees, NP-hard problems become easy",
"keys": [
"separator"
]
},
{
"term_html": "tree decomposition",
"html": "A tree with a bag \\(B_t \\subseteq V\\) per node such that every edge lies in some bag, and the bags containing each vertex form a connected subtree (Robertson–Seymour).",
"section": "Treewidth",
"slide": "Tree decompositions",
"keys": [
"tree decomposition"
]
},
{
"term_html": "bag",
"html": "The vertex set at one node of a tree decomposition. Property 2 makes it a separator.",
"section": "Treewidth",
"slide": "Tree decompositions",
"keys": [
"bag"
]
},
{
"term_html": "width",
"html": "\\(\\max |B_t| - 1\\) of a decomposition. The \\(-1\\) makes trees width 1.",
"section": "Treewidth",
"slide": "Tree decompositions",
"keys": [
"width"
]
},
{
"term_html": "treewidth \\(\\mathrm{tw}(G)\\)",
"html": "The minimum width over all decompositions. Trees 1, cycles 2, the \\(k \\times k\\) grid \\(k\\), \\(K_n\\) \\(n - 1\\).",
"section": "Treewidth",
"slide": "Tree decompositions",
"keys": [
"treewidth \\mathrm{tw}(g)"
]
},
{
"term_html": "\\(k\\)-tree",
"html": "A graph built from a \\((k+1)\\)-clique by repeatedly adding a vertex joined to a \\(k\\)-clique. Treewidth exactly \\(k\\); <em>partial</em> \\(k\\)-trees are its subgraphs.",
"section": "Treewidth",
"slide": "Tree decompositions",
"keys": [
"k-tree"
]
},
{
"term_html": "elimination ordering",
"html": "An order to delete vertices: each vertex's bag is itself plus its current neighbours, which are then joined into a clique. Every decomposition comes from one.",
"section": "Treewidth",
"slide": "Finding decompositions: elimination orderings",
"keys": [
"elimination ordering"
]
},
{
"term_html": "fill-in (elimination)",
"html": "The edges added to make a vertex's neighbours a clique before deleting it. The same object sparse Cholesky creates.",
"section": "Treewidth",
"slide": "Finding decompositions: elimination orderings",
"keys": [
"fill-in (elimination)",
"fill-in",
"elimination"
]
},
{
"term_html": "min-degree heuristic",
"html": "Eliminate the vertex of smallest current degree.",
"section": "Treewidth",
"slide": "Finding decompositions: elimination orderings",
"keys": [
"min-degree heuristic"
]
},
{
"term_html": "min-fill heuristic",
"html": "Eliminate the vertex adding the fewest fill edges. Exact on chordal graphs.",
"section": "Treewidth",
"slide": "Finding decompositions: elimination orderings",
"keys": [
"min-fill heuristic"
]
},
{
"term_html": "chordal graph",
"html": "One where every cycle of four or more vertices has a chord.",
"section": "Treewidth",
"slide": "Finding decompositions: elimination orderings",
"keys": [
"chordal graph"
]
},
{
"term_html": "simplicial vertex",
"html": "One whose neighbours already form a clique, so eliminating it adds no fill.",
"section": "Treewidth",
"slide": "Finding decompositions: elimination orderings",
"keys": [
"simplicial vertex"
]
},
{
"term_html": "DP over a decomposition",
"html": "For each bag and each subset of it, the best partial solution below; children combined by grouping their tables on the shared vertices. Total about \\(\\sum_t 2^{|B_t|}\\).",
"section": "Treewidth",
"slide": "DP over a decomposition — and predicting its runtime",
"keys": [
"dp over a decomposition"
]
},
{
"term_html": "nice tree decomposition",
"html": "One whose nodes are introduce, forget or join, each changing one vertex. Textbook form; the lab skips it.",
"section": "Treewidth",
"slide": "DP over a decomposition — and predicting its runtime",
"keys": [
"nice tree decomposition"
]
},
{
"term_html": "monadic second-order logic (MSO₂)",
"html": "Logic quantifying over vertices, edges and sets of them.",
"section": "Treewidth",
"slide": "Courcelle's theorem: why all of these work",
"keys": [
"monadic second-order logic (mso₂)",
"monadic second-order logic",
"mso₂"
]
},
{
"term_html": "Courcelle's theorem",
"html": "Every MSO₂-expressible graph property is decidable in \\(f(k, |\\varphi|) \\cdot n\\) time on treewidth \\(\\le k\\) (1990), with \\(f\\) a tower of exponentials.",
"section": "Treewidth",
"slide": "Courcelle's theorem: why all of these work",
"keys": [
"courcelle's theorem"
]
},
{
"term_html": "parameter \\(k\\)",
"html": "A measure of the input, besides its size, that the hardness might live in: solution size, treewidth.",
"section": "Parameters",
"slide": "FPT, XP, and kernels",
"keys": [
"parameter k"
]
},
{
"term_html": "FPT (fixed-parameter tractable)",
"html": "Time \\(f(k) \\cdot n^{O(1)}\\), with the exponential confined to \\(k\\).",
"section": "Parameters",
"slide": "FPT, XP, and kernels",
"keys": [
"fpt (fixed-parameter tractable)",
"fpt",
"fixed-parameter tractable"
]
},
{
"term_html": "XP",
"html": "Time \\(n^{f(k)}\\): polynomial for each fixed \\(k\\), with \\(k\\) in the exponent.",
"section": "Parameters",
"slide": "FPT, XP, and kernels",
"keys": [
"xp"
]
},
{
"term_html": "W[1]-hard",
"html": "Believed not FPT, like \\(k\\)-clique.",
"section": "Parameters",
"slide": "FPT, XP, and kernels",
"keys": [
"w[1]-hard"
]
},
{
"term_html": "kernelization",
"html": "A polynomial reduction to an equivalent instance of size \\(g(k)\\). A decidable problem is FPT iff it has a kernel.",
"section": "Parameters",
"slide": "FPT, XP, and kernels",
"keys": [
"kernelization"
]
},
{
"term_html": "Buss's kernel",
"html": "For vertex cover \\(\\le k\\): take every vertex of degree \\(&gt; k\\); if more than \\(k^2\\) edges remain, answer no. Leaves \\(O(k^2)\\) edges.",
"section": "Parameters",
"slide": "FPT, XP, and kernels",
"keys": [
"buss's kernel"
]
}
];
