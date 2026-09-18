// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "column generation",
"html": "Solving an LP with exponentially many variables by keeping only a few and asking a pricing problem for one with negative reduced cost. The dual picture of unit 09's row generation.",
"section": "Too many columns",
"slide": "",
"keys": [
"column generation"
]
},
{
"term_html": "cutting stock",
"html": "Cut rolls of width \\(W\\) into items of widths \\(w_i\\) to meet demands \\(d_i\\) with the fewest rolls.",
"section": "Too many columns",
"slide": "Cutting stock, two ways",
"keys": [
"cutting stock"
]
},
{
"term_html": "Kantorovich model",
"html": "The compact cutting-stock model, with a roll-used variable and item copies per roll. LP bound is the trivial area bound, and rolls give \\(K!\\) symmetric copies.",
"section": "Too many columns",
"slide": "Cutting stock, two ways",
"keys": [
"kantorovich model"
]
},
{
"term_html": "pattern",
"html": "A way to cut one roll: \\(a \\in \\mathbb{Z}_{\\ge 0}^m\\) with \\(w^\\top a \\le W\\).",
"section": "Too many columns",
"slide": "Cutting stock, two ways",
"keys": [
"pattern"
]
},
{
"term_html": "Gilmore–Gomory model",
"html": "One variable per pattern: \\(\\min \\sum_p x_p\\) subject to \\(\\sum_p a_{ip} x_p \\ge d_i\\). No symmetry, very strong bound, exponentially many columns.",
"section": "Too many columns",
"slide": "Cutting stock, two ways",
"keys": [
"gilmore–gomory model"
]
},
{
"term_html": "integer round-up property (IRUP)",
"html": "The cutting-stock optimum equals \\(\\lceil z_{LP} \\rceil\\). Usually true, sometimes false; MIRUP conjectures the optimum is at most \\(\\lceil z_{LP} \\rceil + 1\\), still open.",
"section": "Too many columns",
"slide": "Cutting stock, two ways",
"keys": [
"integer round-up property (irup)",
"integer round-up property",
"irup"
]
},
{
"term_html": "master problem",
"html": "The LP over all columns.",
"section": "Too many columns",
"slide": "Cutting stock, two ways",
"keys": [
"master problem"
]
},
{
"term_html": "restricted master problem (RMP)",
"html": "The master over only the columns generated so far. Its dual is a relaxation of the full dual.",
"section": "Too many columns",
"slide": "Cutting stock, two ways",
"keys": [
"restricted master problem (rmp)",
"restricted master problem",
"rmp"
]
},
{
"term_html": "pricing problem",
"html": "\\(\\min_{a \\in \\mathcal{A}}\\ c(a) - y^\\top a\\): find the most negative reduced cost among implicitly defined columns. For cutting stock, a knapsack with the duals as values.",
"section": "Too many columns",
"slide": "Pricing is minimising the reduced cost",
"keys": [
"pricing problem"
]
},
{
"term_html": "pricing = dual separation",
"html": "The RMP's duals are optimal for the full dual iff no column violates \\(y^\\top a \\le c(a)\\). Finding one that does is unit 09's separation problem applied to the dual.",
"section": "Too many columns",
"slide": "Pricing is minimising the reduced cost",
"keys": [
"pricing = dual separation"
]
},
{
"term_html": "column-generation loop",
"html": "Solve the RMP, price at its duals, add any negative-reduced-cost columns, repeat until pricing proves none exist.",
"section": "Too many columns",
"slide": "The loop",
"keys": [
"column-generation loop"
]
},
{
"term_html": "heuristic pricing",
"html": "Any method that finds some negative column. Allowed in every iteration except the last, where only exact pricing proves optimality.",
"section": "Too many columns",
"slide": "The loop",
"keys": [
"heuristic pricing"
]
},
{
"term_html": "block-angular structure",
"html": "Independent blocks \\(x_k \\in X_k\\) tied together by a few linking constraints \\(\\sum_k D_k x_k \\ge d\\).",
"section": "Dantzig–Wolfe",
"slide": "Decomposition of block-angular programs",
"keys": [
"block-angular structure"
]
},
{
"term_html": "Dantzig–Wolfe decomposition",
"html": "Replace each \\(X_k\\) by \\(\\mathrm{conv}(X_k)\\), written as convex combinations \\(\\lambda_{kp}\\) of its extreme points; the \\(\\lambda\\) are the master's columns.",
"section": "Dantzig–Wolfe",
"slide": "Decomposition of block-angular programs",
"keys": [
"dantzig–wolfe decomposition"
]
},
{
"term_html": "convexification",
"html": "That replacement. Strengthens the formulation by taking the hull of a substructure.",
"section": "Dantzig–Wolfe",
"slide": "Decomposition of block-angular programs",
"keys": [
"convexification"
]
},
{
"term_html": "linking constraints",
"html": "The constraints that tie the blocks together; they stay in the master.",
"section": "Dantzig–Wolfe",
"slide": "Decomposition of block-angular programs",
"keys": [
"linking constraints"
]
},
{
"term_html": "convexity constraint",
"html": "\\(\\sum_p \\lambda_{kp} = 1\\), one per block, with dual \\(\\mu_k\\).",
"section": "Dantzig–Wolfe",
"slide": "Decomposition of block-angular programs",
"keys": [
"convexity constraint"
]
},
{
"term_html": "DW pricing",
"html": "For block \\(k\\), \\(\\min_{x \\in X_k} (c_k - D_k^\\top y)^\\top x - \\mu_k\\).",
"section": "Dantzig–Wolfe",
"slide": "Decomposition of block-angular programs",
"keys": [
"dw pricing"
]
},
{
"term_html": "Dantzig–Wolfe bound",
"html": "\\(z_{DW} = \\min\\{c^\\top x : Dx \\ge d,\\ x_k \\in \\mathrm{conv}(X_k)\\} \\ge z_{LP}\\). Equal to the Lagrangian dual bound of unit 11 (Geoffrion 1974).",
"section": "Dantzig–Wolfe",
"slide": "Decomposition of block-angular programs",
"keys": [
"dantzig–wolfe bound"
]
},
{
"term_html": "integrality property",
"html": "A block whose LP relaxation is already integral. Then \\(z_{DW} = z_{LP}\\): no bound gain. The bound improves only when pricing is a hard integer problem.",
"section": "Dantzig–Wolfe",
"slide": "A hard pricing problem is a feature",
"keys": [
"integrality property"
]
},
{
"term_html": "identical blocks (aggregation)",
"html": "When every block is the same, as with rolls, they merge into one pricing problem, removing the symmetry.",
"section": "Dantzig–Wolfe",
"slide": "A hard pricing problem is a feature",
"keys": [
"identical blocks (aggregation)",
"identical blocks",
"aggregation"
]
},
{
"term_html": "ESPPRC",
"html": "The elementary shortest path problem with resource constraints: pricing for vehicle routing. Strongly NP-hard.",
"section": "Dantzig–Wolfe",
"slide": "A hard pricing problem is a feature",
"keys": [
"espprc"
]
},
{
"term_html": "ng-routes",
"html": "A relaxation of elementarity that forbids cycles only within small neighbourhoods. A weaker bound for a far cheaper pricer.",
"section": "Dantzig–Wolfe",
"slide": "A hard pricing problem is a feature",
"keys": [
"ng-routes"
]
},
{
"term_html": "Lagrangian bound (Lasdon)",
"html": "If some optimum uses at most \\(\\kappa\\) columns, \\(z_{RMP} + \\kappa \\min_a \\bar c(a) \\le z_{LP}\\). A lower bound at every iteration.",
"section": "Bounds and stability",
"slide": "A lower bound at every iteration",
"keys": [
"lagrangian bound (lasdon)",
"lagrangian bound",
"lasdon"
]
},
{
"term_html": "Farley bound",
"html": "For unit column costs and any \\(y \\ge 0\\) with \\(v = \\max_a y^\\top a\\), \\(y/v\\) is dual feasible, so \\(z_{LP} \\ge d^\\top y / v\\). Lab step 2.",
"section": "Bounds and stability",
"slide": "A lower bound at every iteration",
"keys": [
"farley bound"
]
},
{
"term_html": "early termination",
"html": "Stopping when \\(\\lceil \\text{bound} \\rceil = \\lceil z_{RMP} \\rceil\\), since the integer optimum is then known.",
"section": "Bounds and stability",
"slide": "A lower bound at every iteration",
"keys": [
"early termination"
]
},
{
"term_html": "dual degeneracy",
"html": "The RMP has many dual optima, so its duals jump between them.",
"section": "Bounds and stability",
"slide": "Dual oscillation, and smoothing",
"keys": [
"dual degeneracy"
]
},
{
"term_html": "dual oscillation",
"html": "Those jumps, which generate columns useless later and make up most of the slow tail.",
"section": "Bounds and stability",
"slide": "Dual oscillation, and smoothing",
"keys": [
"dual oscillation"
]
},
{
"term_html": "stabilisation",
"html": "Keeping duals near a good centre: boxstep (a box around it), penalties (a cost for leaving it), or smoothing.",
"section": "Bounds and stability",
"slide": "Dual oscillation, and smoothing",
"keys": [
"stabilisation"
]
},
{
"term_html": "stability centre \\(\\hat y\\)",
"html": "The best dual point found so far, around which stabilisation works.",
"section": "Bounds and stability",
"slide": "Dual oscillation, and smoothing",
"keys": [
"stability centre \\hat y"
]
},
{
"term_html": "Wentges smoothing",
"html": "Price at \\(\\alpha \\hat y + (1 - \\alpha) y\\) instead of the master duals.",
"section": "Bounds and stability",
"slide": "Dual oscillation, and smoothing",
"keys": [
"wentges smoothing"
]
},
{
"term_html": "mis-price",
"html": "A smoothed pricing call that finds no column useful at the master duals. Must fall back to pricing at the master duals, the only place optimality can be certified.",
"section": "Bounds and stability",
"slide": "Dual oscillation, and smoothing",
"keys": [
"mis-price"
]
},
{
"term_html": "branch-and-price",
"html": "Branch and bound with column generation at every node.",
"section": "Branch-and-price",
"slide": "Why naive branching destroys pricing",
"keys": [
"branch-and-price"
]
},
{
"term_html": "price-and-branch",
"html": "Generating columns at the root only, then solving the restricted master as an IP. No optimality guarantee.",
"section": "Branch-and-price",
"slide": "Why naive branching destroys pricing",
"keys": [
"price-and-branch"
]
},
{
"term_html": "restricted master IP",
"html": "The RMP with integrality restored, over the columns generated so far.",
"section": "Branch-and-price",
"slide": "Why naive branching destroys pricing",
"keys": [
"restricted master ip"
]
},
{
"term_html": "branching on master variables",
"html": "Fixing \\(x_p = 0\\) is invisible to pricing, which regenerates the same column, and barely moves the bound.",
"section": "Branch-and-price",
"slide": "Why naive branching destroys pricing",
"keys": [
"branching on master variables"
]
},
{
"term_html": "Ryan–Foster branching",
"html": "Pick two items fractionally together; one branch forces them together, the other apart. Both are easy for pricing to respect.",
"section": "Branch-and-price",
"slide": "Why naive branching destroys pricing",
"keys": [
"ryan–foster branching"
]
},
{
"term_html": "branch on original structure",
"html": "The general principle: branch on something the pricing problem can see, such as arcs in routing.",
"section": "Branch-and-price",
"slide": "Why naive branching destroys pricing",
"keys": [
"branch on original structure"
]
},
{
"term_html": "set partitioning over routes",
"html": "The CVRP master: every customer on exactly one chosen route.",
"section": "Branch-and-price",
"slide": "Vehicle routing: where column generation stops being a toy",
"keys": [
"set partitioning over routes"
]
},
{
"term_html": "CVRP",
"html": "The capacitated vehicle routing problem.",
"section": "Branch-and-price",
"slide": "Vehicle routing: where column generation stops being a toy",
"keys": [
"cvrp"
]
},
{
"term_html": "labelling algorithm",
"html": "A DP for resource-constrained paths: labels of cost, load and visited set at each vertex, extended forward and pruned by dominance.",
"section": "Branch-and-price",
"slide": "Vehicle routing: where column generation stops being a toy",
"keys": [
"labelling algorithm"
]
},
{
"term_html": "dominance",
"html": "A label dominates another at the same vertex if it is no worse in cost and load and its visited set is a subset. Dropping the subset condition loses optimal routes.",
"section": "Branch-and-price",
"slide": "Vehicle routing: where column generation stops being a toy",
"keys": [
"dominance"
]
},
{
"term_html": "branch-price-and-cut",
"html": "Column generation, cuts and branching together; the state of the art for vehicle routing and crew scheduling.",
"section": "Branch-and-price",
"slide": "Vehicle routing: where column generation stops being a toy",
"keys": [
"branch-price-and-cut"
]
}
];
