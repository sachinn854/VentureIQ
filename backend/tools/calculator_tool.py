def ltv_cac_ratio(ltv: float, cac: float) -> float:
    """LTV:CAC ratio. Healthy = 3x+. Returns 0 if CAC is zero."""
    if cac <= 0:
        return 0.0
    return round(ltv / cac, 2)


def breakeven_months(revenue_per_customer: float, cac: float) -> int:
    """Months to recover CAC from per-customer revenue.
    Returns -1 if revenue_per_customer <= 0 (never breaks even).
    """
    if revenue_per_customer <= 0:
        return -1
    months = cac / revenue_per_customer
    return max(1, round(months))


def estimate_year1_revenue(
    som: float,
    market_capture_rate: float,
    avg_ticket_size: float,
) -> float:
    """Rough Year 1 revenue estimate.

    som                 — Serviceable Obtainable Market in INR
    market_capture_rate — fraction of SOM captured in Year 1 (e.g. 0.01 = 1%)
    avg_ticket_size     — average revenue per customer in INR
    """
    if som <= 0 or market_capture_rate <= 0 or avg_ticket_size <= 0:
        return 0.0
    customers = (som * market_capture_rate) / avg_ticket_size
    return round(customers * avg_ticket_size, 2)


def score_financials(ltv_cac: float, breakeven: int) -> float:
    """Produce a 0–10 financial health score from key metrics."""
    score = 0.0

    # LTV:CAC scoring (max 5 points)
    if ltv_cac >= 5:
        score += 5.0
    elif ltv_cac >= 3:
        score += 4.0
    elif ltv_cac >= 2:
        score += 2.5
    elif ltv_cac >= 1:
        score += 1.0

    # Break-even scoring (max 5 points)
    if breakeven == -1:
        score += 0.0
    elif breakeven <= 6:
        score += 5.0
    elif breakeven <= 12:
        score += 4.0
    elif breakeven <= 18:
        score += 3.0
    elif breakeven <= 24:
        score += 1.5

    return round(score, 1)
