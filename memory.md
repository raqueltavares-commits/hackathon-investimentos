# memory.md --- hackathon-investimentos

Decisoes arquiteturais, estado atual, links uteis.
Eu anexo automaticamente quando voce decidir algo ("vamos com X").

---

## >>> ESTADO ATUAL (2026-05-27, noite) — leia isto primeiro

**FASE 2 ENTREGUE + memorial estruturado.** Skill `orcamento-decor` construida, instalada, testada. Aba "Orcamento" do dashboard no ar. Suite: **83 passed** (`python -m pytest tests/ -q`).

**MEMORIAL ESTRUTURADO (feito 2026-05-27 noite):** a skill gera SOZINHA o memorial no formato oficial da Raquel (modelo `1-S14JTOVV689UNJAW5lyuv5gDsPOAQq_fG6XEDatj6E`): 12 colunas (ITEM/TIPO, AMBIENTE, IMAGEM, ITEM, FICHA TECNICA+valor, FORNECEDOR, QUANT., REFERENCIA, VALOR UNITARIO, VALOR TOTAL), 4 linhas por item (Largura/Altura/Profundidade/Acabamento), categoria/ambiente "mescladas", TOTAL por categoria, servicos como itens (INSUMOS), Taxa Decor + Taxa Adm, total headline = SEM jacuzzi ("com jacuzzi" so aparece quando ha jacuzzi). Acabamento por estilo (paleta embutida em `acabamentos.py`; Biofilico calibrado do exemplo). Scripts novos: `acabamentos.py`, `servicos.py`, `gerar_xlsx.py` (.xlsx multi-aba: Resumo + 1 aba/tipologia). `montar_orcamento.py` reescrito (`serializar_estruturado` + `total_com_jacuzzi`). Spec/plano: `docs/superpowers/specs/2026-05-27-memorial-estruturado-design.md` + `docs/superpowers/plans/2026-05-27-memorial-estruturado.md`.

**BONITO testado (orcamento):** rodei pras 6 tipologias, estilo Biofilico, precos de referencia. Dashboard (aba Orcamento) mostra Natal + Bonito.

### >>> RETOMAR AQUI (proxima sessao) — subir o memorial do Bonito no Drive
A Raquel JA RECONECTOU o conector do Drive como raquel.tavares (confirmar o owner no 1o upload). Nesta sessao anterior as tools do Drive (composio) tinham caido; na nova devem estar OK (`/mcp` se nao).
Passos:
1. Regenerar o xlsx (tmp/ e apagado ao fechar a sessao):
   ```
   printf '%s' '[{"tipologia":"A","terraco":"Garden","tipo":"Padrão","capacidade":2},{"tipologia":"B","terraco":"Garden","tipo":"Padrão","capacidade":4},{"tipologia":"C","terraco":"Garden","tipo":"Padrão","capacidade":4},{"tipologia":"D","terraco":"Sem sacada","tipo":"Padrão","capacidade":2},{"tipologia":"E","terraco":"Sem sacada","tipo":"Padrão","capacidade":2},{"tipologia":"F","terraco":"Sem sacada","tipo":"Padrão","capacidade":2}]' > tmp/bonito_tips.json
   python skills/orcamento-decor/scripts/montar_orcamento.py --tipologias tmp/bonito_tips.json --estilo biofilico --spot "Bonito Spot" > tmp/memoriais_bonito.json
   python skills/orcamento-decor/scripts/gerar_xlsx.py --memoriais tmp/memoriais_bonito.json --spot "Bonito Spot" --saida tmp/Orcamento_Decor_Bonito.xlsx
   ```
2. Subir como UM Google Sheet (base64 do xlsx, conversao) na pasta `03 - Memorial descritivo` = `1n8j1M74BfZuQKva7UiqKIwxdc-JydbB5`. Confirmar owner = raquel.tavares.
3. orcamentos.js: consolidado_url + memorial_url (todas as tipologias) = link do Sheet novo; rodar gerar_dashboard_js.py (ver SKILL.md passo 7). Commit.
4. Apagar os 4 Sheets ERRADOS na `02 - Imagens` (owner rachel.souto, sem delete por MCP -> Raquel manda pra lixeira): resumo `1jVKKo4wnauDk4-aTd3njIY8m8dsAnSBvWiUp6NMdMrw`, A `1dA-TxfWsRGINpyxSuPFImmGnMhnmbR7l7U9z0CbTM3c`, B/C `1e3_4GtP3r6k0QFfI4U0zhOHjTicysq0WZVuooNI9Ww8`, D/E/F `1Rc0ncLXkYMCBWFjvVpXwFgugUr25e8XJWJaxnkbfQYA`.
5. Push pro GitHub (commits locais acumulados em master) quando a Raquel autorizar.
6. Recriar o cron de checkpoint (20 min) se quiser: CronCreate "13,33,53 * * * *" (session-only).

