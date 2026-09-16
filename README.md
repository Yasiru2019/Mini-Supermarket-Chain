# Mini Supermarket Chain — Management Software

Status: **design phase — no application code yet.** This repo exists so every coding session works from the same shared history instead of a one-off chat.

## Design docs
Full design lives as two interactive pages, plus a running spec doc:
- [System Blueprint](https://claude.ai/code/artifact/081b3eec-64fa-4ab6-b165-bbbcfb0b0bd1) — architecture, module map, core flows (till sale, purchasing/GRN, carton→unit costing)
- [Data Model & Module Links](https://claude.ai/artifact/T6Fo3R9enAgAa4qmABSQrA) — entities per module and how they connect
- [docs/DESIGN.md](docs/DESIGN.md) — the same content in plain text, kept in this repo for offline reference

## Decisions confirmed so far
- **Connectivity**: one local server per outlet holds the database; every till/warehouse/office PC on that outlet's network talks to it. Designed hybrid-ready so a cloud sync layer can be added later across outlets.
- **Platform**: browser-based app hosted on the outlet's own server (not an installed desktop program) — chosen for single-point upgrades.
- **Rollout**: build and test on localhost during development; move to a small always-on machine (Raspberry Pi or a repurposed old PC) at the outlet before go-live.
- **Build order**: Phase 1 = Cashier/Till, Inventory & Stock, Purchasing & Suppliers. Phase 2 = Customers & Credit, Accounting & Finance, Admin & Hardware, Reports & Analytics.

## Not decided yet
- Tech stack (language/framework + database) for the actual application — next thing to confirm before any Phase 1 code is written.
- Server hardware for go-live (Raspberry Pi vs. old PC).
- Currency/tax configuration (assuming PGK + GST, rate to be confirmed).

## Working style
No code is written or committed to this repo without it being described and approved first — see the design docs above for the agreed process.
