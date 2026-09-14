// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "polynomial (Karp) reduction \\(A \\le_p B\\)",
"html": "A polynomial map \\(f\\) with \\(x \\in A \\iff f(x) \\in B\\); for optimization, plus a map \\(g\\) taking solutions of \\(f(x)\\) back to solutions of \\(x\\).",
"section": "Reductions",
"slide": "Karp's chain",
"keys": [
"polynomial (karp) reduction a \\le_p b"
]
},
{
"term_html": "direction of a reduction",
"html": "To show a new problem \\(B\\) hard, reduce a known hard problem <em>to</em> \\(B\\). The reverse only shows \\(B\\) is no harder.",
"section": "Reductions",
"slide": "Karp's chain",
"keys": [
"direction of a reduction"
]
},
{
"term_html": "NP-complete",
"html": "In NP and NP-hard.",
"section": "Reductions",
"slide": "Karp's chain",
"keys": [
"np-complete"
]
},
{
"term_html": "NP-hard",
"html": "At least as hard as every problem in NP under polynomial reductions.",
"section": "Reductions",
"slide": "Karp's chain",
"keys": [
"np-hard"
]
},
{
"term_html": "Cook–Levin theorem",
"html": "SAT is NP-complete (1971, 1973).",
"section": "Reductions",
"slide": "Karp's chain",
"keys": [
"cook–levin theorem"
]
},
{
"term_html": "Karp's 21 problems",
"html": "The NP-complete problems Karp derived from SAT by reductions in 1972.",
"section": "Reductions",
"slide": "Karp's chain",
"keys": [
"karp's 21 problems"
]
},
{
"term_html": "gadget",
"html": "A small piece of the target instance that simulates one part of the source, such as a triangle per clause.",
"section": "Reductions",
"slide": "3-SAT → vertex cover, and back",
"keys": [
"gadget"
]
},
{
"term_html": "3-SAT to vertex cover",
"html": "An edge per variable (its two literals), a triangle per clause, links from each corner to its literal. Satisfiable iff a cover of size \\(k = n + 2m\\) exists.",
"section": "Reductions",
"slide": "3-SAT → vertex cover, and back",
"keys": [
"3-sat to vertex cover"
]
},
{
"term_html": "solution map",
"html": "The function taking a solution of the reduced instance back to one of the original.",
"section": "Reductions",
"slide": "3-SAT → vertex cover, and back",
"keys": [
"solution map"
]
},
{
"term_html": "clause splitting",
"html": "Turning any CNF into exactly-3-CNF with fresh variables, plus a map extending assignments. Lab step 2.",
"section": "Reductions",
"slide": "3-SAT → vertex cover, and back",
"keys": [
"clause splitting"
]
},
{
"term_html": "exponential time hypothesis (ETH)",
"html": "That 3-SAT needs \\(2^{\\Omega(n)}\\) time. Transferring it needs reductions of linear size.",
"section": "Reductions",
"slide": "3-SAT → vertex cover, and back",
"keys": [
"exponential time hypothesis (eth)",
"exponential time hypothesis",
"eth"
]
},
{
"term_html": "decision-preserving reduction",
"html": "Maps yes-instances to yes-instances. Enough for NP-hardness.",
"section": "Reductions",
"slide": "What a reduction preserves, and what it doesn't",
"keys": [
"decision-preserving reduction"
]
},
{
"term_html": "optimum-preserving reduction",
"html": "\\(\\mathrm{OPT}(f(x))\\) is determined by \\(\\mathrm{OPT}(x)\\), with solutions mapped back, like vertex cover to set cover.",
"section": "Reductions",
"slide": "What a reduction preserves, and what it doesn't",
"keys": [
"optimum-preserving reduction"
]
},
{
"term_html": "gap-preserving reduction",
"html": "Maps near-optimal solutions to near-optimal ones (L-reductions, AP-reductions). Needed to transfer hardness of approximation.",
"section": "Reductions",
"slide": "What a reduction preserves, and what it doesn't",
"keys": [
"gap-preserving reduction"
]
},
{
"term_html": "MaxSAT",
"html": "Maximize the number of satisfied clauses.",
"section": "Reductions",
"slide": "What a reduction preserves, and what it doesn't",
"keys": [
"maxsat"
]
},
{
"term_html": "pseudo-polynomial time",
"html": "Polynomial in the value of the numbers, exponential in their bit length.",
"section": "Numbers",
"slide": "Weak and strong NP-hardness",
"keys": [
"pseudo-polynomial time"
]
},
{
"term_html": "weakly NP-hard",
"html": "NP-hard, but solvable in time polynomial in \\(n\\) and the largest number: knapsack, subset sum, partition.",
"section": "Numbers",
"slide": "Weak and strong NP-hardness",
"keys": [
"weakly np-hard"
]
},
{
"term_html": "strongly NP-hard",
"html": "Still NP-hard when every number is polynomial in \\(n\\) (written in unary): bin packing, 3-partition, and problems with no numbers.",
"section": "Numbers",
"slide": "Weak and strong NP-hardness",
"keys": [
"strongly np-hard"
]
},
{
"term_html": "unary encoding",
"html": "Writing a number \\(N\\) with \\(N\\) symbols, so its size is its value.",
"section": "Numbers",
"slide": "Weak and strong NP-hardness",
"keys": [
"unary encoding"
]
},
{
"term_html": "partition",
"html": "Split numbers into two sets of equal sum. Weakly NP-hard; bin packing with two bins.",
"section": "Numbers",
"slide": "Weak and strong NP-hardness",
"keys": [
"partition"
]
},
{
"term_html": "3-partition",
"html": "Split \\(3m\\) numbers into \\(m\\) triples of equal sum. Strongly NP-hard.",
"section": "Numbers",
"slide": "Weak and strong NP-hardness",
"keys": [
"3-partition"
]
},
{
"term_html": "Garey–Johnson theorem (no FPTAS)",
"html": "A strongly NP-hard problem with integer objective bounded by a polynomial in \\(n\\) and the largest number has no FPTAS unless P = NP.",
"section": "Numbers",
"slide": "Weak and strong NP-hardness",
"keys": [
"garey–johnson theorem (no fptas)",
"garey–johnson theorem",
"no fptas"
]
},
{
"term_html": "FPTAS",
"html": "Fully polynomial-time approximation scheme: ratio \\(1 \\pm \\varepsilon\\) in time polynomial in \\(n\\) and \\(1/\\varepsilon\\).",
"section": "Numbers",
"slide": "The knapsack FPTAS (Ibarra & Kim 1975)",
"keys": [
"fptas"
]
},
{
"term_html": "knapsack FPTAS",
"html": "Drop items that do not fit alone, round values to multiples of \\(K = \\varepsilon v_{\\max} / n\\), solve exactly by value. \\(O(n^3 / \\varepsilon)\\), at least \\((1 - \\varepsilon)\\mathrm{OPT}\\).",
"section": "Numbers",
"slide": "The knapsack FPTAS (Ibarra & Kim 1975)",
"keys": [
"knapsack fptas"
]
},
{
"term_html": "approximation ratio",
"html": "The worst-case factor between an algorithm's value and the optimum.",
"section": "The hierarchy",
"slide": "FPTAS ⊂ PTAS ⊂ APX ⊂ log-APX ⊂ poly-APX",
"keys": [
"approximation ratio"
]
},
{
"term_html": "PTAS",
"html": "Ratio \\(1 \\pm \\varepsilon\\) in polynomial time for each fixed \\(\\varepsilon\\), possibly like \\(n^{1/\\varepsilon}\\).",
"section": "The hierarchy",
"slide": "FPTAS ⊂ PTAS ⊂ APX ⊂ log-APX ⊂ poly-APX",
"keys": [
"ptas"
]
},
{
"term_html": "APX",
"html": "Problems with some constant-ratio polynomial algorithm.",
"section": "The hierarchy",
"slide": "FPTAS ⊂ PTAS ⊂ APX ⊂ log-APX ⊂ poly-APX",
"keys": [
"apx"
]
},
{
"term_html": "log-APX",
"html": "Problems with an \\(O(\\log n)\\) ratio.",
"section": "The hierarchy",
"slide": "FPTAS ⊂ PTAS ⊂ APX ⊂ log-APX ⊂ poly-APX",
"keys": [
"log-apx"
]
},
{
"term_html": "poly-APX",
"html": "Problems with an \\(n^c\\) ratio.",
"section": "The hierarchy",
"slide": "FPTAS ⊂ PTAS ⊂ APX ⊂ log-APX ⊂ poly-APX",
"keys": [
"poly-apx"
]
},
{
"term_html": "gap technique",
"html": "If telling \\(\\mathrm{OPT} \\le a\\) from \\(\\mathrm{OPT} \\ge b\\) is NP-hard, no algorithm beats ratio \\(b/a\\) unless P = NP.",
"section": "The hierarchy",
"slide": "FPTAS ⊂ PTAS ⊂ APX ⊂ log-APX ⊂ poly-APX",
"keys": [
"gap technique"
]
},
{
"term_html": "absolute vs asymptotic ratio",
"html": "A guarantee for every instance, versus one that only holds as OPT grows. Bin packing's \\(3/2\\) is absolute; asymptotically it has a PTAS.",
"section": "The hierarchy",
"slide": "FPTAS ⊂ PTAS ⊂ APX ⊂ log-APX ⊂ poly-APX",
"keys": [
"absolute vs asymptotic ratio"
]
},
{
"term_html": "asymptotic PTAS",
"html": "A PTAS whose guarantee holds up to an additive term, for large OPT.",
"section": "The hierarchy",
"slide": "FPTAS ⊂ PTAS ⊂ APX ⊂ log-APX ⊂ poly-APX",
"keys": [
"asymptotic ptas"
]
},
{
"term_html": "PCP theorem",
"html": "\\(\\mathrm{NP} = \\mathrm{PCP}(O(\\log n), O(1))\\): every NP claim has a proof checkable by reading a constant number of randomly chosen bits. Equivalently, gap 3-SAT is NP-hard.",
"section": "The hierarchy",
"slide": "The PCP theorem: where approximation hardness comes from",
"keys": [
"pcp theorem"
]
},
{
"term_html": "probabilistically checkable proof",
"html": "A proof format a randomized verifier checks by sampling a few bits, accepting correct proofs and rejecting false claims with probability at least ½.",
"section": "The hierarchy",
"slide": "The PCP theorem: where approximation hardness comes from",
"keys": [
"probabilistically checkable proof"
]
},
{
"term_html": "gap amplification",
"html": "Dinur's combinatorial proof of the PCP theorem (2007).",
"section": "The hierarchy",
"slide": "The PCP theorem: where approximation hardness comes from",
"keys": [
"gap amplification"
]
},
{
"term_html": "Håstad's theorem",
"html": "Max-3SAT is NP-hard to approximate within \\(7/8 + \\varepsilon\\), which a random assignment achieves (2001).",
"section": "The hierarchy",
"slide": "The PCP theorem: where approximation hardness comes from",
"keys": [
"håstad's theorem"
]
},
{
"term_html": "Unique Games Conjecture (UGC)",
"html": "That distinguishing almost-satisfiable from almost-unsatisfiable label-permutation constraint systems is NP-hard (Khot 2002). Open. If true, 2 for vertex cover and \\(\\alpha_{GW}\\) for Max-Cut are optimal.",
"section": "The hierarchy",
"slide": "Three thresholds, and the Unique Games Conjecture",
"keys": [
"unique games conjecture (ugc)",
"unique games conjecture",
"ugc"
]
},
{
"term_html": "UGC-hard",
"html": "Hard assuming the Unique Games Conjecture.",
"section": "The hierarchy",
"slide": "Three thresholds, and the Unique Games Conjecture",
"keys": [
"ugc-hard"
]
},
{
"term_html": "\\(H_n\\)",
"html": "The harmonic number \\(1 + \\tfrac12 + \\dots + \\tfrac1n \\le \\ln n + 1\\): greedy set cover's ratio.",
"section": "The hierarchy",
"slide": "Three thresholds, and the Unique Games Conjecture",
"keys": [
"h_n"
]
},
{
"term_html": "2-to-2 Games theorem",
"html": "A proved weaker cousin of UGC giving \\(\\sqrt 2 - \\varepsilon\\) hardness for vertex cover (Khot, Minzer &amp; Safra 2018).",
"section": "The hierarchy",
"slide": "Three thresholds, and the Unique Games Conjecture",
"keys": [
"2-to-2 games theorem"
]
},
{
"term_html": "open gap",
"html": "The distance between the best known guarantee and the best known hardness for a problem.",
"section": "The hierarchy",
"slide": "Best ratio, best hardness, the gap",
"keys": [
"open gap"
]
},
{
"term_html": "FFD",
"html": "First-fit decreasing for bin packing: \\(\\tfrac{11}{9}\\mathrm{OPT} + \\tfrac69\\) bins.",
"section": "The hierarchy",
"slide": "Best ratio, best hardness, the gap",
"keys": [
"ffd"
]
}
];
