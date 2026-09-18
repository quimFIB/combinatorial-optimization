# Lab 14 — Network flows

**Time:** about 3 hours. **Before:** the slides (`uv run co slides 14`).
**You write:** 6 functions in `lab.py`, 150–200 lines in all.
**Needs:** unit 13 for the augmenting-path idea. Unit 06 explains why the flows
come out integral.

Three maximum-flow algorithms, and the reasons each exists. Then the min-cut
certificate, min-cost flow with potentials, and a reduction that turns a
selection problem into a cut. The real skill of this unit is spotting flows in
disguise. Edmonds–Karp is the version you'd write in an interview; the reduction
is the part you'll use.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| networkx, OR-Tools (tests and `then`) | Edmonds–Karp, and the min cut from the final residual graph |
| | Dinic: level graphs and blocking flows |
| | FIFO push–relabel |
| | Min-cost flow by successive shortest paths with potentials |
| | Project selection as a minimum cut |

## Running it

```fish
uv run co test 14
uv run co test 14 --solution functional
```

## Style

Flow algorithms are naturally stateful. The functional reference keeps residual
capacities in an immutable tuple, rebuilt on every push, and writes each
algorithm as an unfold. It is much slower but clear, and fine at test sizes. If you
write the imperative version, keep the mutation inside a small residual-graph
class, as `solution/lab.py` does.

---

## Step 1 — Edmonds–Karp, and the cut  *(40 min)*

*Shape: BFS for a path, find the bottleneck, push, repeat.* Build the residual
graph once, with edge `e`'s reverse at `e ^ 1`.

**Done when** `step 1 ✓`: the textbook network gives 5, 30 random networks match
networkx, every flow is valid, and **your min cut's capacity equals your flow
value**. That equality is the optimality certificate.

## Step 2 — Dinic  *(35 min)*

*Shape: phases, each a BFS for levels, then repeated DFS along level-increasing arcs.*
The "current edge" pointer per node is what makes a phase linear.

**Done when** `step 2 ✓` on 30 random networks.

## Step 3 — Push–relabel  *(40 min)*

*Shape: a queue of active nodes and local operations.* There are no paths at all:
excess moves downhill one arc at a time.

**Done when** `step 3 ✓` on 30 random networks, and every run finishes within the time
limit.

*Think about:* why does the final preflow have no excess anywhere except *s* and
*t*? Why is it then a maximum flow? (Heights certify that *t* is unreachable from
*s* in the residual graph.)

## Step 4 — Min-cost flow  *(40 min)*

*Shape: Bellman–Ford once, then Dijkstra on reduced costs, repeatedly.* Potentials
make every residual arc's reduced cost nonnegative, including the negative-cost
reverse arcs that flow creates.

**Done when** `step 4 ✓`: it matches networkx's network simplex on 30 random
networks and on one with negative-cost arcs, returns None when the demand exceeds
the max flow, and your reported cost equals the cost of your flow.

## Step 5 — Project selection  *(20 min)*

*Shape: a reduction.*

**Done when** `step 5 ✓`: optimal on 40 random instances (checked by brute force),
and your chosen set is closed under the prerequisites.

---

## Then — against OR-Tools and networkx  *(5 min, runs ~7 s)*

```fish
uv run co then 14
```

Seconds; all algorithms agree on every value.

| family | arcs | EK | Dinic | push–relabel | OR-Tools | networkx |
|---|---:|---:|---:|---:|---:|---:|
| layered 40×40 | 4 760 | 0.241 | **0.057** | 3.706 | 0.0029 | 0.131 |
| random n = 1500 | 9 284 | 0.808 | 0.036 | **0.027** | 0.0039 | 0.080 |
| bipartite 300×300 | 3 323 | 0.046 | 0.006 | 0.007 | 0.0013 | 0.056 |

Push–relabel beats Dinic on the random sparse family and loses badly on deep layered
networks. Without the gap and global-relabelling heuristics that production codes
add, it wastes relabels climbing heights one layer at a time. OR-Tools is 5–20×
faster than your best on every family. Min-cost flow agrees with OR-Tools'
`SimpleMinCostFlow` on all three sizes.

## Checkpoint

- [ ] `uv run co test 14` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** handed a problem you have not seen, you can
      decide whether it is a flow in disguise and write the reduction, including
      the capacities that encode the objective. Try baseball elimination (is team
      *x* mathematically eliminated?) before reading the slide "More flows in
      disguise", which gives the reduction.
- [ ] You can explain why integer capacities give an integer maximum flow in two
      ways: augmenting paths, and total unimodularity (unit 06).

## Reading

- Korte & Vygen, ch. 8 (max flow) and ch. 9 (min-cost flow).
- Kleinberg & Tardos, *Algorithm Design*, ch. 7. The best collection of flow
  reductions: baseball elimination, project selection, image segmentation.
- Optional: Goldberg & Tarjan, "A new approach to the maximum-flow problem",
  *JACM* 35 (1988), the push–relabel paper.
