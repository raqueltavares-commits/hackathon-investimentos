# Navegação no Drive até o anteprojeto

Pasta raiz dos projetos: `1D9y8aKfkGGE13WbGMlw07G8Euu0Pg7fF`

Caminho por empreendimento:

```
[Spot "1.X - [código] Nome Spot"]
  / 02 - Projetos
    / 05 - Projeto Arquitetônico
      / 03 - Anteprojeto
        / [última versão LANÇAMENTOS]
          / LANÇAMENTO_AP_<nome>_V0X.pdf   (+ ANÁLISE_..._V0X.xlsx)
```

## Regra rígida de versão
Dentro de `03 - Anteprojeto`, escolher a última pasta/arquivo que contém
**"LANÇAMENTO(S)"** no nome. **NUNCA** usar "COMPATIBILIZADO INTERIORES".
Número de versão maior NÃO implica correta — filtrar por LANÇAMENTOS primeiro,
depois pegar a mais recente.

## Destino da tabela gerada (onde criar o Google Sheet)
Mesma lógica de navegação do anteprojeto, terminando em Interiores:
```
[Spot] / 02 - Projetos / 05 - Projeto Arquitetônico / 10 - Projeto de Interiores / 02 - Imagens
```
Criar o Google Sheet da tabela de tipologias **dentro de "02 - Imagens"**. Não
sobrescrever nada que já existe lá. Exemplo Natal: pasta `02 - Imagens` =
`1Afu8ZGleIT7EdiaYAISInqApi0BSpEjt`.

## Fontes de dados (ordem de preferência)
1. `ANÁLISE_LANÇAMENTO_..._V0X.xlsx` — dados estruturados (unidade → área → terraço).
2. Página de QUADRO DE ÁREAS / QUADRO DE UNIDADES dentro do PDF.
3. Plantas de pavimento (leitura multimodal página a página) — menor confiança.

## Ferramentas MCP
- `GOOGLEDRIVE_FIND_FILE` (listar/buscar por `folder_id`).
- `GOOGLEDRIVE_DOWNLOAD_FILE` (baixar PDF/xlsx; retorna URL temporária — baixar com curl).

## Exemplo validado (Natal Spot, 2026-05-26)
- Pasta do Spot: `1.42 - [6953] Natal Spot`.
- Anteprojeto LANÇAMENTOS: `V04- LANÇAMENTOS - 23/10 (96 UN)` →
  `LANÇAMENTO_AP_NATAL SPOT_V04_2025.10.23.pdf` (+ `ANÁLISE_LANÇAMENTO_AP_NATAL SPOT_V04_2025.10.23.xlsx`).
- Verdade conhecida: **5 tipologias / 96 unidades**.
