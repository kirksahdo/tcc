# TCC - Inferencia de Avaliacoes em Cenarios de Item Cold Start

Repositorio do artigo: **"Inferencia de Avaliacoes em Cenarios de Item Cold Start a Partir de Grafos de Conhecimento de Produtos Enriquecidos com Opinioes"** (Kirk Sahdo, Tiago de Melo - UEA/EST). TCC de Engenharia da Computacao.

## Sobre o Projeto

O trabalho aborda o problema de **item cold start** em sistemas de recomendacao, propondo a construcao de **Product Knowledge Graphs (PKGs)** enriquecidos com opinioes extraidas de avaliacoes de usuarios via LLM (Sabia-3.1, Maritaca AI). O metodo adapta o **PGOpi** (Moreira et al., 2022) substituindo deep learning por LLM para extracao de opinioes baseada em aspectos em portugues.

- **Dominio**: smartphones (6 dispositivos, Samsung Galaxy A35 5G como alvo)
- **Resultado principal**: 88.9% de concordancia na classificacao de polaridade, MAE de 0.167
- **LLM**: Sabia-3.1 (Maritaca AI)
- **Dados**: 6.166 avaliacoes, 14.389 tuplas de opiniao extraidas

## Pipeline do Experimento

1. **Coleta de avaliacoes** (`scraper.py`) - API do Mercado Livre, 6.166 avaliacoes
2. **Extracao de opinioes** (`sabia_sentiment_analysis.py`) - Sabia-3.1 extrai tuplas `<aspecto, polaridade, evidencia, categoria, sentenca>` para 9 categorias, polaridade numerica de -1.0 a +1.0
3. **Dados extraidos** (`avaliacoes_opinioes.xlsx`, `_2.xlsx`, `_3.xlsx`) - 14.389 tuplas de opiniao com polaridade numerica
4. **Construcao do PKG** (`pkgs.py`) - grafo basico com PyVis (6 smartphones + atributos tecnicos)
5. **Enriquecimento do PKG** (`pkgs_enriquecido.py`) - adiciona nos de opiniao ligados aos atributos, excluindo o produto alvo (cold start)
6. **Analise comparativa** (`analise_comparativa.py`) - reproduz a Tabela 2 do artigo (MAE e concordancia)

## Estrutura de Arquivos

### Scripts principais
| Arquivo | Descricao |
|---|---|
| `sabia_sentiment_analysis.py` | Extracao de opiniao baseada em aspectos via API Sabia-3.1 |
| `pkgs.py` | Construcao do PKG basico com PyVis (6 smartphones, 9 atributos) |
| `pkgs_enriquecido.py` | PKG enriquecido com nos de opiniao (exclui produto alvo) |
| `analise_comparativa.py` | Reproducao da Tabela 2: MAE (0.167) e concordancia (8/9) |
| `single_pkg.py` | Exemplo de PKG para um unico produto (Samsung Galaxy A35 5G) |
| `scraper.py` | Coleta de avaliacoes via API do Mercado Livre |

### Dados
| Arquivo | Descricao |
|---|---|
| `avaliacoes_opinioes.xlsx` | Tuplas de opiniao extraidas (parte 1) |
| `avaliacoes_opinioes_2.xlsx` | Tuplas de opiniao extraidas (parte 2) |
| `avaliacoes_opinioes_3.xlsx` | Tuplas de opiniao extraidas (parte 3) |
| `celulares.json` | Especificacoes tecnicas dos 6 smartphones (fonte: GSMArena) |
| `db/tcc.db` | Banco SQLite com dados dos smartphones |
| `data/reviews/` | CSVs com as 6.166 avaliacoes coletadas do Mercado Livre |

### Outros scripts de visualizacao (nao commitados)
| Arquivo | Descricao |
|---|---|
| `PKG_Graph_Enrichment.py` | Grafos de comparacao entre metodos (3 grafos HTML) |
| `PKG_Graph_Opinions.py` | PKG com nos de opiniao individuais e polaridade no label |
| `pkgs_todas_opinioes.py` | PKG com todas as opinioes (versao completa) |

## Config do Sabia-3.1 (Reprodutibilidade)

```
Modelo: sabia-3.1
Endpoint: https://chat.maritaca.ai/api/chat/inference
Temperature: 0.1
Top_p: 1.0 (padrao da API)
Max_tokens: 1000
Seed: nao fixado (API nao suportava na epoca)
Data da coleta: setembro-novembro 2025
API key: variavel de ambiente MARITACA_API_KEY
```

## 9 Categorias de Aspecto

armazenamento, processador, ram, tela, resolucao, camera_frontal, camera_traseira, bateria, sistema_operacional

## Smartphones do Estudo

| Smartphone | Papel |
|---|---|
| Samsung Galaxy A35 5G | **Alvo** (cold start simulado - opinioes excluidas do PKG) |
| Samsung Galaxy A54 5G | Similar |
| Motorola Moto G84 | Similar |
| Xiaomi Redmi Note 13 Pro 5G | Similar |
| Infinix Note 40 5G | Similar |
| Poco X6 Pro | Similar |

## Como executar

```bash
# Instalar dependencias
pip install -r requirements.txt

# Reproduzir Tabela 2 (MAE e concordancia)
python analise_comparativa.py

# Gerar PKG basico
python pkgs.py

# Gerar PKG enriquecido com opinioes
python pkgs_enriquecido.py

# Extracao de opinioes (requer MARITACA_API_KEY)
export MARITACA_API_KEY='sua_chave'
python sabia_sentiment_analysis.py
```

## Convencoes

- Codigo e comentarios em portugues
- Polaridade de opinioes: numerica de -1.0 (muito negativo) a +1.0 (muito positivo)
- Tupla de opiniao: `<aspecto, polaridade, evidencia, categoria, sentenca>`
- PKG: grafo direcionado G = <V, E, LV, LE>
- Nos de opiniao coloridos por polaridade: verde (positivo), rosa (negativo), amarelo (neutro)
- Arestas de opiniao com rotulo "opiniao"
