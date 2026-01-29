# TL;DR 1-minute overview (EN)

**Global Equity Momentum (GEM) Strategy** is a Power BI portfolio project implementing the Global Equity Momentum (GEM) investment strategy using real market data.

The project addresses a common real-world problem: correctly applying GEM rules (12-month momentum excluding the most recent month, monthly rebalancing, single-asset allocation) without manual calculations or misinterpretation.

Market data is collected daily via a Python ETL script from Stooq, stored as a Parquet snapshot, and analyzed in Power BI. All strategy logic (time windows, reference dates, asset selection) is implemented directly in DAX.

The dashboard is updated manually once per month, aligned with the classic GEM rebalancing schedule. The project focuses on logical correctness, transparent data modeling, and clear end-to-end ownership rather than unnecessary automation.

---

# TL;DR 1-minute overview (EN)

**Global Equity Momentum (GEM) Strategy** to projekt portfolio w Power BI prezentujący implementację strategii inwestycyjnej Global Equity Momentum (GEM) w oparciu o rzeczywiste dane rynkowe.

Projekt rozwiązuje praktyczny problem: poprawne odwzorowanie zasad GEM (momentum 12M z wyłączeniem ostatniego miesiąca, miesięczny rebalancing, jedno aktywo w portfelu) bez ręcznego liczenia i błędów interpretacyjnych.

Dane rynkowe są pobierane codziennie skryptem Python z serwisu Stooq, zapisywane jako snapshot Parquet i analizowane w Power BI. Cała logika strategii (okna czasowe, daty referencyjne, wybór aktywa) została zaimplementowana w DAX.

Dashboard jest aktualizowany ręcznie raz w miesiącu, zgodnie z klasycznym założeniem strategii GEM. Projekt kładzie nacisk na poprawność logiczną, przejrzystość modelu danych oraz pełną kontrolę nad algorytmem decyzyjnym.

---

# Full Project Description

## Project Overview
This project implements the Global Equity Momentum (GEM) investment strategy as an end-to-end data analytics solution using Python, Parquet and Power BI.

The goal of the project is to solve a real-world problem faced by beginner investors:
how to correctly implement and monitor the GEM strategy using real market data, proper time windows and clear decision rules, without relying on complex or expensive tooling.

The final result is a Power BI dashboard that always indicates the currently selected asset according to GEM rules, based on up-to-date market data.
#
## Strategy Summary (GEM)
The Global Equity Momentum strategy is based on relative momentum and monthly portfolio rebalancing.

**Core assumptions:**
- The portfolio is fully invested in one asset at a time
- Assets are grouped into:
    - Developed markets equities
    - Emerging markets equities
    - Long-term bonds
    - Short-term bonds (cash proxy)
- Once per month, the asset with the highest 12-month return is selected
- The most recent month is excluded from the momentum window to reduce short-term noise

**The strategy aims to:**
- Participate in equity bull markets
- Reduce drawdowns during prolonged bear markets
- Improve risk-adjusted returns compared to passive investing

All strategy logic is implemented directly in DAX, not hard-coded in visuals.
#
## Data Pipeline
**End-to-end flow:**
Stooq.pl (CSV)
   ↓
Python ETL
   ↓
Parquet snapshot (OneDrive)
   ↓
Power BI Desktop
   ↓
Power BI Service (manual publish)

**Data Sources**
- CNDX.UK
- CSPX.UK
- IWDA.UK
- EIMI.UK
- VFEM.UK
- CBU0.UK
- IDTL.UK
- IB01.UK

**ETL (Python)**
The Python Script:
- Downloads daily CSV data
- Normalizes column names and formats
- Removes the current trading day (unstable close)
- Saves a Parquet snapshot for Power BI
- Optionally inserts data into a MySQL database (private use)

ETL script:
[etl/stooq_to_parquet.py](                                                                                          )
#
## Data Model
The Power BI model follows a simple star schema:
**Fact table**
- *market_data gem_prices_daily*
  (daily prices per ticker)
**Dimensions**
- *Dim_Date* - custom calendar table (auto-date disabled)
- *DIM-Ticker* - ticker dimension
- *tickery_opis* - descriptive metadata (display only)
Relationships are 1-to-many, single-directional.
A model diagram is available in:
[powerbi/model.png](____________________________________________________________________________________)
#
## Key DAX Logic
All GEM logic is implemented in **DAX measures and helper columns**, including:
- Rolling 12-month momentum window (excluding last month)
- Anchor price selection
- Current index calculation
- Monthly (End-of-Month) variant of the strategy
Example logic:
- Identification of valid momentum window
- Dynamic handling of month-end edge cases
- Separation of Current vs End-of-Month calculations
Details:
[docs/dax-key-measures.md](______________________________________________________________________________)
#
## Refresh & Automation
Important design decision
- Market data is collected daily via Python ETL
- Power BI Desktop uses the Parquet file as its fact table source
- Power BI Service is not automatically refreshed
Refresh schedule
- The dashboard is updated manually once per month
- Refresh is performed:
    - after morning ETL
    - on the first trading day of the month
- This schedule is fully aligned with GEM’s monthly rebalancing logic
This approach avoids unnecessary complexity (gateways, licenses) while remaining fully correct from a strategy perspective.

Detailed steps:
[docs/refresh-process.md](_________________________________________________________________________________)
#
## Dashboard Preview
Screenshots of the report:
- Overall dashboard view
- Asset selection according to GEM
- Performance comparison
Available in:
[screenshots/](_________________________________________________________________________________________)
#
## How to Run Locally
1. Clone the repository
2. Run the ETL script:
   [python etl/stooq_to_parquet.py](_______________________________________________________________)
3. Open:
   [powerbi/GEM_public_autorefresh.pbix](_____________________________________________________)
4. Click **Refresh**
#
## Design Choices & Limitations
- Manual monthly refresh instead of scheduled Service refresh
- Parquet chosen to avoid on-premise gateway dependency
- Strategy logic intentionally kept transparent and auditable in DAX
- Focus on correctness and clarity rather than real-time automation
#
## Project Purpose
This project was created as a portfolio project for a junior data analyst role.

It demonstrates:
- Business problem understanding
- Time-series data handling
- DAX-based algorithm implementation
- End-to-end ownership of a data solution
