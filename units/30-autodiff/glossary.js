// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "symbolic differentiation",
"html": "Rewriting the formula by the rules of calculus. Suffers expression swell and cannot handle loops or branches.",
"section": "Three kinds of derivative",
"slide": "Symbolic, numerical, automatic",
"keys": [
"symbolic differentiation"
]
},
{
"term_html": "expression swell",
"html": "The blow-up of symbolic derivatives: a product of \\(n\\) factors has \\(n\\) terms of \\(n - 1\\) factors.",
"section": "Three kinds of derivative",
"slide": "Symbolic, numerical, automatic",
"keys": [
"expression swell"
]
},
{
"term_html": "numerical differentiation",
"html": "Finite differences such as \\((f(x + h) - f(x - h)) / 2h\\). Truncation error \\(O(h^2)\\) against rounding error \\(O(\\epsilon / h)\\); one evaluation pair per input. Used as the test oracle.",
"section": "Three kinds of derivative",
"slide": "Symbolic, numerical, automatic",
"keys": [
"numerical differentiation"
]
},
{
"term_html": "automatic differentiation (autodiff)",
"html": "Applying the chain rule to the operations a program actually executed. Exact up to floating point, at a small constant times the program's cost.",
"section": "Three kinds of derivative",
"slide": "Symbolic, numerical, automatic",
"keys": [
"automatic differentiation (autodiff)",
"automatic differentiation",
"autodiff"
]
},
{
"term_html": "dual number",
"html": "\\(a + b\\varepsilon\\) with \\(\\varepsilon^2 = 0\\). Arithmetic on dual numbers carries derivatives: \\(g(a + b\\varepsilon) = g(a) + g'(a)\\, b\\, \\varepsilon\\).",
"section": "Three kinds of derivative",
"slide": "Symbolic, numerical, automatic",
"keys": [
"dual number"
]
},
{
"term_html": "forward mode",
"html": "Seed an input with \\(\\varepsilon\\) part 1, run the program, read the derivative off the \\(\\varepsilon\\) part. One pass per input direction, so \\(n\\) passes for a gradient.",
"section": "Three kinds of derivative",
"slide": "Symbolic, numerical, automatic",
"keys": [
"forward mode"
]
},
{
"term_html": "seed",
"html": "The \\(\\varepsilon\\) part given to the inputs, choosing which derivative forward mode computes.",
"section": "Three kinds of derivative",
"slide": "Symbolic, numerical, automatic",
"keys": [
"seed"
]
},
{
"term_html": "Wengert tape",
"html": "A record of every operation with its inputs and local derivatives, made during the forward pass.",
"section": "Reverse mode",
"slide": "The Wengert tape",
"keys": [
"wengert tape"
]
},
{
"term_html": "adjoint \\(\\bar v\\)",
"html": "\\(\\partial f / \\partial v\\) for an intermediate \\(v\\), accumulated backwards by \\(\\bar u \\mathrel{+}= \\bar v \\cdot \\partial v / \\partial u\\).",
"section": "Reverse mode",
"slide": "The Wengert tape",
"keys": [
"adjoint \\bar v"
]
},
{
"term_html": "reverse mode",
"html": "Record a tape, then sweep backwards in reverse topological order propagating adjoints. One sweep gives the full gradient.",
"section": "Reverse mode",
"slide": "The Wengert tape",
"keys": [
"reverse mode"
]
},
{
"term_html": "backward pass (sweep)",
"html": "The reverse traversal of the tape.",
"section": "Reverse mode",
"slide": "The Wengert tape",
"keys": [
"backward pass (sweep)",
"backward pass",
"sweep"
]
},
{
"term_html": "cheap gradient principle",
"html": "A full gradient costs a small constant multiple (about 4–5) of one function evaluation, whatever the number of inputs (Griewank).",
"section": "Reverse mode",
"slide": "The Wengert tape",
"keys": [
"cheap gradient principle"
]
},
{
"term_html": "backpropagation",
"html": "Reverse mode applied to a neural network (Rumelhart, Hinton &amp; Williams 1986).",
"section": "Reverse mode",
"slide": "The Wengert tape",
"keys": [
"backpropagation"
]
},
{
"term_html": "each node once",
"html": "The sweep must visit each node a single time in topological order, not follow paths, or a graph with exponentially many paths explodes.",
"section": "Reverse mode",
"slide": "The Wengert tape",
"keys": [
"each node once"
]
},
{
"term_html": "tape memory",
"html": "The intermediates reverse mode must keep until the backward sweep reaches them. Grows with batch × width × depth.",
"section": "Memory and higher order",
"slide": "What the tape holds, and checkpointing",
"keys": [
"tape memory"
]
},
{
"term_html": "activation",
"html": "An intermediate output of a network layer, such as a tanh output, saved for the backward pass.",
"section": "Memory and higher order",
"slide": "What the tape holds, and checkpointing",
"keys": [
"activation"
]
},
{
"term_html": "checkpointing (rematerialization)",
"html": "Keeping only some intermediates and recomputing the rest during the backward sweep. Every \\(\\sqrt L\\)-th layer gives \\(O(\\sqrt L)\\) memory for about one extra forward pass.",
"section": "Memory and higher order",
"slide": "What the tape holds, and checkpointing",
"keys": [
"checkpointing (rematerialization)",
"checkpointing",
"rematerialization"
]
},
{
"term_html": "revolve",
"html": "Griewank's optimal checkpointing schedule for chains: \\(O(\\log L)\\) memory for \\(O(\\log L)\\) times the compute.",
"section": "Memory and higher order",
"slide": "What the tape holds, and checkpointing",
"keys": [
"revolve"
]
},
{
"term_html": "in-place mutation",
"html": "Overwriting an array that the tape saved, so the backward pass silently uses wrong values.",
"section": "Memory and higher order",
"slide": "What the tape holds, and checkpointing",
"keys": [
"in-place mutation"
]
},
{
"term_html": "Jacobian",
"html": "The matrix of partial derivatives of a vector function.",
"section": "Memory and higher order",
"slide": "What the tape holds, and checkpointing",
"keys": [
"jacobian"
]
},
{
"term_html": "JVP (Jacobian-vector product)",
"html": "\\(Jv\\), one directional derivative. What forward mode computes per pass.",
"section": "Memory and higher order",
"slide": "JVPs, VJPs, and Hessian-vector products",
"keys": [
"jvp (jacobian-vector product)",
"jvp",
"jacobian-vector product"
]
},
{
"term_html": "VJP (vector-Jacobian product)",
"html": "\\(u^\\top J\\), one weighted row combination. What reverse mode computes per pass; every op in an array tape defines one.",
"section": "Memory and higher order",
"slide": "JVPs, VJPs, and Hessian-vector products",
"keys": [
"vjp (vector-jacobian product)",
"vjp",
"vector-jacobian product"
]
},
{
"term_html": "Hessian-vector product (HVP)",
"html": "\\(Hv = \\frac{d}{d\\varepsilon} \\nabla f(x + \\varepsilon v)\\), computed without forming \\(H\\).",
"section": "Memory and higher order",
"slide": "JVPs, VJPs, and Hessian-vector products",
"keys": [
"hessian-vector product (hvp)",
"hessian-vector product",
"hvp"
]
},
{
"term_html": "forward over reverse",
"html": "Running a reverse-mode tape on dual numbers to get HVPs in one forward and one backward pass.",
"section": "Memory and higher order",
"slide": "JVPs, VJPs, and Hessian-vector products",
"keys": [
"forward over reverse"
]
},
{
"term_html": "hyper-dual numbers",
"html": "Nested dual numbers, giving higher derivatives.",
"section": "Memory and higher order",
"slide": "JVPs, VJPs, and Hessian-vector products",
"keys": [
"hyper-dual numbers"
]
},
{
"term_html": "MLP",
"html": "A multilayer perceptron: alternating matrix multiplications, bias additions and nonlinearities.",
"section": "Real data, and lies",
"slide": "An MLP on terrain elevations",
"keys": [
"mlp"
]
},
{
"term_html": "tanh",
"html": "The hyperbolic tangent, the lab MLP's nonlinearity.",
"section": "Real data, and lies",
"slide": "An MLP on terrain elevations",
"keys": [
"tanh"
]
},
{
"term_html": "SGD",
"html": "Stochastic gradient descent on mini-batches.",
"section": "Real data, and lies",
"slide": "An MLP on terrain elevations",
"keys": [
"sgd"
]
},
{
"term_html": "epoch",
"html": "One pass over the training data.",
"section": "Real data, and lies",
"slide": "An MLP on terrain elevations",
"keys": [
"epoch"
]
},
{
"term_html": "RMSE",
"html": "Root mean squared error.",
"section": "Real data, and lies",
"slide": "An MLP on terrain elevations",
"keys": [
"rmse"
]
},
{
"term_html": "train vs test error",
"html": "Error on the data used for fitting, versus on held-out data. The honest measure is the second.",
"section": "Real data, and lies",
"slide": "An MLP on terrain elevations",
"keys": [
"train vs test error"
]
},
{
"term_html": "baseline",
"html": "A simple model (predict the mean, a plane) that a learned model must beat for the claim to mean anything.",
"section": "Real data, and lies",
"slide": "An MLP on terrain elevations",
"keys": [
"baseline"
]
},
{
"term_html": "autodiff lies",
"html": "Where the result is a convention, not a derivative: kinks such as ReLU or \\(|x|\\) at 0, branches on a value, \\(\\sqrt{x^2}\\) at 0 giving nan, and argmax, sorting and rounding, whose derivatives are zero almost everywhere.",
"section": "Real data, and lies",
"slide": "Where autodiff quietly lies",
"keys": [
"autodiff lies"
]
},
{
"term_html": "differentiate the program, not the function",
"html": "Autodiff sees only the branch that ran; two programs computing the same function can give different gradients.",
"section": "Real data, and lies",
"slide": "Where autodiff quietly lies",
"keys": [
"differentiate the program, not the function",
"differentiate the program",
"not the function"
]
},
{
"term_html": "almost everywhere (a.e.)",
"html": "Everywhere except a set of measure zero, such as the switching points of an argmax.",
"section": "Real data, and lies",
"slide": "Where autodiff quietly lies",
"keys": [
"almost everywhere (a.e.)",
"almost everywhere",
"a.e."
]
}
];
