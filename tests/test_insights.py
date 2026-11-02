from src.insights import overview_insights

STATES = [{"estado": "SP", "faturamento": 300.0}, {"estado": "RJ", "faturamento": 100.0}]
CATEGORIES = [
    {"macro_categoria": "Moda", "pedidos": 2, "taxa_cancelamento": 0.5},
    {"macro_categoria": "Tecnologia", "pedidos": 2, "taxa_cancelamento": 0.0},
]


def test_all_findings_come_from_the_data():
    findings = overview_insights({"faturamento": -0.1}, STATES, CATEGORIES)
    assert findings == [
        "Faturamento caiu 10,0% sobre o período anterior.",
        "SP lidera com R$ 300,00 (75,0% do total).",
        "Moda tem a maior taxa de cancelamento: 50,0%.",
    ]


def test_missing_base_drops_the_finding():
    assert overview_insights({"faturamento": None}, STATES[:1], CATEGORIES[:1]) == []
