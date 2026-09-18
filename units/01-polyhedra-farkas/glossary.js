// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "halfspace",
"html": "\\(\\{x : ax \\le \\beta\\}\\) with \\(a \\ne 0\\).",
"section": "Polyhedra",
"slide": "Halfspaces, polyhedra, polytopes",
"keys": [
"halfspace"
]
},
{
"term_html": "hyperplane",
"html": "The boundary \\(\\{x : ax = \\beta\\}\\) of a halfspace.",
"section": "Polyhedra",
"slide": "Halfspaces, polyhedra, polytopes",
"keys": [
"hyperplane"
]
},
{
"term_html": "polyhedron",
"html": "An intersection of finitely many halfspaces, \\(\\{x : Ax \\le b\\}\\). Always convex and closed.",
"section": "Polyhedra",
"slide": "Halfspaces, polyhedra, polytopes",
"keys": [
"polyhedron"
]
},
{
"term_html": "polytope",
"html": "A bounded polyhedron.",
"section": "Polyhedra",
"slide": "Halfspaces, polyhedra, polytopes",
"keys": [
"polytope"
]
},
{
"term_html": "standard form",
"html": "\\(\\{x : Ax = b,\\ x \\ge 0\\}\\). What simplex works in (unit 02). This unit uses \\(Ax \\le b\\) instead; the conversions are on the same slide.",
"section": "Polyhedra",
"slide": "Halfspaces, polyhedra, polytopes",
"keys": [
"standard form"
]
},
{
"term_html": "slack variable",
"html": "The \\(s \\ge 0\\) that turns \\(ax \\le \\beta\\) into \\(ax + s = \\beta\\).",
"section": "Polyhedra",
"slide": "Halfspaces, polyhedra, polytopes",
"keys": [
"slack variable"
]
},
{
"term_html": "valid inequality",
"html": "\\(cx \\le \\delta\\) is valid for \\(P\\) if every point of \\(P\\) satisfies it.",
"section": "Polyhedra",
"slide": "Faces",
"keys": [
"valid inequality"
]
},
{
"term_html": "face",
"html": "\\(P \\cap \\{x : cx = \\delta\\}\\) for a valid inequality \\(cx \\le \\delta\\). Equivalently: turn some of the constraints of \\(Ax \\le b\\) into equalities. \\(\\emptyset\\) and \\(P\\) itself are the <em>improper</em> faces.",
"section": "Polyhedra",
"slide": "Faces",
"keys": [
"face"
]
},
{
"term_html": "vertex, edge, facet",
"html": "Faces of dimension \\(0\\), \\(1\\), and \\(\\dim P - 1\\).",
"section": "Polyhedra",
"slide": "Faces",
"keys": [
"vertex, edge, facet",
"vertex",
"edge",
"facet"
]
},
{
"term_html": "redundant inequality",
"html": "One that can be deleted without changing \\(P\\). A full-dimensional polyhedron has a unique minimal description: one inequality per facet, everything else redundant.",
"section": "Polyhedra",
"slide": "Faces",
"keys": [
"redundant inequality"
]
},
{
"term_html": "tight constraint",
"html": "Constraint \\(i\\) is tight at the point \\(x\\) when it holds with equality there, \\(a_i x = b_i\\): \\(x\\) lies on that constraint's line (its hyperplane), pressed against that wall. Tightness belongs to a constraint <em>at a point</em>: \\(x + y \\le 4\\) is tight at \\((2.5, 1.5)\\) and not at \\((1, 1)\\). Other books say <em>active</em> or <em>binding</em>, and matrix-minded ones say <em>tight row</em>, since constraint \\(i\\) is row \\(i\\) of \\(Ax \\le b\\).",
"section": "Corners",
"slide": "Tight constraints, and counting them",
"keys": [
"tight constraint"
]
},
{
"term_html": "\\(I(x)\\)",
"html": "The set of constraints tight at \\(x\\), \\(\\{i : a_i x = b_i\\}\\).",
"section": "Corners",
"slide": "Tight constraints, and counting them",
"keys": [
"i(x)"
]
},
{
"term_html": "rank of the tight constraints",
"html": "The rank of the matrix whose rows are \\(\\{a_i : i \\in I(x)\\}\\): how many independent directions the tight constraints pin down. Rank \\(n\\) means they fix \\(x\\) completely. Sometimes shortened to \"tight rank\"; not a separate term.",
"section": "Corners",
"slide": "Tight constraints, and counting them",
"keys": [
"rank of the tight constraints"
]
},
{
"term_html": "vertex",
"html": "A point \\(x \\in P\\) that some objective \\(c\\) makes the <em>unique</em> maximizer of \\(cy\\) over \\(P\\). The geometric name for a corner.",
"section": "Corners",
"slide": "Vertex, extreme point, basic feasible solution",
"keys": [
"vertex"
]
},
{
"term_html": "extreme point",
"html": "A point of \\(P\\) that is not a strict convex combination \\(\\lambda y + (1-\\lambda) z\\) of two different points of \\(P\\). The convexity name.",
"section": "Corners",
"slide": "Vertex, extreme point, basic feasible solution",
"keys": [
"extreme point"
]
},
{
"term_html": "basic feasible solution (BFS)",
"html": "A point of \\(P\\) whose tight constraints have rank \\(n\\). The algebraic name, and the one a computer can check. In standard form it is usually stated with columns instead: the columns of \\(A\\) for the positive entries of \\(x\\) are independent.",
"section": "Corners",
"slide": "Vertex, extreme point, basic feasible solution",
"keys": [
"basic feasible solution (bfs)",
"basic feasible solution",
"bfs"
]
},
{
"term_html": "basic solution",
"html": "A point where \\(n\\) linearly independent constraints are tight, whether or not it lies in \\(P\\). Lab step 3 generates these and discards the infeasible ones.",
"section": "Corners",
"slide": "Finding corners by trying pairs of constraints",
"keys": [
"basic solution"
]
},
{
"term_html": "basis",
"html": "A choice of \\(n\\) independent constraints whose equalities determine a basic solution.",
"section": "Corners",
"slide": "Finding corners by trying pairs of constraints",
"keys": [
"basis"
]
},
{
"term_html": "degenerate vertex",
"html": "A vertex with more than \\(n\\) tight constraints, \\(|I(x)| &gt; n\\), so several bases name the same point. Example: adding \\(3x - y \\le 6\\) to the running example makes \\((2.5, 1.5)\\) tight on 3 constraints with rank 2; in \\(\\mathbb{R}^3\\), the apex of a square pyramid has 4 tight constraints and rank 3. Harmless geometrically; the reason simplex can cycle (unit 02), and the reason lab step 3 must deduplicate.",
"section": "Corners",
"slide": "Finding corners by trying pairs of constraints",
"keys": [
"degenerate vertex"
]
},
{
"term_html": "pointed",
"html": "\\(P\\) has at least one vertex. For nonempty \\(P\\) this is the same as \"contains no line\" and as \\(\\operatorname{rank} A = n\\). Anything inside \\(x \\ge 0\\) is pointed.",
"section": "Corners",
"slide": "Not every polyhedron has a corner",
"keys": [
"pointed"
]
},
{
"term_html": "lineality space",
"html": "\\(\\{d : Ad = 0\\}\\), the directions along which \\(P\\) contains whole lines. \\(P\\) is pointed exactly when this is \\(\\{0\\}\\).",
"section": "Corners",
"slide": "Not every polyhedron has a corner",
"keys": [
"lineality space"
]
},
{
"term_html": "crossover",
"html": "Walking from an arbitrary point of \\(P\\) to a BFS by moving along the null space of the tight constraints until the rank reaches \\(n\\). How solvers turn an interior-point answer into a basic one (unit 04).",
"section": "Corners",
"slide": "Not every polyhedron has a corner",
"keys": [
"crossover"
]
},
{
"term_html": "\\(\\operatorname{conv}(V)\\) (convex hull)",
"html": "\\(\\{\\sum \\lambda_v v : \\lambda \\ge 0,\\ \\sum \\lambda_v = 1\\}\\).",
"section": "Two descriptions",
"slide": "Two descriptions: Minkowski–Weyl",
"keys": [
"\\operatorname{conv}(v) (convex hull)",
"\\operatorname{conv}(v)",
"convex hull"
]
},
{
"term_html": "\\(\\operatorname{cone}(R)\\) (conic hull)",
"html": "\\(\\{\\sum \\mu_r r : \\mu \\ge 0\\}\\). A <em>finitely generated cone</em> when \\(R\\) is finite.",
"section": "Two descriptions",
"slide": "Two descriptions: Minkowski–Weyl",
"keys": [
"\\operatorname{cone}(r) (conic hull)",
"\\operatorname{cone}(r)",
"conic hull"
]
},
{
"term_html": "recession cone",
"html": "\\(\\{d : Ad \\le 0\\}\\), the directions in which \\(P\\) goes off to infinity.",
"section": "Two descriptions",
"slide": "Two descriptions: Minkowski–Weyl",
"keys": [
"recession cone"
]
},
{
"term_html": "extreme ray",
"html": "A direction of the recession cone that is not a positive combination of two other, non-parallel, directions in it. The corners of a cone, in the same sense that vertices are the corners of a polytope.",
"section": "Two descriptions",
"slide": "Two descriptions: Minkowski–Weyl",
"keys": [
"extreme ray"
]
},
{
"term_html": "H-description",
"html": "\\(P\\) given by inequalities \\(Ax \\le b\\).",
"section": "Two descriptions",
"slide": "Two descriptions: Minkowski–Weyl",
"keys": [
"h-description"
]
},
{
"term_html": "V-description",
"html": "\\(P\\) given as \\(\\operatorname{conv}(V) + \\operatorname{cone}(R)\\). Either description can be exponentially larger than the other: the \\(n\\)-cube has \\(2n\\) facets and \\(2^n\\) vertices.",
"section": "Two descriptions",
"slide": "Two descriptions: Minkowski–Weyl",
"keys": [
"v-description"
]
},
{
"term_html": "Minkowski–Weyl theorem",
"html": "Every polyhedron has both descriptions. In particular a polytope is the convex hull of its vertices.",
"section": "Two descriptions",
"slide": "Two descriptions: Minkowski–Weyl",
"keys": [
"minkowski–weyl theorem"
]
},
{
"term_html": "projection",
"html": "\\(\\{x' : \\exists x_k,\\ (x', x_k) \\in P\\}\\), the shadow of \\(P\\) with one coordinate dropped. Always a polyhedron.",
"section": "Fourier–Motzkin elimination",
"slide": "Eliminating one variable",
"keys": [
"projection"
]
},
{
"term_html": "Fourier–Motzkin elimination (FM)",
"html": "Computing that projection by pairing every constraint that bounds \\(x_k\\) from above with every constraint that bounds it from below, using positive multipliers so \\(x_k\\) cancels. Gaussian elimination for inequalities.",
"section": "Fourier–Motzkin elimination",
"slide": "Eliminating one variable",
"keys": [
"fourier–motzkin elimination (fm)",
"fourier–motzkin elimination",
"fm"
]
},
{
"term_html": "\\(Z\\), \\(U\\), \\(L\\)",
"html": "The constraints with \\(a_{ik} = 0\\), \\(a_{ik} &gt; 0\\) (upper bounds on \\(x_k\\)) and \\(a_{ik} &lt; 0\\) (lower bounds). FM outputs \\(|Z| + |U|\\cdot|L|\\) constraints.",
"section": "Fourier–Motzkin elimination",
"slide": "Eliminating one variable",
"keys": [
"z, u, l",
"z",
"u",
"l"
]
},
{
"term_html": "nonnegative combination",
"html": "\\(\\sum y_i (a_i, b_i)\\) with every \\(y_i \\ge 0\\). The only way to combine inequalities that keeps them true; the one fact FM and Farkas both rest on.",
"section": "Fourier–Motzkin elimination",
"slide": "Eliminating one variable",
"keys": [
"nonnegative combination"
]
},
{
"term_html": "FM blow-up",
"html": "Constraint count going roughly \\(m \\to m^2/4\\) per eliminated variable, almost all of it redundant.",
"section": "Fourier–Motzkin elimination",
"slide": "Deciding feasibility, and the explosion",
"keys": [
"fm blow-up"
]
},
{
"term_html": "Chernikov's rule, Imbert's acceleration",
"html": "Bookkeeping that discards redundant FM constraints by tracking which original constraints each derived constraint came from. Not implemented in the lab; named in the slide notes.",
"section": "Fourier–Motzkin elimination",
"slide": "Deciding feasibility, and the explosion",
"keys": [
"chernikov's rule, imbert's acceleration",
"chernikov's rule",
"imbert's acceleration"
]
},
{
"term_html": "Farkas certificate",
"html": "\\(y \\in \\mathbb{R}^m\\) with \\(y \\ge 0\\), \\(y^\\top A = 0\\), \\(y^\\top b &lt; 0\\): a nonnegative combination of the constraints that reads \\(0 \\le\\) (negative). It proves \\(Ax \\le b\\) has no solution.",
"section": "Farkas' lemma",
"slide": "A certificate of infeasibility",
"keys": [
"farkas certificate"
]
},
{
"term_html": "Farkas' lemma",
"html": "Exactly one of: \\(Ax \\le b\\) has a solution, or a Farkas certificate exists. Standard form: exactly one of \\(\\exists x \\ge 0 : Ax = b\\) and \\(\\exists y : A^\\top y \\ge 0,\\ b^\\top y &lt; 0\\).",
"section": "Farkas' lemma",
"slide": "Farkas' lemma",
"keys": [
"farkas' lemma"
]
},
{
"term_html": "theorem of the alternative",
"html": "Any statement of the shape \"exactly one of these two systems is solvable\". Gordan's, Stiemke's and Motzkin's are relatives of Farkas'.",
"section": "Farkas' lemma",
"slide": "Farkas' lemma",
"keys": [
"theorem of the alternative"
]
},
{
"term_html": "tail trick",
"html": "Append the unit vector \\(e_i\\) to constraint \\(i\\) as extra columns that are never eliminated. After FM, a constraint \\(0 \\le c\\) with \\(c &lt; 0\\) carries its own certificate in those columns. Lab step 5.",
"section": "Farkas' lemma",
"slide": "Farkas, constructively",
"keys": [
"tail trick"
]
},
{
"term_html": "separating hyperplane",
"html": "A hyperplane with a set on one side and a point strictly on the other. Farkas, read geometrically: a point outside a finitely generated cone can be separated from it.",
"section": "Farkas' lemma",
"slide": "Farkas, geometrically",
"keys": [
"separating hyperplane"
]
},
{
"term_html": "constraint qualification",
"html": "The extra hypothesis duality needs when the cone is not closed, as in SDP (unit 25). LP never needs one.",
"section": "Farkas' lemma",
"slide": "Farkas, geometrically",
"keys": [
"constraint qualification"
]
},
{
"term_html": "NP ∩ coNP",
"html": "Linear feasibility has short \"yes\" certificates (a solution) and short \"no\" certificates (a Farkas vector, of polynomial bit size by Cramer's rule).",
"section": "Farkas' lemma",
"slide": "Farkas, constructively",
"keys": [
"np ∩ conp"
]
},
{
"term_html": "fundamental theorem of LP (FTLP)",
"html": "If \\(P\\) is nonempty and pointed, then \\(\\max\\{c^\\top x : x \\in P\\}\\) is either unbounded or attained at a vertex. So an LP is infeasible, unbounded, or solved at a corner.",
"section": "Closing the loop",
"slide": "The fundamental theorem of LP",
"keys": [
"fundamental theorem of lp (ftlp)",
"fundamental theorem of lp",
"ftlp"
]
},
{
"term_html": "LP relaxation",
"html": "The LP obtained from an integer program by dropping integrality. Why Part II needs this unit. <em>Title slide notes.</em>",
"section": "Closing the loop",
"slide": "The fundamental theorem of LP",
"keys": [
"lp relaxation"
]
},
{
"term_html": "Chvátal–Gomory cut",
"html": "A nonnegative combination of constraints with integer coefficients and the right side rounded down: Farkas plus rounding (unit 08).",
"section": "Closing the loop",
"slide": "Why this is the root of the trunk",
"keys": [
"chvátal–gomory cut"
]
},
{
"term_html": "row <code>(a, b)</code>",
"html": "One constraint, as a tuple of Python ints meaning \\(a \\cdot x \\le b\\). Exact integers throughout, so a certificate is a proof and not an approximation.",
"section": "In the lab",
"slide": "",
"keys": [
"row ~(a, b)~"
]
},
{
"term_html": "<code>normalize</code>",
"html": "Divides a row by the gcd of its entries, so equal rows compare equal and FM can deduplicate.",
"section": "In the lab",
"slide": "",
"keys": [
"~normalize~"
]
},
{
"term_html": "<code>solve_exact</code>",
"html": "Solves a square system in <code>Fraction</code>'s, returning <code>None</code> when it is singular (the chosen rows are not independent, so not a basis). Given in <code>colib.polyhedra</code>, used by step 3.",
"section": "In the lab",
"slide": "",
"keys": [
"~solve_exact~"
]
},
{
"term_html": "basis enumeration",
"html": "Step 3's method: try all \\(\\binom{m}{n}\\) row subsets as equalities, keep the feasible solutions.",
"section": "In the lab",
"slide": "",
"keys": [
"basis enumeration"
]
}
];
