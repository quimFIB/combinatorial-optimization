// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "global constraint",
"html": "A constraint over an unbounded number of variables with a dedicated propagator that sees its whole structure.",
"section": "Why global",
"slide": "",
"keys": [
"global constraint"
]
},
{
"term_html": "decomposition",
"html": "Writing a global constraint as many small ones, such as alldifferent as pairwise \\(\\ne\\). Its arc consistency is at most as strong as the global's GAC, and often weaker.",
"section": "Why global",
"slide": "What pairwise ≠ cannot see",
"keys": [
"decomposition"
]
},
{
"term_html": "alldifferent",
"html": "All the given variables take different values.",
"section": "Why global",
"slide": "What pairwise ≠ cannot see",
"keys": [
"alldifferent"
]
},
{
"term_html": "generalised arc consistency (GAC)",
"html": "Every remaining value belongs to some satisfying tuple of the constraint; unit 17's domain consistency.",
"section": "Why global",
"slide": "What pairwise ≠ cannot see",
"keys": [
"generalised arc consistency (gac)",
"generalised arc consistency",
"gac"
]
},
{
"term_html": "Hall set",
"html": "\\(k\\) variables whose domains together hold exactly \\(k\\) values. Those values are used up, so every other variable loses them. By Hall's theorem, alldifferent is satisfiable iff no set has fewer values than members.",
"section": "Why global",
"slide": "What pairwise ≠ cannot see",
"keys": [
"hall set"
]
},
{
"term_html": "strength vs cost",
"html": "A stronger propagator removes more and costs more per call. It wins only if the nodes saved outweigh the time per node: the one design question in CP.",
"section": "Why global",
"slide": "What pairwise ≠ cannot see",
"keys": [
"strength vs cost"
]
},
{
"term_html": "value graph",
"html": "The bipartite graph with variables on one side, values on the other, and an edge for each value in each domain.",
"section": "alldifferent",
"slide": "Régin 1994: matching-based filtering",
"keys": [
"value graph"
]
},
{
"term_html": "Régin's filter",
"html": "Find a maximum matching of the value graph (fail if it misses a variable), then remove every edge that lies in no maximum matching. GAC for alldifferent in \\(O(m \\sqrt n)\\).",
"section": "alldifferent",
"slide": "Régin 1994: matching-based filtering",
"keys": [
"régin's filter"
]
},
{
"term_html": "edge in some maximum matching",
"html": "By Berge: matched, or on an even alternating cycle, or on an even alternating path from a free value.",
"section": "alldifferent",
"slide": "Régin 1994: matching-based filtering",
"keys": [
"edge in some maximum matching"
]
},
{
"term_html": "orientation (Régin)",
"html": "Matched edges value → variable, the rest variable → value, so alternating cycles become strongly connected components and alternating paths become reachability to free values.",
"section": "alldifferent",
"slide": "Régin 1994: matching-based filtering",
"keys": [
"orientation (régin)",
"orientation",
"régin"
]
},
{
"term_html": "strongly connected component (SCC)",
"html": "A maximal set of nodes each reachable from every other.",
"section": "alldifferent",
"slide": "Régin 1994: matching-based filtering",
"keys": [
"strongly connected component (scc)",
"strongly connected component",
"scc"
]
},
{
"term_html": "incremental matching",
"html": "Repairing the previous matching after a domain change instead of recomputing it.",
"section": "alldifferent",
"slide": "Régin 1994: matching-based filtering",
"keys": [
"incremental matching"
]
},
{
"term_html": "Hall set behind a removal",
"html": "The closed set reachable from a removed value's node: its variables have exactly as many values as members. The explanation a propagator gives in unit 21.",
"section": "alldifferent",
"slide": "Régin 1994: matching-based filtering",
"keys": [
"hall set behind a removal"
]
},
{
"term_html": "Hall interval",
"html": "A Hall set whose values form an interval; the basis of \\(O(n \\log n)\\) bounds-consistent alldifferent.",
"section": "alldifferent",
"slide": "Régin 1994: matching-based filtering",
"keys": [
"hall interval"
]
},
{
"term_html": "pigeonhole",
"html": "\\(n + 1\\) variables with \\(n\\) values under alldifferent. No perfect matching at the root, while pairwise \\(\\ne\\) needs exhaustive search.",
"section": "alldifferent",
"slide": "Measured: when it pays, and when it doesn't",
"keys": [
"pigeonhole"
]
},
{
"term_html": "cumulative",
"html": "\\(\\text{cumulative}(s, d, r, C)\\): tasks with starts \\(s_i\\), durations \\(d_i\\) and demands \\(r_i\\) never use more than \\(C\\) at once.",
"section": "Scheduling",
"slide": "Cumulative, and timetable filtering",
"keys": [
"cumulative"
]
},
{
"term_html": "compulsory part",
"html": "\\([\\max s_i,\\ \\min s_i + d_i)\\) when non-empty: the time task \\(i\\) runs whatever start it takes.",
"section": "Scheduling",
"slide": "Cumulative, and timetable filtering",
"keys": [
"compulsory part"
]
},
{
"term_html": "profile",
"html": "The total demand of compulsory parts at each time. Above \\(C\\) means failure.",
"section": "Scheduling",
"slide": "Cumulative, and timetable filtering",
"keys": [
"profile"
]
},
{
"term_html": "timetable filtering",
"html": "Removing a start of task \\(i\\) if it would overload a time where the other tasks' compulsory parts already sit. Must subtract the task's own compulsory part. Weak with wide time windows.",
"section": "Scheduling",
"slide": "Cumulative, and timetable filtering",
"keys": [
"timetable filtering"
]
},
{
"term_html": "disjunctive (no-overlap)",
"html": "Cumulative with \\(C = 1\\) and unit demands: one machine, tasks may not overlap.",
"section": "Scheduling",
"slide": "Cumulative, and timetable filtering",
"keys": [
"disjunctive (no-overlap)",
"disjunctive",
"no-overlap"
]
},
{
"term_html": "job-shop",
"html": "Jobs made of ordered operations, each on one machine, minimizing the finish time. The lab's ft06 has optimum 55.",
"section": "Scheduling",
"slide": "Cumulative, and timetable filtering",
"keys": [
"job-shop"
]
},
{
"term_html": "edge-finding",
"html": "If a task cannot finish before a set \\(\\Omega\\) of tasks all end, it must end last among them, raising its start.",
"section": "Scheduling",
"slide": "Stronger scheduling reasoning",
"keys": [
"edge-finding"
]
},
{
"term_html": "\\(\\Theta\\)-tree",
"html": "A balanced tree keyed by earliest start that makes edge-finding \\(O(n \\log n)\\) (Vilím 2004).",
"section": "Scheduling",
"slide": "Stronger scheduling reasoning",
"keys": [
"\\theta-tree"
]
},
{
"term_html": "est, lct",
"html": "Earliest start time and latest completion time of a task or set.",
"section": "Scheduling",
"slide": "Stronger scheduling reasoning",
"keys": [
"est, lct",
"est",
"lct"
]
},
{
"term_html": "not-first / not-last",
"html": "Detecting that a task cannot come first, or last, among a set.",
"section": "Scheduling",
"slide": "Stronger scheduling reasoning",
"keys": [
"not-first / not-last"
]
},
{
"term_html": "energetic reasoning",
"html": "Comparing the minimum energy tasks must spend inside an interval with \\(C\\) times its length.",
"section": "Scheduling",
"slide": "Stronger scheduling reasoning",
"keys": [
"energetic reasoning"
]
},
{
"term_html": "time-table edge-finding",
"html": "Edge-finding that also uses the compulsory-part profile (Vilím 2011).",
"section": "Scheduling",
"slide": "Stronger scheduling reasoning",
"keys": [
"time-table edge-finding"
]
},
{
"term_html": "element",
"html": "\\(\\text{element}(i, T, v)\\): \\(v = T[i]\\) with \\(i\\) a variable.",
"section": "The catalogue",
"slide": "A few globals worth knowing",
"keys": [
"element"
]
},
{
"term_html": "table",
"html": "The variables' tuple must be one of an explicit list; filtered by STR, compact tables or MDDs.",
"section": "The catalogue",
"slide": "A few globals worth knowing",
"keys": [
"table"
]
},
{
"term_html": "global cardinality (gcc)",
"html": "Each value \\(a\\) is used between \\(l_a\\) and \\(u_a\\) times. Filtered by flow (Régin 1996); alldifferent is the case \\(l_a = 0\\), \\(u_a = 1\\).",
"section": "The catalogue",
"slide": "A few globals worth knowing",
"keys": [
"global cardinality (gcc)",
"global cardinality",
"gcc"
]
},
{
"term_html": "regular",
"html": "The sequence of variables spells a word accepted by a finite automaton. Filtered by reachability in a layered graph (Pesant 2004).",
"section": "The catalogue",
"slide": "A few globals worth knowing",
"keys": [
"regular"
]
},
{
"term_html": "circuit",
"html": "Successor variables form a single Hamiltonian cycle.",
"section": "The catalogue",
"slide": "A few globals worth knowing",
"keys": [
"circuit"
]
},
{
"term_html": "Global Constraint Catalog",
"html": "Beldiceanu, Carlsson &amp; Rampon's reference of 400+ constraints with semantics, decompositions and filtering algorithms.",
"section": "The catalogue",
"slide": "A few globals worth knowing",
"keys": [
"global constraint catalog"
]
}
];
