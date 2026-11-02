"""Plain-language findings derived from query results, with no invented facts."""

from src.formatting import format_currency, format_percent


def overview_insights(
    growth: dict[str, float | None],
    states: list[dict[str, object]],
    categories: list[dict[str, object]],
) -> list[str]:
    """Up to three sentences; each exists only when its data supports it."""
    findings: list[str] = []
    revenue_growth = growth.get("faturamento")
    if revenue_growth is not None:
        direction = "cresceu" if revenue_growth >= 0 else "caiu"
        findings.append(f"Faturamento {direction} {format_percent(abs(revenue_growth))} sobre o período anterior.")
    if len(states) > 1:
        leader = max(states, key=lambda row: row["faturamento"])
        total = sum(row["faturamento"] for row in states)
        if total:
            share = format_percent(leader["faturamento"] / total)
            findings.append(f"{leader['estado']} lidera com {format_currency(leader['faturamento'])} ({share} do total).")
    rated = [row for row in categories if row.get("taxa_cancelamento") is not None and row.get("pedidos")]
    if len(rated) > 1:
        worst = max(rated, key=lambda row: row["taxa_cancelamento"])
        findings.append(
            f"{worst['macro_categoria']} tem a maior taxa de cancelamento: "
            f"{format_percent(worst['taxa_cancelamento'])}."
        )
    return findings
