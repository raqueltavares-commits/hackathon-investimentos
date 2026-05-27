"""Metadata de itens (ambiente/fornecedor) + paleta de acabamento por estilo.

A paleta é EMBUTIDA e calibravel: Biofilico veio do memorial-exemplo da Raquel;
Clean/Industrial/Bruma sao paletas iniciais coerentes com o estilo. Fallback "A confirmar".
"""

# Ambiente por role (independe do estilo)
META_ITEM: dict[str, dict[str, str]] = {
    "gabinete_inferior":   {"ambiente": "Cozinha"},
    "gabinete_superior":   {"ambiente": "Cozinha"},
    "cabeceira":           {"ambiente": "Quarto"},
    "arara_roupas":        {"ambiente": "Quarto"},
    "bancada_refeicao":    {"ambiente": "Cozinha"},
    "movel_apoio":         {"ambiente": "Quarto"},
    "prateleira_banheiro": {"ambiente": "Banheiro"},
    "bancada_coz_pedra":   {"ambiente": "Cozinha"},
    "bancada_ban_pedra":   {"ambiente": "Banheiro"},
    "cama_queen":          {"ambiente": "Quarto"},
    "sofa_cama":           {"ambiente": "Quarto"},
    "puff":                {"ambiente": "Quarto"},
    "cadeira_jantar":      {"ambiente": "Cozinha"},
    "torneira_coz":        {"ambiente": "Cozinha"},
    "cuba_coz":            {"ambiente": "Cozinha"},
    "cuba_ban":            {"ambiente": "Banheiro"},
    "torneira_ban":        {"ambiente": "Banheiro"},
    "box_banheiro":        {"ambiente": "Banheiro"},
    "filtro_agua":         {"ambiente": "Cozinha"},
    "toalheiro_termico":   {"ambiente": "Banheiro"},
    "kit_metais":          {"ambiente": "Banheiro"},
    "cooktop":             {"ambiente": "Cozinha"},
    "frigobar":            {"ambiente": "Cozinha"},
    "microondas":          {"ambiente": "Cozinha"},
    "cafeteira":           {"ambiente": "Cozinha"},
    "chaleira":            {"ambiente": "Cozinha"},
    "liquidificador":      {"ambiente": "Cozinha"},
    "depurador":           {"ambiente": "Cozinha"},
    "mini_grill":          {"ambiente": "Cozinha"},
    "tv":                  {"ambiente": "Quarto"},
    "iluminacao":          {"ambiente": "Geral"},
    "jacuzzi":             {"ambiente": "Garden"},
    "mesa_externa":        {"ambiente": "Garden"},
}

# Acabamento por estilo -> role. Biofilico calibrado do exemplo.
_ACABAMENTO: dict[str, dict[str, str]] = {
    "biofilico": {
        "gabinete_inferior":   "Mdf areia",
        "gabinete_superior":   "Mdf sava e palhinha com metal bege claro",
        "cabeceira":           "Mdf savana",
        "arara_roupas":        "Mdf savana, areia, palhinha e metal bege claro",
        "bancada_refeicao":    "Mdf areia",
        "movel_apoio":         "Mdf areia",
        "prateleira_banheiro": "Mdf savana e metal bege claro",
        "bancada_coz_pedra":   "Granito pitaya",
        "bancada_ban_pedra":   "Granito pitaya",
        "cama_queen":          "Suede preto",
        "sofa_cama":           "Linho cru",
        "puff":                "Linho cru",
        "cadeira_jantar":      "Madeira clara com palhinha",
        "iluminacao":          "Led / bege",
    },
    "clean": {
        "gabinete_inferior":   "Mdf branco",
        "gabinete_superior":   "Mdf branco com metal cromado",
        "cabeceira":           "Mdf off-white",
        "arara_roupas":        "Mdf branco e metal cromado",
        "bancada_refeicao":    "Mdf branco",
        "movel_apoio":         "Mdf branco",
        "prateleira_banheiro": "Mdf branco",
        "bancada_coz_pedra":   "Granito branco",
        "bancada_ban_pedra":   "Granito branco",
        "cama_queen":          "Suede off-white",
        "sofa_cama":           "Linho cinza claro",
        "puff":                "Linho cinza claro",
        "cadeira_jantar":      "Madeira clara",
        "iluminacao":          "Led / branco",
    },
    "industrial": {
        "gabinete_inferior":   "Mdf grafite",
        "gabinete_superior":   "Mdf grafite com metal preto",
        "cabeceira":           "Mdf carvalho escuro",
        "arara_roupas":        "Metal preto",
        "bancada_refeicao":    "Mdf grafite",
        "movel_apoio":         "Mdf grafite",
        "prateleira_banheiro": "Metal preto",
        "bancada_coz_pedra":   "Granito preto",
        "bancada_ban_pedra":   "Granito preto",
        "cama_queen":          "Suede grafite",
        "sofa_cama":           "Couro caramelo",
        "puff":                "Couro caramelo",
        "cadeira_jantar":      "Metal preto com madeira escura",
        "iluminacao":          "Led / preto",
    },
    "bruma": {
        "gabinete_inferior":   "Mdf fendi",
        "gabinete_superior":   "Mdf fendi com metal champagne",
        "cabeceira":           "Mdf cinza claro",
        "arara_roupas":        "Mdf fendi e metal champagne",
        "bancada_refeicao":    "Mdf fendi",
        "movel_apoio":         "Mdf fendi",
        "prateleira_banheiro": "Mdf fendi",
        "bancada_coz_pedra":   "Granito cinza",
        "bancada_ban_pedra":   "Granito cinza",
        "cama_queen":          "Suede cinza",
        "sofa_cama":           "Linho areia",
        "puff":                "Linho areia",
        "cadeira_jantar":      "Madeira acinzentada",
        "iluminacao":          "Led / champagne",
    },
}

# Acabamentos de metais/eletros independem do estilo
_ACABAMENTO_FIXO: dict[str, str] = {
    "torneira_coz":      "Cromado",
    "cuba_coz":          "Inox acetinado",
    "cuba_ban":          "Branco",
    "torneira_ban":      "Cromado",
    "box_banheiro":      "Alumínio escovado",
    "filtro_agua":       "Branco",
    "toalheiro_termico": "Cromado",
    "kit_metais":        "Cromado",
    "cooktop":           "Preto",
    "frigobar":          "Preto",
    "microondas":        "Inox espelhado",
    "cafeteira":         "Inox/Preto",
    "chaleira":          "Inox/Preto",
    "liquidificador":    "Preto",
    "depurador":         "Inox",
    "mini_grill":        "Inox/Preto",
    "tv":                "Preto",
    "jacuzzi":           "N/A",
    "mesa_externa":      "Preto",
}


def acabamento_de(estilo: str, role: str) -> str:
    e = (estilo or "").strip().lower()
    if role in _ACABAMENTO_FIXO:
        return _ACABAMENTO_FIXO[role]
    return _ACABAMENTO.get(e, {}).get(role, "A confirmar")
