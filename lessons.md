# lessons.md --- hackathon-investimentos

Erros que ja aconteceram neste projeto. NAO repetir.
Formato: `YYYY-MM-DD --- o que aconteceu -> o que evitar`

---

2026-05-26 --- abri a tipologia pela pasta "V05 - COMPATIBILIZADO INTERIORES" -> SEMPRE usar a ultima versao de **LANÇAMENTOS** (ex.: "V04- LANÇAMENTOS - 23/10"), NUNCA a versao "COMPATIBILIZADO INTERIORES". A skill deve filtrar pastas/arquivos por "LANÇAMENTO(S)" e pegar a mais recente entre essas, ignorando compatibilizado de interiores. Numero de versao maior NAO significa que e a correta.

2026-05-26 --- confiei na coluna CAPACIDADE do ANALISE.xlsx e marquei a unidade 408 como cap 5 (o arquivo trazia 5, mas o certo e cap 3). -> A capacidade NUNCA vem do ANALISE; ela e SEMPRE deduzida pela area INTERNA da unidade (privativa coberta) seguindo a Matriz de Capacidade. NAO contar a area de sacada/varanda/terraco pra capacidade (so conta a area interna). O ANALISE serve so pras areas; a capacidade dele e nao-confiavel.

2026-05-26 --- abreviei os numeros das unidades em faixas (101-107) ao mostrar a tabela. -> A Raquel quer SEMPRE todos os numeros listados um a um, sem abreviar, tanto no chat quanto na planilha.

2026-05-26 --- criei a skill e o dashboard em branches separadas (feat/tabela-tipologias e feat/dashboard-padrao-spot) partindo de master -> os 4 arquivos de base ficaram fragmentados entre branches (memory/lessons so na branch da skill). Pra projeto solo pequeno, manter tudo numa branch (ou mergear cedo) evita ter que reconciliar os arquivos de base depois.
