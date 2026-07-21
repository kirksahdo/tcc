"""
PKG enriquecido com opinioes extraidas pelo Sabia-3.1.
Carrega smartphones do banco SQLite e opinioes dos xlsx.
Exclui opinioes do produto alvo (Samsung Galaxy A35 5G) para simular item cold start.
Nos de opiniao coloridos por polaridade: verde (positivo), rosa (negativo), amarelo (neutro).
"""

import pandas as pd
from pyvis.network import Network
from pkgs import carregar_smartphones


# ============================================================================
# 1. CARREGAR DADOS
# ============================================================================

# Smartphones do banco de dados
smartphones = carregar_smartphones()

# Opinioes extraidas pelo Sabia-3.1
df1 = pd.read_excel("avaliacoes_opinioes.xlsx")
df2 = pd.read_excel("avaliacoes_opinioes_2.xlsx")
df3 = pd.read_excel("avaliacoes_opinioes_3.xlsx")
df_opinioes = pd.concat([df1, df2, df3], ignore_index=True)

# Remover opinioes do produto alvo (simulacao de item cold start)
df_opinioes = df_opinioes[df_opinioes["celular"] != "Samsung Galaxy A35 5G"]

print(f"Smartphones carregados: {len(smartphones)}")
print(f"Opinioes para enriquecimento: {len(df_opinioes)}")

# ============================================================================
# 2. CONSTRUIR GRAFO
# ============================================================================

net = Network(height="3000px", width="100%", directed=True, notebook=True)

# Mapeamento de categorias de opiniao para atributos do grafo
mapa_categoria = {
    "camera_traseira": "camera_traseira",
    "camera_frontal": "camera_frontal",
    "tela": "tela",
    "bateria": "bateria",
    "processador": "processador",
    "resolucao": "resolucao",
    "ram": "ram",
    "armazenamento": "armazenamento",
    "sistema_operacional": "sistema",
}

empty_node = 0
opinion_node_id = 100000


def adicionar_opinioes(celular_nome, atributo_key, node_value):
    """Adiciona nos de opiniao conectados a um no de atributo"""
    global opinion_node_id

    opinioes_filtradas = df_opinioes[
        (df_opinioes["celular"] == celular_nome)
        & (df_opinioes["categoria"] == atributo_key)
    ]

    for _, row in opinioes_filtradas.iterrows():
        evidencia = row["evidencia"]
        polaridade = row["polaridade"]

        if polaridade > 0:
            cor_opiniao = "#90EE90"
        elif polaridade < 0:
            cor_opiniao = "#FFB6C1"
        else:
            cor_opiniao = "#FFFACD"

        net.add_node(
            opinion_node_id,
            label=f"{evidencia}",
            shape="ellipse",
            color=cor_opiniao,
            shadow=True,
            size=30,
            font={"size": 24, "face": "Arial"},
        )
        net.add_edge(node_value, opinion_node_id, label="opiniao")
        opinion_node_id += 1


# Adicionar smartphones e atributos ao grafo
for phone in smartphones:
    net.add_node(
        phone["nome"],
        label=phone["nome"],
        shape="hexagon",
        color="#4682B4",
        size=60,
        borderWidth=3,
        borderWidthSelected=4,
        font={"size": 32, "color": "#000000", "face": "Arial", "bold": True},
    )

    for key, value in phone.items():
        if key == "nome":
            continue

        if isinstance(value, list):
            for item in value:
                net.add_node(
                    item, label=item, shape="box", color="#F0FFF0",
                    shadow=True, size=30, font={"size": 24, "face": "Arial"},
                )
                net.add_edge(phone["nome"], item, label=key)
                if key in mapa_categoria.values():
                    adicionar_opinioes(phone["nome"], key, item)

        elif isinstance(value, dict):
            net.add_node(
                n_id=empty_node, label="", shape="box", color="#F0FFF0", shadow=True
            )
            net.add_edge(phone["nome"], empty_node, label=key)
            for sub_key, sub_value in value.items():
                net.add_node(
                    sub_value, label=sub_value, shape="box", color="#ffffcc",
                    shadow=True, size=30, font={"size": 24, "face": "Arial"},
                )
                net.add_edge(empty_node, sub_value, label=sub_key)
                if key == "tela":
                    adicionar_opinioes(phone["nome"], "tela", sub_value)
            empty_node += 1

        else:
            net.add_node(
                value, label=value, shape="box", color="#ffffcc",
                shadow=True, size=30, font={"size": 24, "face": "Arial"},
            )
            net.add_edge(phone["nome"], value, label=key)
            if key in mapa_categoria.values():
                adicionar_opinioes(phone["nome"], key, value)

# ============================================================================
# 3. CONFIGURAR E SALVAR
# ============================================================================

net.set_options("""
var options = {
  "nodes": {
    "font": {"size": 28, "face": "Arial", "color": "#2B2B2B", "bold": {"color": "#2B2B2B"}},
    "shadow": {"enabled": true, "color": "rgba(0,0,0,0.3)", "size": 15, "x": 7, "y": 7}
  },
  "edges": {
    "font": {
      "size": 24, "face": "Arial", "color": "#1a237e",
      "background": "#ffffff", "strokeWidth": 4, "strokeColor": "#e3e3e3", "align": "middle"
    },
    "width": 3
  },
  "physics": {
    "enabled": true,
    "forceAtlas2Based": {
      "gravitationalConstant": -200, "springLength": 350,
      "springConstant": 0.02, "damping": 0.4
    },
    "maxVelocity": 30, "minVelocity": 0.75,
    "solver": "forceAtlas2Based",
    "stabilization": {"enabled": true, "iterations": 200, "fit": true}
  }
}
""")

net.show("pkg_celulares_com_opinioes.html")
print(f"PKG enriquecido gerado: pkg_celulares_com_opinioes.html")
print(f"Total de nos de opiniao adicionados: {opinion_node_id - 100000}")
