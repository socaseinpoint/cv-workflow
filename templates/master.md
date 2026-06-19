# master — what it is and its format

**Master = a general `cv.json`** for the generator
([cv-generator](https://github.com/socaseinpoint/ats-cv-generator)), assembled with NO vacancy (driven
by `spec@master`). Tailoring to a title/company is edits to that same `cv.json` → re-render.
One format, fewest entities.

## Assembly

```
core (data/facts.md) × spec@master (data/spec/master.md)   → data/master.cv.json
master.cv.json × spec@title/@company + JD                    → data/targets/<target>.cv.json
<target>.cv.json → CV.pdf                                    (cv-generator/render.py)
```

## Data format

The `cv.json` schema — see `cv.example.json` in
[cv-generator](https://github.com/socaseinpoint/ats-cv-generator)
(header / summary / skills / experience / languages). Every line must rest on the core; a number rests
on the evidence bank with provenance. No fact in the core → placeholder or cut.

*Real `*.cv.json` files are your data and never go to git (`.gitignore`).*
