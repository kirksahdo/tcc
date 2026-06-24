from pyvis.network import Network
import pandas as pd

net = Network(height="3000px", width="100%", directed=True, notebook=True)

# Carregar as planilhas de opiniões
df1 = pd.read_excel("avaliacoes_opinoes_limpas.xlsx")

# Combinar as planilhas
df_opinioes = pd.concat([df1], ignore_index=True)

# FILTRAR: Remover opiniões do Samsung Galaxy A35 5G
# df_opinioes = df_opinioes[df_opinioes["celular"] != "Samsung Galaxy A35 5G"]
df_opinioes = df_opinioes[df_opinioes["celular"] == "Samsung Galaxy A54 5G"]

# Lista de smartphones com atributos e subatributos
smartphones = [
    {
        "nome": "Samsung Galaxy A35 5G",
        "processador": "Exynos 1380",
        "ram": "8GB",
        "armazenamento": ["128GB", "256GB"],
        "tela": {
            "tamanho": '6.6"',
            "tipo": "Super AMOLED",
        },
        "resolucao": "1080x2340",
        "camera_traseira": ["50MP", "8MP", "5MP"],
        "camera_frontal": "13MP",
        "bateria": "5000mAh",
        "sistema": "Android 13",
    },
    {
        "nome": "Samsung Galaxy A54 5G",
        "processador": "Exynos 1380",
        "ram": "8GB",
        "armazenamento": ["128GB", "256GB"],
        "tela": {
            "tamanho": '6.4"',
            "tipo": "Super AMOLED",
        },
        "resolucao": "1080x2340",
        "camera_traseira": ["50MP", "12MP", "5MP"],
        "camera_frontal": "32MP",
        "bateria": "5000mAh",
        "sistema": "Android 13",
    },
    {
        "nome": "Xiaomi Redmi Note 13 Pro 5G",
        "processador": "Snapdragon 7s Gen 2",
        "ram": "8GB",
        "armazenamento": ["128GB", "256GB"],
        "tela": {
            "tamanho": '6.67"',
            "tipo": "AMOLED",
        },
        "resolucao": "1220x2712",
        "camera_traseira": ["200MP", "8MP", "2MP"],
        "camera_frontal": "16MP",
        "bateria": "5100mAh",
        "sistema": "Android 13",
    },
    {
        "nome": "Motorola Moto G84",
        "processador": "Snapdragon 695",
        "ram": "8GB",
        "armazenamento": ["128GB", "256GB"],
        "tela": {
            "tamanho": '6.55"',
            "tipo": "P-OLED",
        },
        "resolucao": "1080x2400",
        "camera_traseira": ["50MP", "8MP"],
        "camera_frontal": "16MP",
        "bateria": "5000mAh",
        "sistema": "Android 13",
    },
    {
        "nome": "Infinix Note 40 5G",
        "processador": "Dimensity 7020",
        "ram": "8GB",
        "armazenamento": ["256GB"],
        "tela": {
            "tamanho": '6.78"',
            "tipo": "AMOLED",
        },
        "resolucao": "1080x2436",
        "camera_traseira": ["108MP", "2MP", "2MP"],
        "camera_frontal": "32MP",
        "bateria": "5000mAh",
        "sistema": "Android 14",
    },
    {
        "nome": "Poco X6 Pro",
        "processador": "Dimensity 8300 Ultra",
        "ram": "12GB",
        "armazenamento": ["256GB", "512GB"],
        "tela": {
            "tamanho": '6.67"',
            "tipo": "AMOLED",
        },
        "resolucao": "1220x2712",
        "camera_traseira": ["64MP", "8MP", "2MP"],
        "camera_frontal": "16MP",
        "bateria": "5000mAh",
        "sistema": "Android 14",
    },
]

# Mapeamento de categorias para atributos do grafo
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

# Variável para o nó vazio (atributos com subatributos)
empty_node = 0
opinion_node_id = 100000  # ID inicial para nós de opinião


