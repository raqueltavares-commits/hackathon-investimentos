# Skill `tabela-tipologias` — Design

**Data:** 2026-05-26
**Autora:** Raquel Ângelo (Especialista em Interiores · Lançamentos · Seazone Investimentos)
**Contexto:** Hackathon SZI — IA First Investimentos. Trilha Decor.
**Fase:** 1 de 2 (Fase 2 = orçamento preliminar do decor puxando do catálogo).

---

## Problema

Hoje, para cada empreendimento Spot, a tabela de tipologias é montada à mão: abrir o anteprojeto, olhar cada unidade em cada pavimento, classificar e agrupar. É lento e repetitivo, e a Raquel faz isso a cada lançamento.

## Objetivo (uma linha)

Uma skill onde a Raquel pede *"monta a tabela de tipologias do `<Spot>`"* e o Claude puxa o anteprojeto do Drive, avalia cada unidade de todos os pavimentos, classifica e agrupa em tipologias, entregando uma planilha **editável** + resumo do que revisar.

## Não-objetivos (fora de escopo nesta fase)

- Orçamento, match com catálogo, preços (Fase 2).
- Gerar plantas/layouts ou alterar o anteprojeto.
- Definir capacidade definitiva — a skill entrega **previsão** (ver abaixo).

---

## Fluxo

### 1. Localizar o anteprojeto no Drive

A partir do nome do Spot, navegar pela convenção de pastas (validada em 2026-05-26):

```
[Spot] / 02 - Projetos / 05 - Projeto Arquitetônico / 03 - Anteprojeto / [última versão LANÇAMENTOS] / LANÇAMENTO_AP_<nome>_V0X.pdf
```

- Pasta raiz dos projetos: `1D9y8aKfkGGE13WbGMlw07G8Euu0Pg7fF`.
- **Regra rígida:** dentro de `03 - Anteprojeto`, escolher a última versão que contém **"LANÇAMENTO(S)"** no nome. **NUNCA** usar pastas/arquivos "COMPATIBILIZADO INTERIORES". Número de versão maior não implica correta — filtrar por LANÇAMENTOS primeiro, depois pegar a mais recente.
- Capturar também o `ANÁLISE_LANÇAMENTO_..._V0X.xlsx` da mesma pasta, se existir (fonte estruturada secundária, mais confiável que o PDF de ~33 MB).

### 2. Levantar as unidades (todos os pavimentos)

O PDF do anteprojeto é grande (~33 MB, muitas pranchas). Estratégia em camadas para não ler tudo:

1. **Preferir o `ANÁLISE_...xlsx`** quando existir — já traz unidade → área útil → terraço de forma estruturada.
2. Senão, varrer a camada de texto do PDF para localizar a página de **QUADRO DE ÁREAS / QUADRO DE UNIDADES** e ler só ela.
3. Em último caso, ler as plantas de pavimento como imagem (Claude multimodal) e enumerar unidades.

Saída desta etapa: lista de **todas** as unidades (ex.: 101, 102… por andar) com `área útil` e `terraço`.

### 3. Classificar e agrupar (o miolo de IA)

Para cada unidade, derivar — reusando a lógica do projeto `mapeamento-completo-de-mobilirio--unidade-spot`:

- **Terraço / Área externa:** Sem · Sacada · Garden · Terraço.
- **Tipo construtivo:** Padrão · PCD · Mezanino · Único.
- **Capacidade (PREVISÃO):** derivada de área útil + terraço + programa, pela Matriz Capacidade:
  - Base cap. 2: Cama Queen + cabeceira + copa + bancada + arara + vassoureiro + TV.
  - **Cama auxiliar** cabe ao lado da Queen → habilita **cap. 3 e 5**.
  - **Sofá-cama** aberto = leito → habilita **cap. 4 e 5**.
  - Mesa redonda / jacuzzi externos → quando há garden/terraço/varanda.
- **Área útil (m²)** e **área da unidade (m²)** (privativa total).