**Checkpoint cron:** a cada 20 min (min 13/33/53) faz flush dos arquivos-base. Session-only (job 23eb097e), morre ao fechar, expira em 7 dias.

**O que existe agora:**
- **Skill `orcamento-decor`** (`skills/orcamento-decor/`): gera memorial descritivo de decor por tipologia (pacote **Plus** fixo; estilo Clean/Biofilico/Industrial/Bruma). Scripts: `modelos.py` (dataclasses), `ler_catalogo.py` (CSV db002->produtos), `montar_orcamento.py` (itens por cap/terraco/PCD + calculos + CSV), `gerar_dashboard_js.py` (upsert do spot em orcamentos.js). Instalada em `~/Claude/.claude/skills/orcamento-decor/`.
- **Aba Orcamento no dashboard**: `dashboard/data/orcamentos.js` (`window.ORCAMENTOS`, arquivo SEPARADO de tipologias.js) + painel `#panel-orcamento` + IIFE de render em app.js. Mostra custo por tipologia + chip de estilo + botoes Drive (consolidado + memorial por tipologia). Natal e Bonito ja na vitrine.
- **Bonito CORRIGIDO** no tipologias.js/dashboard: agora **6 tipologias / 53 un** (era rascunho de 4), batendo com a tabela autoritativa da Raquel (Sheet `1L5EZXvCum72iN819CcHClLYuSDYBrloXsBy_32_DUNE`). 104/105 = Garden **Padrao** cap4 (NAO PCD); Sem sacada separada em D/E/F por layout de esquina; nota "somente 113 com jacuzzi".

**Decisoes Fase 2:**
- Dados do orcamento embutidos em `orcamentos.js` (hibrido: resumo na pagina + link pro Drive). Custo = numero puro; pagina formata em R$.
- Memorial descritivo no Drive vai na pasta **`03 - Memorial descritivo`** (`1n8j1M74BfZuQKva7UiqKIwxdc-JydbB5`), dentro de `10 - Projeto de Interiores` — NAO na `02 - Imagens` (la vai so a tabela de tipologias).
- Formato do memorial: **UM unico Google Sheet com uma ABA por tipologia** (+ aba Resumo). Multi-aba via upload de `.xlsx` (openpyxl) com conversao pra Sheet (o CSV so faz 1 aba).
- Scripts forcam `sys.stdout.reconfigure(encoding=utf-8)` — Windows escreve cp1252 em stdout redirecionado e corrompia acentos no JSON/Sheet.
- Regra "Garden=jacuzzi" NAO e universal: no Bonito so a unidade 113 tem jacuzzi. Tratar jacuzzi como excecao por projeto (a skill ainda adiciona por padrao -> revisar).

**Drive autenticado como raquel.tavares** — conector reconectado 2026-05-27 noite. Owner dos novos arquivos = raquel.tavares. Composio as vezes para de responder mesmo com status Connected — fechar/abrir aba MCP resolve.

**PENDENCIAS (proxima retomada):**
1. Upload do xlsx multi-aba do Bonito no Drive (`03 - Memorial descritivo` = `1n8j1M74BfZuQKva7UiqKIwxdc-JydbB5`). Xlsx local gerado (`tmp/Orcamento_Decor_Bonito.xlsx`, 7 abas). Desafio: xlsx nao chega no sandbox Composio via base64. Metodo confirmado: chunks via bash->workbench->`GOOGLEDRIVE_RESUMABLE_UPLOAD`.
2. Atualizar orcamentos.js: `consolidado_url` = link do xlsx no Drive (mesmo arquivo, sem `memorial_url` individual — e UM arquivo).
3. Apagar os 7 Sheets ERRADOS criados na `03 - Memorial descritivo` (separados em vez de multi-aba): `16xSVLo7rrrr9qblGb7tCTlW2u3ZHQ1WBphHLSAIPTZI` (Resumo), `15kvKMBc_7lwJ02id_PGYLVjuh0nWGyAQAlo2qum3tU0` (A), `1rVGoPLb4-2NJO1Di4hs9UL6ly1kM5adN7Odu7cQEqXg` (B), `1YShLfXgTCoX7U7PM44-kiyxkJHZN-k6qbINnqti15MA` (C), `1nvv6_xn08aQB2ADzmCAUb1JPdGv9XgIQfitHiCtmMy4` (D), `1d1DTxxwgX5Db_bBQRCaqyxP6ScUxkQ3k8Qe0L7MVHP4` (E), `1lGl6b2Ugw23Z1j_cFLTCBgvfq9mMT5JBCtAws4NP0JY` (F). Sem delete por MCP -> Raquel manda pra lixeira.
4. Dashboard: tirar `em_construcao:true` do Bonito apos upload.
5. Push pro GitHub (commit docs/arquivos-base feito `9e7b53c`).

