// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "complicating constraints",
"html": "The constraints \\(Ax \\ge b\\) that make the problem hard; the ones to move into the objective.",
"section": "Dualising",
"slide": "The Lagrangian function",
"keys": [
"complicating constraints"
]
},
{
"term_html": "dualising (relaxing) a constraint",
"html": "Removing it and adding a price for its violation to the objective.",
"section": "Dualising",
"slide": "The Lagrangian function",
"keys": [
"dualising (relaxing) a constraint"
]
},
{
"term_html": "Lagrange multipliers",
"html": "The prices \\(u \\ge 0\\), one per dualised constraint; free sign for equality constraints.",
"section": "Dualising",
"slide": "The Lagrangian function",
"keys": [
"lagrange multipliers"
]
},
{
"term_html": "Lagrangian function",
"html": "\\(L(u) = \\min_{x \\in X} c^\\top x + u^\\top (b - Ax)\\).",
"section": "Dualising",
"slide": "The Lagrangian function",
"keys": [
"lagrangian function"
]
},
{
"term_html": "Lagrangian subproblem",
"html": "The easy minimization over \\(X\\) that evaluates \\(L(u)\\).",
"section": "Dualising",
"slide": "The Lagrangian function",
"keys": [
"lagrangian subproblem"
]
},
{
"term_html": "weak duality (Lagrangian)",
"html": "\\(L(u) \\le z\\) for every \\(u \\ge 0\\).",
"section": "Dualising",
"slide": "The Lagrangian function",
"keys": [
"weak duality (lagrangian)",
"weak duality",
"lagrangian"
]
},
{
"term_html": "Lagrangian dual",
"html": "\\(z_{LD} = \\max_{u \\ge 0} L(u)\\). A concave maximization with no local maxima but no gradient.",
"section": "Dualising",
"slide": "The Lagrangian function",
"keys": [
"lagrangian dual"
]
},
{
"term_html": "concave, piecewise linear",
"html": "\\(L\\) is the lower envelope of one affine function per \\(x \\in X\\), non-differentiable at its kinks, where the maximum almost always sits.",
"section": "Dualising",
"slide": "The Lagrangian function",
"keys": [
"concave, piecewise linear",
"concave",
"piecewise linear"
]
},
{
"term_html": "Geoffrion's theorem",
"html": "\\(z_{LD} = \\min\\{c^\\top x : Ax \\ge b,\\ x \\in \\mathrm{conv}(X)\\}\\), so \\(z_{LP} \\le z_{LD} \\le z\\) (1974).",
"section": "Dualising",
"slide": "Geoffrion 1974: which bound you get",
"keys": [
"geoffrion's theorem"
]
},
{
"term_html": "integrality property",
"html": "\\(\\mathrm{conv}(X)\\) equals the LP description of \\(X\\). Then \\(z_{LD} = z_{LP}\\): the relaxation gives nothing the LP didn't, though it may be faster. The prediction the checkpoint asks for.",
"section": "Dualising",
"slide": "Geoffrion 1974: which bound you get",
"keys": [
"integrality property"
]
},
{
"term_html": "GAP",
"html": "The generalized assignment problem: assign each job to one agent, respecting agent capacities, at minimum cost.",
"section": "Dualising",
"slide": "Geoffrion 1974: which bound you get",
"keys": [
"gap"
]
},
{
"term_html": "relaxation A (knapsacks)",
"html": "Dualise \"each job exactly once\", leaving one knapsack per agent. No integrality property, so it beats the LP.",
"section": "Dualising",
"slide": "Geoffrion 1974: which bound you get",
"keys": [
"relaxation a (knapsacks)",
"relaxation a",
"knapsacks"
]
},
{
"term_html": "relaxation B (one agent per job)",
"html": "Dualise the capacities, leaving \"each job picks an agent\". Integral LP, so it stops at the LP bound.",
"section": "Dualising",
"slide": "Geoffrion 1974: which bound you get",
"keys": [
"relaxation b (one agent per job)",
"relaxation b",
"one agent per job"
]
},
{
"term_html": "subgradient",
"html": "\\(g\\) with \\(L(v) \\le L(u) + g^\\top (v - u)\\) for all \\(v\\). For the Lagrangian, \\(g = b - Ax(u)\\), the violation of the dualised constraints: free to compute.",
"section": "Subgradients",
"slide": "Subgradient ascent",
"keys": [
"subgradient"
]
},
{
"term_html": "subgradient ascent",
"html": "\\(u \\leftarrow [u + t_k g]_+\\), projecting back onto \\(u \\ge 0\\).",
"section": "Subgradients",
"slide": "Subgradient ascent",
"keys": [
"subgradient ascent"
]
},
{
"term_html": "diminishing step rule",
"html": "\\(\\sum t_k = \\infty\\), \\(\\sum t_k^2 &lt; \\infty\\). Converges, slowly: \\(O(1/\\varepsilon^2)\\) iterations.",
"section": "Subgradients",
"slide": "Subgradient ascent",
"keys": [
"diminishing step rule"
]
},
{
"term_html": "Polyak step",
"html": "\\(t_k = \\lambda_k (\\bar z - L(u)) / \\|g\\|^2\\), with \\(\\bar z\\) an upper bound.",
"section": "Subgradients",
"slide": "Subgradient ascent",
"keys": [
"polyak step"
]
},
{
"term_html": "Held–Wolfe–Crowder rule",
"html": "Halve \\(\\lambda\\) when the bound stops improving. Lab step 2.",
"section": "Subgradients",
"slide": "Subgradient ascent",
"keys": [
"held–wolfe–crowder rule"
]
},
{
"term_html": "not an ascent method",
"html": "A subgradient step can lower \\(L\\) even when small; it only brings \\(u\\) closer to the optimal multipliers. Always keep the best bound seen.",
"section": "Subgradients",
"slide": "Subgradient ascent",
"keys": [
"not an ascent method"
]
},
{
"term_html": "zig-zag",
"html": "The bouncing of \\(L(u)\\) under a fixed large step.",
"section": "Subgradients",
"slide": "Subgradient ascent",
"keys": [
"zig-zag"
]
},
{
"term_html": "Kelley's cutting-plane method",
"html": "Maximize the envelope of the affine pieces seen so far as an LP. Its dual is unit 10's restricted master.",
"section": "Subgradients",
"slide": "Beyond plain subgradients",
"keys": [
"kelley's cutting-plane method"
]
},
{
"term_html": "bundle method",
"html": "The cutting-plane model plus a quadratic proximal term: the stabilised version, with convergence guarantees.",
"section": "Subgradients",
"slide": "Beyond plain subgradients",
"keys": [
"bundle method"
]
},
{
"term_html": "volume algorithm",
"html": "A subgradient method that also averages relaxed solutions into an approximate primal LP solution (Barahona &amp; Anbil 2000).",
"section": "Subgradients",
"slide": "Beyond plain subgradients",
"keys": [
"volume algorithm"
]
},
{
"term_html": "primal recovery",
"html": "Weighted averages of the \\(x(u_k)\\) converging to an optimal point over \\(\\mathrm{conv}(X)\\).",
"section": "Subgradients",
"slide": "Beyond plain subgradients",
"keys": [
"primal recovery"
]
},
{
"term_html": "1-tree",
"html": "A spanning tree on vertices \\(1, \\dots, n-1\\) plus two edges at vertex 0. Every tour is a 1-tree with all degrees 2.",
"section": "Held–Karp",
"slide": "1-trees and the Held–Karp bound (1970–71)",
"keys": [
"1-tree"
]
},
{
"term_html": "vertex penalties \\(\\pi_v\\)",
"html": "Multipliers on \"degree = 2\", turning edge costs into \\(d_{ij} + \\pi_i + \\pi_j\\).",
"section": "Held–Karp",
"slide": "1-trees and the Held–Karp bound (1970–71)",
"keys": [
"vertex penalties \\pi_v"
]
},
{
"term_html": "1-tree subgradient",
"html": "\\(g_v = \\deg_T(v) - 2\\). If it is 0, the 1-tree is an optimal tour.",
"section": "Held–Karp",
"slide": "1-trees and the Held–Karp bound (1970–71)",
"keys": [
"1-tree subgradient"
]
},
{
"term_html": "Held–Karp bound",
"html": "\\(\\max_\\pi L(\\pi)\\) over 1-trees. Equal to the subtour LP bound, by Geoffrion, since the 1-tree polytope has the integrality property.",
"section": "Held–Karp",
"slide": "1-trees and the Held–Karp bound (1970–71)",
"keys": [
"held–karp bound"
]
},
{
"term_html": "α-nearness",
"html": "How much the cheapest 1-tree grows when forced to contain an edge: that forced 1-tree's cost minus the minimum 1-tree's. LKH builds its candidate edge lists from it.",
"section": "Held–Karp",
"slide": "1-trees and the Held–Karp bound (1970–71)",
"keys": [
"α-nearness"
]
},
{
"term_html": "LKH",
"html": "Helsgaun's Lin–Kernighan implementation, the best TSP heuristic (unit 26).",
"section": "Held–Karp",
"slide": "1-trees and the Held–Karp bound (1970–71)",
"keys": [
"lkh"
]
},
{
"term_html": "reduced-cost fixing",
"html": "If every solution with \\(x_e = 1\\) has Lagrangian value above the incumbent \\(\\bar z\\), fix \\(x_e = 0\\).",
"section": "Using the multipliers",
"slide": "Fixing variables, and repairing solutions",
"keys": [
"reduced-cost fixing"
]
},
{
"term_html": "1-tree reduced cost \\(\\rho_e\\)",
"html": "\\(c_e\\) minus the heaviest edge on the tree path between its endpoints: the matroid exchange of unit 13.",
"section": "Using the multipliers",
"slide": "Fixing variables, and repairing solutions",
"keys": [
"1-tree reduced cost \\rho_e"
]
},
{
"term_html": "Lagrangian heuristic",
"html": "Repairing the relaxed solution, which violates only the dualised constraints, into a feasible one.",
"section": "Using the multipliers",
"slide": "Fixing variables, and repairing solutions",
"keys": [
"lagrangian heuristic"
]
},
{
"term_html": "regret",
"html": "The cost difference between a job's best and second-best placement, used to decide which job to place first in the GAP repair.",
"section": "Using the multipliers",
"slide": "Fixing variables, and repairing solutions",
"keys": [
"regret"
]
}
];
