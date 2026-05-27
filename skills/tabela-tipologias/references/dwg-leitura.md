# Leitura de DWG (fonte mais precisa pro agrupamento)

O DWG/DXF do projeto é a fonte **mais precisa** pra tipologia: tem as esquadrias como
blocos discretos, com marcas de tipo, mais áreas e rótulos. Permite **contar esquadrias
por unidade** — exatamente o que a regra de agrupamento exige (ver `classificacao-spot.md`).

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

## Como contar esquadrias por unidade (abordagem)
1. Pegar os polígonos de unidade (boundaries em `A-AREA-BNDY` ou cômodos).
2. Para cada janela (INSERT em `A-GLAZ-IDEN`, ou bloco de janela em `A-GLAZ`), ver
   dentro de qual polígono de unidade o ponto de inserção cai.
3. Contar esquadrias por unidade → unidades com nº/tipo de esquadrias diferentes são
   tipologias diferentes (a de esquina costuma ter 1 a mais).
4. Espelhamento NÃO separa; só o nº/tipo de esquadrias (e banheiro/desenho) separa.

## Cuidados
- Blocos vêm do Revit com nomes longos ("...-02 - SEGUNDO PAVIMENTO PROPOSTA"); agrupar
  por prefixo/marca de tipo, não pelo nome inteiro.
- O nº da unidade (101, 201…) pode estar em atributo de bloco ou em texto de outro layer
  — localizar antes de confiar. Conferir o total contra o quadro do PDF/planilha.
- DWG é mais preciso, mas a associação espacial exige cuidado; sempre validar contra
  verdade conhecida (ex.: Natal 5 tip/96 un) antes de confiar no automático.
