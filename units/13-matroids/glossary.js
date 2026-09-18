// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "ground set \\(E\\)",
"html": "The elements to choose from.",
"section": "Greedy and matroids",
"slide": "Independence systems, and one algorithm for all of them",
"keys": [
"ground set e"
]
},
{
"term_html": "independence system",
"html": "A family \\(\\mathcal{I}\\) of subsets of \\(E\\) containing \\(\\emptyset\\) and closed under taking subsets.",
"section": "Greedy and matroids",
"slide": "Independence systems, and one algorithm for all of them",
"keys": [
"independence system"
]
},
{
"term_html": "independent set",
"html": "A member of \\(\\mathcal{I}\\).",
"section": "Greedy and matroids",
"slide": "Independence systems, and one algorithm for all of them",
"keys": [
"independent set"
]
},
{
"term_html": "greedy algorithm (max weight)",
"html": "Sort by decreasing weight; take each positive-weight element if the chosen set stays independent.",
"section": "Greedy and matroids",
"slide": "Independence systems, and one algorithm for all of them",
"keys": [
"greedy algorithm (max weight)",
"greedy algorithm",
"max weight"
]
},
{
"term_html": "independence oracle",
"html": "A function answering \"is this set independent?\". The lab's greedy is written against one, never against a data structure.",
"section": "Greedy and matroids",
"slide": "Independence systems, and one algorithm for all of them",
"keys": [
"independence oracle"
]
},
{
"term_html": "hereditary axiom",
"html": "A subset of an independent set is independent.",
"section": "Greedy and matroids",
"slide": "The matroid axioms",
"keys": [
"hereditary axiom"
]
},
{
"term_html": "exchange axiom",
"html": "If \\(A, B\\) are independent and \\(|A| &lt; |B|\\), some \\(b \\in B \\setminus A\\) has \\(A + b\\) independent.",
"section": "Greedy and matroids",
"slide": "The matroid axioms",
"keys": [
"exchange axiom"
]
},
{
"term_html": "matroid",
"html": "An independence system satisfying the exchange axiom.",
"section": "Greedy and matroids",
"slide": "The matroid axioms",
"keys": [
"matroid"
]
},
{
"term_html": "basis (matroid)",
"html": "A maximal independent set. All bases of any subset have the same size.",
"section": "Greedy and matroids",
"slide": "The matroid axioms",
"keys": [
"basis (matroid)",
"basis",
"matroid"
]
},
{
"term_html": "rank \\(r(S)\\)",
"html": "The size of a basis of \\(S\\).",
"section": "Greedy and matroids",
"slide": "The matroid axioms",
"keys": [
"rank r(s)"
]
},
{
"term_html": "graphic matroid",
"html": "The forests of a graph.",
"section": "Greedy and matroids",
"slide": "The matroid axioms",
"keys": [
"graphic matroid"
]
},
{
"term_html": "uniform matroid \\(U_{k,n}\\)",
"html": "All sets of at most \\(k\\) of \\(n\\) elements.",
"section": "Greedy and matroids",
"slide": "The matroid axioms",
"keys": [
"uniform matroid u_{k,n}"
]
},
{
"term_html": "partition matroid",
"html": "At most \\(c_b\\) elements from each block \\(b\\) of a partition of \\(E\\).",
"section": "Greedy and matroids",
"slide": "The matroid axioms",
"keys": [
"partition matroid"
]
},
{
"term_html": "linear matroid",
"html": "The linearly independent sets of a list of vectors. Where the axioms come from (Whitney 1935).",
"section": "Greedy and matroids",
"slide": "The matroid axioms",
"keys": [
"linear matroid"
]
},
{
"term_html": "transversal matroid",
"html": "The sets matchable into the other side of a bipartite graph. Unit-time jobs with deadlines form one.",
"section": "Greedy and matroids",
"slide": "The matroid axioms",
"keys": [
"transversal matroid"
]
},
{
"term_html": "Rado–Edmonds theorem",
"html": "Greedy finds a maximum-weight independent set for every weight function if and only if the system is a matroid.",
"section": "Greedy and matroids",
"slide": "Rado–Edmonds: greedy works exactly on matroids",
"keys": [
"rado–edmonds theorem"
]
},
{
"term_html": "exchange witness",
"html": "A pair \\((A, B)\\) violating the exchange axiom. Weighting \\(A\\) at \\(1 + \\varepsilon\\) and \\(B \\setminus A\\) at 1 builds an instance where greedy fails. Lab step 3 finds it.",
"section": "Greedy and matroids",
"slide": "Rado–Edmonds: greedy works exactly on matroids",
"keys": [
"exchange witness"
]
},
{
"term_html": "Kruskal's algorithm",
"html": "Greedy on the graphic matroid: a minimum or maximum spanning forest.",
"section": "Greedy and matroids",
"slide": "Rado–Edmonds: greedy works exactly on matroids",
"keys": [
"kruskal's algorithm"
]
},
{
"term_html": "incidence vector",
"html": "The 0/1 vector of a subset of \\(E\\).",
"section": "Greedy and matroids",
"slide": "Rado–Edmonds: greedy works exactly on matroids",
"keys": [
"incidence vector"
]
},
{
"term_html": "matroid polytope",
"html": "\\(P(M) = \\{x \\ge 0 : \\sum_{e \\in S} x_e \\le r(S)\\ \\forall S \\subseteq E\\}\\), the convex hull of the independent sets (Edmonds 1970). TDI, with exponentially many constraints.",
"section": "Greedy and matroids",
"slide": "The matroid polytope",
"keys": [
"matroid polytope"
]
},
{
"term_html": "greedy dual certificate",
"html": "\\(y_{S_i} = w(e_i) - w(e_{i+1})\\) on the prefixes of greedy's order: a dual solution proving greedy optimal by LP duality.",
"section": "Greedy and matroids",
"slide": "The matroid polytope",
"keys": [
"greedy dual certificate"
]
},
{
"term_html": "matroid intersection",
"html": "The largest set independent in two matroids \\(M_1\\) and \\(M_2\\) at once.",
"section": "Two matroids",
"slide": "Matroid intersection",
"keys": [
"matroid intersection"
]
},
{
"term_html": "common independent set",
"html": "A set independent in both.",
"section": "Two matroids",
"slide": "Matroid intersection",
"keys": [
"common independent set"
]
},
{
"term_html": "Edmonds' intersection theorem",
"html": "\\(\\max |I| = \\min_{A \\subseteq E} r_1(A) + r_2(E \\setminus A)\\). König's theorem is the case of two partition matroids.",
"section": "Two matroids",
"slide": "Matroid intersection",
"keys": [
"edmonds' intersection theorem"
]
},
{
"term_html": "rainbow spanning forest",
"html": "A forest using at most one edge of each colour: graphic intersected with a partition matroid.",
"section": "Two matroids",
"slide": "Matroid intersection",
"keys": [
"rainbow spanning forest"
]
},
{
"term_html": "exchange graph",
"html": "Arcs \\(x \\to y\\) (\\(x \\in I\\), \\(y \\notin I\\)) when \\(I - x + y\\) is independent in \\(M_1\\), and \\(y \\to x\\) when it is independent in \\(M_2\\). Sources can be added to \\(I\\) in \\(M_1\\), sinks in \\(M_2\\).",
"section": "Two matroids",
"slide": "Matroid intersection",
"keys": [
"exchange graph"
]
},
{
"term_html": "augmenting path (matroid)",
"html": "A shortest source-to-sink path in the exchange graph; flipping it grows \\(I\\) by one. It must be shortest for the result to stay independent.",
"section": "Two matroids",
"slide": "Matroid intersection",
"keys": [
"augmenting path (matroid)",
"augmenting path",
"matroid"
]
},
{
"term_html": "three-matroid intersection",
"html": "NP-hard: a directed Hamiltonian path is a common independent set of size \\(n - 1\\) in a graphic and two partition matroids.",
"section": "Two matroids",
"slide": "Two is polynomial, three is NP-hard",
"keys": [
"three-matroid intersection"
]
},
{
"term_html": "matroid parity",
"html": "A generalization of matching to matroids; polynomial for linear matroids, intractable in the oracle model.",
"section": "Two matroids",
"slide": "Two is polynomial, three is NP-hard",
"keys": [
"matroid parity"
]
},
{
"term_html": "marginal gain",
"html": "\\(f(A + e) - f(A)\\), what adding \\(e\\) contributes.",
"section": "Beyond matroids: submodularity",
"slide": "Diminishing returns, and 1 − 1/e",
"keys": [
"marginal gain"
]
},
{
"term_html": "submodular function",
"html": "\\(f(A + e) - f(A) \\ge f(B + e) - f(B)\\) whenever \\(A \\subseteq B\\) and \\(e \\notin B\\): diminishing returns. Rank and coverage functions are submodular.",
"section": "Beyond matroids: submodularity",
"slide": "Diminishing returns, and 1 − 1/e",
"keys": [
"submodular function"
]
},
{
"term_html": "monotone",
"html": "\\(f(A) \\le f(B)\\) whenever \\(A \\subseteq B\\).",
"section": "Beyond matroids: submodularity",
"slide": "Diminishing returns, and 1 − 1/e",
"keys": [
"monotone"
]
},
{
"term_html": "submodular function minimization",
"html": "Polynomial; separation over the matroid polytope is an instance of it.",
"section": "Beyond matroids: submodularity",
"slide": "Diminishing returns, and 1 − 1/e",
"keys": [
"submodular function minimization"
]
},
{
"term_html": "maximum coverage",
"html": "Choose \\(k\\) sets to cover the most elements.",
"section": "Beyond matroids: submodularity",
"slide": "Diminishing returns, and 1 − 1/e",
"keys": [
"maximum coverage"
]
},
{
"term_html": "\\(1 - 1/e\\) guarantee",
"html": "For monotone submodular \\(f\\) under a cardinality limit, greedy reaches at least \\((1 - 1/e) \\cdot \\mathrm{OPT}\\) (Nemhauser, Wolsey &amp; Fisher 1978). Best possible for max coverage unless P = NP (Feige 1998).",
"section": "Beyond matroids: submodularity",
"slide": "Diminishing returns, and 1 − 1/e",
"keys": [
"1 - 1/e guarantee"
]
},
{
"term_html": "worst-case guarantee",
"html": "A floor, not a forecast: on random instances greedy reached 93–99% against the 63% bound.",
"section": "Beyond matroids: submodularity",
"slide": "The guarantee against the typical case",
"keys": [
"worst-case guarantee"
]
}
];