**Catalogo de precos:** o export CSV do catalogo (`1Q_AiMW7CICEMrpQR3jTchx6xknSEiCQxEZbpm97Yx_o`) traz so a 1a aba (Controle Financeiro Decor), NAO a `db002_produtos` (gid 1263042396) — o MCP nao mira gid. Por isso o Bonito saiu com **precos de referencia Plus 2026** (defaults de `_ITENS_PLUS`), a revisar. Pra precos reais: Raquel exporta a aba db002 como CSV.

---

## COMO RETOMAR AMANHA (terminal) — leia isto primeiro

**Pasta do projeto:** `C:\Users\Seazone\Claude\seazone\hackathon-investimentos`
**Git:** tudo em `master`, working tree limpo (branches feat/* ja mergeadas). `git log --oneline -10` mostra o historico.

**Dependencias (ja instaladas globalmente nesta maquina, persistem):**
- Python 3.12 (usar `python`, NAO `python3`). Pacotes: `pytest`, `openpyxl`, `pymupdf` (import `fitz`), `pillow`, `ezdxf`.
- **ODA File Converter** (DWG->DXF) via winget em `C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe`.
- Se faltar algo: `python -m pip install pytest openpyxl pymupdf pillow ezdxf`.

**Rodar os testes da skill:**
```
cd C:\Users\Seazone\Claude\seazone\hackathon-investimentos
python -m pytest tests/ -q        # esperado: 71 passed (Fase 1 + Fase 2)
```

**Rodar o helper da tabela (parte deterministica):**
```
python skills/tabela-tipologias/scripts/montar_tabela.py --total <N_UNIDADES> < unidades.json
# unidades.json = lista de {unidade,pavimento,terraco,tipo,capacidade,area_util,area_unidade}
```

**Abrir o dashboard:**
- Simples: abrir `dashboard/index.html` no navegador (funciona via file://).
- Com servidor: `python -m http.server 5500 --directory dashboard` e abrir http://localhost:5500
- (No Claude Code o preview usa `.claude/launch.json` -> server "dashboard-spot".)

**Ler DWG (fonte ideal + precisa):** ver `skills/tabela-tipologias/references/dwg-leitura.md`. Em runtime:
```python
import ezdxf; from ezdxf.addons import odafc
ezdxf.options.set("odafc-addon","win_exec_path", r"C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe")
doc = odafc.readfile("plano.dwg"); msp = doc.modelspace()   # esquadrias no layer A-GLAZ
```

**ONDE PARAMOS (2026-05-27, fim da sessao):** TUDO o que importa pro hackathon esta PRONTO e commitado em `master`:
- **Skill `tabela-tipologias` INSTALADA E FUNCIONANDO**: copiada pra `~/Claude/.claude/skills/tabela-tipologias/` (descobrivel globalmente; aparece na lista de skills). Testada ponta-a-ponta com o DWG real (separa esquinas de padrao). O repo do projeto e a fonte; a copia global e o que roda. Pra atualizar a instalada: recopiar SKILL.md/references/scripts pra a pasta global.
- **Leitura DWG**: ler_dwg.py reescrito com NEAREST-LABEL + normalizacao. Layers CONFIGURAVEIS (`label_layer`, `janela_layers`) + `listar_layers()` + CLI `--listar-layers`/`--label-layer`/`--janela-layers` (nomes de layer variam por projeto; defaults AIA/Revit NAO universais). A janela e UM sinal, nao universal — TODO pavimento pode diferir e abrir por porta; avaliar piso a piso. 27 testes passando.
- **Dashboard "Padrao Spot"** completo: aba Logica & Regras; aba Tipologias por Spot com bloco "De onde vem a precisao" (3 fontes PDF/Analise/DWG), tags verde/vermelho por spot (campo `fontes`), e o bloco "Gerar uma tabela nova" (resumo + 6 passos + comando copiavel).

**[DESATUALIZADO — ver bloco "SESSAO 2026-05-27 (tarde)" mais abaixo pro estado atual.]** Este bloco "ONDE PARAMOS" e da manha de 27/05. Desde entao: a skill JA foi testada num spot novo (Novo Campeche II, deu certo apos correcao da Raquel) e o projeto JA esta no GitHub publico.
**PROXIMO PASSO:** gravar video + transcricao + montar a pasta de entrega no Drive + enviar formulario do hackathon.
**DWGs baixados do Drive (pasta DWG do anteprojeto LANCAMENTOS Bonito):** tmp/bonito_terreo.dwg, tmp/bonito_tipo.dwg, tmp/bonito_rooftop.dwg. IDs no Drive: terreo 1ItWYy5q27tn39AtlXEK5r-jrPvwVFJkj, tipo 1OaldjeRa2X3f9IMf6AYpT1aDlLuDY_Gh, rooftop 1TjKvyDJEpH7oqSkv_J5VUuSbvmkYtc0k. Pasta DWG: 1knRQbcvUhvBimcZ-iiA08pi9-t1RjXtY. Download via composio retorna base64 > limite -> salva em tool-results .txt -> decodificar com base64. (tmp/ NAO versionar.)

**Pendencias menores:** Raquel dividir o agrupamento por layout do Bonito (rascunho); conectar Google Sheets (hoje so Drive).

**Checkpoint de aprendizados (cron):** a cada 30 min (min 7 e 37) faz flush dos arquivos base — CRON E SESSION-ONLY, morre ao fechar. Amanha, recriar se quiser (CronCreate, "7,37 * * * *", durable: true).

**Links das tabelas geradas:** Natal https://docs.google.com/spreadsheets/d/1Ffn359MFIgtERfKWiR-UfMFJVUOWDotSaSQLm8PxXQ8/edit · Bonito (rascunho) https://docs.google.com/spreadsheets/d/1iq7gvHOmMwSrw0HwK8iT6Ssa0MRFyKIeAobpdZ7txNM/edit · Novo Campeche II (corrigida, 12 tip/49 un) https://docs.google.com/spreadsheets/d/17YkdQ69TQgDU4Mo35dTpQU38-0bbnd_Q0OJmNwNEKuw/edit (o antigo 16nq4ty... de 8 tip foi SUPERADO — Raquel descarta)

---

## TESTAR UM SPOT NOVO (runbook — o que a Raquel vai fazer na conversa nova)
Objetivo: rodar a skill `tabela-tipologias` num empreendimento novo de ponta a ponta e
conferir se funciona, seguindo os passos do dashboard, antes de gravar o video.

1. **Pedir ao Claude:** "monta a tabela de tipologias do <NOME DO SPOT>" (ou `/tabela-tipologias`).
2. O Claude segue o SKILL.md (`~/Claude/.claude/skills/tabela-tipologias/SKILL.md`):
   a. Acha o anteprojeto **LANÇAMENTOS** do Spot no Drive (raiz dos projetos:
      `1D9y8aKfkGGE13WbGMlw07G8Euu0Pg7fF` → Spot → `02 - Projetos / 05 - Projeto
      Arquitetonico / 03 - Anteprojeto / [versao LANÇAMENTOS]`). NUNCA COMPATIBILIZADO INTERIORES.
   b. Le o PDF (metragem, nº/total de unidades). Se houver subpasta `DWG`, baixa os DWGs
      dos pavimentos (composio: search_files por parentId → download_file_content → base64
      salvo em tool-results .txt → decodificar pra tmp/).
   c. **Inspeciona os layers** de cada DWG (`unidades_dwg.py --dwg X --listar-layers`),
      identifica o layer dos numeros e o(s) de esquadria (variam por projeto!), e conta
      (`--label-layer ... --janela-layers ...` se diferirem dos defaults A-AREA-IDEN/A-GLAZ).
   d. Classifica (terraco, tipo, capacidade-previsao pela area interna), agrupa, valida o total.
   e. Cria o Google Sheet editavel no Drive do Spot (`05 - Projeto Arquitetonico /
      10 - Projeto de Interiores / 02 - Imagens`), sem sobrescrever, e devolve o link.
   f. (So neste projeto) alimenta `dashboard/data/tipologias.js` com o campo `fontes`.
3. **Conferir:** total bate com o PDF? unidades de esquina/PCD/garden separadas? capacidade
   coerente? Lembrar: capacidade e PREVISAO; agrupamento por DWG/planta e ponto de partida,
   conferir na planta. Avaliar TODO pavimento (nenhum e caso especial).

## REGRAS DO HACKATHON (https://hackathon-szi.seazone.dev/#regras — lido 2026-05-27)
- **Prazo de entrega: 27/05 ate 18h** (apos isso nada e aceito). Avaliacao assincrona dia 28+.
- **Individual**, **usar Claude Code** (ferramenta oficial), **dados reais da SZI**.
- **Trilha: Decor** (a da Raquel).
- **ENTREGAVEIS** (formulario no site): (1) **pasta no Drive** compartilhada com avaliadores
  contendo `claude.md`, `lessons.md`, `memory.md` + o codigo do projeto; (2) **video** curto
  (problema, solucao, como usar); (3) **transcricao** do video. Enviar pelo formulario com
  e-mail @seazone.com.br + trilha.
- **Criterios:** resolve problema SZI real 30% · qualidade da IA 20% · qualidade dos arquivos
  de contexto (claude/lessons/memory) 20% · skill funcional pro dia a dia 15% · clareza da demo 15%.
- **GAPS de entrega (atualizado 2026-05-27 tarde):** GitHub FEITO (repo publico
  https://github.com/raqueltavares-commits/hackathon-investimentos). Ainda abertos:
  montar a pasta de entrega no Drive (com claude.md/lessons.md/memory.md + codigo);
  gravar video; transcricao; enviar formulario. (Confirmar com a organizacao se
  `claude.md/lessons.md/memory.md` sao pastas ou so os arquivos.)

## COMMITS DA SESSAO 2026-05-27 (todos em master, SEM push)
- `e519cb9` dashboard: fonte DWG na precisao + selos PDF/Analise/DWG por spot
- `57c4b68` docs: PLANO.md atualizado + plano DWG
- `deefe13` docs: aprendizados (puxar DWG do Drive, estado dashboard)
- `ad4d7bd` feat(dwg): reescreve ler_dwg com nearest-label, validado em DWG real
- `86d4e74` docs(skill): SKILL.md leitura DWG automatica, paths skill-relative, campo fontes
- `7ad2933` feat(dashboard): bloco "Gerar uma tabela nova" (resumo + passo a passo)
- `cd79aaa` fix(dwg): layers configuraveis + janela como sinal nao-universal

---

## [CONCLUIDO] FASE 2: Orcamento preliminar do decor
Fase 1 (tabela-tipologias + dashboard) e Fase 2 (skill `orcamento-decor` + aba Orcamento)
estao PRONTAS. Estado atual e pendencias no bloco ">>> ESTADO ATUAL" no topo deste arquivo.
Spec/plano da Fase 2: `docs/superpowers/specs/2026-05-27-orcamento-decor-design.md` e
`docs/superpowers/plans/2026-05-27-orcamento-decor.md`. Aba Orcamento:
`docs/superpowers/specs/2026-05-27-aba-orcamento-dashboard-design.md`.

## SESSAO 2026-05-27 (tarde) — Novo Campeche II gerado + repo no GitHub
- **3o Spot gerado: Novo Campeche Spot II** (cod 6320, anteprojeto V04 LANCAMENTO `1AKpL6OBpWhCZ31PPtyyIAie_EIn5NI0m`). Cruzei PDF + comparativo de areas + DWG R03 (ODA). Minha 1a versao deu 8 tipologias; a tabela da Raquel (verdade) tem **12 tip / 49 un** — corrigi tudo (Sheet 17Ykd..., dashboard, CSV). Validacao de referencia NOVA: **Novo Campeche II = 12 tipologias / 49 unidades**.
- **5 erros meus (corrigidos, ver lessons.md 2026-05-27)** que viraram calibracao da skill (`classificacao-spot.md`): (1) terraco pelo PAVIMENTO — terreo=Garden por menor que seja, nunca Sacada; (2) cap5 a partir de ~22m2 (nao 23); (3) PCD rende -1 nivel (PCD ~20m2=cap3); (4)+(5) o helper FUNDE demais — planta vence area, separar conferindo planta; sinal de layout no render NAO se descarta. Raquel confirmou: criterio de agrupamento e SO layout, sem fator oculto.
- **Projeto agora no GitHub (PUBLICO):** https://github.com/raqueltavares-commits/hackathon-investimentos (conta `raqueltavares-commits`, branch `master` com upstream `origin/master`). Push direto em master OK (master = branch de trabalho; nao ha `main` remoto). Resolve o GAP "so existe em git local".
- **Skill instalada vs repo:** editei AMBOS (instalada `~/Claude/.claude/skills/...` e a fonte no repo `skills/...`) e mantive em sincronia. Commit desta sessao: `ffe26d9`.

2026-05-26 --- Fase 1 do projeto = skill `tabela-tipologias`: puxa o anteprojeto LANÇAMENTOS do Drive, avalia cada unidade em todos os pavimentos, classifica (Terraço + Tipo + Capacidade) e agrupa em tipologias. Reusa a logica do projeto antigo `mapeamento-completo-de-mobilirio--unidade-spot`. Fase 2 (depois) = orcamento preliminar do decor puxando do catalogo (Google Sheets).

2026-05-26 --- DECISAO de arquitetura (geracao da tabela): a planilha ANALISE/ÁREA UNDS e feita por OUTRA equipe (analise de arquitetura) e NAO e confiavel pros proximos lancamentos — a Raquel nem a produz. Logo: NAO depender dela; o **PDF do anteprojeto e a fonte principal** (sempre existe). Ler PDF precisa da inteligencia do Claude, entao a geracao FICA com o Claude (skill), NAO vira ferramenta so-navegador. Dashboard = VITRINE (todo mundo ve as tabelas + link do Drive). Self-service no navegador (backend + API Claude lendo PDF) = evolucao futura (opcao 3), fora do escopo agora. Ordem de fonte da skill: 1) planilha ÁREA UNDS se existir (exato); 2) quadro de areas em texto no PDF (exato); 3) leitura visual das plantas (estimativa, marcar pra conferir).

2026-05-26 --- Saida TEM que ser tabela EDITAVEL (xlsx / Google Sheet), porque a Raquel altera a coluna Capacidade depois que o layout final fica pronto.

2026-05-26 --- Agrupamento de tipologias: unidades com o MESMO layout/desenho + Terraco + Tipo + Capacidade sao a mesma tipologia, MESMO que o m2 difira por pouco (variacao pequena tolerada). Diferenca grande de m2 (layout distinto) separa. A tabela tem 2 colunas de area: ÁREA ÚTIL (m²) e ÁREA DA UNIDADE (m², privativa total). Casos de fronteira -> sinalizar no resumo.

2026-05-26 --- Coluna Capacidade = PREVISAO (nao definitiva). Deduzida SEMPRE pela area INTERNA da unidade (privativa coberta) via Matriz: cama auxiliar ao lado da queen -> cap 3 e 5; sofa-cama aberto = leito -> cap 4 e 5. NUNCA contar area de sacada/varanda/terraco pra capacidade. NUNCA confiar na coluna CAPACIDADE do ANALISE.xlsx (veio errada no Natal: 408 estava 5, o certo e 3). Unidades com mesma area interna = mesma capacidade, com ou sem sacada. A tabela traz aviso de que capacidade e previsao ate o layout final confirmar.

### Mapa do Drive (validado 2026-05-26)
Caminho ate o anteprojeto de qualquer Spot:
`[Spot] / 02 - Projetos / 05 - Projeto Arquitetonico / 03 - Anteprojeto / [ultima versao LANCAMENTOS] / LANCAMENTO_AP_<nome>_V0X.pdf`
- Pasta raiz dos projetos: https://drive.google.com/drive/folders/1D9y8aKfkGGE13WbGMlw07G8Euu0Pg7fF
- Na pasta da versao LANCAMENTOS costuma ter tambem `ANALISE_LANCAMENTO_..._V0X.xlsx` (dados estruturados, fonte secundaria mais confiavel que o PDF de 33 MB).
- Validacao Natal Spot: 5 tipologias / 96 unidades (bate com o CSV do projeto antigo).
- Bonito Spot: a FONTE DE VERDADE e o PROJETO (anteprojeto V03 PDF) = 53 unidades (401-408, NAO existe 409). Eixo terraco = GARDEN (terreo) / SEM SACADA (demais; rooftop nao tem terraco privativo, a cobertura/piscina e comum). Unidades maiores (~19-23m2) = cap 4. REGRA: sempre seguir o projeto, nao tratar tabela manual como verdade.
  - **[ATUALIZADO 2026-05-27 noite]** A tabela AUTORITATIVA FINAL da Raquel (Sheet `1L5EZXvCum72iN819CcHClLYuSDYBrloXsBy_32_DUNE`) = **6 tipologias / 53 un**: Garden A(101,102,103,107-113,cap2,"so 113 c/ jacuzzi")+B(104,105,cap4)+C(106,cap4) TODAS **PADRAO**; Sem sacada D(30)+E(6 esquinas)+F(4 esquinas) cap2. Ou seja: **104/105 sao PADRAO, NAO PCD** (a decisao final reverteu o "W.C PCD"), e nenhuma unidade tem 409. O tipologias.js/dashboard ja foi corrigido pra essa versao. NAO marcar PCD por conta propria; PADRAO e o default. Detalhe em lessons.md (2026-05-27).

### FONTE IDEAL da tabela = DWG + PDF (decisao Raquel 2026-05-26)
Cruzar os dois: do **PDF** vem a metragem por unidade, o nº/total de unidades e os textos
relevantes; do **DWG** vem a geometria pro agrupamento (esquadrias no layer A-GLAZ, layout,
banheiro, espelhamento). Nenhum sozinho basta — PDF dá numeros/texto, DWG dá agrupamento.

### DWG como fonte mais precisa (testado 2026-05-26)
Teste de viabilidade no DWG do Bonito (pavimento tipo): POSITIVO. O DWG (export Revit)
tem as esquadrias como blocos no layer `A-GLAZ` + tags em `A-GLAZ-IDEN` (marcas V14..V52),
areas, portas (`A-DOOR`), polígonos de área (`A-AREA-BNDY`) — layers padrão AIA. Dá pra
CONTAR esquadrias por unidade (o que a regra de agrupamento exige). Ferramenta instalada:
**ODA File Converter** (winget `ODA.ODAFileConverter`, em `C:\Program Files\ODA\ODAFileConverter 27.1.0\`)
+ **ezdxf** (lê DXF). Detalhes e abordagem em `skills/tabela-tipologias/references/dwg-leitura.md`.
Pendente: construir a leitura DWG->contagem de esquadrias->agrupamento na skill (associação
espacial janela↔unidade) e validar contra verdade conhecida.

### Integração Google (2026-05-26)
O toolkit **Google Sheets (composio) NÃO está conectado** na conta raquel.tavares@seazone.com.br — só o **Google Drive**. Pra criar a planilha, NÃO usar `GOOGLESHEETS_CREATE_*`; usar `GOOGLEDRIVE_CREATE_FILE_FROM_TEXT` com `mime_type=application/vnd.google-apps.spreadsheet` passando o CSV (o Drive converte em Sheet editável). Validar exportando de volta com `GOOGLEDRIVE_DOWNLOAD_FILE mime_type=text/csv`. (Se um dia conectarem o Sheets, dá pra formatar célula/nota.)
- Primeira tabela gerada (Natal): https://docs.google.com/spreadsheets/d/1Ffn359MFIgtERfKWiR-UfMFJVUOWDotSaSQLm8PxXQ8/edit

### Destino da tabela gerada no Drive (confirmado 2026-05-26)
O Google Sheet da tabela e criado DENTRO do proprio Spot, em:
`05 - Projeto Arquitetonico / 10 - Projeto de Interiores / 02 - Imagens`.
- Exemplo Natal `02 - Imagens`: https://drive.google.com/drive/folders/1Afu8ZGleIT7EdiaYAISInqApi0BSpEjt
- Nunca sobrescrever o que ja existe la.

### Dashboard (branch feat/dashboard-padrao-spot)
Site estatico em `dashboard/`, identidade Seazone (Helvetica, azul #0054FC, navy #000C3C, coral #F06054). Aba "Logica & Regras" pronta. Dev server: `python -m http.server 5500 --directory hackathon-investimentos/dashboard` (em .claude/launch.json na raiz do workspace).

## Estado atual / feitos (atualizado 2026-05-26)
TUDO consolidado em `master` (branches feat/* ja mergeadas).
- **Skill `tabela-tipologias`**: helper Python testado (13/13), referencias, SKILL.md. Le anteprojeto do Drive (planilha ÁREA UNDS quando existe, senao PDF), classifica, gera CSV + cria Google Sheet em `Projeto de Interiores / 02 - Imagens` + alimenta a vitrine (escreve `dashboard/data/tipologias.js` com `fonte`).
- **Capacidade (previsao) por metragem interna** (CALIBRADA 2026-05-27 no Novo Campeche II): <=17m2 cap2, ~18 cap3, ~19-21 cap4 (sofa-cama), **>=~22 cap5** (antes era ~23, alto demais). **PCD rende -1 nivel** (PCD ~20m2 = cap3, nao cap4). Em `references/classificacao-spot.md`.
- **Dashboard "Padrao Spot"** (2 abas): "Logica & Regras" (revisada pela Raquel) + "Tipologias por Spot" (vitrine: busca, cards, ver tabela, abrir no Drive, comando pra gerar Spot novo). Bloco "De onde vem a precisao" = 3 FONTES (PDF da numeros / Analise confirma areas / DWG resolve agrupamento por desenho). Selos por spot = 3 tags PDF/Analise/DWG (verde tem, vermelho nao) via campo `fontes` em tipologias.js. Aviso: terreo/pavimentos/rooftop podem ter unidades diferentes; capacidade e previsao ate layout final. "Orcamento" = em breve. Dev server na 5500 (.claude/launch.json). Commits dashboard: e519cb9 (feature) + 57c4b68 (docs/PLANO). NOTA: o server de preview cacheia assets agressivamente — pra ver mudanca, hard refresh (Ctrl+Shift+R).
- **Spots gerados**: Natal (fonte=analise, 5 tip/96 un) e Bonito (fonte=pdf RASCUNHO, 4 tip/53 un — falta a Raquel dividir a tipologia A por layout). Ambos na vitrine + Sheet no Drive.
- **Checkpoint de aprendizados**: cron a cada 30 min (so nesta sessao) faz flush dos arquivos base.
- **Pendente**: Fase 2 (Orcamento do decor); Raquel editar agrupamento por layout do Bonito; hospedar o dashboard num link; (opcional) conectar Google Sheets pra formatar planilha.
### REGRA DE AGRUPAMENTO (definida pela Raquel 2026-05-26) — decide pela PLANTA
- ESPELHAMENTO (unidade idêntica, só espelhada) = MESMA tipologia.
- Mesmo desenho/posição de banheiro/nº de esquadrias, só muda um pouco o m² = MESMA tipologia.
- UMA ESQUADRIA A MAIS (ex.: janela de esquina) = OUTRA tipologia (geralmente a de esquina é maior).
A metragem é só pista; o que decide é desenho + nº de esquadrias, visto na planta.

- **Natal (RESOLVIDO)**: a tabela da Raquel mantem A=74 (5 tipologias / 96 un) — as x01 (17,29m²) FICAM no A. Minha geracao do Natal estava CORRETA (A=74). Eu tinha inferido errado que a x01 maior = +1 esquadria; metragem maior sozinha NAO significa esquadria extra. Tabela da Raquel (Natal): https://docs.google.com/spreadsheets/d/1Fe4FYtQByBtQRF2zgdJvt7gOqLqo6dNv7jwgOcVmHHs/edit — bate com a gerada (so difere a ordem das letras B/C e D/E).

### Leitura DWG (2026-05-27) — REESCRITA com nearest-label, validada no DWG real
ler_dwg.py reescrito: nearest-label de blocos A-GLAZ por numero de unidade + normalizacao pela contagem-base do piso. Validado nos 3 pisos do Bonito (tipo 12+4 esquina, rooftop 6+2, terreo ~0). 27 testes passando. Detalhes e contrato em `skills/tabela-tipologias/references/arquitetura-dwg.md`. (A 1a versao usava point-in-polygon e retornava {} no DWG real — ver lessons.md 2026-05-27.)
- **Layers configuraveis** (variam por projeto): `ler_dwg(..., label_layer=, janela_layers=)` + `listar_layers(dwg)` + CLI `--listar-layers`/`--label-layer`/`--janela-layers`. Defaults AIA/Revit NAO sao universais.
- **A janela e UM sinal, nao universal**: TODO pavimento pode ter unidades diferentes e pode abrir por porta -> avaliar pavimento a pavimento, nunca excluir nenhum (ver lessons.md 2026-05-27).

- **`ler_dwg.py`** — extrai esquadrias por unidade via ezdxf+ODA+shapely. Layers: A-AREA-BNDY (poligonos), A-AREA-IDEN (textos=unidade), A-GLAZ-IDEN (janelas). Point-in-polygon associa janela a unidade. Commit: 613a042.
- **`unidades_dwg.py`** — CLI: `python unidades_dwg.py --dwg caminho/arquivo.dwg` → JSON `{unidade: contagem}`. Commits: c83a73f, 203dd37.
- **`montar_tabela.py`** — integrado: `--dwg` ativa leitura de esquadrias, `agrupar(esquadrias_por_unidade=...)` separa tipologias com contagem diferente. Commits: 8f84b71, 36f7335.
- **`tests/fixtures/dxf_fixtures.py`** — DXF gerado na memoria (3 unidades, 2+2+3 esquadrias) pra testes sem arquivo real. Commit: 47f2b8e.
- **`skills/tabela-tipologias/references/arquitetura-dwg.md`** — doc interno com fluxo, limitacoes, validacao real.

**VALIDACAO REAL (Natal NAO tem DWG local — usar Bonito):**
```bash
python skills/tabela-tipologias/scripts/unidades_dwg.py --dwg caminho/bonito.dwg
```
Verificar: totais batem com PDF? unidades de esquina tem +1 esquadria?esperado: 4 tipologias (A=45, B=4, C=2, D=2) ou conforme configurado.

**Pendencias:**
- Validar com DWG real do Bonito (baixar do Drive)
- Fase 2 (Orcamento do decor)
- Hospedar dashboard num link
