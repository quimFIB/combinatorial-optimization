// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "local search",
"html": "Repeatedly apply an improving move from a neighbourhood until none exists.",
"section": "Local search, engineered",
"slide": "",
"keys": [
"local search"
]
},
{
"term_html": "2-opt",
"html": "Remove edges \\(ab\\) and \\(cd\\), add \\(ac\\) and \\(bd\\), reversing the stretch between (Croes 1958).",
"section": "Local search, engineered",
"slide": "2-opt, neighbour lists, don't-look bits",
"keys": [
"2-opt"
]
},
{
"term_html": "neighbour list",
"html": "Each city's \\(k\\) nearest cities, sorted by distance. An improving 2-opt move is visible from one endpoint's list, and the scan can stop at the first neighbour farther than the tour edge.",
"section": "Local search, engineered",
"slide": "2-opt, neighbour lists, don't-look bits",
"keys": [
"neighbour list"
]
},
{
"term_html": "don't-look bits",
"html": "Skip a city whose surroundings have not changed since it last failed to improve; re-queue the four endpoints of every applied move (Bentley 1992).",
"section": "Local search, engineered",
"slide": "2-opt, neighbour lists, don't-look bits",
"keys": [
"don't-look bits"
]
},
{
"term_html": "sweep",
"html": "Scanning every city for an improving move in turn, without don't-look bits.",
"section": "Local search, engineered",
"slide": "2-opt, neighbour lists, don't-look bits",
"keys": [
"sweep"
]
},
{
"term_html": "nearest neighbour tour",
"html": "Start anywhere and always go to the closest unvisited city. A common starting tour.",
"section": "Local search, engineered",
"slide": "2-opt, neighbour lists, don't-look bits",
"keys": [
"nearest neighbour tour"
]
},
{
"term_html": "Or-opt",
"html": "Move a segment of 1–3 cities elsewhere, possibly reversed (Or 1976).",
"section": "Local search, engineered",
"slide": "From 2-opt to Lin–Kernighan and LKH",
"keys": [
"or-opt"
]
},
{
"term_html": "3-opt",
"html": "Remove three edges and reconnect.",
"section": "Local search, engineered",
"slide": "From 2-opt to Lin–Kernighan and LKH",
"keys": [
"3-opt"
]
},
{
"term_html": "Lin–Kernighan (LK)",
"html": "A variable-depth sequence of exchanges, extended while the cumulative gain stays positive (1973).",
"section": "Local search, engineered",
"slide": "From 2-opt to Lin–Kernighan and LKH",
"keys": [
"lin–kernighan (lk)",
"lin–kernighan",
"lk"
]
},
{
"term_html": "LKH",
"html": "Helsgaun's LK implementation with 5-opt moves and α-nearness candidates. The reference TSP heuristic.",
"section": "Local search, engineered",
"slide": "From 2-opt to Lin–Kernighan and LKH",
"keys": [
"lkh"
]
},
{
"term_html": "α-nearness",
"html": "How much the minimum 1-tree grows if an edge is forced in (unit 11). Picks candidate edges better than distance.",
"section": "Local search, engineered",
"slide": "From 2-opt to Lin–Kernighan and LKH",
"keys": [
"α-nearness"
]
},
{
"term_html": "Concorde",
"html": "The exact TSP solver (unit 09), the other half of \"state of the art\" for TSP.",
"section": "Local search, engineered",
"slide": "From 2-opt to Lin–Kernighan and LKH",
"keys": [
"concorde"
]
},
{
"term_html": "metaheuristic",
"html": "A general strategy for escaping local optima, wrapped around a local search. Promises nothing; only measurement supports one.",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"metaheuristic"
]
},
{
"term_html": "simulated annealing",
"html": "Accept a worsening move \\(\\Delta\\) with probability \\(e^{-\\Delta/T}\\), lowering \\(T\\) over time.",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"simulated annealing"
]
},
{
"term_html": "Metropolis acceptance",
"html": "That acceptance rule: always take improvements, take worsening moves with probability \\(e^{-\\Delta/T}\\).",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"metropolis acceptance"
]
},
{
"term_html": "temperature \\(T\\)",
"html": "The parameter controlling how often worsening moves are accepted. Tune it in units of a typical \\(\\Delta\\).",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"temperature t"
]
},
{
"term_html": "cooling schedule",
"html": "How \\(T\\) falls. <em>Geometric</em> cooling multiplies it by a constant each step. Hajek's \\(T_k \\ge c / \\log k\\) guarantees convergence and is too slow to use.",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"cooling schedule"
]
},
{
"term_html": "tabu search",
"html": "Take the best non-tabu move even if it worsens; recent moves are forbidden for a <em>tenure</em>, unless an <em>aspiration criterion</em> overrides (Glover 1986).",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"tabu search"
]
},
{
"term_html": "GRASP",
"html": "Greedy randomized adaptive search: restart from randomized greedy constructions, each followed by local search (Feo &amp; Resende 1995).",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"grasp"
]
},
{
"term_html": "restricted candidate list",
"html": "The near-best choices a GRASP construction picks from at random; its greediness \\(\\alpha\\) sets how near.",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"restricted candidate list"
]
},
{
"term_html": "iterated local search (ILS)",
"html": "Kick the local optimum and descend again, keeping the result by an acceptance rule.",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"iterated local search (ils)",
"iterated local search",
"ils"
]
},
{
"term_html": "kick (perturbation)",
"html": "The move that leaves a local optimum in ILS.",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"kick (perturbation)",
"kick",
"perturbation"
]
},
{
"term_html": "double bridge",
"html": "A 4-opt kick \\(A\\,B\\,C\\,D \\to A\\,C\\,B\\,D\\) that 2-opt and 3-opt cannot undo in one step.",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"double bridge"
]
},
{
"term_html": "multi-start",
"html": "Independent local searches from fresh starting points.",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"multi-start"
]
},
{
"term_html": "ALNS",
"html": "Adaptive large neighbourhood search: destroy and repair, choosing operators by adaptive weights (unit 19).",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"alns"
]
},
{
"term_html": "adaptive weights",
"html": "Scores per operator, updated from how well each has done, that set the probability of choosing it.",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"adaptive weights"
]
},
{
"term_html": "random removal, worst removal",
"html": "Destroy operators that remove random customers, or the customers costing most in their current position.",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"random removal, worst removal",
"random removal",
"worst removal"
]
},
{
"term_html": "greedy insertion",
"html": "Repair by inserting each removed customer where it adds least cost.",
"section": "Metaheuristics",
"slide": "Annealing, tabu, GRASP, ILS, ALNS",
"keys": [
"greedy insertion"
]
},
{
"term_html": "genetic algorithm",
"html": "A population recombined by crossover and mutated. Usually a poor fit for structured problems.",
"section": "Metaheuristics",
"slide": "Genetic algorithms: usually the wrong answer, with one notable exception",
"keys": [
"genetic algorithm"
]
},
{
"term_html": "crossover",
"html": "Combining two parent solutions into a child.",
"section": "Metaheuristics",
"slide": "Genetic algorithms: usually the wrong answer, with one notable exception",
"keys": [
"crossover"
]
},
{
"term_html": "memetic algorithm",
"html": "A genetic algorithm whose children are improved by local search.",
"section": "Metaheuristics",
"slide": "Genetic algorithms: usually the wrong answer, with one notable exception",
"keys": [
"memetic algorithm"
]
},
{
"term_html": "hybrid genetic search (HGS)",
"html": "The memetic algorithm for vehicle routing (Vidal et al.), among the best CVRP heuristics: strong local search, route-preserving crossover, diversity management.",
"section": "Metaheuristics",
"slide": "Genetic algorithms: usually the wrong answer, with one notable exception",
"keys": [
"hybrid genetic search (hgs)",
"hybrid genetic search",
"hgs"
]
},
{
"term_html": "giant tour",
"html": "A CVRP solution written as one sequence of customers, split into routes afterwards; what HGS's crossover operates on.",
"section": "Metaheuristics",
"slide": "Genetic algorithms: usually the wrong answer, with one notable exception",
"keys": [
"giant tour"
]
},
{
"term_html": "equal budget",
"html": "The same wall-clock time on the same machine, or the same number of evaluations, for every method compared.",
"section": "Honest comparison",
"slide": "How \"our metaheuristic beat theirs\" goes wrong",
"keys": [
"equal budget"
]
},
{
"term_html": "training set",
"html": "Instances used for tuning, kept separate from the test instances.",
"section": "Honest comparison",
"slide": "How \"our metaheuristic beat theirs\" goes wrong",
"keys": [
"training set"
]
},
{
"term_html": "state-of-the-art baseline",
"html": "The best known method, engineered equally; without it a comparison has not been made.",
"section": "Honest comparison",
"slide": "How \"our metaheuristic beat theirs\" goes wrong",
"keys": [
"state-of-the-art baseline"
]
},
{
"term_html": "time-to-target (TTT) plot",
"html": "The empirical CDF of the time each seed takes to reach a fixed target value, with failures kept in the denominator (Aiex, Resende &amp; Ribeiro 2007).",
"section": "Honest comparison",
"slide": "How \"our metaheuristic beat theirs\" goes wrong",
"keys": [
"time-to-target (ttt) plot"
]
},
{
"term_html": "empirical CDF",
"html": "The fraction of runs finished by each time.",
"section": "Honest comparison",
"slide": "How \"our metaheuristic beat theirs\" goes wrong",
"keys": [
"empirical cdf"
]
},
{
"term_html": "Mann–Whitney U test",
"html": "A rank-based test of whether one algorithm's times tend to be smaller. No normality assumption; capped runs count as the cap.",
"section": "Honest comparison",
"slide": "How \"our metaheuristic beat theirs\" goes wrong",
"keys": [
"mann–whitney u test"
]
},
{
"term_html": "not rejecting ≠ equal",
"html": "A non-significant test means the data cannot tell, not that the methods are the same.",
"section": "Honest comparison",
"slide": "How \"our metaheuristic beat theirs\" goes wrong",
"keys": [
"not rejecting ≠ equal"
]
},
{
"term_html": "multiple comparisons",
"html": "Running many tests raises the chance of a false positive: six at \\(\\alpha = 0.05\\) give about 26% (unit 28).",
"section": "Honest comparison",
"slide": "How \"our metaheuristic beat theirs\" goes wrong",
"keys": [
"multiple comparisons"
]
},
{
"term_html": "guided local search (GLS)",
"html": "OR-Tools routing's metaheuristic: penalizes features of local optima to escape them.",
"section": "Honest comparison",
"slide": "Equal budgets: TSP and CVRP",
"keys": [
"guided local search (gls)",
"guided local search",
"gls"
]
},
{
"term_html": "best found",
"html": "The best solution any method reached, used as the reference when no optimum or bound is known.",
"section": "Honest comparison",
"slide": "Equal budgets: TSP and CVRP",
"keys": [
"best found"
]
}
];
