# Arquitetura -- ler_dwg.py

## Responsabilidade
Le DWG via ezdxf+ODA, extrai esquadrias (A-GLAZ-IDEN) por unidade via Point-in-Polygon.

## Dependencias
- `ezdxf` — leitura de DXF/DWG
- `shapely` — geometria (Point-in-Polygon)
- ODA File Converter — conversao DWG->DXF em tempo de execucao

## Fluxo
```
ler_dwg(path)
1. ODA converte DWG->DXF
2. ezdxf abre o DXF (modelspace)
3. _coletar_poligonos:
   - A-AREA-BNDY → poligonos de area (Polyline)
   - A-AREA-IDEN → textos (numero da unidade)
   - Para cada poligono, encontra o texto mais proximo → nome da unidade
4. _coletar_janelas:
   - A-GLAZ-IDEN → INSERT com atributo MARK/TAG → marca + posicao
5. _associar_janelas_a_unidades:
   - shapely Point-in-Polygon: cada janela eassociada a unidade que a contem
```

## Camadas do DWG referenciadas
| Layer | Conteudo |
|---|---|
| `A-AREA-BNDY` | Poligonos das areas das unidades (Polyline fechada) |
| `A-AREA-IDEN` | Textos com numero da unidade (101, 201...) |
| `A-GLAZ-IDEN` | Blocos de esquadria com atributo MARK |

## Limitacoes
- Exige ODA File Converter instalado em `C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe`
- Nome da unidade vem do texto mais proximo ao poligono (heuristica) — pode falhar se layer nao existir
- Se todos os layers_existirem mas o texto nao for numerico, retorna string vazia
- Se layer nao existir, retorna dict vazio
