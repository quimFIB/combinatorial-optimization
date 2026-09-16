# Lab 19 — Search, restarts, and large neighbourhood search

**Time:** about 2½ hours. **Before:** the slides (`uv run co slides 19`).
**You write:** 10 functions and a heuristic class in `lab.py`, 140–200 lines in all.
**Needs:** unit 17 (the engine's `choose` and `on_failure` hooks) and unit 18 (the job-shop model).

Propagation decides what search has left to do; the search strategy decides how long that
takes. This lab builds the strategies CP solvers ship: randomised first-fail, dom/wdeg
(learn which constraints fail and branch there), Luby restarts, and large neighbourhood
search. The centrepiece is a measurement. Run 100 seeds on one instance, look at the
distribution of search effort, and see its **heavy tail**: most runs are quick, and a few
take 100× longer. That tail, not any single run, is the actual justification for restarts.
The lab also finds an instance **without** a tail, where restarts only cost.

## Given, and what you write

| Given | Yours in `lab.py` |
|---|---|
| `colib.csp.quasigroup_completion`; unit 17's engine as `cp`; unit 18 as `gc` | The Luby sequence, randomised first-fail, the QCP model |
| `colib.problems.JobShop`, `schedule_makespan` | dom/wdeg |
| OR-Tools CP-SAT and routing (in `then`) | Restarts with a Luby schedule and a node budget |
| | Runtime distributions and their summary statistics |
| | A greedy schedule, and LNS for job-shop |

## Running it

```fish
uv run co test 19
uv run co test 19 --solution functional
```

## Style

The engine's hooks are callbacks, so they have side effects by nature. The functional reference
keeps dom/wdeg's weights in a persistent map that it rebinds on each failure. Everything else is
an unfold: restarts over (index, accumulated stats), and LNS over (incumbent, trace).

---

## Step 1 — Building blocks  *(20 min)*

*Shape: a recursion, a closure, a model builder.*

**Done when** `step 1 ✓`: Luby matches the recursive definition for i < 300. Random first-fail
picks every tied variable and nothing else, and is reproducible from its seed. The QCP model's
solutions are Latin squares that respect the givens.

## Step 2 — dom/wdeg  *(30 min)*

*Shape: a weight per propagator, a score per variable.*

**Done when** `step 2 ✓`: weights and scores are exact in a worked example (including a
propagator excluded because its other variable is fixed), and infinite-score ties are random.
The unit's first surprise: on a 14-variable easy chain plus a hidden 5-into-4 pigeonhole,
**first-fail runs out of 20 000 nodes, and dom/wdeg proves infeasibility in under 500**.

## Step 3 — Restarts  *(20 min)*

*Shape: a loop over Luby-scaled node limits.*

**Done when** `step 3 ✓`: the node limits your searches receive are exactly
3·luby(1), 3·luby(2), …. A complete search proves infeasibility without restarting, the budget
is respected, and dom/wdeg with restarts solves QCP.

## Step 4 — Runtime distributions  *(20 min)*

*Shape: map over seeds, then order statistics.*

**Done when** `step 4 ✓`: the summary statistics match hand-computed ones. On the heavy
instance, plain search has p90/median > 4, and restarts **halve the mean and cut the maximum**.
On the light instance, restarts **raise** the mean.

## Step 5 — LNS for job-shop  *(40 min)*

*Shape: destroy (free some jobs), repair (search with the rest's machine order fixed).*

**Done when** `step 5 ✓`: the greedy schedule is feasible. LNS schedules are feasible, strictly
improving, and better than greedy. Over three instances, LNS beats branch-and-bound given the
same total nodes.

---

## Then — distributions, neighbourhoods, and the tools  *(10 min, runs ~3 minutes)*

```fish
uv run co then 19
```

**Runtime distributions** (100 seeds, cap 3 000 nodes):

| instance | strategy | solved | mean | median | p90 | max |
|---|---|---:|---:|---:|---:|---:|
| QCP(12, 55%) heavy | random first-fail | 97% | 153.6 | 31 | 174 | 3 000 (cap) |
| | + Luby restarts | 100% | **52.1** | 49.5 | 89 | **202** |
| | dom/wdeg + restarts | 100% | 85.2 | 60 | 177 | 412 |
| QCP(12, 58%) light | random first-fail | 100% | **48.7** | 35 | 46 | 668 |
| | + Luby restarts | 100% | 92.3 | 93 | 119 | 217 |
| | dom/wdeg + restarts | 100% | 110.8 | 99 | 180 | 287 |

On the heavy instance, half the runs finish in under 32 nodes, and 3 runs never finish. Restarts
make the **mean 3× better** and the maximum 15× better: a run stuck in a bad subtree gets abandoned.

*Corrected after unit 28's audit.* An earlier version of this sheet also said restarts make the median
worse (31 → 49.5). That doesn't survive: the 95% bootstrap intervals, [28.5, 35] and [28.5, 53.5],
overlap, and on eight more instances of the family restarts raised the median on only 3 (Wilcoxon
p = 0.79). The mean of 153.6 is also an artefact of the 3 000-node cap, since the 3 capped runs
contribute 90 of it. What does hold across the family is the tail: restarts lowered the mean on 7 of 8
instances (p = 0.03).
On the light instance there is no tail to cut, and restarts double the mean. dom/wdeg doesn't help
QCP, whose constraints are all alike.

**LNS vs branch-and-bound** (22 500 nodes each): 8×4: **49** vs 57; 10×5: **66** vs 77;
12×6: **78** vs 84 (greedy 117). LNS spends its nodes near a good schedule, while
branch-and-bound spends them at the bottom of one subtree.

**CP-SAT, 30×15 job-shop, 10 s:** 8 workers reach 1837–1851 with LNS and 1852 without, within
run-to-run noise. 1 worker reaches 2047–2049, and the bound is 1828 in all runs. On this
instance the parallel portfolio matters far more than the LNS switch.

**OR-Tools routing** (guided local search, 5 s) on unit 10's CVRPs: 442 / 483 / 680 against LP
bounds of 422 / 478.2 / 662: gaps of 4.5% / 1.0% / 2.6% of the routing cost. That certifies the
heuristic's quality without knowing the optimum.

## Checkpoint

- [ ] `uv run co test 19` shows all five steps ✓.
- [ ] **The curriculum's checkpoint:** you can show the heavy-tailed runtime histogram from your own
      solver (`then` prints it) and demonstrate that restarts move its mean, with the
      distributions, not with one lucky run.
- [ ] You can explain why restarts cut the tail (and so the capped mean) without a reliable effect on the
      median, and why they hurt on the light instance.

## Reading

- Gomes, Selman, Crato & Kautz, "Heavy-tailed phenomena in satisfiability and constraint
  satisfaction problems", *J. Automated Reasoning* 24 (2000).
- Luby, Sinclair & Zuckerman, "Optimal speedup of Las Vegas algorithms", *IPL* 47 (1993).
- Boussemart, Hemery, Lecoutre & Sais, "Boosting systematic search by weighting constraints",
  *ECAI* 2004.
- Shaw, "Using constraint programming and local search methods to solve vehicle routing problems",
  *CP* 1998: the LNS paper.
