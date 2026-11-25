# Income Protection (IP)

[Product Specification](product-spec.md) defines the representative product and
[Technical Notes](technical-notes.md) derive its liability cash flow model.
[Implementation Notes](model.md) explain how `IP_UK_S` implements those notes and what was
standardized to do so; the cells reference generated from the model's own docstrings
follows it. How `IP_UK_SEC` extends `IP_UK_S` is explained in [In-Force Implementation
Notes](model-sec.md), and the cells reference of `IP_UK_SEC` follows it. Every source any of
them cites is in [Sources](sources.md).

```{toctree}
:maxdepth: 1

product-spec
technical-notes
model
IP_UK_S/IP_UK_S
model-sec
IP_UK_SEC/IP_UK_SEC
sources
```
