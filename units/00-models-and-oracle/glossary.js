// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "optimization problem",
"html": "A set of instances. Claims like \"vertex cover is NP-hard\" are about the problem, meaning every graph.",
"section": "What makes a problem combinatorial",
"slide": "Problems and instances",
"keys": [
"optimization problem"
]
},
{
"term_html": "instance",
"html": "One concrete input: a pair \\((F, c)\\) of a feasible set and an objective. \"This graph has a cover of size 12\" is a claim about an instance.",
"section": "What makes a problem combinatorial",
"slide": "Problems and instances",
"keys": [
"instance"
]
},
{
"term_html": "feasible set",
"html": "\\(F\\), the solutions that satisfy the constraints.",
"section": "What makes a problem combinatorial",
"slide": "Problems and instances",
"keys": [
"feasible set"
]
},
{
"term_html": "objective",
"html": "\\(c : F \\to \\mathbb{R}\\), the value to minimize or maximize.",
"section": "What makes a problem combinatorial",
"slide": "Problems and instances",
"keys": [
"objective"
]
},
{
"term_html": "combinatorial",
"html": "\\(F\\) is finite and given <em>implicitly</em>: a simple, enumerable space \\(S\\) plus constraints, \\(F = \\{x \\in S : x \\text{ satisfies the constraints}\\}\\). Finite makes enumeration possible; implicit makes it useless.",
"section": "What makes a problem combinatorial",
"slide": "Problems and instances",
"keys": [
"combinatorial"
]
},
{
"term_html": "space",
"html": "The enumerable set \\(S\\) that candidates are drawn from, such as \\(\\{0,1\\}^n\\), permutations, or set partitions.",
"section": "What makes a problem combinatorial",
"slide": "Problems and instances",
"keys": [
"space"
]
},
{
"term_html": "encoding size",
"html": "The number of bits needed to write an instance down. Running times are measured against it.",
"section": "What makes a problem combinatorial",
"slide": "Problems and instances",
"keys": [
"encoding size"
]
},
{
"term_html": "decision version",
"html": "\"Is there \\(x \\in F\\) with \\(c(x) \\le k\\)?\" Complexity classes are defined on these.",
"section": "What makes a problem combinatorial",
"slide": "Four questions about one instance",
"keys": [
"decision version"
]
},
{
"term_html": "evaluation version",
"html": "\"What is \\(\\min_{x \\in F} c(x)\\)?\"",
"section": "What makes a problem combinatorial",
"slide": "Four questions about one instance",
"keys": [
"evaluation version"
]
},
{
"term_html": "search (optimization) version",
"html": "\"Find an \\(x^*\\) achieving the optimum.\"",
"section": "What makes a problem combinatorial",
"slide": "Four questions about one instance",
"keys": [
"search (optimization) version"
]
},
{
"term_html": "counting version",
"html": "\"How many \\(x \\in F\\) have \\(c(x) \\le k\\)?\" Can be far harder than the other three: counting perfect matchings is #P-complete, while finding one is polynomial.",
"section": "What makes a problem combinatorial",
"slide": "Four questions about one instance",
"keys": [
"counting version"
]
},
{
"term_html": "self-reducibility",
"html": "Turning an evaluation oracle into a search algorithm by fixing one decision at a time and asking whether the optimum survives.",
"section": "What makes a problem combinatorial",
"slide": "Four questions about one instance",
"keys": [
"self-reducibility"
]
},
{
"term_html": "knapsack",
"html": "Choose items under a capacity to maximize value. Space \\(\\{0,1\\}^n\\).",
"section": "The nine problems",
"slide": "The cast",
"keys": [
"knapsack"
]
},
{
"term_html": "set cover",
"html": "Choose the fewest sets whose union covers every element.",
"section": "The nine problems",
"slide": "The cast",
"keys": [
"set cover"
]
},
{
"term_html": "assignment",
"html": "Match \\(n\\) workers to \\(n\\) jobs at minimum cost. The one polynomial problem of the nine: its LP relaxation is already integral.",
"section": "The nine problems",
"slide": "The cast",
"keys": [
"assignment"
]
},
{
"term_html": "bin packing",
"html": "Pack items into the fewest bins of fixed capacity. Space: set partitions.",
"section": "The nine problems",
"slide": "The cast",
"keys": [
"bin packing"
]
},
{
"term_html": "graph colouring",
"html": "Colour vertices so adjacent ones differ, using the fewest colours.",
"section": "The nine problems",
"slide": "The cast",
"keys": [
"graph colouring"
]
},
{
"term_html": "max-cut",
"html": "Split the vertices in two to maximize the edges crossing. No constraints at all; every subset is feasible.",
"section": "The nine problems",
"slide": "The cast",
"keys": [
"max-cut"
]
},
{
"term_html": "TSP",
"html": "The shortest tour visiting every city once.",
"section": "The nine problems",
"slide": "The cast",
"keys": [
"tsp"
]
},
{
"term_html": "job-shop",
"html": "Order jobs on machines to minimize the finishing time.",
"section": "The nine problems",
"slide": "The cast",
"keys": [
"job-shop"
]
},
{
"term_html": "vertex cover",
"html": "The fewest vertices touching every edge. Space \\(\\{0,1\\}^V\\), constraints \\(x_u + x_v \\ge 1\\) for every edge \\(uv\\).",
"section": "The nine problems",
"slide": "The cast",
"keys": [
"vertex cover"
]
},
{
"term_html": "pseudo-polynomial",
"html": "Polynomial in the numeric values rather than their bit size, like knapsack's \\(O(nC)\\) DP. Fast when numbers are small.",
"section": "The nine problems",
"slide": "The cast",
"keys": [
"pseudo-polynomial"
]
},
{
"term_html": "strongly NP-hard",
"html": "NP-hard even when every number is small, as bin packing is. Rules out a pseudo-polynomial algorithm (unit 22).",
"section": "The nine problems",
"slide": "The cast",
"keys": [
"strongly np-hard"
]
},
{
"term_html": "predicate model",
"html": "A problem given only as <code>is_feasible</code> and <code>objective</code> code. A black box: enumeration is the only algorithm it admits.",
"section": "The nine problems",
"slide": "One problem, three descriptions",
"keys": [
"predicate model"
]
},
{
"term_html": "integer program",
"html": "The same problem as linear constraints over integer variables. Exposes linear structure an LP relaxation can use.",
"section": "The nine problems",
"slide": "One problem, three descriptions",
"keys": [
"integer program"
]
},
{
"term_html": "constraint model",
"html": "The same problem in a CP solver's language. Exposes logical structure a propagator can use.",
"section": "The nine problems",
"slide": "One problem, three descriptions",
"keys": [
"constraint model"
]
},
{
"term_html": "set partition",
"html": "A split of \\(\\{0, \\dots, n-1\\}\\) into unlabelled blocks; how bin packing and colouring are enumerated.",
"section": "Spaces and symmetry",
"slide": "The space is a modelling choice",
"keys": [
"set partition"
]
},
{
"term_html": "Bell number \\(B_n\\)",
"html": "The number of set partitions of \\(n\\) items: \\(1, 1, 2, 5, 15, 52, \\dots\\) and \\(115\\,975\\) at \\(n = 10\\).",
"section": "Spaces and symmetry",
"slide": "The space is a modelling choice",
"keys": [
"bell number b_n"
]
},
{
"term_html": "restricted growth string",
"html": "A sequence with \\(a_0 = 0\\) and \\(a_i \\le 1 + \\max(a_0, \\dots, a_{i-1})\\), where \\(a_i\\) is item \\(i\\)'s bin. Each set partition has exactly one, so enumerating these lists every packing once.",
"section": "Spaces and symmetry",
"slide": "The space is a modelling choice",
"keys": [
"restricted growth string"
]
},
{
"term_html": "symmetry",
"html": "Different labellings of the same solution, such as renaming the bins. Enumerating them all repeats work.",
"section": "Spaces and symmetry",
"slide": "The space is a modelling choice",
"keys": [
"symmetry"
]
},
{
"term_html": "symmetry breaking",
"html": "Choosing a space or constraint so each solution is represented once. The biggest single lever on real MIP and CP models (units 05, 27).",
"section": "Spaces and symmetry",
"slide": "The space is a modelling choice",
"keys": [
"symmetry breaking"
]
},
{
"term_html": "certificate",
"html": "A short, checkable piece of evidence for a claim about an instance.",
"section": "Certificates",
"slide": "Two kinds of evidence",
"keys": [
"certificate"
]
},
{
"term_html": "upper-bound certificate",
"html": "For a minimization, a feasible \\(x\\) with \\(c(x) = k\\): proves the optimum is at most \\(k\\). Checking it is polynomial, which is what puts decision versions in NP.",
"section": "Certificates",
"slide": "Two kinds of evidence",
"keys": [
"upper-bound certificate"
]
},
{
"term_html": "lower-bound certificate",
"html": "An argument that <em>no</em> \\(x \\in F\\) has \\(c(x) &lt; k\\). Enumeration is one, exponentially long. Short ones are not expected in general (NP \\(\\ne\\) coNP) but often exist for particular instances; finding them is most of the course.",
"section": "Certificates",
"slide": "Two kinds of evidence",
"keys": [
"lower-bound certificate"
]
},
{
"term_html": "NP, coNP",
"html": "Decision problems with short checkable \"yes\" certificates, and with short checkable \"no\" certificates.",
"section": "Certificates",
"slide": "Two kinds of evidence",
"keys": [
"np, conp",
"np",
"conp"
]
},
{
"term_html": "matching",
"html": "A set of edges no two of which share an endpoint.",
"section": "Certificates",
"slide": "A lower bound for vertex cover",
"keys": [
"matching"
]
},
{
"term_html": "matching lower bound",
"html": "For any matching \\(M\\) and cover \\(C\\) in the same graph, \\(|C| \\ge |M|\\). A cover and a matching of equal size prove each other optimal.",
"section": "Certificates",
"slide": "A lower bound for vertex cover",
"keys": [
"matching lower bound"
]
},
{
"term_html": "\\(\\nu(G)\\), \\(\\tau(G)\\)",
"html": "The size of a largest matching and of a smallest vertex cover.",
"section": "Certificates",
"slide": "A lower bound for vertex cover",
"keys": [
"\\nu(g), \\tau(g)",
"\\nu(g)",
"\\tau(g)"
]
},
{
"term_html": "weak duality",
"html": "\\(\\nu(G) \\le \\tau(G)\\) for every graph: any feasible solution of one problem bounds every solution of the other. The pattern of unit 03.",
"section": "Certificates",
"slide": "A lower bound for vertex cover",
"keys": [
"weak duality"
]
},
{
"term_html": "duality gap",
"html": "When the best bound is strictly below the optimum. On a triangle \\(\\nu = 1\\) but \\(\\tau = 2\\), so no matching certifies the cover.",
"section": "Certificates",
"slide": "When the bound is not enough",
"keys": [
"duality gap"
]
},
{
"term_html": "König's theorem",
"html": "In a bipartite graph \\(\\max |M| = \\min |C|\\), so the matching certificate always exists.",
"section": "Certificates",
"slide": "When the bound is not enough",
"keys": [
"könig's theorem"
]
},
{
"term_html": "bipartite graph",
"html": "One whose vertices split into two sides with every edge crossing. Equivalently, no odd cycle.",
"section": "Certificates",
"slide": "When the bound is not enough",
"keys": [
"bipartite graph"
]
},
{
"term_html": "fractional relaxation",
"html": "Allowing \\(0 \\le x \\le 1\\) instead of \\(x \\in \\{0,1\\}\\). On the triangle both relaxations reach \\(\\tfrac32\\), so the gap comes from integrality, not from duality.",
"section": "Certificates",
"slide": "When the bound is not enough",
"keys": [
"fractional relaxation"
]
},
{
"term_html": "oracle",
"html": "A slow, obviously correct solver that other code is checked against. Here: brute force.",
"section": "An oracle you trust",
"slide": "Brute force, done once and done right",
"keys": [
"oracle"
]
},
{
"term_html": "brute force",
"html": "Evaluating every candidate in the space and keeping the best feasible one. The definition of the optimum, executed.",
"section": "An oracle you trust",
"slide": "Brute force, done once and done right",
"keys": [
"brute force"
]
},
{
"term_html": "self-certifying",
"html": "The oracle's own count, <code>examined == space.size()</code>, is the proof that nothing was skipped.",
"section": "An oracle you trust",
"slide": "Brute force, done once and done right",
"keys": [
"self-certifying"
]
},
{
"term_html": "problem interface",
"html": "<code>space()</code>, <code>is_feasible</code>, <code>objective</code>, <code>sense</code>. Every colib problem has it, which is what makes one oracle work for all nine.",
"section": "An oracle you trust",
"slide": "Brute force, done once and done right",
"keys": [
"problem interface"
]
},
{
"term_html": "<code>sense</code>",
"html": "Whether the problem minimizes or maximizes.",
"section": "An oracle you trust",
"slide": "Brute force, done once and done right",
"keys": [
"~sense~"
]
},
{
"term_html": "differential testing",
"html": "Running your algorithm and the oracle on the same generated instances and reporting any disagreement.",
"section": "An oracle you trust",
"slide": "Differential testing",
"keys": [
"differential testing"
]
},
{
"term_html": "smallest first",
"html": "Sweeping instance sizes upward so the first failure is the smallest counterexample, the one you can draw. Used in place of shrinking.",
"section": "An oracle you trust",
"slide": "Differential testing",
"keys": [
"smallest first"
]
},
{
"term_html": "ratio mode",
"html": "Checking an approximation algorithm against a guaranteed ratio (say <code>ratio=2</code>) instead of equality.",
"section": "An oracle you trust",
"slide": "Differential testing",
"keys": [
"ratio mode"
]
},
{
"term_html": "max-degree greedy",
"html": "Repeatedly take the vertex covering the most uncovered edges. Plausible and wrong: fails on a 7-vertex spider.",
"section": "An oracle you trust",
"slide": "The harness catches what you believe",
"keys": [
"max-degree greedy"
]
},
{
"term_html": "the wall",
"html": "The largest \\(n\\) brute force can handle in a given time. Sets the test sizes for the rest of the course: \\(n \\le 12\\) for subset spaces, \\(n \\le 8\\) for tours and partitions.",
"section": "An oracle you trust",
"slide": "The wall",
"keys": [
"the wall"
]
}
];
