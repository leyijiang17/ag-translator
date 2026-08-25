# OSCAR (Julia) ↔ Macaulay2 concept glossary — toric geometry

Scope: everything used in Simon Telen's "Introduction to Toric Geometry" notebooks (lectures 3, 7, 11), plus the ring/ideal basics that sit underneath any of it. Grounded in the current OSCAR.jl docs (docs.oscar-system.org, stable) and the current Macaulay2 `Polyhedra`, `NormalToricVarieties`, `Quasidegrees`, and `FourTiTwo` package docs.

**Confidence key** — every row is tagged:
- `MATCH` — direct correspondence, high confidence from docs.
- `IDIOM` — no 1:1 function; translating this means generating a short pattern, not a rename.
- `GAP` — one side has no equivalent notion; needs a workaround or is definitionally true/false on the other side.
- `VERIFY` — plausible from docs but not confirmed by execution; the pipeline's live-introspection step (see below) should double check before trusting it.

Because this glossary was built from documentation, not execution (this environment can't run Julia/OSCAR or Macaulay2 — see project notes), **every translation should still be confirmed live** the first time it's used: in Julia, `?functionname` or `methods(functionname)`; in Macaulay2, `apropos "name"` or `? functionName`. Treat this file as a fast first guess the agent looks up before generating code, not ground truth to skip verification.

**Update (2026-08-19, Lucy, verified against a real install — OSCAR v1.5.0 and current Macaulay2):** the first end-to-end run on real installs caught several bugs that pure-documentation research missed. Rows below tagged `CONFIRMED` were checked against actual output, not just docs. This is the expected pattern going forward — every real run is a chance to upgrade a `VERIFY`/`IDIOM` row to `CONFIRMED` or catch a wrong one, so keep this file updated as more of it gets exercised for real rather than treating it as finished.

**Update (2026-08-25, Lucy, first full-notebook run — Telen's `Notebook_lecture3.ipynb`):** translating the complete notebook (not just the hand-picked excerpt used in the first update) surfaced one more real bug and one misleading note, both fixed below (`toric_ideal`'s "variety route" and the `is_affine` note). It also confirmed two rows that had been sitting at `VERIFY` since the docs-only pass (`positive_hull`/`coneFromVData` orientation, and `polarize`/`dualCone`) — both upgraded to `CONFIRMED`. One genuinely new case came up that the earlier two example files never touched: `visualize(...)`, which has no Macaulay2 equivalent at all — see the new "Interactive/visualization-only functions" section. Note that fixing dated syntax in the *source* notebook itself (e.g. `issmooth` → `is_smooth`, `NormalToricVariety(σ)` → `normal_toric_variety(σ)`, raw `Polymake.*` calls → their current OSCAR wrappers) is a separate concern from this glossary — that's "does the OSCAR/Julia source run at all on a current install," not "how does OSCAR map to Macaulay2" — and belongs in comments on the translated source file, not here.

## Cones

| OSCAR (Julia) | Macaulay2 | Notes |
|---|---|---|
| `positive_hull(M)` | `coneFromVData M` | `MATCH`, `CONFIRMED`. Watch orientation: OSCAR's example code passes rays as **rows** of `M`; M2's `Polyhedra` package convention is rays as **columns**. Transpose when translating literal matrices — confirmed correct (matching ray sets on both sides) across multiple independent translations now, not just a first guess. |
| `rays(C)` | `rays C` | `MATCH`. Return shapes differ (OSCAR: iterator of row vectors; M2: matrix with rays as columns) — comparison in the verifier needs to normalize both to a set of vectors before comparing. |
| `facets(C)` | `facets C` | `MATCH`. |
| `polarize(C)` / dual cone | `dualCone C` | `MATCH` in concept, `CONFIRMED`. OSCAR's dual/polar operation name has shifted historically (`Polymake.polytope.polarize(C.pm_cone)` in Telen's original notebook → `polarize(C)` directly in current OSCAR, confirmed live via `methods(polarize)` and by running it). If you see the raw `Polymake.polytope.polarize(...).pm_cone` form in source being translated, that's dated syntax to modernize on the OSCAR side first, not something to translate literally. |
| `intersect(C0, C1)` | `intersect(C0, C1)` | `MATCH` — same name in both. |
| `dim(C)` | `dim C` | `MATCH`. |
| `hilbert_basis(C)` | `hilbertBasis C` | `MATCH`. |

