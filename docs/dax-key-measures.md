# Key DAX Measures – GEM Strategy

This document presents the most important DAX measures used to implement
the Global Equity Momentum (GEM) strategy logic in Power BI.

Only core measures are included to keep the logic readable and auditable.

---


```DAX
Current | Reference Date =
MAX ( 'market_data gem_prices_daily'[price_date] )

# Determines the most recent available trading date in the dataset.

Is Current 12M =
VAR RefDate =
    CALCULATE (
        MAX ( 'market_data gem_prices_daily'[price_date] ),
        ALL ( 'market_data gem_prices_daily' )
    )
VAR WindowEnd =
    EDATE ( RefDate, -1 )
VAR WindowStart =
    EDATE ( WindowEnd, -12 ) + 1
RETURN
    Dim_Date[Date] >= WindowStart
        && Dim_Date[Date] <= WindowEnd


# Identifies dates belonging to the 12-month momentum window
excluding the most recent month.

Current || Price Anchor =
VAR RefDate =
    CALCULATE (
        MAX ( 'market_data gem_prices_daily'[price_date] ),
        ALL ( Dim_Date )
    )
VAR LogicalAnchorDate =
    EDATE ( RefDate, -13 ) + 1
VAR AnchorDate =
    CALCULATE (
        MIN ( 'market_data gem_prices_daily'[price_date] ),
        ALL ( 'market_data gem_prices_daily' ),
        'market_data gem_prices_daily'[price_date] >= LogicalAnchorDate
    )
RETURN
    CALCULATE (
        MAX ( 'market_data gem_prices_daily'[close_price] ),
        ALL ( Dim_Date ),
        Dim_Date[Date] = AnchorDate
    )

# Returns the price used as a reference point for momentum calculations.

Current Day Price =
CALCULATE (
    MAX ( 'market_data gem_prices_daily'[close_price] ),
    KEEPFILTERS ( Dim_Date[Date] )
)

# Returns the current price for a given asset and date context.

Current || Index =
DIVIDE ( [Current Day Price], [Current || Price Anchor] ) - 1

Calculates the relative momentum index used for asset ranking.

---
