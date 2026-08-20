# Incremental translation protocol

The goal: when the user adds new code to a source file that's already been translated, re-translate only the new/changed material, in the same style as what's already there, and splice it into the existing output — don't regenerate the whole file. This is the same basic idea as translation memory in professional CAT (computer-assisted translation) tools, applied to code instead of prose.

## The manifest

Next to the output file, maintain `<output-file>.ag_manifest.json`:

```json
{
  "source_file": "toric_notebook.jl",
  "source_language": "oscar",
  "target_file": "toric_notebook_translated.m2",
  "target_language": "macaulay2",
  "blocks": [
    {
      "id": "block-1",
      "source_hash": "sha256:...",
      "source_excerpt": "σ = positive_hull([-2 5; 1 0])",
      "status": "verified",
      "checkpoints": ["rays(σ) matches rays translated cone"],
      "notes": ""
    }
  ]
}
```

`source_hash` is a hash of the block's source text with insignificant whitespace normalized (strip trailing whitespace, collapse blank lines) — the goal is to detect *meaningful* changes, not reformatting noise. `scripts/manifest_tools.py` implements this hashing consistently; use it rather than hand-rolling a hash so re-runs agree with what was stored.

## On a re-run

1. Segment the current source file the same way as before.
2. Hash each block and compare against the manifest.
3. Classify each block: **unchanged** (hash matches, skip entirely — don't even re-verify), **changed** (hash differs from a block with the same id/position — re-translate and re-verify just this one), **new** (no corresponding manifest entry — translate and verify as usual), **removed** (manifest has an entry with no corresponding source block anymore — remove its translated code from the output and drop it from the manifest, but flag this to the user since silently deleting code is the kind of thing that should be visible, not assumed).
4. For changed/new blocks, before generating the translation, read the surrounding *already-translated* output file as style context — variable naming choices, comment conventions, formatting — so the new block reads as if it was translated in the same pass as everything else, not bolted on. Consistency here matters more than any single stylistic choice being "right."
5. Splice: replace changed blocks in place (between their markers), insert new blocks at the position corresponding to their location in the source, remove markers for deleted blocks. Leave every unchanged block's text completely untouched — don't reformat things you didn't need to touch, even if you'd have written them slightly differently today.
6. Update the manifest: new hashes, new statuses, preserved entries for unchanged blocks.

## Block markers in the output file

Wrap every translated block so it's unambiguous where one starts and ends, using the target language's own comment syntax:

Macaulay2:
```
-- ag-translate: block-1 start
...translated code...
-- ag-translate: block-1 end
```

Julia:
```
# ag-translate: block-1 start
...translated code...
# ag-translate: block-1 end
```

Keep block ids stable across re-runs (tie them to position/order in the source, e.g. `block-1`, `block-2`, ... in source order) so the manifest and the markers stay in sync even as blocks are added in the middle of a file.
