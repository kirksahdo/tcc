from pyvis.network import Network

net = Network(height="3000px", width="100%", directed=True, notebook=True)

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
        "sistema": "Android 14",
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

# Variável para o nó vazio (atributos com subatributos)
empty_node = 0

# Adiciona o nó principal (smartphone) e os atributos simples
for phone in smartphones:
    net.add_node(
        phone["nome"],
        label=phone["nome"],
        shape="hexagon",
        color="#4682B4",
        size=40,
        borderWidth=2,
        borderWidthSelected=3,
    )

    for key, value in phone.items():
        if key != "nome":
            # Nó com varios valores
            if isinstance(value, list):
                for item in value:
                    net.add_node(
                        item, label=item, shape="box", color="#F0FFF0", shadow=True
                    )
                    net.add_edge(phone["nome"], item, label=key)
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
                    )
                    net.add_edge(empty_node, sub_value, label=sub_key)
                empty_node += 1
            # Nó simples
            else:
                net.add_node(
                    value, label=value, shape="box", color="#ffffcc", shadow=True
                )
                net.add_edge(phone["nome"], value, label=key)

# Aumenta o espaçamento entre os nós
net.set_options(
    """
var options = {
  "nodes": {
    "font": {
      "size": 20,
      "face": "Arial",
      "color": "#2B2B2B"
    },
    "shadow": {
      "enabled": true,
      "color": "rgba(0,0,0,0.2)",
      "size": 10,
      "x": 5,
      "y": 5
    }
  },
  "edges": {
    "font": {
      "size": 18,
      "face": "Verdana",
      "color": "#1a237e",
      "background": "#ffffff",
      "strokeWidth": 3,
      "strokeColor": "#e3e3e3",
      "align": "middle"
    }
  },
  "physics": {
    "enabled": true,
    "forceAtlas2Based": {
      "gravitationalConstant": -150,
      "springLength": 250,
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
"""
)


net.show("pkg_celulares.html")
