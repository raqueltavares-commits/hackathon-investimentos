# Paleta de acabamento por estilo

Embutida em `scripts/acabamentos.py` (`_ACABAMENTO` + `_ACABAMENTO_FIXO`). Calibravel.

- **Biofilico**: calibrado do memorial-exemplo da Raquel (Mdf areia/savana/palhinha, metal bege claro, granito pitaya, suede preto).
- **Clean**: madeira clara/branco, metal cromado, granito branco.
- **Industrial**: Mdf grafite/carvalho, metal preto, granito preto, couro caramelo.
- **Bruma**: Mdf fendi/cinza, metal champagne, granito cinza, linho areia.
- **Metais/eletros** (`_ACABAMENTO_FIXO`): independem do estilo (cromado, inox, preto, aluminio escovado...).
- Fallback: "A confirmar".

## Como o acabamento entra no memorial
`montar_orcamento.itens_para_tipologia(..., estilo=...)` chama `acabamento_de(estilo, role)`
e grava em `LinhaMemorial.acabamento`. O serializador estruturado coloca isso na linha
"Acabamento" (4a linha de cada item, na ficha tecnica). Largura/Altura/Profundidade saem
"A confirmar" por padrao.

## Recalibrar
Ajustar os dicts em `acabamentos.py` conforme:
- os **moodboards** por estilo (IDs no SKILL.md / spec da Fase 2);
- o **Sheet de marcenaria por estilo** `1VnEZ-2UscCx03cwEGEDVA9vbfaUw4Y04wiM_lh9YRYI`.
Acrescentar/editar `role -> acabamento` por estilo. Onde nao houver entrada, cai em "A confirmar".
