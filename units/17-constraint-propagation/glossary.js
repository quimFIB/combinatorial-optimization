// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "constraint satisfaction problem (CSP)",
"html": "Variables \\(x_1, \\dots, x_n\\), finite domains \\(D_i\\), and constraints over subsets of the variables.",
"section": "The formalism",
"slide": "Constraint satisfaction problems",
"keys": [
"constraint satisfaction problem (csp)",
"constraint satisfaction problem",
"csp"
]
},
{
"term_html": "domain",
"html": "The set of values a variable may still take.",
"section": "The formalism",
"slide": "Constraint satisfaction problems",
"keys": [
"domain"
]
},
{
"term_html": "constraint",
"html": "An arbitrary relation over some variables' domains: \"≠\", \"all different\", a table of allowed tuples. No linearity required.",
"section": "The formalism",
"slide": "Constraint satisfaction problems",
"keys": [
"constraint"
]
},
{
"term_html": "solution (CSP)",
"html": "An assignment of a domain value to every variable satisfying every constraint.",
"section": "The formalism",
"slide": "Constraint satisfaction problems",
"keys": [
"solution (csp)",
"solution",
"csp"
]
},
{
"term_html": "optimization in CP",
"html": "Adding \"objective &lt; best\" after each solution and continuing to search.",
"section": "The formalism",
"slide": "Constraint satisfaction problems",
"keys": [
"optimization in cp"
]
},
{
"term_html": "prune vs relax",
"html": "CP's core move removes impossible values; MIP's relaxes and bounds. Neither dominates.",
"section": "The formalism",
"slide": "Constraint satisfaction problems",
"keys": [
"prune vs relax"
]
},
{
"term_html": "consistency level",
"html": "How much local reasoning a propagation step enforces.",
"section": "Consistency",
"slide": "A ladder of consistency levels",
"keys": [
"consistency level"
]
},
{
"term_html": "node consistency",
"html": "Every value satisfies the unary constraints.",
"section": "Consistency",
"slide": "A ladder of consistency levels",
"keys": [
"node consistency"
]
},
{
"term_html": "support",
"html": "For a binary constraint on \\((x, y)\\), a value \\(b \\in D_y\\) compatible with \\(a \\in D_x\\).",
"section": "Consistency",
"slide": "A ladder of consistency levels",
"keys": [
"support"
]
},
{
"term_html": "arc consistency (AC)",
"html": "Every value of every variable has a support on every binary constraint.",
"section": "Consistency",
"slide": "A ladder of consistency levels",
"keys": [
"arc consistency (ac)",
"arc consistency",
"ac"
]
},
{
"term_html": "path consistency",
"html": "Every consistent pair of values extends to any third variable. Rarely enforced.",
"section": "Consistency",
"slide": "A ladder of consistency levels",
"keys": [
"path consistency"
]
},
{
"term_html": "\\(k\\)-consistency",
"html": "Every consistent assignment to \\(k - 1\\) variables extends to any \\(k\\)-th. Costs \\(O(n^k d^k)\\).",
"section": "Consistency",
"slide": "A ladder of consistency levels",
"keys": [
"k-consistency"
]
},
{
"term_html": "strong \\(k\\)-consistency",
"html": "\\(j\\)-consistency for every \\(j \\le k\\). Strong \\(n\\)-consistency means backtrack-free search.",
"section": "Consistency",
"slide": "A ladder of consistency levels",
"keys": [
"strong k-consistency"
]
},
{
"term_html": "constraint graph",
"html": "Variables as nodes, an edge for each binary constraint.",
"section": "Consistency",
"slide": "A ladder of consistency levels",
"keys": [
"constraint graph"
]
},
{
"term_html": "revise",
"html": "Removing the values of \\(x\\) that have no support in \\(y\\) for one arc. The step AC-3 repeats.",
"section": "Consistency",
"slide": "A ladder of consistency levels",
"keys": [
"revise"
]
},
{
"term_html": "AC-3",
"html": "A queue of arcs, revised until none changes anything. \\(O(ed^3)\\) (Mackworth 1977).",
"section": "Consistency",
"slide": "A ladder of consistency levels",
"keys": [
"ac-3"
]
},
{
"term_html": "AC-4",
"html": "Support counters per value. \\(O(ed^2)\\) time, heavy in memory.",
"section": "Consistency",
"slide": "A ladder of consistency levels",
"keys": [
"ac-4"
]
},
{
"term_html": "AC-2001",
"html": "AC-3 plus a \"last support\" pointer per value, reaching \\(O(ed^2)\\).",
"section": "Consistency",
"slide": "A ladder of consistency levels",
"keys": [
"ac-2001"
]
},
{
"term_html": "Freuder's theorem",
"html": "On a tree-shaped constraint graph, arc consistency makes search backtrack-free; width \\(w\\) plus strong \\((w+1)\\)-consistency does in general (1982).",
"section": "Consistency",
"slide": "A ladder of consistency levels",
"keys": [
"freuder's theorem"
]
},
{
"term_html": "sound",
"html": "Never removes a value that belongs to a solution.",
"section": "Consistency",
"slide": "Arc consistent, yet unsatisfiable",
"keys": [
"sound"
]
},
{
"term_html": "complete",
"html": "Removes every value that belongs to no solution. Arc consistency is sound but not complete: an odd cycle with two colours is arc consistent and unsatisfiable.",
"section": "Consistency",
"slide": "Arc consistent, yet unsatisfiable",
"keys": [
"complete"
]
},
{
"term_html": "confluence",
"html": "The fixpoint does not depend on the order propagators run in; only the number of propagations does.",
"section": "Consistency",
"slide": "Arc consistent, yet unsatisfiable",
"keys": [
"confluence"
]
},
{
"term_html": "domain (generalised arc) consistency",
"html": "Every value in every domain belongs to some satisfying tuple of the constraint.",
"section": "Consistency",
"slide": "Bounds consistency vs domain consistency",
"keys": [
"domain (generalised arc) consistency"
]
},
{
"term_html": "bounds consistency",
"html": "Only each domain's min and max need supports, with the others relaxed to intervals. Interior holes are ignored.",
"section": "Consistency",
"slide": "Bounds consistency vs domain consistency",
"keys": [
"bounds consistency"
]
},
{
"term_html": "redundant (implied) constraint",
"html": "A constraint that changes nothing semantically but gives propagation more to work with, like \\(\\sum_i s_i = n\\) in magic series.",
"section": "Consistency",
"slide": "Bounds consistency vs domain consistency",
"keys": [
"redundant (implied) constraint"
]
},
{
"term_html": "propagator",
"html": "A function \\(p : D \\to D\\) for one constraint that narrows domains.",
"section": "The engine",
"slide": "Propagators and the fixpoint",
"keys": [
"propagator"
]
},
{
"term_html": "contracting",
"html": "\\(p(D) \\subseteq D\\).",
"section": "The engine",
"slide": "Propagators and the fixpoint",
"keys": [
"contracting"
]
},
{
"term_html": "monotone (propagator)",
"html": "\\(D \\subseteq D'\\) implies \\(p(D) \\subseteq p(D')\\). Needed for confluence.",
"section": "The engine",
"slide": "Propagators and the fixpoint",
"keys": [
"monotone (propagator)",
"monotone",
"propagator"
]
},
{
"term_html": "idempotent",
"html": "Running the propagator twice gives nothing more than running it once. LinearEq and Count are not, so they are re-queued.",
"section": "The engine",
"slide": "Propagators and the fixpoint",
"keys": [
"idempotent"
]
},
{
"term_html": "fixpoint",
"html": "The domains after running propagators until none changes anything: the greatest common fixpoint, independent of order (Apt 1999).",
"section": "The engine",
"slide": "Propagators and the fixpoint",
"keys": [
"fixpoint"
]
},
{
"term_html": "watch list",
"html": "For each variable, the propagators to wake when it changes.",
"section": "The engine",
"slide": "Propagators and the fixpoint",
"keys": [
"watch list"
]
},
{
"term_html": "propagation (count)",
"html": "One propagator call; the measure of inference effort.",
"section": "The engine",
"slide": "Propagators and the fixpoint",
"keys": [
"propagation (count)",
"propagation",
"count"
]
},
{
"term_html": "propagation events",
"html": "Finer wake-up reasons: fixed, bounds changed, any change.",
"section": "The engine",
"slide": "Propagators and the fixpoint",
"keys": [
"propagation events"
]
},
{
"term_html": "trailing",
"html": "Logging each domain change so it can be undone back to a mark on backtrack.",
"section": "The engine",
"slide": "Trailing, copying, or recomputing",
"keys": [
"trailing"
]
},
{
"term_html": "trail",
"html": "The log itself.",
"section": "The engine",
"slide": "Trailing, copying, or recomputing",
"keys": [
"trail"
]
},
{
"term_html": "copying",
"html": "Snapshotting the whole store at each search node.",
"section": "The engine",
"slide": "Trailing, copying, or recomputing",
"keys": [
"copying"
]
},
{
"term_html": "recomputation",
"html": "Storing only the decisions and replaying them on backtrack.",
"section": "The engine",
"slide": "Trailing, copying, or recomputing",
"keys": [
"recomputation"
]
},
{
"term_html": "structural sharing",
"html": "Immutable domain tuples that share unchanged parts, making copying cheap; the functional engine's approach.",
"section": "The engine",
"slide": "Trailing, copying, or recomputing",
"keys": [
"structural sharing"
]
},
{
"term_html": "CP search loop",
"html": "Propagate to a fixpoint; fail on an empty domain; accept when all variables are fixed; otherwise branch and recurse.",
"section": "Search",
"slide": "The CP loop, and its two numbers",
"keys": [
"cp search loop"
]
},
{
"term_html": "first-fail",
"html": "Branch on the variable with the smallest domain, so dead ends show up near the root.",
"section": "Search",
"slide": "The CP loop, and its two numbers",
"keys": [
"first-fail"
]
},
{
"term_html": "binary branching",
"html": "\\(x = a\\), then \\(x \\ne a\\). The second branch is propagated, unlike \\(d\\)-way branching with one child per value.",
"section": "Search",
"slide": "The CP loop, and its two numbers",
"keys": [
"binary branching"
]
},
{
"term_html": "node (search)",
"html": "One search state; the measure of search effort.",
"section": "Search",
"slide": "The CP loop, and its two numbers",
"keys": [
"node (search)",
"node",
"search"
]
},
{
"term_html": "failure",
"html": "A node where some domain became empty.",
"section": "Search",
"slide": "The CP loop, and its two numbers",
"keys": [
"failure"
]
},
{
"term_html": "nodes vs propagations",
"html": "Stronger propagation lowers nodes and raises propagations per node. Units 18–21 each trade one against the other.",
"section": "Search",
"slide": "The CP loop, and its two numbers",
"keys": [
"nodes vs propagations"
]
},
{
"term_html": "magic series",
"html": "A sequence \\(s_0, \\dots, s_{n-1}\\) where \\(s_i\\) counts the occurrences of \\(i\\) in the sequence. One of the lab's models.",
"section": "Search",
"slide": "The CP loop, and its two numbers",
"keys": [
"magic series"
]
}
];
