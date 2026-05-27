# lessons.md --- hackathon-investimentos

Erros que ja aconteceram neste projeto. NAO repetir.
Formato: `YYYY-MM-DD --- o que aconteceu -> o que evitar`

---

2026-05-26 --- abri a tipologia pela pasta "V05 - COMPATIBILIZADO INTERIORES" -> SEMPRE usar a ultima versao de **LANÇAMENTOS** (ex.: "V04- LANÇAMENTOS - 23/10"), NUNCA a versao "COMPATIBILIZADO INTERIORES". A skill deve filtrar pastas/arquivos por "LANÇAMENTO(S)" e pegar a mais recente entre essas, ignorando compatibilizado de interiores. Numero de versao maior NAO significa que e a correta.

2026-05-26 --- confiei na coluna CAPACIDADE do ANALISE.xlsx e marquei a unidade 408 como cap 5 (o arquivo trazia 5, mas o certo e cap 3). -> A capacidade NUNCA vem do ANALISE; ela e SEMPRE deduzida pela area INTERNA da unidade (privativa coberta) seguindo a Matriz de Capacidade. NAO contar a area de sacada/varanda/terraco pra capacidade (so conta a area interna). O ANALISE serve so pras areas; a capacidade dele e nao-confiavel.

2026-05-26 --- abreviei os numeros das unidades em faixas (101-107) ao mostrar a tabela. -> A Raquel quer SEMPRE todos os numeros listados um a um, sem abreviar, tanto no chat quanto na planilha.

2026-05-26 --- criei a skill e o dashboard em branches separadas (feat/tabela-tipologias e feat/dashboard-padrao-spot) partindo de master -> os 4 arquivos de base ficaram fragmentados entre branches (memory/lessons so na branch da skill). Pra projeto solo pequeno, manter tudo numa branch (ou mergear cedo) evita ter que reconciliar os arquivos de base depois.

2026-05-26 --- gerei a tabela do Bonito Spot lendo só o TEXTO do PDF (áreas + quadro) e errei quase tudo vs a tabela real da Raquel. -> Pra Spot SEM planilha estruturada, ler o texto do PDF NÃO basta. A classificação real exige ENXERGAR AS PLANTAS (renderizar as páginas como imagem e olhar). Erros concretos cometidos: (1) Total 53 em vez de 54 — não vi a unidade 409; o "Total" do PDF tb estava desatualizado, NÃO confiar nele cegamente. (2) Terraço: térreo é GARDEN (não "Sem") e o rooftop deste projeto é SEM SACADA (não terraço) — "rooftop=terraço" NÃO é universal, depende de ter terraço privativo, e isso só se vê na planta. (3) Capacidade: unidades maiores (~19-23m²) são cap 4 (cabe sofá-cama), não cap 2 — minha regra "PCD=acessibilidade / ≤23m²=cap2" estava errada; capacidade = o que REALMENTE cabe de leito, visto na planta. (4) Tipo: não inferir PCD pela área (104/105 de 22,91 eram PADRÃO, não PCD). (5) Agrupamento: tipologias distinguem LAYOUT/posição (esquina, espelhamento: 203/204, 212/213 viram tipologias proprias) — area+terraço+capacidade NÃO captura isso; só a planta. Detalhes como "113 tem jacuzzi" idem. CONCLUSAO: o caminho-PDF tem que ser leitura VISUAL das plantas pagina a pagina, com revisao da Raquel; texto puro gera tabela confiante e errada.
