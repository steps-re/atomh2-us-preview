# Atom H2 — United States field study

Companion to `atomh2-spain-preview`. A single static page arguing where a
containerised solar-hydrogen system actually pencils in the US, and what a
three-month visit should produce.

The page is **generated**, never hand-edited:

```
python3 build_page.py     # us_screen.json -> index.html
```

`us_screen.json` is produced by `build_us_screen.py` in the `atomh2-global`
project (bd-agent repo), which pulls Alaska PCE delivered-diesel invoices, the
FCC Antenna Structure Registration dump and NASA POWER climatology. Copy the
refreshed JSON here and re-run `build_page.py` to update the page.

Steps Ventures is a paid consultant to Atom H2 — see the disclosure in the page footer.
