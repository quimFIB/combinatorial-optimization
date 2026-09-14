// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "Birkhoff polytope \\(\\mathcal{B}\\)",
"html": "The doubly stochastic matrices, whose vertices are the permutation matrices (unit 15).",
"section": "Relax the decision",
"slide": "Sinkhorn: the Hungarian algorithm, softened",
"keys": [
"birkhoff polytope \\mathcal{b}"
]
},
{
"term_html": "entropic regularization",
"html": "Adding \\(\\varepsilon \\sum_{ij} P_{ij}(\\log P_{ij} - 1)\\) to \\(\\langle C, P \\rangle\\), making the minimizer unique, interior and smooth in \\(C\\).",
"section": "Relax the decision",
"slide": "Sinkhorn: the Hungarian algorithm, softened",
"keys": [
"entropic regularization"
]
},
{
"term_html": "entropy \\(H(P)\\)",
"html": "\\(-\\sum_{ij} P_{ij}(\\log P_{ij} - 1)\\) in this unit's convention.",
"section": "Relax the decision",
"slide": "Sinkhorn: the Hungarian algorithm, softened",
"keys": [
"entropy h(p)"
]
},
{
"term_html": "transport plan",
"html": "The soft assignment \\(P\\), with \\(P_{ij} = \\exp((f_i + g_j - C_{ij})/\\varepsilon)\\).",
"section": "Relax the decision",
"slide": "Sinkhorn: the Hungarian algorithm, softened",
"keys": [
"transport plan"
]
},
{
"term_html": "Sinkhorn iterations",
"html": "Alternately rescale rows and columns to sum to 1: choose \\(f\\) for the rows, then \\(g\\) for the columns.",
"section": "Relax the decision",
"slide": "Sinkhorn: the Hungarian algorithm, softened",
"keys": [
"sinkhorn iterations"
]
},
{
"term_html": "log domain",
"html": "Carrying out Sinkhorn with logsumexp on \\(f\\) and \\(g\\) instead of multiplying kernels, which underflow as \\(\\varepsilon\\) shrinks.",
"section": "Relax the decision",
"slide": "Sinkhorn: the Hungarian algorithm, softened",
"keys": [
"log domain"
]
},
{
"term_html": "logsumexp",
"html": "\\(\\log \\sum_i e^{a_i}\\), computed stably.",
"section": "Relax the decision",
"slide": "Sinkhorn: the Hungarian algorithm, softened",
"keys": [
"logsumexp"
]
},
{
"term_html": "temperature \\(\\varepsilon\\)",
"html": "The regularization weight. As \\(\\varepsilon \\to 0\\) the plan concentrates on an optimal permutation, and iterations grow like \\(1/\\varepsilon\\).",
"section": "Relax the decision",
"slide": "Sinkhorn: the Hungarian algorithm, softened",
"keys": [
"temperature \\varepsilon"
]
},
{
"term_html": "envelope theorem",
"html": "The gradient of an optimal value with respect to a parameter is the partial derivative at the optimum: here \\(\\nabla_C = P^*_\\varepsilon\\).",
"section": "Relax the decision",
"slide": "Sinkhorn: the Hungarian algorithm, softened",
"keys": [
"envelope theorem"
]
},
{
"term_html": "greedy rounding",
"html": "Turning a soft plan into a permutation by repeatedly taking its largest remaining entry.",
"section": "Relax the decision",
"slide": "Sinkhorn: the Hungarian algorithm, softened",
"keys": [
"greedy rounding"
]
},
{
"term_html": "optimal transport",
"html": "Moving one distribution onto another at least cost; assignment is the case with uniform marginals.",
"section": "Relax the decision",
"slide": "Sinkhorn: the Hungarian algorithm, softened",
"keys": [
"optimal transport"
]
},
{
"term_html": "Gumbel-Sinkhorn",
"html": "Noise plus Sinkhorn, for learning latent permutations.",
"section": "Relax the decision",
"slide": "Sinkhorn: the Hungarian algorithm, softened",
"keys": [
"gumbel-sinkhorn"
]
},
{
"term_html": "differentiable sorting",
"html": "Soft sorts and ranks via optimal transport or projections onto the permutahedron.",
"section": "Relax the decision",
"slide": "Sinkhorn: the Hungarian algorithm, softened",
"keys": [
"differentiable sorting"
]
},
{
"term_html": "Gumbel noise",
"html": "Samples \\(G = -\\log(-\\log U)\\) with \\(U\\) uniform.",
"section": "Sample the decision",
"slide": "Gumbel, straight-through, REINFORCE",
"keys": [
"gumbel noise"
]
},
{
"term_html": "Gumbel-max trick",
"html": "\\(\\arg\\max_i (\\ell_i + G_i)\\) samples exactly from \\(\\mathrm{softmax}(\\ell)\\).",
"section": "Sample the decision",
"slide": "Gumbel, straight-through, REINFORCE",
"keys": [
"gumbel-max trick"
]
},
{
"term_html": "softmax",
"html": "\\(p_i = e^{\\ell_i} / \\sum_j e^{\\ell_j}\\).",
"section": "Sample the decision",
"slide": "Gumbel, straight-through, REINFORCE",
"keys": [
"softmax"
]
},
{
"term_html": "logits \\(\\ell\\)",
"html": "The unnormalized scores a softmax turns into probabilities.",
"section": "Sample the decision",
"slide": "Gumbel, straight-through, REINFORCE",
"keys": [
"logits \\ell"
]
},
{
"term_html": "Gumbel-softmax",
"html": "\\(\\mathrm{softmax}((\\ell + G)/\\tau)\\): a differentiable relaxed sample, sharper as \\(\\tau\\) falls.",
"section": "Sample the decision",
"slide": "Gumbel, straight-through, REINFORCE",
"keys": [
"gumbel-softmax"
]
},
{
"term_html": "straight-through estimator",
"html": "Forward the hard one-hot, backward the soft sample's gradient: <code>hard + soft - stop_gradient(soft)</code>. Biased.",
"section": "Sample the decision",
"slide": "Gumbel, straight-through, REINFORCE",
"keys": [
"straight-through estimator"
]
},
{
"term_html": "<code>stop_gradient</code>",
"html": "An operation that passes values through unchanged but blocks gradients.",
"section": "Sample the decision",
"slide": "Gumbel, straight-through, REINFORCE",
"keys": [
"~stop_gradient~"
]
},
{
"term_html": "REINFORCE (score-function estimator)",
"html": "\\(\\nabla_\\ell \\mathbb{E}[f(k)] = \\mathbb{E}[f(k)(e_k - p)]\\). Unbiased, needs no derivative of \\(f\\), high variance.",
"section": "Sample the decision",
"slide": "Gumbel, straight-through, REINFORCE",
"keys": [
"reinforce (score-function estimator)",
"reinforce",
"score-function estimator"
]
},
{
"term_html": "baseline (REINFORCE)",
"html": "A running mean subtracted from \\(f\\) to cut variance without adding bias.",
"section": "Sample the decision",
"slide": "Gumbel, straight-through, REINFORCE",
"keys": [
"baseline (reinforce)",
"baseline",
"reinforce"
]
},
{
"term_html": "bias–variance trade-off",
"html": "Lower-variance estimators like straight-through at high \\(\\tau\\) pay with bias; unbiased REINFORCE pays with variance.",
"section": "Sample the decision",
"slide": "Gumbel, straight-through, REINFORCE",
"keys": [
"bias–variance trade-off"
]
},
{
"term_html": "argmin layer",
"html": "A model component whose output is the solution of an optimization problem, with gradients flowing through it.",
"section": "Differentiate the optimum",
"slide": "The implicit function theorem on KKT",
"keys": [
"argmin layer"
]
},
{
"term_html": "implicit function theorem",
"html": "If equations \\(F(x, q) = 0\\) define \\(x\\) as a function of \\(q\\), its derivative comes from one linear solve with \\(\\partial F / \\partial x\\).",
"section": "Differentiate the optimum",
"slide": "The implicit function theorem on KKT",
"keys": [
"implicit function theorem"
]
},
{
"term_html": "active set \\(S\\)",
"html": "The constraints holding with equality at the optimum.",
"section": "Differentiate the optimum",
"slide": "The implicit function theorem on KKT",
"keys": [
"active set s"
]
},
{
"term_html": "strict complementarity",
"html": "Every active constraint has a positive multiplier. Needed for the active set to stay fixed under small changes.",
"section": "Differentiate the optimum",
"slide": "The implicit function theorem on KKT",
"keys": [
"strict complementarity"
]
},
{
"term_html": "argmin Jacobian",
"html": "\\(\\partial x^* / \\partial q\\), from differentiating the KKT system with the active set fixed.",
"section": "Differentiate the optimum",
"slide": "The implicit function theorem on KKT",
"keys": [
"argmin jacobian"
]
},
{
"term_html": "OptNet",
"html": "Differentiable QP layers (Amos &amp; Kolter 2017).",
"section": "Differentiate the optimum",
"slide": "The implicit function theorem on KKT",
"keys": [
"optnet"
]
},
{
"term_html": "cvxpylayers",
"html": "Differentiable layers for disciplined parametrized convex programs (Agrawal et al. 2019).",
"section": "Differentiate the optimum",
"slide": "The implicit function theorem on KKT",
"keys": [
"cvxpylayers"
]
},
{
"term_html": "unrolling",
"html": "Differentiating through a solver's iterations instead of its optimality conditions. Gives the truncated algorithm's gradient.",
"section": "Differentiate the optimum",
"slide": "The implicit function theorem on KKT",
"keys": [
"unrolling"
]
},
{
"term_html": "degenerate point",
"html": "A constraint active with zero multiplier, where the active set can change and \\(x^*(q)\\) is not differentiable.",
"section": "Differentiate the optimum",
"slide": "The implicit function theorem on KKT",
"keys": [
"degenerate point"
]
},
{
"term_html": "perturbed optimizers",
"html": "Averaging an argmax over random cost perturbations to get a smooth surrogate (Berthet et al. 2020).",
"section": "Differentiate the optimum",
"slide": "The implicit function theorem on KKT",
"keys": [
"perturbed optimizers"
]
},
{
"term_html": "learning to branch",
"html": "Training a cheap model to imitate strong branching's choices inside branch and bound.",
"section": "Learn to optimize",
"slide": "Learned branching, cuts, and neural combinatorial optimisation",
"keys": [
"learning to branch"
]
},
{
"term_html": "imitation learning",
"html": "Training a policy to reproduce an expert's decisions, here strong branching.",
"section": "Learn to optimize",
"slide": "Learned branching, cuts, and neural combinatorial optimisation",
"keys": [
"imitation learning"
]
},
{
"term_html": "ranker",
"html": "A model scoring candidates so the highest-scored one is chosen; the lab's is linear over five features.",
"section": "Learn to optimize",
"slide": "Learned branching, cuts, and neural combinatorial optimisation",
"keys": [
"ranker"
]
},
{
"term_html": "branching features",
"html": "Cheap per-variable descriptors such as fractionality. Strong branching's signal lives in child LP bounds, which the lab's features lack.",
"section": "Learn to optimize",
"slide": "Learned branching, cuts, and neural combinatorial optimisation",
"keys": [
"branching features"
]
},
{
"term_html": "graph neural network (GNN)",
"html": "A network over the variable–constraint bipartite graph; used for learned branching (Gasse et al. 2019).",
"section": "Learn to optimize",
"slide": "Learned branching, cuts, and neural combinatorial optimisation",
"keys": [
"graph neural network (gnn)",
"graph neural network",
"gnn"
]
},
{
"term_html": "neural combinatorial optimization",
"html": "Networks that construct solutions directly: pointer networks, attention models trained with REINFORCE, POMO.",
"section": "Learn to optimize",
"slide": "Learned branching, cuts, and neural combinatorial optimisation",
"keys": [
"neural combinatorial optimization"
]
},
{
"term_html": "pointer network",
"html": "A sequence model whose output attends to input positions, used to emit tours (Vinyals et al. 2015).",
"section": "Learn to optimize",
"slide": "Learned branching, cuts, and neural combinatorial optimisation",
"keys": [
"pointer network"
]
},
{
"term_html": "held-out instances",
"html": "Test instances not used in training, often larger or from a different distribution to test generalization.",
"section": "Learn to optimize",
"slide": "Learned branching, cuts, and neural combinatorial optimisation",
"keys": [
"held-out instances"
]
},
{
"term_html": "imitation accuracy",
"html": "How often the learned rule agrees with the expert. Compared with a trivial rule's agreement, it shows whether the features carry the signal.",
"section": "Learn to optimize",
"slide": "Measured: the lab's learned rule, judged by unit 28's method",
"keys": [
"imitation accuracy"
]
},
{
"term_html": "generalization",
"html": "Performing well on instances unlike the training set; the recurring weakness of learned solvers.",
"section": "Learn to optimize",
"slide": "Measured: the lab's learned rule, judged by unit 28's method",
"keys": [
"generalization"
]
}
];
