# Functional Python for the labs — a Haskell-to-Python sheet

For writing lab code in a functional style without searching for names. Every
row below was run and checked on this project's Python (3.12, toolz 1.1).

```python
from functools import reduce
from itertools import accumulate, takewhile, dropwhile, starmap, product, combinations
from operator import add, mul, itemgetter
import toolz as tz
from toolz.curried import map as cmap, filter as cfilter   # curried, for pipe
```

`toolz` is a dependency of the project; the rest is standard library. Plain
`map`, `filter` and `zip` are lazy iterators, like Haskell lists. Wrap them in
`list(...)` when you need to use a result twice.

## Folds and scans

| Haskell | Python | Note |
|---|---|---|
| `foldl f z xs` | `reduce(f, xs, z)` | `f(acc, x)`, same order as Haskell |
| `foldl1 f xs` | `reduce(f, xs)` | |
| `foldr f z xs` | `reduce(lambda acc, x: f(x, acc), reversed(list(xs)), z)` | no built-in; not lazy |
| `scanl f z xs` | `accumulate(xs, f, initial=z)` | lazy |
| `scanl1 f xs` | `accumulate(xs, f)` | |
| `and`, `or` | `all(...)`, `any(...)` | these short-circuit; `reduce` never stops early |
| `sum`, `product` | `sum(xs)`, `math.prod(xs)` | |
| `maximumBy (comparing f)` | `max(xs, key=f)` | first maximum wins on ties |

## Lists and iterators

| Haskell | Python |
|---|---|
| `map f xs`, `filter p xs` | `map(f, xs)`, `filter(p, xs)`, or a comprehension `[f(x) for x in xs if p(x)]` |
| `zipWith f xs ys` | `map(f, xs, ys)` |
| `uncurry f <$> pairs` | `starmap(f, pairs)` |
| `concat`, `concatMap f` | `tz.concat(xss)`, `tz.mapcat(f, xs)` |
| `iterate f x`, `take n` | `tz.iterate(f, x)`, `tz.take(n, it)` |
| `takeWhile`, `dropWhile` | `takewhile(p, xs)`, `dropwhile(p, xs)` |
| `head`, `last`, `xs !! n` | `tz.first(xs)`, `tz.last(xs)`, `tz.nth(n, xs)` |
| `find p xs` (→ `Maybe`) | `next((x for x in xs if p(x)), None)` |
| `partition p xs` | `(list(filter(p, xs)), list(tz.remove(p, xs)))` |
| `nub` | `tz.unique(xs)`, which keeps the order |
| `sequence` for lists (cartesian product) | `itertools.product(*xss)` |
| sliding pairs, `zip xs (tail xs)` | `tz.sliding_window(2, xs)` |

## Grouping and counting

| Haskell (Data.Map idioms) | Python |
|---|---|
| `fromListWith (++)` by key | `tz.groupby(key, xs)` → `{k: [x, …]}` |
| `fromListWith f` by key | `tz.reduceby(key, f, xs, init)` → `{k: folded}` |
| count occurrences | `tz.frequencies(xs)` → `{x: count}` |

## Functions

| Haskell | Python |
|---|---|
| `f . g` | `tz.compose(f, g)` (right to left), `tz.compose_left(g, f)` |
| `x & f & g` | `tz.pipe(x, f, g)` |
| partial application | `tz.curry(f)(a)(b)`, or `functools.partial(f, a)` |
| `flip f` | `tz.flip(f, a, b)` calls `f(b, a)` |
| operator sections `(+)`, `(!! 0)` | `operator.add`, `operator.itemgetter(0)` |

A pipeline in the style the labs use:

```python
tz.pipe(rows,
        cmap(normalize),
        cfilter(says_something),
        tz.unique,
        list)
```

## Where Python differs, and it matters here

- **No tail calls.** Recursion depth is capped around 1000. That is fine for
  recursing over *n* ≤ 20 items. It is not fine for recursing once per candidate
  in a 2ⁿ space, which is what `reduce` is for.
- **Immutable records.** colib's instances and `Result` are frozen dataclasses:
  `dataclasses.replace(r, field=new)` is record update syntax.
- **Tuples and frozensets** are the immutable, hashable containers. Lists, dicts
  and sets are mutable; building new ones in a comprehension is fine.
- **Speed.** A `reduce` that builds a new accumulator per element is measurably
  slower than a loop: lab 00's `then` shows the oracle's reach dropping from
  n = 26 to n = 24. For the course's small instances it never matters.
