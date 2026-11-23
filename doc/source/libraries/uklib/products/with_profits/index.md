# With-Profits (WP)

[Product Specification](product-spec.md) defines the representative product and
[Technical Notes](technical-notes.md) derive its liability cash flow model.
[Implementation Notes](model.md) explain how `WP_UK_S` implements those notes and what was
standardized to do so; the cells reference generated from the model's own docstrings
follows it. How `WP_UK_SEC` extends `WP_UK_S` is explained in [In-Force Implementation
Notes](model-sec.md), and the cells reference of `WP_UK_SEC` follows it. Every source any of
them cites is in [Sources](sources.md).

```{toctree}
:maxdepth: 1

product-spec
technical-notes
model
WP_UK_S/WP_UK_S
model-sec
WP_UK_SEC/WP_UK_SEC
sources
```
