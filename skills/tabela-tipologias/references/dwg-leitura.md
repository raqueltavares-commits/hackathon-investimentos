# Leitura de DWG (fonte mais precisa pro agrupamento)

## FONTE IDEAL = DWG + PDF (usar os DOIS)
Nenhuma fonte sozinha basta — o ideal é **cruzar DWG + PDF**:
- **PDF** (anteprojeto): **metragem por unidade**, **nº e total de unidades**, quadro de
  áreas e demais **textos relevantes** (rótulos, totais, observações). É a fonte dos
  NÚMEROS e do texto.
- **DWG**: a **geometria exata** — esquadrias (layer `A-GLAZ`), portas, layout, posição
  do banheiro, espelhamento. É a fonte do **AGRUPAMENTO** (contar esquadrias por unidade,
  comparar layouts).
Fluxo: PDF dá metragem + contagem + textos; DWG confirma/define o agrupamento por layout
e esquadrias. Validar um contra o outro (ex.: total de unidades do PDF vs do DWG).

O DWG/DXF tem as esquadrias como blocos discretos, com marcas de tipo, mais áreas e
rótulos. Permite **contar esquadrias por unidade** — exatamente o que a regra de
agrupamento exige (ver `classificacao-spot.md`).

## Ferramenta (instalada 2026-05-26)
- **ODA File Converter** (grátis, via winget `ODA.ODAFileConverter`):
  `C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe`
- **ezdxf** (Python) lê o DXF. Setar o caminho do ODA em runtime:
```python
import ezdxf
from ezdxf.addons import odafc
ezdxf.options.set("odafc-addon", "win_exec_path",
                  r"C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe")
doc = odafc.readfile("plano.dwg")   # converte DWG->DXF e abre
msp = doc.modelspace()
```

## Convenção de layers (padrão AIA — validado no Bonito, export Revit)
- **`A-GLAZ`** = vidros/**janelas (esquadrias)**. `A-GLAZ-CWMG` = montantes/cortina.
- **`A-GLAZ-IDEN`** = **tags de janela** (marca de tipo: V14, V15… V52). Contar estas
  dá o nº de esquadrias do pavimento (melhor que contar todos os blocos, que incluem
  folhas/montantes separados).
- **`A-DOOR`** / `A-DOOR-IDEN` = portas.
- **`A-AREA`**, `A-AREA-BNDY`, `A-AREA-IDEN` = polígonos e rótulos de área/cômodo.
- `A-WALL`, `I-FURN` (mobiliário), `P-SANR-FIXT` (louças), `S-STRS` (escada).

## Como contar esquadrias por unidade (abordagem NEAREST-LABEL)
Point-in-polygon NÃO funciona no export Revit real: `A-AREA-BNDY` vem como segmentos
`LINE` soltos (não polilinhas) e o arquivo pode ter 2 plantas lado a lado. Abordagem
implementada em `ler_dwg.py` (ver `arquitetura-dwg.md`):
1. Coletar os **números de unidade** em `A-AREA-IDEN` (TEXT/MTEXT, padrão `\d{3}(-\d{3})?`).
2. Coletar os blocos de esquadria (INSERT em `A-GLAZ`/`A-GLAZ-IDEN`) **dentro da bbox
   dos números** + margem (exclui 2ª planta/legendas distantes).
3. **Nearest-label**: cada bloco conta pra unidade cujo número está mais perto.
4. **Normalizar**: dividir a contagem crua pela contagem-base do piso (= nº de blocos
   por janela) → nº de janelas por unidade. Unidades com nº diferente = tipologias
   diferentes (a de esquina costuma ter 1 a mais).
5. Espelhamento NÃO separa; só o nº de esquadrias (e banheiro/desenho) separa.
6. A janela é UM sinal, não universal: QUALQUER pavimento pode ter unidades diferentes e
   pode abrir por porta (não janela) → contagem ~0; aí agrupa pela área (PDF) + layout.
   Avaliar pavimento a pavimento; nunca excluir nenhum.
7. Os nomes de layer variam por projeto — confirme com `--listar-layers` antes de contar
   (os layers AIA acima foram o caso do Bonito, não são regra).

## Cuidados
- Blocos vêm do Revit com nomes longos ("...-02 - SEGUNDO PAVIMENTO PROPOSTA"); agrupar
  por prefixo/marca de tipo, não pelo nome inteiro.
- O nº da unidade (101, 201…) pode estar em atributo de bloco ou em texto de outro layer
  — localizar antes de confiar. Conferir o total contra o quadro do PDF/planilha.
- DWG é mais preciso, mas a associação espacial exige cuidado; sempre validar contra
  verdade conhecida (ex.: Natal 5 tip/96 un) antes de confiar no automático.
