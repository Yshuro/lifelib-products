# Whole of Life (WOL)

[Product Specification](product-spec.md) defines the representative product and
[Technical Notes](technical-notes.md) derive its liability cash flow model.
[Implementation Notes](model.md) explain how `WOL_UK_S` implements those notes and what was
standardized to do so; the cells reference generated from the model's own docstrings
follows it. How `WOL_UK_SEC` extends `WOL_UK_S` is explained in [In-Force Implementation
Notes](model-sec.md), and the cells reference of `WOL_UK_SEC` follows it. Every source any
of them cites is in [Sources](sources.md).

```{toctree}
:maxdepth: 1

product-spec
technical-notes
model
WOL_UK_S/WOL_UK_S
model-sec
WOL_UK_SEC/WOL_UK_SEC
sources
```
