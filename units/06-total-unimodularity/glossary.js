// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "totally unimodular (TU)",
"html": "A matrix every square submatrix of which has determinant in \\(\\{-1, 0, 1\\}\\). In particular every entry is \\(-1\\), \\(0\\) or \\(1\\).",
"section": "The theorem",
"slide": "Totally unimodular matrices",
"keys": [
"totally unimodular (tu)",
"totally unimodular",
"tu"
]
},
{
"term_html": "square submatrix",
"html": "The matrix left after choosing \\(k\\) rows and \\(k\\) columns, for any \\(k\\).",
"section": "The theorem",
"slide": "Totally unimodular matrices",
"keys": [
"square submatrix"
]
},
{
"term_html": "Hoffman–Kruskal theorem",
"html": "For integral \\(A\\), \\(\\{x \\ge 0 : Ax \\le b\\}\\) has only integral vertices for every integral \\(b\\) if and only if \\(A\\) is TU (1956).",
"section": "The theorem",
"slide": "Totally unimodular matrices",
"keys": [
"hoffman–kruskal theorem"
]
},
{
"term_html": "integral polyhedron",
"html": "One whose vertices are all integral, so the LP relaxation solves the integer problem.",
"section": "The theorem",
"slide": "Totally unimodular matrices",
"keys": [
"integral polyhedron"
]
},
{
"term_html": "Cramer's rule",
"html": "\\(x_B = \\mathrm{adj}(B)\\, b' / \\det B\\). With \\(\\det B = \\pm 1\\) and integral data, the vertex is integral: the whole \"if\" direction.",
"section": "The theorem",
"slide": "Totally unimodular matrices",
"keys": [
"cramer's rule"
]
},
{
"term_html": "\"for every integral \\(b\\)\"",
"html": "The part of the theorem that matters. A non-TU matrix can be integral for one \\(b\\); TU survives any change of right-hand side, as branching and data changes require.",
"section": "The theorem",
"slide": "Totally unimodular matrices",
"keys": [
"\"for every integral b\""
]
},
{
"term_html": "min–max theorem",
"html": "A combinatorial \"max = min\" statement such as König's, which is LP duality with both LPs integral.",
"section": "The theorem",
"slide": "Consequences you already rely on",
"keys": [
"min–max theorem"
]
},
{
"term_html": "bipartite incidence matrix",
"html": "Rows are the vertices of a bipartite graph; each column (edge) has one 1 on each side. TU.",
"section": "Recognizing TU",
"slide": "Three families",
"keys": [
"bipartite incidence matrix"
]
},
{
"term_html": "directed incidence (network) matrix",
"html": "Each column has one \\(+1\\) and one \\(-1\\), the tail and head of an arc. TU. Tutte's network matrices generalize it.",
"section": "Recognizing TU",
"slide": "Three families",
"keys": [
"directed incidence (network) matrix"
]
},
{
"term_html": "interval matrix",
"html": "Every row (or column) has its ones consecutive, as in interval scheduling. TU.",
"section": "Recognizing TU",
"slide": "Three families",
"keys": [
"interval matrix"
]
},
{
"term_html": "consecutive-ones property",
"html": "The defining property of an interval matrix.",
"section": "Recognizing TU",
"slide": "Three families",
"keys": [
"consecutive-ones property"
]
},
{
"term_html": "Ghouila-Houri's theorem",
"html": "\\(A\\) is TU if and only if every subset \\(R\\) of rows has a signing \\(\\sigma \\in \\{\\pm 1\\}^R\\) with \\(\\sum_{r \\in R} \\sigma_r a_r \\in \\{-1, 0, 1\\}^n\\) (1962).",
"section": "Recognizing TU",
"slide": "Three families",
"keys": [
"ghouila-houri's theorem"
]
},
{
"term_html": "signing",
"html": "The \\(\\pm 1\\) choice per row in Ghouila-Houri's test. A row subset with no valid signing is the <em>witness</em> that \\(A\\) is not TU.",
"section": "Recognizing TU",
"slide": "Three families",
"keys": [
"signing"
]
},
{
"term_html": "TU-preserving operations",
"html": "Transposing, negating a row or column, permuting, duplicating or deleting rows and columns, appending a unit row or column, and pivoting. A flow model with bound constraints stays TU.",
"section": "Recognizing TU",
"slide": "Three families",
"keys": [
"tu-preserving operations"
]
},
{
"term_html": "Seymour's decomposition",
"html": "Every TU matrix is built by 1-, 2- and 3-sums from network matrices, their transposes and two special \\(5 \\times 5\\) matrices (1980). Gives polynomial recognition.",
"section": "Recognizing TU",
"slide": "Three families",
"keys": [
"seymour's decomposition"
]
},
{
"term_html": "TU core with side constraints",
"html": "A mostly TU model broken by a few extra constraints, such as a flow with a budget constraint. The setting Lagrangian relaxation exploits (unit 11).",
"section": "Recognizing TU",
"slide": "Testing by brute force, and why nobody does",
"keys": [
"tu core with side constraints"
]
},
{
"term_html": "odd cycle",
"html": "A cycle with an odd number of edges. Its incidence matrix has determinant \\(\\pm 2\\), so a graph's incidence matrix is TU exactly when the graph is bipartite.",
"section": "Where it ends",
"slide": "The odd cycle",
"keys": [
"odd cycle"
]
},
{
"term_html": "fractional matching polytope",
"html": "\\(\\{x \\ge 0 : \\sum_{e \\ni v} x_e \\le 1\\}\\), the LP relaxation of matching.",
"section": "Where it ends",
"slide": "Half-integrality, and Edmonds' fix",
"keys": [
"fractional matching polytope"
]
},
{
"term_html": "half-integral",
"html": "Every entry in \\(\\{0, \\tfrac12, 1\\}\\). Every vertex of the fractional matching polytope is, with the \\(\\tfrac12\\) entries forming vertex-disjoint odd cycles (Balinski 1965).",
"section": "Where it ends",
"slide": "Half-integrality, and Edmonds' fix",
"keys": [
"half-integral"
]
},
{
"term_html": "odd-set inequalities",
"html": "For every vertex set \\(S\\) of odd size, \\(\\sum_{e \\subseteq S} x_e \\le (|S| - 1)/2\\). Adding them all gives the matching polytope for every graph (Edmonds 1965).",
"section": "Where it ends",
"slide": "Half-integrality, and Edmonds' fix",
"keys": [
"odd-set inequalities"
]
},
{
"term_html": "matching polytope",
"html": "The convex hull of the matchings of a graph. Exponentially many facets and no polynomial extended formulation.",
"section": "Where it ends",
"slide": "Half-integrality, and Edmonds' fix",
"keys": [
"matching polytope"
]
},
{
"term_html": "blossom algorithm",
"html": "Edmonds' polynomial matching algorithm, which never writes the exponential LP down (unit 15).",
"section": "Where it ends",
"slide": "Half-integrality, and Edmonds' fix",
"keys": [
"blossom algorithm"
]
},
{
"term_html": "balanced matrix",
"html": "A 0/1 matrix with no odd submatrix cycle. Set packing, covering and partitioning over one have integral LPs.",
"section": "Where it ends",
"slide": "Beyond TU",
"keys": [
"balanced matrix"
]
},
{
"term_html": "perfect matrix",
"html": "The clique constraints of a perfect graph; the stable-set LP with clique constraints is integral.",
"section": "Where it ends",
"slide": "Beyond TU",
"keys": [
"perfect matrix"
]
},
{
"term_html": "total dual integrality (TDI)",
"html": "A system whose dual has integral optima for every integral objective. With integral \\(b\\) the primal polyhedron is integral, whatever \\(A\\) is (Edmonds &amp; Giles 1977).",
"section": "Where it ends",
"slide": "Beyond TU",
"keys": [
"total dual integrality (tdi)",
"total dual integrality",
"tdi"
]
},
{
"term_html": "polynomial islands",
"html": "The rest of the course's pattern: each integral polyhedron comes with a combinatorial algorithm and a min–max theorem.",
"section": "Where it ends",
"slide": "Beyond TU",
"keys": [
"polynomial islands"
]
}
];
