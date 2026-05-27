# lessons.md --- hackathon-investimentos

Erros que ja aconteceram neste projeto. NAO repetir.
Formato: `YYYY-MM-DD --- o que aconteceu -> o que evitar`

---

2026-05-26 --- abri a tipologia pela pasta "V05 - COMPATIBILIZADO INTERIORES" -> SEMPRE usar a ultima versao de **LANÇAMENTOS** (ex.: "V04- LANÇAMENTOS - 23/10"), NUNCA a versao "COMPATIBILIZADO INTERIORES". A skill deve filtrar pastas/arquivos por "LANÇAMENTO(S)" e pegar a mais recente entre essas, ignorando compatibilizado de interiores. Numero de versao maior NAO significa que e a correta.

2026-05-26 --- confiei na coluna CAPACIDADE do ANALISE.xlsx e marquei a unidade 408 como cap 5 (o arquivo trazia 5, mas o certo e cap 3). -> A capacidade NUNCA vem do ANALISE; ela e SEMPRE deduzida pela area INTERNA da unidade (privativa coberta) seguindo a Matriz de Capacidade. NAO contar a area de sacada/varanda/terraco pra capacidade (so conta a area interna). O ANALISE serve so pras areas; a capacidade dele e nao-confiavel.

2026-05-26 --- abreviei os numeros das unidades em faixas (101-107) ao mostrar a tabela. -> A Raquel quer SEMPRE todos os numeros listados um a um, sem abreviar, tanto no chat quanto na planilha.

2026-05-26 --- criei a skill e o dashboard em branches separadas (feat/tabela-tipologias e feat/dashboard-padrao-spot) partindo de master -> os 4 arquivos de base ficaram fragmentados entre branches (memory/lessons so na branch da skill). Pra projeto solo pequeno, manter tudo numa branch (ou mergear cedo) evita ter que reconciliar os arquivos de base depois.

2026-05-26 --- Bonito Spot, comparacao texto-PDF vs leitura visual vs tabela manual. FONTE DE VERDADE = o PROJETO (anteprojeto PDF), NUNCA a tabela manual (a da Raquel tinha 2 erros: inventou unidade 409 -> total 54 em vez de 53; e marcou 104/105 como PADRAO sendo PCD). Meus erros lendo SO o texto do PDF (corrigidos depois enxergando as plantas): (1) Terraço: terreo e GARDEN (eu pus "Sem") e o rooftop deste projeto e SEM SACADA, nao terraço — "rooftop=terraço" NAO e universal: so e terraço se a unidade tiver terraço privativo; aqui a cobertura (piscina) e area comum. So a planta mostra isso. (2) Capacidade: unidades maiores (~19-23m²) sao cap 4 (cabe sofa-cama), nao cap 2 — capacidade e PREVISAO pela metragem (maior area -> mais leito), sempre com disclaimer. (3) Agrupamento por LAYOUT/posicao (esquina, espelhamento: 203/204, 212/213) so se ve na planta; area+terraço+capacidade nao captura — essa parte fica pro humano editar. O que eu ACERTEI e a tabela manual errou: total 53 e PCD nas 104/105 (W.C PCD na planta -> PODE marcar PCD). CONCLUSAO: caminho-PDF = leitura VISUAL das plantas (render pagina a pagina) + seguir sempre o projeto + entregar como rascunho pra Raquel editar o agrupamento por layout.

2026-05-26 --- gerei o Natal SO pela planilha ÁREA UNDS, sem olhar a planta, e agrupei por area+terraço+capacidade. ERRO de metodo: a planilha da areas/unidades EXATAS mas NAO da a identidade de LAYOUT — duas unidades com metragem parecida podem ser tipologias completamente diferentes (layout/posicao/orientacao). -> O agrupamento em tipologias SEMPRE exige olhar a PLANTA, mesmo quando existe a planilha de analise. Modelo correto: planilha (ou quadro do PDF) = areas/terraço exatos; PLANTA = agrupamento por layout. Usar os DOIS. O selo "gerado com analise" NAO garante agrupamento certo se a planta nao foi conferida. (Natal foi area-only -> precisa reconferir o agrupamento na planta.)
