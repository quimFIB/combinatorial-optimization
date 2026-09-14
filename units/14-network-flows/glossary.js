// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "network",
"html": "A directed graph with a source \\(s\\), a sink \\(t\\), and a capacity \\(c\\) on every arc.",
"section": "Max flow, min cut",
"slide": "Flows, cuts, and weak duality",
"keys": [
"network"
]
},
{
"term_html": "flow",
"html": "An assignment \\(0 \\le f \\le c\\) on arcs with conservation at every node except \\(s\\) and \\(t\\).",
"section": "Max flow, min cut",
"slide": "Flows, cuts, and weak duality",
"keys": [
"flow"
]
},
{
"term_html": "flow conservation",
"html": "Flow in equals flow out at a node.",
"section": "Max flow, min cut",
"slide": "Flows, cuts, and weak duality",
"keys": [
"flow conservation"
]
},
{
"term_html": "flow value",
"html": "The net flow out of \\(s\\).",
"section": "Max flow, min cut",
"slide": "Flows, cuts, and weak duality",
"keys": [
"flow value"
]
},
{
"term_html": "\\(s\\)–\\(t\\) cut",
"html": "A node set \\(S\\) with \\(s \\in S\\) and \\(t \\notin S\\). Its capacity is the total capacity of arcs leaving \\(S\\).",
"section": "Max flow, min cut",
"slide": "Flows, cuts, and weak duality",
"keys": [
"s–t cut"
]
},
{
"term_html": "weak duality (flows)",
"html": "Every flow's value is at most every cut's capacity. A cut is a certificate that no flow is larger.",
"section": "Max flow, min cut",
"slide": "Flows, cuts, and weak duality",
"keys": [
"weak duality (flows)",
"weak duality",
"flows"
]
},
{
"term_html": "max-flow min-cut theorem",
"html": "The maximum flow value equals the minimum cut capacity, and integer capacities admit an integral maximum flow (Ford &amp; Fulkerson 1956).",
"section": "Max flow, min cut",
"slide": "Max-flow min-cut",
"keys": [
"max-flow min-cut theorem"
]
},
{
"term_html": "residual graph",
"html": "For each arc, a forward residual arc with capacity \\(c - f\\) and a backward one with capacity \\(f\\). Backward arcs let an algorithm undo earlier choices.",
"section": "Max flow, min cut",
"slide": "Max-flow min-cut",
"keys": [
"residual graph"
]
},
{
"term_html": "augmenting path",
"html": "An \\(s\\)–\\(t\\) path in the residual graph.",
"section": "Max flow, min cut",
"slide": "Max-flow min-cut",
"keys": [
"augmenting path"
]
},
{
"term_html": "bottleneck",
"html": "The smallest residual capacity on an augmenting path: how much can be pushed along it.",
"section": "Max flow, min cut",
"slide": "Max-flow min-cut",
"keys": [
"bottleneck"
]
},
{
"term_html": "saturated arc",
"html": "One carrying flow equal to its capacity.",
"section": "Max flow, min cut",
"slide": "Max-flow min-cut",
"keys": [
"saturated arc"
]
},
{
"term_html": "minimum cut from the residual graph",
"html": "At a maximum flow, the nodes reachable from \\(s\\) form a minimum cut.",
"section": "Max flow, min cut",
"slide": "Max-flow min-cut",
"keys": [
"minimum cut from the residual graph"
]
},
{
"term_html": "Ford–Fulkerson method",
"html": "Augment along any path until none remains. Not polynomial; with irrational capacities it may not terminate.",
"section": "Max flow, min cut",
"slide": "Choosing paths: Ford–Fulkerson to Edmonds–Karp to Dinic",
"keys": [
"ford–fulkerson method"
]
},
{
"term_html": "Edmonds–Karp",
"html": "Augment along shortest paths found by BFS. \\(O(VE^2)\\).",
"section": "Max flow, min cut",
"slide": "Choosing paths: Ford–Fulkerson to Edmonds–Karp to Dinic",
"keys": [
"edmonds–karp"
]
},
{
"term_html": "Dinic's algorithm",
"html": "Phases of all shortest paths at once: a BFS level graph, then a blocking flow. \\(O(V^2 E)\\), and \\(O(E \\sqrt V)\\) on unit capacities.",
"section": "Max flow, min cut",
"slide": "Choosing paths: Ford–Fulkerson to Edmonds–Karp to Dinic",
"keys": [
"dinic's algorithm"
]
},
{
"term_html": "level graph",
"html": "The arcs from BFS level \\(i\\) to level \\(i + 1\\).",
"section": "Max flow, min cut",
"slide": "Choosing paths: Ford–Fulkerson to Edmonds–Karp to Dinic",
"keys": [
"level graph"
]
},
{
"term_html": "blocking flow",
"html": "A flow in the level graph after which every \\(s\\)–\\(t\\) path there has a saturated arc.",
"section": "Max flow, min cut",
"slide": "Choosing paths: Ford–Fulkerson to Edmonds–Karp to Dinic",
"keys": [
"blocking flow"
]
},
{
"term_html": "current-edge pointer",
"html": "Per node, the next arc to try in a phase; dead arcs are skipped for the rest of the phase.",
"section": "Max flow, min cut",
"slide": "Choosing paths: Ford–Fulkerson to Edmonds–Karp to Dinic",
"keys": [
"current-edge pointer"
]
},
{
"term_html": "preflow",
"html": "A flow that may leave excess at nodes: more in than out.",
"section": "Max flow, min cut",
"slide": "Push–relabel, and the heuristics that make it fast",
"keys": [
"preflow"
]
},
{
"term_html": "excess",
"html": "Inflow minus outflow at a node under a preflow.",
"section": "Max flow, min cut",
"slide": "Push–relabel, and the heuristics that make it fast",
"keys": [
"excess"
]
},
{
"term_html": "height (label)",
"html": "A number per node with \\(h(s) = n\\), \\(h(t) = 0\\) and \\(h(u) \\le h(v) + 1\\) on every residual arc.",
"section": "Max flow, min cut",
"slide": "Push–relabel, and the heuristics that make it fast",
"keys": [
"height (label)",
"height",
"label"
]
},
{
"term_html": "push",
"html": "Move excess from \\(u\\) to \\(v\\) along a residual arc with \\(h(u) = h(v) + 1\\).",
"section": "Max flow, min cut",
"slide": "Push–relabel, and the heuristics that make it fast",
"keys": [
"push"
]
},
{
"term_html": "relabel",
"html": "Raise \\(u\\) to \\(1 + \\min h(v)\\) over its residual neighbours when it cannot push.",
"section": "Max flow, min cut",
"slide": "Push–relabel, and the heuristics that make it fast",
"keys": [
"relabel"
]
},
{
"term_html": "push–relabel",
"html": "Goldberg &amp; Tarjan's algorithm: push and relabel until no excess remains. \\(O(V^3)\\) with FIFO node order.",
"section": "Max flow, min cut",
"slide": "Push–relabel, and the heuristics that make it fast",
"keys": [
"push–relabel"
]
},
{
"term_html": "gap heuristic",
"html": "If no node has height \\(k\\), lift every node above \\(k\\) at once.",
"section": "Max flow, min cut",
"slide": "Push–relabel, and the heuristics that make it fast",
"keys": [
"gap heuristic"
]
},
{
"term_html": "global relabelling",
"html": "Periodically resetting heights to exact distances by a backward BFS from \\(t\\).",
"section": "Max flow, min cut",
"slide": "Push–relabel, and the heuristics that make it fast",
"keys": [
"global relabelling"
]
},
{
"term_html": "almost-linear-time max flow",
"html": "\\(E^{1+o(1)}\\) for max flow and min-cost flow (Chen et al. 2022), via an interior-point method with graph data structures. Not used in practice.",
"section": "Max flow, min cut",
"slide": "The theoretical frontier moved recently",
"keys": [
"almost-linear-time max flow"
]
},
{
"term_html": "min-cost flow",
"html": "Send \\(d\\) units from \\(s\\) to \\(t\\) minimizing \\(\\sum_e \\text{cost}_e f_e\\) within capacities.",
"section": "Costs",
"slide": "Min-cost flow",
"keys": [
"min-cost flow"
]
},
{
"term_html": "negative-cycle optimality",
"html": "A feasible flow is minimum-cost iff its residual graph has no negative-cost cycle. Reverse arcs carry cost \\(-c\\).",
"section": "Costs",
"slide": "Min-cost flow",
"keys": [
"negative-cycle optimality"
]
},
{
"term_html": "cycle canceling",
"html": "Push flow around negative cycles until none remain (Klein 1967).",
"section": "Costs",
"slide": "Min-cost flow",
"keys": [
"cycle canceling"
]
},
{
"term_html": "network simplex",
"html": "The simplex method specialized to flows, where bases are spanning trees.",
"section": "Costs",
"slide": "Min-cost flow",
"keys": [
"network simplex"
]
},
{
"term_html": "successive shortest paths",
"html": "Repeatedly augment along a cheapest \\(s\\)–\\(t\\) path in the residual graph.",
"section": "Costs",
"slide": "Min-cost flow",
"keys": [
"successive shortest paths"
]
},
{
"term_html": "node potentials \\(\\pi\\)",
"html": "Values per node, the dual variables of the min-cost flow LP.",
"section": "Costs",
"slide": "Min-cost flow",
"keys": [
"node potentials \\pi"
]
},
{
"term_html": "reduced cost (flows)",
"html": "\\(c_\\pi(u, v) = c(u, v) + \\pi(u) - \\pi(v)\\). Kept nonnegative by updating \\(\\pi\\) with Dijkstra distances, so Dijkstra stays valid.",
"section": "Costs",
"slide": "Min-cost flow",
"keys": [
"reduced cost (flows)",
"reduced cost",
"flows"
]
},
{
"term_html": "Bellman–Ford",
"html": "Shortest paths with negative arc costs, used once for the initial potentials.",
"section": "Costs",
"slide": "Min-cost flow",
"keys": [
"bellman–ford"
]
},
{
"term_html": "Dijkstra's algorithm",
"html": "Shortest paths with nonnegative arc costs; run on reduced costs.",
"section": "Costs",
"slide": "Min-cost flow",
"keys": [
"dijkstra's algorithm"
]
},
{
"term_html": "reduction to flow",
"html": "Recognizing a problem as max flow or min cut in disguise. The checkpoint skill.",
"section": "Reductions",
"slide": "",
"keys": [
"reduction to flow"
]
},
{
"term_html": "closure",
"html": "A set of nodes closed under \"requires\": if \\(p\\) is in and \\(p\\) requires \\(q\\), then \\(q\\) is in.",
"section": "Reductions",
"slide": "Project selection: a maximum closure is a minimum cut",
"keys": [
"closure"
]
},
{
"term_html": "project selection (maximum-weight closure)",
"html": "Choose projects with profits, closed under requirements. \\(s \\to p\\) arcs for profits, \\(p \\to t\\) for costs, infinite arcs for requirements; best profit is the positive profits minus the minimum cut (Picard 1976). Lab step 5.",
"section": "Reductions",
"slide": "Project selection: a maximum closure is a minimum cut",
"keys": [
"project selection (maximum-weight closure)",
"project selection",
"maximum-weight closure"
]
},
{
"term_html": "bipartite matching as flow",
"html": "Unit capacities from \\(s\\) to the left side, along edges, and to \\(t\\). Max flow is max matching; the min cut is König's cover.",
"section": "Reductions",
"slide": "More flows in disguise",
"keys": [
"bipartite matching as flow"
]
},
{
"term_html": "baseball elimination",
"html": "Can a team still finish first? Game nodes feed team nodes, with team capacities set to the wins each can still afford. Eliminated iff the flow fails to saturate the game arcs, and the cut names the set of teams that proves it.",
"section": "Reductions",
"slide": "More flows in disguise",
"keys": [
"baseball elimination"
]
},
{
"term_html": "image segmentation (graph cuts)",
"html": "Pixels as nodes, \\(s\\) and \\(t\\) arcs for how foreground or background each looks, neighbour arcs for similarity. The minimum cut is the best labelling.",
"section": "Reductions",
"slide": "More flows in disguise",
"keys": [
"image segmentation (graph cuts)",
"image segmentation",
"graph cuts"
]
}
];
