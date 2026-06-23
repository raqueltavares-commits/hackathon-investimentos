"""Serviços e instalações. Entram como itens (categoria SERVIÇOS) no memorial.

Valores default = espelho da base Supabase (categoria Serviços, subcategoria 2.2.x).
O código liga ao produto real via depara-catalogo.json; quando o catálogo está
disponível, o preço vem dele (fonte de verdade). Default é só fallback offline.
"""

# (role, nome, ambiente, codigo, valor_default)  — codigo casa com depara-catalogo.json
SERVICOS = [
    ("inst_eletrica",   "Instalações elétricas",          "Serviços", "SRV0005", 700.0),  # produto 33
    ("inst_hidraulica", "Instalações hidráulicas",        "Serviços", "SRV0006", 550.0),  # produto 32
    ("inst_ar",         "Instalação de ar condicionado",  "Serviços", "SRV0007", 800.0),  # produto 31
    ("inst_geral",      "Instalações gerais",             "Serviços", "SRV0008", 250.0),  # produto 30
    ("pintura",         "Pintura efeito",                 "Serviços", "SRV0001", 100.0),  # produto 35
    ("feltro",          "Aplicação de feltro nos mobiliários", "Serviços", "SRV0003", 250.0),  # produto 34
    ("limpeza",         "Limpeza e arrumação",            "Serviços", "SRV0010", 450.0),  # produto 29
]
