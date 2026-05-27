# Arquitetura -- ler_dwg.py

## Responsabilidade
Le DWG via ezdxf+ODA e conta esquadrias por unidade pra AGRUPAR tipologias
(diferenciar o DESENHO das unidades). NAO monta tabela de esquadrias — o objetivo
e separar unidades de mesma area que diferem pela janela de esquina.

## Dependencias
- `ezdxf` — leitura de DXF/DWG
- ODA File Converter — conversao DWG->DXF em tempo de execucao (so no `ler_dwg`)
- (shapely NAO e mais necessario — abandonamos point-in-polygon)

## Por que nearest-label (e nao point-in-polygon)
Validado no DWG real do Bonito (export Revit): os limites de area em `A-AREA-BNDY`
vem como segmentos `LINE` soltos, NAO polilinhas fechadas — `.points()` estoura e
nao da pra reconstruir poligono confiavel. Alem disso o arquivo pode ter DUAS plantas
lado a lado (arquitetonica com tags de janela; de areas com numeros+blocos). Por isso:
contamos o bloco `A-GLAZ` mais proximo de cada NUMERO de unidade, restritos a regiao
dos numeros.

## Fluxo
```
ler_dwg(path)  -> extrair(msp)
1. ODA converte DWG->DXF, ezdxf abre o modelspace
2. _coletar_labels_unidade: A-AREA-IDEN (TEXT/MTEXT) casando \d{3}(-\d{3})? -> (nome,x,y)
3. _coletar_janelas: blocos INSERT em A-GLAZ / A-GLAZ-IDEN, DENTRO da bbox dos
   numeros + margem (exclui 2a planta / legendas distantes)
4. _contar_por_unidade: nearest-label (cada bloco conta pra unidade mais proxima)
5. ExtraidosDWG.janelas_por_unidade(): normaliza a contagem CRUA de blocos dividindo
   pela contagem-base do piso (= nº de blocos por janela, a contagem mais comum),
   limpando ruido do nearest-label.
```

## Contrato
- `ExtraidosDWG.contagem_blocos` — dict label -> nº cru de blocos A-GLAZ.
- `ExtraidosDWG.janelas_por_unidade()` / `contagem_por_unidade()` — dict label -> nº
  estimado de janelas (normalizado). E o que o agrupamento usa.
- Labels pareados ("201-301") sao expandidos pra cada unidade na integracao do
  `montar_tabela` (`label.split("-")`).

## Limitacoes / o que varia por projeto
- Exige ODA File Converter (so no `ler_dwg`; `extrair(msp)` e testavel sem ODA).
- **Nomes de layer variam por projeto** (desenhistas diferentes). `label_layer` e
  `janela_layers` sao parametros; os defaults (`A-AREA-IDEN`, `A-GLAZ`/`A-GLAZ-IDEN`)
  seguem AIA/Revit e NAO sao universais. Use `listar_layers(dwg)` (ou o CLI
  `--listar-layers`) pra inspecionar um arquivo novo e ajustar.
- **A janela e UM sinal, nao universal.** QUALQUER pavimento (terreo, tipo, rooftop) pode
  ter unidades diferentes e pode abrir por porta em vez de janela -> contagem ~0; ai o
  agrupamento sai da AREA (PDF) + layout. Avaliar pavimento a pavimento; nunca excluir
  nenhum pavimento.
- Portas (A-DOOR) NAO entram na assinatura (area comum contamina o nearest-label).

## Validacao real (Bonito, 2026-05-27)
DWGs baixados do Drive (pasta DWG do anteprojeto LANCAMENTOS). Resultado (janelas/unid):
- **Pavimento tipo** (201-216): 12 unidades = 1 janela, 4 = 2 janelas (203,204,212,213).
- **Rooftop** (401-408): 6 = 1 janela, 2 = 2 janelas (403,404).
- **Terreo** (101-113): ~0 janela (abre por porta) -> agrupa pela area do PDF.
Bate com a tabela de janelas do PDF (J02: tipo 20 = 12x1+4x2; rooftop 10 = 6x1+2x2).

Rodar:
```bash
python skills/tabela-tipologias/scripts/unidades_dwg.py --dwg caminho/arquivo.dwg
```