## Polytopes

| OSCAR (Julia) | Macaulay2 | Notes |
|---|---|---|
| `convex_hull(pts)` | `convexHull pts` | `MATCH` in concept. Same row-vs-column orientation caveat as cones. |
| `vertices(P)` | `vertices P` | `MATCH`. |
| `facets(P)` | `facets P` | `MATCH`. |
| `lattice_points(P)` | `latticePoints P` | `MATCH`. |
| `normal_fan(P)` | `normalFan P` | `MATCH`. |
| `ehrhart_polynomial(P)` (current name; old notebook used the raw polymake property `P.pm_polytope.EHRHART_POLYNOMIAL`) | `ehrhart P` | `MATCH` in concept, `VERIFY` exact current OSCAR name. |
| `is_simple(P)` | *no direct predicate* | `GAP`. M2's `Polyhedra` package has `isSimplicial` (dual notion, for cones/fans) and `isFullDimensional`, `isLatticePolytope`, but no `isSimple` for polytopes. Simple = every vertex meets exactly `dim P` facets; translate as an idiom checking facet-vertex incidence counts, or note it's unverified and flag for manual check. |
| `is_normal(P)` | *no direct predicate* | `GAP` — see toric variety normality note below; same underlying issue. |

## Fans and normal toric varieties

