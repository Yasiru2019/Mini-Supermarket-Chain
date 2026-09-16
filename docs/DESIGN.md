# Supermarket Chain Management Software — Blueprint v0.1

Status: working draft, not yet approved for build.
- Architecture, module map, core flows: https://claude.ai/code/artifact/081b3eec-64fa-4ab6-b165-bbbcfb0b0bd1
- Database entities per module + cross-module links: https://claude.ai/artifact/T6Fo3R9enAgAa4qmABSQrA

## Business context
- New supermarket chain, no name decided yet.
- Starting with 1–2 outlets, planned expansion to more locations later.
- Assume PGK currency and GST until confirmed.
- Working style: always describe what's about to be implemented, wait for explicit confirmation, THEN write code.

## Decisions confirmed
- **Connectivity/architecture**: Local server per outlet (on-site database), designed hybrid-ready so a cloud sync layer can be added later to give head office a cross-outlet view once the chain grows.
- **Platform**: Browser-based app hosted on the outlet's own server. Rollout path: build and test on localhost during development; before go-live, deploy the same app onto a small always-on machine at the outlet (single-board computer e.g. Raspberry Pi 4/5, or a repurposed old PC). Go-live checklist: fixed local IP for the server, app auto-starts on boot, server on a UPS, and if using a Pi run the database off a USB SSD (not the SD card).
- **Build order**: Phased. Phase 1 = Cashier/Till, Inventory & Stock, Purchasing & Suppliers. Phase 2 = Customers & Credit, Accounting & Finance, Admin & Hardware, Reports & Analytics. Phase 3 (future) = cross-outlet cloud sync.

## Module map
1. **MOD-01 Cashier / Till** (Phase 1) — barcode scan w/ instant lookup, manual entry fallback, cart, cash/card/credit payment, receipt printing, held sales, returns.
2. **MOD-02 Inventory & Stock** (Phase 1) — item catalogue (SKU, barcode, units-per-carton), live per-outlet stock, low-stock alerts, damage/wastage write-off with reason codes.
3. **MOD-03 Purchasing & Suppliers** (Phase 1) — purchase orders by the carton, goods-received notes (GRN), carton→unit conversion, supplier catalogue/pricing.
4. **MOD-04 Customers & Credit** (Phase 2) — customer profiles, credit limits/running balances, payment history.
5. **MOD-05 Accounting & Finance** (Phase 2) — sales ledger, accounts payable, accounts receivable, expenses, basic P&L.
6. **MOD-06 Admin & Hardware** (Phase 2) — staff logins/PINs per till, printer-to-PC mapping, scanner pairing, outlet settings, tax configuration.
7. **MOD-07 Reports & Analytics** (Phase 2) — daily sales/EOD reconciliation, stock movement, best/worst sellers, margin reports, credit aging, purchase history.

## Core flows
- **POS sale**: scan → look up SKU in local DB → add to cart → (repeat) → apply credit/discount if flagged → take payment → print receipt + decrement stock simultaneously → log to sales ledger.
- **Purchasing/GRN**: create PO by carton → send to supplier → goods received at warehouse → GRN confirms actual qty → system converts cartons to units → stock updated at unit level + unit cost recalculated → supplier invoice recorded → if on credit, added to accounts payable.
- **Costing**: carton cost ÷ units-per-carton = unit cost; unit cost + margin% = shelf/selling price.

## Data model
Shared foundation: `outlets`, `users` referenced everywhere. Design pattern used throughout: stock and customer credit are never a single overwritten number — every change (sale, delivery, write-off, payment) is an immutable line in a ledger table (`stock_ledger`, `customer_credit_ledger`), and the current balance is the running total. Everything eventually posts into a general `ledger_entries` table, which is the one place Reports (MOD-07) reads from. Full entity/field breakdown per module: see the Data Model artifact linked above.

## Open questions
1. Tech stack (language/framework + database) — not yet chosen.
2. Server hardware for go-live: repurpose an old PC, or buy a Raspberry Pi 4/5?
3. Confirm currency/tax rules — assuming PGK + GST, need exact rate and receipt format.
4. What till hardware exists or is planned (printers, barcode scanners, cash drawers, till PCs)?