# Função para adicionar opiniões ao grafo
def adicionar_opinioes(celular_nome, atributo_key, node_value):
    """
    Adiciona nós de opinião conectados a um nó de atributo específico
    """
    global opinion_node_id

    # Filtrar opiniões para este celular e categoria
    opinioes_filtradas = df_opinioes[
        (df_opinioes["celular"] == celular_nome)
        & (df_opinioes["categoria"] == atributo_key)
    ]

    # Adicionar uma amostra de opiniões (máximo 5 por atributo para não sobrecarregar o grafo)
    for idx, row in opinioes_filtradas.iterrows():
        evidencia = row["evidencia"]
        polaridade = row["polaridade"]

        # Definir cor baseada na polaridade
        if polaridade > 0:
            cor_opiniao = "#90EE90"
        elif polaridade < 0:
            cor_opiniao = "#FFB6C1"
        else:
            cor_opiniao = "#FFFACD"

        # Criar nó de opinião
        net.add_node(
            opinion_node_id,
            label=f"{evidencia}",
            shape="ellipse",
            color=cor_opiniao,
            shadow=True,
            size=30,
            font={"size": 24, "face": "Arial"},
        )

        # Conectar ao nó de atributo
        net.add_edge(node_value, opinion_node_id, label="opiniao")

        opinion_node_id += 1


# Adiciona o nó principal (smartphone) e os atributos simples
for phone in smartphones:
    net.add_node(
        phone["nome"],
        label=phone["nome"],
        shape="hexagon",
        color="#4682B4",
        size=60,  # Aumentado de 40 para 60
        borderWidth=3,
        borderWidthSelected=4,
        font={
            "size": 32,
            "color": "#000000",
            "face": "Arial",
            "bold": True,
        },  # Fonte maior e em negrito
    )

    for key, value in phone.items():
        if key != "nome":
            # Nó com varios valores
            if isinstance(value, list):
                for item in value:
                    net.add_node(
                        item,
                        label=item,
                        shape="box",
                        color="#F0FFF0",
                        shadow=True,
                        size=30,  # Aumentado de 15 para 30
                        font={"size": 24, "face": "Arial"},  # Fonte maior
                    )
                    net.add_edge(phone["nome"], item, label=key)

                    # Adicionar opiniões para este atributo
                    if key in mapa_categoria.values():
                        adicionar_opinioes(phone["nome"], key, item)

            # Nó com subatributos
            elif isinstance(value, dict):
                # Criação do nó vazio para o subatributo
                net.add_node(
                    n_id=empty_node, label="", shape="box", color="#F0FFF0", shadow=True
                )
                net.add_edge(phone["nome"], empty_node, label=key)

                # Adiciona os subatributos como nós filhos do nó vazio
                for sub_key, sub_value in value.items():
                    net.add_node(
                        sub_value,
                        label=sub_value,
                        shape="box",
                        color="#ffffcc",
                        shadow=True,
                        size=30,  # Aumentado de 15 para 30
                        font={"size": 24, "face": "Arial"},  # Fonte maior
                    )
                    net.add_edge(empty_node, sub_value, label=sub_key)

                    # Adicionar opiniões para subatributos da tela
                    if key == "tela":
                        adicionar_opinioes(phone["nome"], "tela", sub_value)

                empty_node += 1

            # Nó simples
            else:
                net.add_node(
                    value,
                    label=value,
                    shape="box",
                    color="#ffffcc",
                    shadow=True,
                    size=30,  # Aumentado de 15 para 30
                    font={"size": 24, "face": "Arial"},  # Fonte maior
                )
                net.add_edge(phone["nome"], value, label=key)

                # Adicionar opiniões para este atributo
                if key in mapa_categoria.values():
                    adicionar_opinioes(phone["nome"], key, value)

net.set_options("""
    var options = {
      "nodes": {
        "font": {
          "size": 28,
          "face": "Arial",
          "color": "#2B2B2B",
          "bold": {
            "color": "#2B2B2B"
          }
        },
        "shadow": {
          "enabled": true,
          "color": "rgba(0,0,0,0.3)",
          "size": 15,
          "x": 7,
          "y": 7
        }
      },
      "edges": {
        "font": {
          "size": 24,
          "face": "Arial",
          "color": "#1a237e",
          "background": "#ffffff",
          "strokeWidth": 4,
          "strokeColor": "#e3e3e3",
          "align": "middle"
        },
        "width": 3
      },
      "physics": {
        "enabled": true,
        "forceAtlas2Based": {
          "gravitationalConstant": -200,
          "springLength": 350,
          "springConstant": 0.02,
          "damping": 0.4
        },
        "maxVelocity": 30,
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based",
        "stabilization": {
          "enabled": true,
          "iterations": 200,
          "fit": true
        }
      }
    }
    """)

net.show("pkg_celulares_com_opinioes.html")
