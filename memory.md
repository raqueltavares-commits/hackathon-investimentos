# memory.md --- hackathon-investimentos

Decisoes arquiteturais, estado atual, links uteis.
Eu anexo automaticamente quando voce decidir algo ("vamos com X").

---

2026-05-26 --- Fase 1 do projeto = skill `tabela-tipologias`: puxa o anteprojeto LANÇAMENTOS do Drive, avalia cada unidade em todos os pavimentos, classifica (Terraço + Tipo + Capacidade) e agrupa em tipologias. Reusa a logica do projeto antigo `mapeamento-completo-de-mobilirio--unidade-spot`. Fase 2 (depois) = orcamento preliminar do decor puxando do catalogo (Google Sheets).

2026-05-26 --- Saida TEM que ser tabela EDITAVEL (xlsx / Google Sheet), porque a Raquel altera a coluna Capacidade depois que o layout final fica pronto.

2026-05-26 --- Agrupamento de tipologias: unidades com o MESMO layout/desenho + Terraco + Tipo + Capacidade sao a mesma tipologia, MESMO que o m2 difira por pouco (variacao pequena tolerada). Diferenca grande de m2 (layout distinto) separa. A tabela tem 2 colunas de area: ÁREA ÚTIL (m²) e ÁREA DA UNIDADE (m², privativa total). Casos de fronteira -> sinalizar no resumo.

2026-05-26 --- Coluna Capacidade = PREVISAO (nao definitiva). Deduzida SEMPRE pela area INTERNA da unidade (privativa coberta) via Matriz: cama auxiliar ao lado da queen -> cap 3 e 5; sofa-cama aberto = leito -> cap 4 e 5. NUNCA contar area de sacada/varanda/terraco pra capacidade. NUNCA confiar na coluna CAPACIDADE do ANALISE.xlsx (veio errada no Natal: 408 estava 5, o certo e 3). Unidades com mesma area interna = mesma capacidade, com ou sem sacada. A tabela traz aviso de que capacidade e previsao ate o layout final confirmar.

### Mapa do Drive (validado 2026-05-26)
Caminho ate o anteprojeto de qualquer Spot:
`[Spot] / 02 - Projetos / 05 - Projeto Arquitetonico / 03 - Anteprojeto / [ultima versao LANCAMENTOS] / LANCAMENTO_AP_<nome>_V0X.pdf`
- Pasta raiz dos projetos: https://drive.google.com/drive/folders/1D9y8aKfkGGE13WbGMlw07G8Euu0Pg7fF
- Na pasta da versao LANCAMENTOS costuma ter tambem `ANALISE_LANCAMENTO_..._V0X.xlsx` (dados estruturados, fonte secundaria mais confiavel que o PDF de 33 MB).
- Validacao Natal Spot: 5 tipologias / 96 unidades (bate com o CSV do projeto antigo).

### Destino da tabela gerada no Drive (confirmado 2026-05-26)
O Google Sheet da tabela e criado DENTRO do proprio Spot, em:
`05 - Projeto Arquitetonico / 10 - Projeto de Interiores / 02 - Imagens`.
- Exemplo Natal `02 - Imagens`: https://drive.google.com/drive/folders/1Afu8ZGleIT7EdiaYAISInqApi0BSpEjt
- Nunca sobrescrever o que ja existe la.

### Dashboard (branch feat/dashboard-padrao-spot)
Site estatico em `dashboard/`, identidade Seazone (Helvetica, azul #0054FC, navy #000C3C, coral #F06054). Aba "Logica & Regras" pronta. Dev server: `python -m http.server 5500 --directory hackathon-investimentos/dashboard` (em .claude/launch.json na raiz do workspace).
