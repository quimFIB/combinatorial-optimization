// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "literal",
"html": "A Boolean variable \\(x\\) or its negation \\(\\lnot x\\).",
"section": "From DPLL to CDCL",
"slide": "CNF, resolution, and unit propagation",
"keys": [
"literal"
]
},
{
"term_html": "clause",
"html": "A disjunction of literals.",
"section": "From DPLL to CDCL",
"slide": "CNF, resolution, and unit propagation",
"keys": [
"clause"
]
},
{
"term_html": "CNF",
"html": "Conjunctive normal form: a conjunction of clauses.",
"section": "From DPLL to CDCL",
"slide": "CNF, resolution, and unit propagation",
"keys": [
"cnf"
]
},
{
"term_html": "SAT",
"html": "Deciding whether a CNF has a satisfying assignment. NP-complete (Cook 1971); 3-SAT already is.",
"section": "From DPLL to CDCL",
"slide": "CNF, resolution, and unit propagation",
"keys": [
"sat"
]
},
{
"term_html": "resolution",
"html": "From \\(C \\lor x\\) and \\(D \\lor \\lnot x\\), derive \\(C \\lor D\\).",
"section": "From DPLL to CDCL",
"slide": "CNF, resolution, and unit propagation",
"keys": [
"resolution"
]
},
{
"term_html": "refutation",
"html": "A derivation of the empty clause, proving unsatisfiability. Resolution is refutation-complete.",
"section": "From DPLL to CDCL",
"slide": "CNF, resolution, and unit propagation",
"keys": [
"refutation"
]
},
{
"term_html": "unit clause",
"html": "A clause with every literal false but one, which forces that literal.",
"section": "From DPLL to CDCL",
"slide": "CNF, resolution, and unit propagation",
"keys": [
"unit clause"
]
},
{
"term_html": "unit propagation",
"html": "Repeatedly assigning the literals unit clauses force.",
"section": "From DPLL to CDCL",
"slide": "CNF, resolution, and unit propagation",
"keys": [
"unit propagation"
]
},
{
"term_html": "conflict",
"html": "A clause with every literal false.",
"section": "From DPLL to CDCL",
"slide": "CNF, resolution, and unit propagation",
"keys": [
"conflict"
]
},
{
"term_html": "DPLL",
"html": "Branch on a variable, unit-propagate, backtrack chronologically on a conflict (Davis, Logemann &amp; Loveland 1962).",
"section": "From DPLL to CDCL",
"slide": "CNF, resolution, and unit propagation",
"keys": [
"dpll"
]
},
{
"term_html": "two watched literals",
"html": "Watch two non-false literals per clause; revisit a clause only when a watched literal becomes false. Backtracking needs no updates (Chaff 2001).",
"section": "From DPLL to CDCL",
"slide": "CNF, resolution, and unit propagation",
"keys": [
"two watched literals"
]
},
{
"term_html": "CDCL",
"html": "Conflict-driven clause learning: DPLL plus learned clauses, non-chronological backjumping, activity-based branching and restarts.",
"section": "Learning",
"slide": "",
"keys": [
"cdcl"
]
},
{
"term_html": "decision level",
"html": "The number of decisions in force when a literal was assigned.",
"section": "Learning",
"slide": "",
"keys": [
"decision level"
]
},
{
"term_html": "trail",
"html": "The assigned literals in order, with their levels and reasons.",
"section": "Learning",
"slide": "",
"keys": [
"trail"
]
},
{
"term_html": "reason clause",
"html": "The clause that forced a propagated literal.",
"section": "Learning",
"slide": "",
"keys": [
"reason clause"
]
},
{
"term_html": "implication graph",
"html": "A node per assigned literal, with edges from the other literals of its reason clause.",
"section": "Learning",
"slide": "The implication graph and the first UIP",
"keys": [
"implication graph"
]
},
{
"term_html": "unique implication point (UIP)",
"html": "A current-level node on every path from the decision to the conflict.",
"section": "Learning",
"slide": "The implication graph and the first UIP",
"keys": [
"unique implication point (uip)",
"unique implication point",
"uip"
]
},
{
"term_html": "first UIP",
"html": "The UIP closest to the conflict. Computed by resolving the conflict clause with reasons of current-level literals until one remains; gives short clauses that assert the most.",
"section": "Learning",
"slide": "The implication graph and the first UIP",
"keys": [
"first uip"
]
},
{
"term_html": "learned clause",
"html": "The clause derived by conflict analysis, added to the formula.",
"section": "Learning",
"slide": "The implication graph and the first UIP",
"keys": [
"learned clause"
]
},
{
"term_html": "asserting clause",
"html": "A learned clause with exactly one literal at the current level, which becomes unit after backjumping.",
"section": "Learning",
"slide": "The implication graph and the first UIP",
"keys": [
"asserting clause"
]
},
{
"term_html": "non-chronological backjumping",
"html": "Jumping back to the second-highest level in the learned clause, possibly skipping many decisions.",
"section": "Learning",
"slide": "The rest of the engine",
"keys": [
"non-chronological backjumping"
]
},
{
"term_html": "VSIDS",
"html": "Bump the activity of variables in each conflict, growing the bump after every conflict so recent ones weigh more; branch on the most active.",
"section": "Learning",
"slide": "The rest of the engine",
"keys": [
"vsids"
]
},
{
"term_html": "activity",
"html": "The score VSIDS keeps per variable.",
"section": "Learning",
"slide": "The rest of the engine",
"keys": [
"activity"
]
},
{
"term_html": "phase saving",
"html": "Re-assigning a variable its last value when branching on it again.",
"section": "Learning",
"slide": "The rest of the engine",
"keys": [
"phase saving"
]
},
{
"term_html": "restart (CDCL)",
"html": "Clearing the trail while keeping learned clauses and activities, so the new search differs.",
"section": "Learning",
"slide": "The rest of the engine",
"keys": [
"restart (cdcl)",
"restart",
"cdcl"
]
},
{
"term_html": "literal block distance (LBD)",
"html": "The number of distinct decision levels among a learned clause's literals.",
"section": "Learning",
"slide": "The rest of the engine",
"keys": [
"literal block distance (lbd)",
"literal block distance",
"lbd"
]
},
{
"term_html": "glue clause",
"html": "A learned clause with LBD at most 2; kept forever.",
"section": "Learning",
"slide": "The rest of the engine",
"keys": [
"glue clause"
]
},
{
"term_html": "clause deletion",
"html": "Periodically removing the worse half of learned clauses by LBD, never a clause that is a current reason (Glucose 2009).",
"section": "Learning",
"slide": "The rest of the engine",
"keys": [
"clause deletion"
]
},
{
"term_html": "DRAT proof",
"html": "A list of every learned and deleted clause in order, ending with the empty clause, that an independent checker replays.",
"section": "Proofs and limits",
"slide": "DRAT: checkable unsatisfiability",
"keys": [
"drat proof"
]
},
{
"term_html": "RUP (reverse unit propagation)",
"html": "A lemma is RUP if assigning its negation and unit-propagating gives a conflict. Every first-UIP clause is.",
"section": "Proofs and limits",
"slide": "DRAT: checkable unsatisfiability",
"keys": [
"rup (reverse unit propagation)",
"rup",
"reverse unit propagation"
]
},
{
"term_html": "RAT",
"html": "A weaker check than RUP that also admits clauses added by inprocessing, such as blocked clauses.",
"section": "Proofs and limits",
"slide": "DRAT: checkable unsatisfiability",
"keys": [
"rat"
]
},
{
"term_html": "drat-trim",
"html": "The standard DRAT proof checker; cake_lpr is a formally verified one.",
"section": "Proofs and limits",
"slide": "DRAT: checkable unsatisfiability",
"keys": [
"drat-trim"
]
},
{
"term_html": "polynomial simulation",
"html": "One proof system can reproduce another's proofs with at most polynomial blow-up. CDCL with restarts polynomially simulates resolution.",
"section": "Proofs and limits",
"slide": "CDCL is resolution, and pigeonhole defeats resolution",
"keys": [
"polynomial simulation"
]
},
{
"term_html": "pigeonhole formula \\(\\mathrm{PHP}^{n+1}_n\\)",
"html": "\\(n + 1\\) pigeons, \\(n\\) holes, no two pigeons in a hole. Unsatisfiable.",
"section": "Proofs and limits",
"slide": "CDCL is resolution, and pigeonhole defeats resolution",
"keys": [
"pigeonhole formula \\mathrm{php}^{n+1}_n"
]
},
{
"term_html": "Haken's theorem",
"html": "Every resolution refutation of \\(\\mathrm{PHP}^{n+1}_n\\) has size \\(2^{\\Omega(n)}\\) (1985), so every CDCL run on it takes exponentially many conflicts.",
"section": "Proofs and limits",
"slide": "CDCL is resolution, and pigeonhole defeats resolution",
"keys": [
"haken's theorem"
]
},
{
"term_html": "clause width",
"html": "The number of literals in a clause. A refutation forced to contain wide clauses must be large (Ben-Sasson &amp; Wigderson 2001).",
"section": "Proofs and limits",
"slide": "CDCL is resolution, and pigeonhole defeats resolution",
"keys": [
"clause width"
]
},
{
"term_html": "stronger proof systems",
"html": "Cutting planes and extended resolution have short pigeonhole proofs; pseudo-Boolean solvers exploit the former.",
"section": "Proofs and limits",
"slide": "CDCL is resolution, and pigeonhole defeats resolution",
"keys": [
"stronger proof systems"
]
},
{
"term_html": "encoding",
"html": "A translation of a constraint into CNF.",
"section": "Encodings",
"slide": "Tseitin, at-most-one, cardinality",
"keys": [
"encoding"
]
},
{
"term_html": "Tseitin transformation",
"html": "Naming every subformula with a fresh variable. Linear size and equisatisfiable (1968).",
"section": "Encodings",
"slide": "Tseitin, at-most-one, cardinality",
"keys": [
"tseitin transformation"
]
},
{
"term_html": "equisatisfiable",
"html": "Satisfiable exactly when the original is, though not necessarily over the same variables.",
"section": "Encodings",
"slide": "Tseitin, at-most-one, cardinality",
"keys": [
"equisatisfiable"
]
},
{
"term_html": "auxiliary variable",
"html": "A fresh variable an encoding introduces.",
"section": "Encodings",
"slide": "Tseitin, at-most-one, cardinality",
"keys": [
"auxiliary variable"
]
},
{
"term_html": "at-most-one (AMO)",
"html": "At most one of \\(n\\) literals is true.",
"section": "Encodings",
"slide": "Tseitin, at-most-one, cardinality",
"keys": [
"at-most-one (amo)",
"at-most-one",
"amo"
]
},
{
"term_html": "pairwise encoding",
"html": "\\(\\binom{n}{2}\\) binary clauses forbidding each pair.",
"section": "Encodings",
"slide": "Tseitin, at-most-one, cardinality",
"keys": [
"pairwise encoding"
]
},
{
"term_html": "sequential counter",
"html": "An AMO encoding with \\(n - 1\\) auxiliaries and \\(3n - 4\\) clauses (Sinz 2005).",
"section": "Encodings",
"slide": "Tseitin, at-most-one, cardinality",
"keys": [
"sequential counter"
]
},
{
"term_html": "bitwise encoding",
"html": "An AMO encoding with \\(\\lceil \\log n \\rceil\\) auxiliaries and \\(n \\lceil \\log n \\rceil\\) clauses. Not arc consistent in general.",
"section": "Encodings",
"slide": "Tseitin, at-most-one, cardinality",
"keys": [
"bitwise encoding"
]
},
{
"term_html": "at-most-\\(k\\)",
"html": "At most \\(k\\) of \\(n\\) literals true: sequential counters, sorting and cardinality networks, totalizers.",
"section": "Encodings",
"slide": "Tseitin, at-most-one, cardinality",
"keys": [
"at-most-k"
]
},
{
"term_html": "arc consistency (encoding)",
"html": "Unit propagation on the encoding prunes as much as the constraint would. More important than clause count.",
"section": "Encodings",
"slide": "Tseitin, at-most-one, cardinality",
"keys": [
"arc consistency (encoding)",
"arc consistency",
"encoding"
]
}
];