Agrupar numa **tipologia** (A, B, C…) as unidades com o **mesmo layout/desenho** + mesmo Terraço + Tipo + Capacidade. A área **não precisa ser idêntica**: unidades iguais em desenho e tamanho cujo m² difere por pouco (variação pequena) entram na mesma tipologia. Diferenças de m² grandes (que indiquem layout distinto) separam em tipologias diferentes. Casos de fronteira (diferença ambígua) vão sinalizados no resumo executivo. Contar `quantidade` e listar os números das unidades por tipologia.

### 4. Saída

**Destino:** novo Google Sheet no Drive da Raquel (não sobrescreve nada) + snapshot `docs/tipologias_<spot>.csv` no projeto para versionar. Link da planilha retornado ao final.

**Colunas** (espelham o quadro real validado no Natal Spot):

| TIPOLOGIA | N DAS UNIDADES | TERRAÇO | TIPO | QUANTIDADE | CAPACIDADE (previsão) | ÁREA ÚTIL (m²) | ÁREA DA UNIDADE (m²) |
|-----------|----------------|---------|------|------------|------------------------|----------------|----------------------|

- Linha de rodapé: **Total de Tipologias** e **Total de Unidades**.
- **Aviso de previsão de capacidade:** cabeçalho da coluna como `CAPACIDADE (previsão)` + nota fixa na planilha: *"⚠️ Capacidade é previsão baseada em área útil + programa de mobiliário. Confirmar/editar quando o layout final estiver pronto."* O mesmo alerta aparece no resumo executivo.
- A planilha é **editável**: a Raquel ajusta a coluna Capacidade depois que o layout final sair.

**Resumo executivo (markdown):**
- Unidades de baixa confiança na classificação (com o motivo).
- Divergências (ex.: soma das quantidades ≠ total de unidades declarado).
- Premissas usadas na previsão de capacidade.

---

## Auto-validação

Antes de entregar, a skill confere: **soma das `QUANTIDADE` == Total de Unidades** declarado no anteprojeto. Se não fechar, avisa no resumo em vez de entregar uma tabela silenciosamente errada.

---

## Por que casa com a rubrica do hackathon

- **#1 Problema SZI real + dados reais:** elimina trabalho manual recorrente de Lançamentos, usando anteprojetos reais do Drive SZI.
- **#2 IA com propósito:** classificação e agrupamento analítico de unidades, não OCR de tabela pronta.
- **#3 Arquivos de contexto:** CLAUDE.md + memory/lessons/rules + este spec.
- **#4 Skill funcional:** a Raquel usa amanhã em qualquer Spot novo.
- **#5 Demo:** "monta a tabela do Natal Spot" → planilha pronta, validada contra a verdade conhecida (5 tipologias / 96 unidades).

## Validação de referência

Natal Spot deve resultar em **5 tipologias / 96 unidades** (A=74 cap2, B=10 cap5, C=10 cap3, D=1 cap5, E=1 cap3), conforme o CSV do projeto antigo e o quadro do anteprojeto.

## Dependências técnicas

- MCP Google Drive (navegar/baixar): `GOOGLEDRIVE_FIND_FILE`, `GOOGLEDRIVE_DOWNLOAD_FILE`.
- MCP Google Sheets (criar planilha de saída): `GOOGLESHEETS_CREATE_GOOGLE_SHEET1` + escrita de valores.
- Read multimodal de PDF; varredura de texto/página para PDFs grandes.
- Dados de referência: lógica de classificação do projeto `mapeamento-completo-de-mobilirio--unidade-spot` (Matriz Capacidade, Tipos, Áreas externas).

## Riscos e mitigações

- **PDF de 33 MB:** preferir o `ANÁLISE_...xlsx`; senão localizar página do quadro antes de ler.
- **Plantas como imagem (sem camada de texto):** cair para leitura multimodal página a página; sinalizar baixa confiança.
- **Variação de nomenclatura entre Spots:** navegar por convenção de pastas + filtro "LANÇAMENTOS"; quando ambíguo, listar candidatos e perguntar.
- **Capacidade errada:** entregue como previsão, com aviso e coluna editável — nunca como verdade final.