| OSCAR (Julia) | Macaulay2 | Notes |
|---|---|---|
| `PolyhedralFan(rays_matrix, IncidenceMatrix([[1,2],[2,3]]))` | `fan {C1, C2, ...}` where each `Ci = coneFromVData ...` | `IDIOM`. M2's `fan` builds a `Fan` from a list of `Cone` objects, not from a (rays, incidence) pair directly. Translating this construction means: build each maximal cone from its ray subset first, then call `fan` on the list — a multi-line expansion, not a renamed call. |
| `maximal_cones(Σ)` on a raw `Fan` Σ | `maxCones Σ` | `MATCH`, but only when the M2 object is a bare `Fan`. |
| `max(X)` where `X` is a `NormalToricVariety` (OSCAR doesn't distinguish this the same way; the M2 side does) | `max X` | `MATCH` — M2 exposes `max` directly on `NormalToricVariety`, separate from `maxCones` on `Fan`. Pick the right one depending on which type is in hand. |
| `normal_toric_variety(C::Cone)` (affine case) | *no `normalToricVariety(Cone)` constructor* | `IDIOM`. M2 has `normalToricVariety(List,List)`, `(Matrix)`, `(Polyhedron)`, `(Fan)`, `(Ring)` — no direct cone-argument form. Idiom: `normalToricVariety(entries transpose rays C, {toList(0 ..< numColumns rays C)})` (single maximal cone spanning all rays). Needs a concrete worked template in the skill, not just a name swap. |
| `normal_toric_variety(P::Polyhedron)` | `normalToricVariety P` | `MATCH`. |
| `normal_toric_variety(PF::PolyhedralFan)` | `normalToricVariety Σ` | `MATCH`. |
| `projective_space(NormalToricVariety, d)` | `toricProjectiveSpace d` | `MATCH`, `CONFIRMED`. Older OSCAR (and Telen's original notebook) used `toric_projective_space(d)` — that name is gone in current OSCAR (v1.5.0 confirmed); it's now the typed-constructor form `projective_space(NormalToricVariety, d)`, matching the same pattern as `affine_space(NormalToricVariety, d)`, `weighted_projective_space(NormalToricVariety, w)`, etc. If you see the bare `toric_projective_space` name in source code being translated, treat it as dated syntax to modernize, not a typo. |
| `is_smooth(X)` | `isSmooth X` | `MATCH`. |
| `is_simplicial(X)` | `isSimplicial X` | `MATCH`. |
| `is_complete(X)` | `isComplete X` | `MATCH`. |
| `is_projective(X)` | `isProjective X` | `MATCH`. |
| `is_fano(X)` | `isFano X` | `MATCH`. |
| `is_affine(X)` | `#maxCones fan X == 1` | `IDIOM`, `CONFIRMED`. **Correction (2026-08-25): OSCAR *does* have a real, public `is_affine` predicate** (`methods(is_affine)` shows one method, on `Union{AffineNormalToricVariety, CyclicQuotientSingularity, NormalToricVariety}`) — the previous wording here ("no named `isAffine` predicate exists on either side") was misleading and wrong about the OSCAR side; it's only Macaulay2 that lacks a named predicate. On the M2 side, "affine" is exactly "the fan has exactly one maximal cone," so it's computable, not just a plausible-looking guess. **Prefer this computed check over hardcoding a literal `true`/`false`, even in a block where you already know the answer** — a hardcoded literal is only correct for the specific object in that block; if the file is later edited (e.g. incremental re-translation adds a new fan/variety reusing the same pattern), a hardcoded answer would silently be wrong while a computed check stays correct. Reserve the hardcode-and-comment pattern for cases with no computable equivalent at all, like `is_normal` below — not for cases where a computed equivalent just takes a little more digging to find. |
| `is_normal(X)` | *no `isNormal` in M2* | `GAP` — genuinely important one. M2's `NormalToricVariety` type is *only ever constructed as normal* — normality isn't checked, it's assumed by construction. Translating `is_normal(X)` where `X` came from a fan/polytope should become `true` by definition in M2, not a function call. This is exactly the kind of semantic mismatch flagged in the investigation report; document it plainly in the output rather than silently inventing a call. |
| `affine_open_covering(X)` | *no direct equivalent found* | `IDIOM`. Build per-maximal-cone affine pieces manually: iterate `max X` (or `maxCones fan X`), construct the corresponding affine `normalToricVariety` per cone using the single-cone idiom above. |
| `star_subdivision(Σ, i)` / `blowup_on_ith_minimal_torus_orbit(X, i)` | `toricBlowup(indices, X, weights)` | `MATCH` in concept — both perform the same geometric operation (star subdivision / toric blowup at a torus orbit), signatures differ enough that this needs careful argument-order translation, not a blind rename. `VERIFY` argument conventions against a small example. |
| `toric_ideal(affine_normal_toric_variety(σ))` (current name; Telen's original notebook used the capitalized `AffineNormalToricVariety(σ)`, which no longer exists — `methods(AffineNormalToricVariety)` only accepts a raw `Polymake.LibPolymake.BigObject`, not a `Cone`) or `toric_ideal(A::Matrix)` | `toricIdeal(A, R)` from the **`Quasidegrees`** package (matrix route — `A` is the embedding's exponent vectors as columns, `R` a ring with one variable per column) | `IDIOM`, `CONFIRMED` (matrix route only). **Correction (2026-08-25): the "variety route" previously listed here — `ideal normalToricVariety σ` — is not just a different shape, it is a different mathematical object, confirmed wrong by live testing.** `ideal` on a `NormalToricVariety` computes the Cox-construction *irrelevant ideal* (M2's own docs literally say so: `? (ideal, NormalToricVariety)` → "make the irrelevant ideal"), not the toric/implicitization ideal of relations among a monomial embedding — a real conceptual gap between "an ideal attached to this variety" (ambiguous — there are several) and "the toric ideal" (one specific one) that a name-level glossary lookup can't distinguish by itself. Worse, it fails *silently*: for a cone built from `positive_hull([-2 5; 1 0])` it returned `ideal 1` (the unit ideal) instead of erroring, which looks like a valid-but-wrong answer rather than an obvious bug. Always use the matrix route instead: build `A` from `hilbertBasis` of the dual cone (`transpose matrix apply(hilbertBasis sigmaV, v -> flatten entries v)`) and call `toricIdeal(A, R)` — confirmed to reproduce OSCAR's ideal exactly (same generators up to the expected Hilbert-basis reordering between systems). If a `NormalToricVariety` object (rather than a bare `Cone`) is what's in scope in the source, first pull its defining cone/rays back out and go through the matrix route the same way — don't reach for `ideal X`. |
| `binomial_exponents_to_ideal(E)` | *no direct function* | `IDIOM`. Nearest building block is `FourTiTwo`'s `toBinomial`, which converts one exponent vector to one binomial. Translating this call means mapping `toBinomial` over the rows of `E` and collecting into an `ideal(...)`. |

## Divisors and groups

| OSCAR (Julia) | Macaulay2 | Notes |
|---|---|---|
| `toric_divisor(X, coeffs::Vector)` | `toricDivisor(coeffs, X)` | `MATCH`, `CONFIRMED` — note argument order is flipped (M2: list first, then variety). The capitalized `ToricDivisor(...)` form from Telen's original notebook is no longer public in current OSCAR (v1.5.0 confirmed); the constructor is lowercase `toric_divisor` now, following the general OSCAR shift away from capitalized function names. |
| `torusinvariant_prime_divisors(X)` (no underscore between "torus" and "invariant" — easy to mistype as `torus_invariant_prime_divisors`, which does not exist) | `apply(#rays X, i -> (toricDivisor X)_i)` — or equivalently indexing the prime divisors of `X` by ray | `IDIOM`, `CONFIRMED` working. Prime divisors correspond 1:1 with rays; there's no single bulk M2 call, but indexing per ray is confirmed correct in practice. |
| `is_cartier(D)` | `isCartier D` | `MATCH`. |
| `is_principal(D)` | *no `isPrincipal` in M2's predicate list* | `GAP`. Principal-ness is "maps to zero in the class group" — translate as checking whether `D`'s image under the Weil-divisor-to-class-group map is `zero`, e.g. `zero((fromWDivToCl X) * vector D)`. **Use `zero(...)`, not `isZero(...)`** — see the "M2 predicate-naming conventions" note below; `isZero` does not exist in Macaulay2 and this exact mistake showed up in the first real test run. |
| `coefficients(D)` | `entries D` or `vector D` | `MATCH` in concept. |
| `polyhedron(D)` | `polytope D` | `MATCH` — different name (`polyhedron` vs. `polytope`) for the same object. |
| `is_feasible(P)` | `not isEmpty P` | `IDIOM`, `CONFIRMED` working. No named `isFeasible` predicate; "feasible" and "nonempty polyhedron" are the same thing. |
| `class_group(X)` | `classGroup X` | `MATCH`. |
| `picard_group(X)` | `picardGroup X` | `MATCH`. |
| `is_free(group)` | *no single predicate* | `IDIOM`. `classGroup`/`picardGroup` in M2 return a `Module` (a cokernel); freeness translates to something like checking the presentation matrix / `isFreeModule` after `prune`, not a one-call rename. |

## Underlying rings (relevant whenever a toric ideal or Cox ring shows up)

| OSCAR (Julia) | Macaulay2 | Notes |
|---|---|---|
| `polynomial_ring(QQ, n)` / `QQ[x_1, ..., x_n]` | `QQ[x_1..x_n]` | `MATCH` in concept; exact syntax differs. |
| `cox_ring(X)` | `ring X` (on a `NormalToricVariety`) | `MATCH` in concept — M2's `ring` on a toric variety returns its Cox ring. |
| `ideal(...)`/generators | `ideal(...)` | `MATCH`, mostly syntactic. |

## M2 predicate-naming conventions (a general trap, not just one function)

Most Macaulay2 boolean predicates keep an `is` prefix (`isCartier`, `isSmooth`, `isSimplicial`, `isComplete`, `isProjective`, `isFano`, `isEmpty` — this list is long and consistent). It's a reasonable default to guess `isX` for a predicate named `is_x` in OSCAR. But **the zero-test is the one well-known exception**: checking whether a ring element, vector, or matrix is zero in Macaulay2 is `zero(...)`, not `isZero(...)` — `isZero` does not exist. This came up for real in the first live test (translating `is_principal`, which reduces to a zero-test): the translation confidently produced `isZero(...)` by analogy with everything else, and it was wrong. When translating anything that reduces to "check this algebraic object is zero," reach for `zero`, and don't assume the `is`-prefix pattern is universal just because it holds almost everywhere else.

## Interactive/visualization-only functions

| OSCAR (Julia) | Macaulay2 | Notes |
|---|---|---|
| `visualize(X)` where `X` is a `Cone`, `Polyhedron`, or `PolyhedralFan` | *no equivalent* | `GAP` — genuinely nothing to translate, not just an unfound name. `visualize` opens an interactive 3D polymake/JavaScript viewer; there is no headless output to capture, compare, or reproduce in a script, and Macaulay2 has no comparable built-in viewer for these objects. Don't invent a plotting substitute — just skip the block and flag it as intentionally not translated. This came up repeatedly in Telen's notebooks (every lecture uses it for cones, polytopes, and fans alike), so expect it whenever translating notebook-style exploratory code rather than a script written to run non-interactively. |

## Known dated-syntax note

Telen's notebooks were written against an older OSCAR release and use `issmooth`, `isnormal`, `isaffine`, `isprojective`, `isfree`, `isfeasible`, `issimple`, `starsubdivision`, `iscartier`, `isprincipal`, `ToricDivisor` (capitalized), `NormalToricVariety(σ)` / `AffineNormalToricVariety(σ)` (capitalized constructors), `toric_projective_space`, and low-level `Polymake.*` calls including direct property access like `σ.pm_cone.CONE_TORIC_IDEAL.BINOMIAL_GENERATORS` or `P.pm_polytope.EHRHART_POLYNOMIAL`. Current OSCAR (v1.5.0, confirmed live) uses the snake_case forms (`is_smooth`, `is_normal`, etc.), exposes several of the old raw-polymake calls as first-class functions (`polarize(C)` instead of `Cone(Polymake.polytope.polarize(C.pm_cone))`, `toric_ideal(affine_normal_toric_variety(σ))` instead of the raw `BINOMIAL_GENERATORS` property poke), has moved to lowercase constructors (`toric_divisor`/`normal_toric_variety`/`affine_normal_toric_variety`, not their capitalized forms — the capitalized names either don't exist at all anymore or now only accept a raw `Polymake.LibPolymake.BigObject`, not the OSCAR-level type you'd actually have in hand), and has renamed a few outright (`toric_projective_space(d)` → `projective_space(NormalToricVariety, d)`). Since the goal is translating current-idiom code, not the notebook's exact 2022 syntax, the skill should modernize the Julia reading (map old name → current name) as part of understanding the source, in addition to producing modernized M2 output — and should not assume this list of dated names is exhaustive, since it's already grown twice from real testing (once per notebook exercised so far). **This modernization pass is about the OSCAR source alone and is intentionally kept out of the rest of this glossary, which is scoped to the OSCAR↔M2 correspondence** — record old→new OSCAR renames as comments on the modernized source file being translated, not as glossary rows here.

Worth noting for calibration: across ~25 translated calls in the first live test, the only genuinely wrong output was the `isZero`/`zero` mistake above. A second full-notebook pass (Telen's `Notebook_lecture3.ipynb` in full, ~15 translatable blocks after excluding the one `visualize` call) surfaced one more real bug (the `toric_ideal` "variety route" above — a wrong object, not a wrong name, and the dangerous kind since it failed silently rather than erroring) and one misleading-but-not-wrong note (`is_affine`'s phrasing). Everything else, including several non-trivial idiom reconstructions carried over from the first pass, was correct. The glossary approach is working; it just needs to keep absorbing real test results like this one, and the failure mode worth watching hardest is a translation that runs and returns a plausible-looking answer for the wrong mathematical object, since that's the kind no amount of "did it error" checking would catch — only a real invariant-based checkpoint does.
