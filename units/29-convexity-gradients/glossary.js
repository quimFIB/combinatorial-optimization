// Generated from GLOSSARY.org by `co glossary`; edit the Org file, not this one.
window.GLOSSARY = [
{
"term_html": "convex function",
"html": "\\(f(\\theta x + (1 - \\theta) y) \\le \\theta f(x) + (1 - \\theta) f(y)\\). For differentiable \\(f\\), \\(f(y) \\ge f(x) + \\nabla f(x)^\\top (y - x)\\): the tangent plane is a global under-estimator.",
"section": "Convexity",
"slide": "Convex, smooth, strongly convex",
"keys": [
"convex function"
]
},
{
"term_html": "global minimum from a zero gradient",
"html": "For convex \\(f\\), \\(\\nabla f(x) = 0\\) means \\(x\\) is a global minimum. Local optimality is global, unlike in combinatorial problems.",
"section": "Convexity",
"slide": "Convex, smooth, strongly convex",
"keys": [
"global minimum from a zero gradient"
]
},
{
"term_html": "subgradient",
"html": "Any \\(g\\) with \\(f(y) \\ge f(x) + g^\\top (y - x)\\) for all \\(y\\); the gradient's replacement where \\(f\\) has a kink (unit 11).",
"section": "Convexity",
"slide": "Convex, smooth, strongly convex",
"keys": [
"subgradient"
]
},
{
"term_html": "\\(L\\)-smooth",
"html": "\\(\\|\\nabla f(x) - \\nabla f(y)\\| \\le L \\|x - y\\|\\). Bounds how far a gradient step can go: step \\(1/L\\). For \\(\\frac12 x^\\top Q x\\), \\(L = \\lambda_{\\max}(Q)\\).",
"section": "Convexity",
"slide": "Convex, smooth, strongly convex",
"keys": [
"l-smooth"
]
},
{
"term_html": "\\(\\mu\\)-strongly convex",
"html": "\\(f(y) \\ge f(x) + \\nabla f(x)^\\top (y - x) + \\frac{\\mu}{2}\\|y - x\\|^2\\). Bounds how flat the bottom can be; \\(\\mu = \\lambda_{\\min}(Q)\\) for a quadratic.",
"section": "Convexity",
"slide": "Convex, smooth, strongly convex",
"keys": [
"\\mu-strongly convex"
]
},
{
"term_html": "condition number \\(\\kappa\\)",
"html": "\\(L / \\mu\\). Decides how many steps a first-order method needs.",
"section": "Convexity",
"slide": "Convex, smooth, strongly convex",
"keys": [
"condition number \\kappa"
]
},
{
"term_html": "central-difference gradient check",
"html": "Comparing a gradient with \\((f(x + h e_i) - f(x - h e_i)) / 2h\\), error \\(O(h^2)\\).",
"section": "Convexity",
"slide": "Convex, smooth, strongly convex",
"keys": [
"central-difference gradient check"
]
},
{
"term_html": "Rosenbrock function",
"html": "A standard non-convex test function with a curved narrow valley.",
"section": "Convexity",
"slide": "Convex, smooth, strongly convex",
"keys": [
"rosenbrock function"
]
},
{
"term_html": "first-order method",
"html": "An optimization method that uses only function values and gradients.",
"section": "First-order methods",
"slide": "Gradient descent, momentum, and the lower bound",
"keys": [
"first-order method"
]
},
{
"term_html": "gradient descent (GD)",
"html": "\\(x \\leftarrow x - \\frac1L \\nabla f(x)\\). Error \\(LR^2/2k\\) for smooth convex \\(f\\), \\((1 - 1/\\kappa)^k\\) when strongly convex, with \\(R = \\|x_0 - x^*\\|\\).",
"section": "First-order methods",
"slide": "Gradient descent, momentum, and the lower bound",
"keys": [
"gradient descent (gd)",
"gradient descent",
"gd"
]
},
{
"term_html": "momentum",
"html": "Adding a multiple of the previous step to the current one.",
"section": "First-order methods",
"slide": "Gradient descent, momentum, and the lower bound",
"keys": [
"momentum"
]
},
{
"term_html": "heavy ball",
"html": "GD plus \\(\\beta (x_k - x_{k-1})\\) (Polyak 1964). Rate \\((\\frac{\\sqrt\\kappa - 1}{\\sqrt\\kappa + 1})^k\\) on quadratics with tuned parameters; no general guarantee.",
"section": "First-order methods",
"slide": "Gradient descent, momentum, and the lower bound",
"keys": [
"heavy ball"
]
},
{
"term_html": "Nesterov's accelerated gradient",
"html": "Take the gradient at \\(x_k + \\frac{k-1}{k+2}(x_k - x_{k-1})\\). Error \\(2LR^2/(k+1)^2\\) for smooth convex \\(f\\) (1983).",
"section": "First-order methods",
"slide": "Gradient descent, momentum, and the lower bound",
"keys": [
"nesterov's accelerated gradient"
]
},
{
"term_html": "first-order lower bound",
"html": "Any method whose iterates lie in the span of past gradients has error \\(\\Omega(LR^2/k^2)\\) on some smooth convex function, so Nesterov's method is optimal up to constants.",
"section": "First-order methods",
"slide": "Gradient descent, momentum, and the lower bound",
"keys": [
"first-order lower bound"
]
},
{
"term_html": "linear convergence",
"html": "Error shrinking by a constant factor per iteration, like \\((1 - 1/\\kappa)^k\\).",
"section": "First-order methods",
"slide": "Gradient descent, momentum, and the lower bound",
"keys": [
"linear convergence"
]
},
{
"term_html": "stochastic gradient",
"html": "An unbiased estimate of \\(\\nabla f\\), such as from a mini-batch. Rate drops to \\(O(1/\\sqrt k)\\) for convex \\(f\\).",
"section": "First-order methods",
"slide": "Gradient descent, momentum, and the lower bound",
"keys": [
"stochastic gradient"
]
},
{
"term_html": "variance reduction",
"html": "SAG, SVRG: recovering linear rates for finite sums.",
"section": "First-order methods",
"slide": "Gradient descent, momentum, and the lower bound",
"keys": [
"variance reduction"
]
},
{
"term_html": "conjugate gradient (CG)",
"html": "A Krylov method optimal on quadratics, needing no parameters.",
"section": "First-order methods",
"slide": "Measured: iterations to 1e−8",
"keys": [
"conjugate gradient (cg)",
"conjugate gradient",
"cg"
]
},
{
"term_html": "L-BFGS",
"html": "A quasi-Newton method that builds curvature from recent gradients with limited memory. The default with unknown conditioning.",
"section": "First-order methods",
"slide": "Measured: iterations to 1e−8",
"keys": [
"l-bfgs"
]
},
{
"term_html": "projection \\(\\Pi_C\\)",
"html": "The closest point of \\(C\\) to a given point.",
"section": "Constraints",
"slide": "Projected gradient and Frank–Wolfe",
"keys": [
"projection \\pi_c"
]
},
{
"term_html": "projected gradient",
"html": "\\(x_{k+1} = \\Pi_C(x_k - \\frac1L \\nabla f(x_k))\\). Same rates as GD when projecting is cheap.",
"section": "Constraints",
"slide": "Projected gradient and Frank–Wolfe",
"keys": [
"projected gradient"
]
},
{
"term_html": "projection onto the simplex",
"html": "Sort, take prefix sums, find a threshold, clip. \\(O(n \\log n)\\). Lab step 3.",
"section": "Constraints",
"slide": "Projected gradient and Frank–Wolfe",
"keys": [
"projection onto the simplex"
]
},
{
"term_html": "probability simplex",
"html": "\\(\\{x \\ge 0 : \\sum_i x_i = 1\\}\\).",
"section": "Constraints",
"slide": "Projected gradient and Frank–Wolfe",
"keys": [
"probability simplex"
]
},
{
"term_html": "linear minimization oracle",
"html": "A routine returning \\(\\arg\\min_{s \\in C} g^\\top s\\): an LP over \\(C\\), or a combinatorial algorithm over a combinatorial polytope.",
"section": "Constraints",
"slide": "Projected gradient and Frank–Wolfe",
"keys": [
"linear minimization oracle"
]
},
{
"term_html": "Frank–Wolfe (conditional gradient)",
"html": "\\(s_k\\) from the linear oracle, then \\(x_{k+1} = x_k + \\frac{2}{k+2}(s_k - x_k)\\) (1956). No projection. Rate \\(O(LD^2/k)\\), with \\(D\\) the diameter of \\(C\\).",
"section": "Constraints",
"slide": "Projected gradient and Frank–Wolfe",
"keys": [
"frank–wolfe (conditional gradient)",
"frank–wolfe",
"conditional gradient"
]
},
{
"term_html": "Frank–Wolfe gap",
"html": "\\(g_k = \\nabla f(x_k)^\\top (x_k - s_k) \\ge f(x_k) - f^*\\): a free certificate of suboptimality.",
"section": "Constraints",
"slide": "Projected gradient and Frank–Wolfe",
"keys": [
"frank–wolfe gap"
]
},
{
"term_html": "KKT conditions",
"html": "For convex \\(\\min f(x)\\) with \\(g_i(x) \\le 0\\): stationarity \\(\\nabla f + \\sum_i \\lambda_i \\nabla g_i = 0\\), feasibility, \\(\\lambda \\ge 0\\), and complementarity \\(\\lambda_i g_i(x^*) = 0\\) (Karush 1939; Kuhn &amp; Tucker 1951).",
"section": "KKT",
"slide": "The KKT conditions, and the LP case",
"keys": [
"kkt conditions"
]
},
{
"term_html": "Lagrange multiplier \\(\\lambda_i\\)",
"html": "The price on constraint \\(i\\) in the KKT conditions.",
"section": "KKT",
"slide": "The KKT conditions, and the LP case",
"keys": [
"lagrange multiplier \\lambda_i"
]
},
{
"term_html": "stationarity",
"html": "The gradient of the Lagrangian vanishes.",
"section": "KKT",
"slide": "The KKT conditions, and the LP case",
"keys": [
"stationarity"
]
},
{
"term_html": "complementarity",
"html": "A constraint with slack has zero multiplier. For an LP this is exactly unit 03's complementary slackness.",
"section": "KKT",
"slide": "The KKT conditions, and the LP case",
"keys": [
"complementarity"
]
},
{
"term_html": "Slater's condition",
"html": "A strictly feasible point exists. Makes KKT necessary for convex problems; not needed with linear constraints.",
"section": "KKT",
"slide": "The KKT conditions, and the LP case",
"keys": [
"slater's condition"
]
},
{
"term_html": "KKT residuals",
"html": "How far a point and multipliers are from satisfying each condition. \"Optimal\" in floating point means residuals below a tolerance.",
"section": "KKT",
"slide": "The KKT conditions, and the LP case",
"keys": [
"kkt residuals"
]
},
{
"term_html": "QP",
"html": "A quadratic program: \\(\\min \\frac12 x^\\top Q x + q^\\top x\\) under linear constraints; stationarity reads \\(Qx + q + A^\\top \\lambda = 0\\).",
"section": "KKT",
"slide": "The KKT conditions, and the LP case",
"keys": [
"qp"
]
}
];
