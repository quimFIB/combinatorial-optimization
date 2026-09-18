// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "positive semidefinite (PSD)",
"html": "A symmetric matrix with all eigenvalues \\(\\ge 0\\), written \\(X \\succeq 0\\).",
"section": "The PSD cone",
"slide": "Semidefinite programs are vector programs",
"keys": [
"positive semidefinite (psd)",
"positive semidefinite",
"psd"
]
},
{
"term_html": "PSD cone",
"html": "The set of PSD matrices: convex, but not polyhedral.",
"section": "The PSD cone",
"slide": "Semidefinite programs are vector programs",
"keys": [
"psd cone"
]
},
{
"term_html": "semidefinite program (SDP)",
"html": "\\(\\max \\langle C, X \\rangle\\) subject to \\(\\langle A_k, X \\rangle = b_k\\) and \\(X \\succeq 0\\). Linear programming over matrices.",
"section": "The PSD cone",
"slide": "Semidefinite programs are vector programs",
"keys": [
"semidefinite program (sdp)",
"semidefinite program",
"sdp"
]
},
{
"term_html": "\\(\\langle C, X \\rangle\\)",
"html": "The trace inner product \\(\\sum_{ij} C_{ij} X_{ij}\\).",
"section": "The PSD cone",
"slide": "Semidefinite programs are vector programs",
"keys": [
"\\langle c, x \\rangle"
]
},
{
"term_html": "Gram matrix",
"html": "\\(X = VV^\\top\\), so \\(X_{ij} = v_i \\cdot v_j\\). Every PSD matrix is one, which makes an SDP an optimization over vectors with linear constraints on their inner products.",
"section": "The PSD cone",
"slide": "Semidefinite programs are vector programs",
"keys": [
"gram matrix"
]
},
{
"term_html": "vector program",
"html": "The SDP read as a choice of vectors \\(v_1, \\dots, v_n\\). Restricting \\(v_i\\) to \\(\\{\\pm 1\\}\\) gives the integer problem.",
"section": "The PSD cone",
"slide": "Semidefinite programs are vector programs",
"keys": [
"vector program"
]
},
{
"term_html": "log-det barrier",
"html": "\\(-\\log\\det X\\), the barrier interior-point methods use for the PSD cone.",
"section": "The PSD cone",
"slide": "Semidefinite programs are vector programs",
"keys": [
"log-det barrier"
]
},
{
"term_html": "Slater point",
"html": "A strictly feasible point (\\(X \\succ 0\\)). SDP strong duality needs one, unlike LP.",
"section": "The PSD cone",
"slide": "Semidefinite programs are vector programs",
"keys": [
"slater point"
]
},
{
"term_html": "low-rank solution",
"html": "Some optimal \\(X\\) has rank \\(r\\) with \\(r(r+1)/2\\) at most the number of constraints (Barvinok 1995; Pataki 1998).",
"section": "The PSD cone",
"slide": "Semidefinite programs are vector programs",
"keys": [
"low-rank solution"
]
},
{
"term_html": "Burer–Monteiro method",
"html": "Optimizing directly over a low-rank factor \\(V\\), non-convexly, instead of over \\(X\\). Scales SDP relaxations to very large \\(n\\).",
"section": "The PSD cone",
"slide": "Semidefinite programs are vector programs",
"keys": [
"burer–monteiro method"
]
},
{
"term_html": "eigendecomposition",
"html": "\\(X = Q \\Lambda Q^\\top\\); the lab recovers vectors from it, clipping tiny negative eigenvalues.",
"section": "The PSD cone",
"slide": "Semidefinite programs are vector programs",
"keys": [
"eigendecomposition"
]
},
{
"term_html": "Max-Cut SDP",
"html": "\\(\\max \\sum_{uv \\in E} w_{uv} (1 - v_u \\cdot v_v)/2\\) with every \\(\\|v_u\\| = 1\\). At least OPT.",
"section": "Goemans–Williamson",
"slide": "The relaxation and the rounding (1995)",
"keys": [
"max-cut sdp"
]
},
{
"term_html": "hyperplane rounding",
"html": "Draw \\(r\\) with independent \\(N(0, 1)\\) entries and put \\(u\\) on the side of \\(\\mathrm{sign}(v_u \\cdot r)\\). Gaussians make the direction uniform; uniform \\([0, 1)\\) coordinates do not.",
"section": "Goemans–Williamson",
"slide": "The relaxation and the rounding (1995)",
"keys": [
"hyperplane rounding"
]
},
{
"term_html": "separation probability",
"html": "Two unit vectors at angle \\(\\theta\\) are separated by a random hyperplane with probability \\(\\theta / \\pi\\).",
"section": "Goemans–Williamson",
"slide": "The relaxation and the rounding (1995)",
"keys": [
"separation probability"
]
},
{
"term_html": "\\(\\alpha_{GW}\\)",
"html": "\\(\\min_\\theta \\frac{\\theta/\\pi}{(1 - \\cos\\theta)/2} \\approx 0.87856\\), attained at about \\(133.6°\\). The Goemans–Williamson ratio.",
"section": "Goemans–Williamson",
"slide": "The relaxation and the rounding (1995)",
"keys": [
"\\alpha_{gw}"
]
},
{
"term_html": "Goemans–Williamson algorithm",
"html": "Solve the Max-Cut SDP, round with a random hyperplane. Expected cut at least \\(0.878 \\cdot \\mathrm{OPT}\\).",
"section": "Goemans–Williamson",
"slide": "The relaxation and the rounding (1995)",
"keys": [
"goemans–williamson algorithm"
]
},
{
"term_html": "edge LP",
"html": "The Max-Cut LP with \\(z_e \\le x_u + x_v\\) and \\(z_e \\le 2 - x_u - x_v\\). Useless: \\(x = \\tfrac12\\) sets every \\(z_e = 1\\).",
"section": "Goemans–Williamson",
"slide": "Measured: the bound ladder and the rounded cuts",
"keys": [
"edge lp"
]
},
{
"term_html": "triangle (metric) LP",
"html": "A variable \\(z_{ij} \\in [0, 1]\\) for every pair, and for every triple \\(z_{ij} + z_{jk} + z_{ik} \\le 2\\) and \\(z_{ij} \\le z_{ik} + z_{jk}\\) with its rotations. Strong on small graphs, stuck at \\(\\tfrac23\\) of the weight on large dense ones, and needs \\(4\\binom{n}{3}\\) constraints.",
"section": "Goemans–Williamson",
"slide": "Measured: the bound ladder and the rounded cuts",
"keys": [
"triangle (metric) lp"
]
},
{
"term_html": "cut polytope",
"html": "The convex hull of cut incidence vectors.",
"section": "Goemans–Williamson",
"slide": "Measured: the bound ladder and the rounded cuts",
"keys": [
"cut polytope"
]
},
{
"term_html": "three senses of tightness",
"html": "The rounding analysis is tight per edge; the SDP itself has integrality gap \\(\\alpha_{GW}\\) (Feige &amp; Schechtman 2002); and no algorithm beats it under UGC (Khot et al. 2007).",
"section": "Goemans–Williamson",
"slide": "Why 0.878 is nonetheless tight",
"keys": [
"three senses of tightness"
]
},
{
"term_html": "Majority is Stablest",
"html": "The Fourier-analytic theorem behind Max-Cut's UGC hardness (Mossel, O'Donnell &amp; Oleszkiewicz 2010).",
"section": "Goemans–Williamson",
"slide": "Why 0.878 is nonetheless tight",
"keys": [
"majority is stablest"
]
},
{
"term_html": "independence number \\(\\alpha(G)\\)",
"html": "The size of a largest independent set.",
"section": "Theta",
"slide": "The Lovász theta function (1979)",
"keys": [
"independence number \\alpha(g)"
]
},
{
"term_html": "clique cover number \\(\\chi(\\bar G)\\)",
"html": "The fewest cliques covering the vertices; the chromatic number of the complement.",
"section": "Theta",
"slide": "The Lovász theta function (1979)",
"keys": [
"clique cover number \\chi(\\bar g)"
]
},
{
"term_html": "graph complement \\(\\bar G\\)",
"html": "The graph with an edge exactly where \\(G\\) has none.",
"section": "Theta",
"slide": "The Lovász theta function (1979)",
"keys": [
"graph complement \\bar g"
]
},
{
"term_html": "Lovász theta function \\(\\vartheta(G)\\)",
"html": "\\(\\max \\sum_{ij} X_{ij}\\) subject to \\(\\mathrm{tr}\\,X = 1\\), \\(X \\succeq 0\\), and \\(X_{uv} = 0\\) on edges.",
"section": "Theta",
"slide": "The Lovász theta function (1979)",
"keys": [
"lovász theta function \\vartheta(g)"
]
},
{
"term_html": "sandwich theorem",
"html": "\\(\\alpha(G) \\le \\vartheta(G) \\le \\chi(\\bar G)\\). Both outer numbers are NP-hard; \\(\\vartheta\\) is computable to any precision.",
"section": "Theta",
"slide": "The Lovász theta function (1979)",
"keys": [
"sandwich theorem"
]
},
{
"term_html": "perfect graph",
"html": "A graph where \\(\\alpha = \\chi(\\bar G)\\) for every induced subgraph. There \\(\\vartheta\\) computes both in polynomial time.",
"section": "Theta",
"slide": "The Lovász theta function (1979)",
"keys": [
"perfect graph"
]
},
{
"term_html": "Shannon capacity",
"html": "The zero-error rate of a noisy channel whose confusable symbols form a graph. For \\(C_5\\) it is \\(\\sqrt 5 = \\vartheta(C_5)\\), which is why Lovász invented \\(\\vartheta\\).",
"section": "Theta",
"slide": "The Lovász theta function (1979)",
"keys": [
"shannon capacity"
]
},
{
"term_html": "Lasserre (sum-of-squares) hierarchy",
"html": "Level \\(r\\) has a variable \\(y_S\\) for every set of at most \\(2r\\) variables and requires the moment matrix to be PSD. Level 1 on Max-Cut is GW's SDP; level \\(n\\) is exact; size \\(n^{O(r)}\\).",
"section": "Hierarchies and cost",
"slide": "Lasserre, sum of squares, and lower bounds against them",
"keys": [
"lasserre (sum-of-squares) hierarchy"
]
},
{
"term_html": "pseudo-distribution",
"html": "The object the \\(y_S\\) describe: consistent low-degree moments without a true distribution behind them.",
"section": "Hierarchies and cost",
"slide": "Lasserre, sum of squares, and lower bounds against them",
"keys": [
"pseudo-distribution"
]
},
{
"term_html": "moment matrix",
"html": "\\((y_{S \\cup T})_{|S|, |T| \\le r}\\), required to be PSD.",
"section": "Hierarchies and cost",
"slide": "Lasserre, sum of squares, and lower bounds against them",
"keys": [
"moment matrix"
]
},
{
"term_html": "sum-of-squares certificate",
"html": "A proof of \\(f \\ge c\\) writing \\(f - c\\) as a sum of squared polynomials modulo the constraints; the dual of the moment relaxation.",
"section": "Hierarchies and cost",
"slide": "Lasserre, sum of squares, and lower bounds against them",
"keys": [
"sum-of-squares certificate"
]
},
{
"term_html": "Sherali–Adams hierarchy",
"html": "The same lifting with linear constraints only.",
"section": "Hierarchies and cost",
"slide": "Lasserre, sum of squares, and lower bounds against them",
"keys": [
"sherali–adams hierarchy"
]
},
{
"term_html": "hierarchy lower bound",
"html": "An instance needing level \\(\\Omega(n)\\) to refute, such as random 3-XOR (Grigoriev 2001). Rules out a whole family of convex relaxations without complexity assumptions.",
"section": "Hierarchies and cost",
"slide": "Lasserre, sum of squares, and lower bounds against them",
"keys": [
"hierarchy lower bound"
]
},
{
"term_html": "3-XOR",
"html": "Constraints saying the sum of three Boolean variables modulo 2 is a given value.",
"section": "Hierarchies and cost",
"slide": "Lasserre, sum of squares, and lower bounds against them",
"keys": [
"3-xor"
]
},
{
"term_html": "SDP-based branch and bound",
"html": "Using SDP bounds inside branch and bound, the state of the art for dense Max-Cut (BiqMac).",
"section": "Hierarchies and cost",
"slide": "Convex, polynomial, and expensive",
"keys": [
"sdp-based branch and bound"
]
}
];
