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

## Validacao real (usuario faz depois)

Para validar contra arquivo real (Bonito ou outro Spot):

1. Baixar o DWG do Drive (pasta do anteprojeto LANCAMENTOS)
2. Rodar:
   ```bash
   python skills/tabela-tipologias/scripts/unidades_dwg.py --dwg caminho/para/bonito.dwg
   ```
3. Verificar contagem:
   - Totais batem com PDF?
   - Unidades de esquina tem +1 esquadria?
   - 5 tipologias (Natal) ou conforme esperado?

### Verdade conhecida Natal
- 5 tipologias / 96 unidades
- A=74 (sem sacada, cap 2, ~14.33m²)
- B=10 (sem sacada, cap 5, ~19.94m²)
- C=10 (sem sacada, cap 3, ~15.18m²)
- D=1 (sacada, cap 5)
- E=1 (sacada, cap 3)
