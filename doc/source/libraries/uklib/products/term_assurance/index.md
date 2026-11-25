# Term Assurance

[Product Specification](product-spec.md) defines the representative product and
[Technical Notes](technical-notes.md) derive its liability cash flow model.
[Implementation Notes](model.md) explain how `Term_UK_S` implements those notes and what was
standardized to do so; the cells reference generated from the model's own docstrings
follows it. How `Term_UK_SEC` extends `Term_UK_S` is explained in [In-Force Implementation
Notes](model-sec.md), and the cells reference of `Term_UK_SEC` follows it. Every source any
of them cites is in [Sources](sources.md).

```{toctree}
:maxdepth: 1

product-spec
technical-notes
model
Term_UK_S/Term_UK_S
model-sec
Term_UK_SEC/Term_UK_SEC
sources
```
