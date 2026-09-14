// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "lazy clause generation (LCG)",
"html": "CP propagators running inside a CDCL solver's propagation loop, each returning a clause that explains its inference so the solver can learn from it (Ohrimenko, Stuckey &amp; Codish 2007–09).",
"section": "Explanations",
"slide": "",
"keys": [
"lazy clause generation (lcg)",
"lazy clause generation",
"lcg"
]
},
{
"term_html": "order encoding",
"html": "One Boolean \\([x \\le v]\\) per threshold of an integer variable, linked by \\([x \\le v] \\rightarrow [x \\le v + 1]\\). A bound change is a single literal.",
"section": "Explanations",
"slide": "Integers as Booleans: the order encoding",
"keys": [
"order encoding"
]
},
{
"term_html": "bound literal",
"html": "\\([x \\le v]\\), or its negation \\(\\lnot[x \\le v]\\), meaning \\(x \\ge v + 1\\).",
"section": "Explanations",
"slide": "Integers as Booleans: the order encoding",
"keys": [
"bound literal"
]
},
{
"term_html": "lazy literal creation",
"html": "Creating \\([x \\le v]\\) only when propagation or an explanation needs it, so large domains stay affordable.",
"section": "Explanations",
"slide": "Integers as Booleans: the order encoding",
"keys": [
"lazy literal creation"
]
},
{
"term_html": "direct encoding",
"html": "One Boolean \\([x = v]\\) per value. Good for \\(\\ne\\) and tables, bad for bounds.",
"section": "Explanations",
"slide": "Integers as Booleans: the order encoding",
"keys": [
"direct encoding"
]
},
{
"term_html": "log encoding",
"html": "The binary digits of \\(x\\). Compact, with weak propagation.",
"section": "Explanations",
"slide": "Integers as Booleans: the order encoding",
"keys": [
"log encoding"
]
},
{
"term_html": "explanation",
"html": "A clause, valid in every solution of the constraint, whose literals are all false now except the newly propagated one.",
"section": "Explanations",
"slide": "A propagator's inference, as a clause",
"keys": [
"explanation"
]
},
{
"term_html": "explained propagator",
"html": "A propagator that returns an explanation with every narrowing.",
"section": "Explanations",
"slide": "A propagator's inference, as a clause",
"keys": [
"explained propagator"
]
},
{
"term_html": "precedence",
"html": "\\(x + d \\le y\\), explained by \\(\\lnot[x \\ge a] \\lor [y \\ge a + d]\\).",
"section": "Explanations",
"slide": "A propagator's inference, as a clause",
"keys": [
"precedence"
]
},
{
"term_html": "reified constraint",
"html": "A constraint tied to a Boolean \\(b\\) so it holds exactly when \\(b\\) is true, such as \"operation 3 precedes operation 7\".",
"section": "Explanations",
"slide": "A propagator's inference, as a clause",
"keys": [
"reified constraint"
]
},
{
"term_html": "unary resource",
"html": "A machine running one task at a time: cumulative with capacity 1.",
"section": "Explanations",
"slide": "A propagator's inference, as a clause",
"keys": [
"unary resource"
]
},
{
"term_html": "lst, ect",
"html": "A task's latest start time and earliest completion time; its compulsory part is \\([lst, ect)\\).",
"section": "Explanations",
"slide": "A propagator's inference, as a clause",
"keys": [
"lst, ect",
"lst",
"ect"
]
},
{
"term_html": "explanation quality",
"html": "The most general explanation (fewest, weakest literals) gives learned clauses that prune the most. Explaining with every current bound is valid and nearly useless.",
"section": "Explanations",
"slide": "A propagator's inference, as a clause",
"keys": [
"explanation quality"
]
},
{
"term_html": "lazy explanation",
"html": "Recording only enough to rebuild an explanation, and building the clause only if conflict analysis resolves through that literal.",
"section": "Explanations",
"slide": "A propagator's inference, as a clause",
"keys": [
"lazy explanation"
]
},
{
"term_html": "ablation",
"html": "Removing one component at a time to measure what it contributes.",
"section": "Explanations",
"slide": "Measured: what learning from propagation buys",
"keys": [
"ablation"
]
},
{
"term_html": "SMT",
"html": "Satisfiability modulo theories: SAT over atoms from a theory such as linear arithmetic or equality with functions.",
"section": "The same idea, elsewhere",
"slide": "SMT, DPLL(T), and logic-based Benders",
"keys": [
"smt"
]
},
{
"term_html": "DPLL(T)",
"html": "A CDCL solver over Boolean abstractions of theory atoms, with a theory solver that returns explanation clauses (Nieuwenhuis, Oliveras &amp; Tinelli 2006). LCG is DPLL(T) with CP propagators as the theory.",
"section": "The same idea, elsewhere",
"slide": "SMT, DPLL(T), and logic-based Benders",
"keys": [
"dpll(t)",
"dpll",
"t"
]
},
{
"term_html": "theory solver",
"html": "The component that checks theory atoms for consistency and explains conflicts and propagations.",
"section": "The same idea, elsewhere",
"slide": "SMT, DPLL(T), and logic-based Benders",
"keys": [
"theory solver"
]
},
{
"term_html": "logic-based Benders",
"html": "Benders with any subproblem solver, which returns an inference about the master's decision (Hooker &amp; Ottosson 2003).",
"section": "The same idea, elsewhere",
"slide": "SMT, DPLL(T), and logic-based Benders",
"keys": [
"logic-based benders"
]
},
{
"term_html": "decide, check, explain",
"html": "The common pattern: decide in one representation, check in a richer one, hand back a certificate of why in the first. Separation, pricing, Benders cuts and LCG all follow it.",
"section": "The same idea, elsewhere",
"slide": "SMT, DPLL(T), and logic-based Benders",
"keys": [
"decide, check, explain",
"decide",
"check",
"explain"
]
},
{
"term_html": "CP-SAT",
"html": "Google's solver: an LCG core, a linear relaxation with cuts, and a portfolio of search and LNS workers.",
"section": "CP-SAT",
"slide": "Reading CP-SAT's log",
"keys": [
"cp-sat"
]
},
{
"term_html": "subsolver (worker)",
"html": "One member of CP-SAT's portfolio, with its own heuristics, restart policy and LP level (<code>default_lp</code>, <code>no_lp</code>, <code>max_lp</code>, <code>quick_restart</code>).",
"section": "CP-SAT",
"slide": "Reading CP-SAT's log",
"keys": [
"subsolver (worker)",
"subsolver",
"worker"
]
},
{
"term_html": "LP worker",
"html": "A worker that maintains the linear relaxation and its cuts, for bounds and reduced-cost fixing.",
"section": "CP-SAT",
"slide": "Reading CP-SAT's log",
"keys": [
"lp worker"
]
},
{
"term_html": "shared incumbent",
"html": "The best solution found, visible to all workers.",
"section": "CP-SAT",
"slide": "Reading CP-SAT's log",
"keys": [
"shared incumbent"
]
},
{
"term_html": "solution hint",
"html": "A starting assignment given to the solver to guide early search.",
"section": "CP-SAT",
"slide": "Reading CP-SAT's log",
"keys": [
"solution hint"
]
},
{
"term_html": "VeriPB",
"html": "A proof format able to justify theory lemmas; needed because an explanation clause is not RUP from the CNF, so DRAT checkers reject LCG proofs.",
"section": "CP-SAT",
"slide": "Reading CP-SAT's log",
"keys": [
"veripb"
]
},
{
"term_html": "the three questions",
"html": "What does the LP relaxation see? What does propagation see? What can learning reuse?",
"section": "Choosing a solver",
"slide": "MIP, CP, SAT, or CP-SAT?",
"keys": [
"the three questions"
]
},
{
"term_html": "MINLP",
"html": "Mixed-integer nonlinear programming, solved by spatial branch and bound; outside this course's solvers.",
"section": "Choosing a solver",
"slide": "MIP, CP, SAT, or CP-SAT?",
"keys": [
"minlp"
]
},
{
"term_html": "nurse rostering",
"html": "Scheduling staff over shifts with coverage, rest and fairness rules. The worked example for choosing CP-SAT first.",
"section": "Choosing a solver",
"slide": "MIP, CP, SAT, or CP-SAT?",
"keys": [
"nurse rostering"
]
}
];
