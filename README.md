# ag-translate

A Claude Code skill that translates algebraic geometry / commutative algebra code between **Julia's OSCAR package** and **Macaulay2**, in either direction — and actually verifies the translation by running both the original and translated code, rather than trusting a one-shot LLM guess.

## The problem

Algebraic geometers split across several incompatible computer algebra systems (Macaulay2, Singular, Sage, Julia/OSCAR, Magma, Mathematica). Collaborators on the same project routinely end up in different languages, and switching costs real research time. Existing tools solve *adjacent* problems — OSCAR unifies several systems natively in Julia, Sage can drive Macaulay2 as a subprocess — but nothing translates an existing script in one system into idiomatic, runnable code in another. That's what this project does, scoped for now to OSCAR ↔ Macaulay2.

## Why this is tractable now

Two things make LLM-based translation viable here in a way it wasn't a couple of years ago:

1. **A grounded glossary.** `ag-translate/references/toric_glossary.md` is a curated correspondence table between OSCAR and Macaulay2 function names/idioms, built from official documentation and corrected against real installs — not just an LLM's (thin, for these languages) training-data memory.
2. **Checkable output.** Algebraic geometry computations have invariants — dimension, degree, a Hilbert basis, whether a group is free — that can be computed in both languages and compared. So instead of trusting a translation, the skill generates one, actually runs both sides locally, compares outputs, and repairs mismatches before handing anything back.

## How it works

See `ag-translate/SKILL.md` for the full workflow. In short: segment the source into blocks → translate each block using the glossary first, live introspection second → propose verification checkpoints per block → run both languages and compare → repair on mismatch (up to 3 attempts) → write output with clearly delimited blocks + a manifest, so a later re-run can re-translate only new/changed material instead of redoing the whole file.

## Installing in Claude Code

```
unzip ag-translate.skill -d ~/.claude/skills/     # if you have the packaged .skill file
# or, from this repo:
cp -r ag-translate ~/.claude/skills/ag-translate
```

(Use a project-local `.claude/skills/` instead of `~/.claude/skills/` if you only want it available in one project.) Then just ask Claude Code to translate a file — the skill's description is written to trigger without needing to invoke it by name.

**Requirements:** the skill shells out to your local `julia` (with OSCAR.jl installed) and `M2` executables to run the verification loop — both need to already be on your PATH.

## Status

This is an early, solo-built prototype, currently scoped to toric geometry (cones, fans, polytopes, toric varieties, divisors, class/Picard groups) — the area covered by the initial test corpus. The glossary is a living document: every real translation run is a chance to catch and fix a wrong entry, and it's already been corrected once against a real OSCAR v1.5.0 + Macaulay2 install (see the glossary file's changelog note). Extending it to other areas of commutative algebra/algebraic geometry (Gröbner bases in general, sheaf cohomology, etc.) is a natural next step and contributions are welcome — see below.

## Test corpus

`ag-translate/evals/files/` contains two small OSCAR scripts used to sanity-check the translator. They're short excerpts adapted (and updated to current OSCAR syntax) from Simon Telen's ["Introduction to Toric Geometry"](https://github.com/simontelen/introduction_to_toric_geometry) course notes (MPI Leipzig) — credit to him for the original teaching material. The full notebooks aren't vendored into this repo; if you want a larger test set, clone his repo separately.

## Contributing

The most valuable contribution right now is glossary entries: if you translate something in a different area of algebraic geometry and find a gap or a wrong entry, add it to `references/toric_glossary.md` (or split off a new reference file for a new area, e.g. `references/groebner_glossary.md`, and point to it from `SKILL.md`) with a PR. Flag whether it's confirmed against a real install or just from documentation — the confidence tags (`MATCH`/`IDIOM`/`GAP`/`VERIFY`/`CONFIRMED`) are there so future users know how much to trust each row.

## License

MIT — see `LICENSE`. (Happy to switch this if you'd prefer something else, e.g. Apache-2.0.)
