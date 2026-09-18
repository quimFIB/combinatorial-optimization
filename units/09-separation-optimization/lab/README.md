# Lab 09 — Separation ⇔ optimization: subtour elimination

**Time:** about 2½ hours. **Before:** the slides (`uv run co slides 09`).
**You write:** 7 functions in `lab.py`, 80–120 lines in all.
**Needs:** units 04 (the ellipsoid idea) and 08 (separation). This is a branch
unit, but the one the curriculum would fight to keep.

The TSP's subtour elimination LP has 2ⁿ⁻¹ − 1 constraints: 8 × 10⁵⁹ of them at
n = 200. This lab solves it, and then the TSP itself, while writing down a few
dozen. A minimum cut finds the violated ones, and that is enough. It is the
engineering face of the most beautiful theorem in the course.

## Given, and what you write

| Given in `colib.tsp` / `colib.mip` | Yours in `lab.py` |
|---|---|
| `edges(n)`, `degree_milp(tsp, integer)` | A subtour constraint; components of the support graph |
| `tour_from_edges`, `tour_length` | Stoer–Wagner minimum cut |
| `lp_relaxation`, `highs_mip` | The separation oracle |
| networkx (tests only) | The subtour LP by lazy constraints |
| | An exact TSP by lazy cuts on the integer program |

## Running it

```fish
uv run co test 09
uv run co test 09 --solution functional
```

## Style

Components can be a BFS or a fixpoint of label propagation. Stoer–Wagner is a
loop of phases, each building a maximum-adjacency order and merging the last two
vertices. The functional reference writes the phase as a fold, and the phases as
an unfold over contracted weight dicts. The two lazy loops are the same unfold,
parameterized by "how to solve" and "how to separate".

---

## Step 1 — A subtour constraint and components  *(20 min)*

*Shape: a comprehension; a BFS.*

**Done when** `step 1 ✓`: the constraint for {0, 1} on 4 vertices crosses exactly the 4
right edges, and components match networkx on 20 random sparse supports.

## Step 2 — Minimum cut  *(45 min)*

*Shape: phases of maximum-adjacency orderings.* In each phase, grow an order by
repeatedly adding the vertex most strongly attached to those already added. The
last vertex's attachment is a "cut of the phase". Merge the last two vertices, and
repeat until one vertex is left. The smallest cut of any phase is a global minimum.

**Done when** `step 2 ✓`: the value matches `networkx.stoer_wagner` on 30 random
weighted graphs, and the set you return realizes that value.

## Step 3 — The separation oracle  *(15 min)*

*Shape: two cases.* A disconnected support gives zero-weight cuts for free. A
connected support needs the minimum cut.

**Done when** `step 3 ✓`: two triangles give both components, a thin bridge of 0.5
and a bridge of total 1.5 are both caught, and a tour gives nothing.

## Step 4 — The subtour LP  *(20 min)*

*Shape: an unfold.* Solve, separate, add, repeat.

**Done when** `step 4 ✓`. On 6 instances with 8 cities, your lazily generated bound
**equals** the LP with all 127 subtour constraints written out. You used fewer constraints, and
your final point satisfies all 254 cut constraints.

*Think about:* why is "no violated constraint found" a proof that the LP over *all*
subtour constraints is solved? (Because the oracle is exact: a minimum cut below 2 exists iff some
subtour constraint is violated.)

## Step 5 — The exact TSP  *(20 min)*

*Shape: the same unfold on the integer program.* Integer solutions are separated by
components alone, since a 0/1 degree-2 solution is a union of cycles.

**Done when** `step 5 ✓`: optimal tours on 6 instances with 9 cities, matching brute force.

---

## Then — a few dozen constraints out of 10⁵⁹  *(5 min, runs ~80 s)*

```fish
uv run co then 09
```

| n | constraints that exist | used by the LP | LP bound | optimum | MIP cuts | MIP s | gap |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 30 | 5.4 × 10⁸ | 6 | 480.5 | 482 | 5 | 0.06 | 0.31% |
| 80 | 6.0 × 10²³ | 16 | 725.0 | 726 | 24 | 1.7 | 0.14% |
| 120 | 6.7 × 10³⁵ | 39 | 813.0 | 819 | 52 | 17 | 0.73% |
| 200 | 8.0 × 10⁵⁹ | 56 | 1083.5 | 1091 | 70 | 46 | 0.69% |

On these instances the subtour LP bound is within 1% of the optimum. Concorde,
which uses this idea plus comb and other cut families inside branch-and-cut, has
solved instances with tens of thousands of cities to optimality. It isn't
installed here.

## Checkpoint

- [ ] `uv run co test 09` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** you can state the separation–optimization
      theorem precisely, and you have solved a TSP over an exponential constraint
      family while only ever writing down a few hundred of its constraints.
- [ ] You can explain why unit 06's odd-set inequalities for matching are
      separable by a (different) minimum cut computation, and what that implies.

In `NOTES.md`: your table, and the theorem in your own words.

## Reading

- Grötschel, Lovász & Schrijver, *Geometric Algorithms and Combinatorial
  Optimization*, ch. 6 (the equivalence), consulted.
- Schrijver, *Combinatorial Optimization*, vol. A, §5.10–5.11 and ch. 58.
- Applegate, Bixby, Chvátal & Cook, *The Traveling Salesman Problem: A
  Computational Study* (2006), ch. 5–6, for how Concorde separates subtours and combs.
- Stoer & Wagner, "A simple min-cut algorithm", *JACM* 44 (1997). Four pages.
