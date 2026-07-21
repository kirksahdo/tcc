"""
Exemplo de PKG para um unico produto (Samsung Galaxy A35 5G - produto alvo do estudo).
Gera um grafo direcionado G = <V, E, LV, LE> com o produto como no central
e seus atributos tecnicos como nos filhos.
"""

from pyvis.network import Network

net = Network(height="2000px", width="100%", directed=True, notebook=True)

produto = "Samsung Galaxy A35 5G"
net.add_node(produto, label=produto, shape="hexagon", color="#4682B4", size=40)

atributos_simples = {
    "processador": "Exynos 1380",
    "ram": "8GB",
    "bateria": "5000mAh",
    "camera_frontal": "13MP",
    "resolucao": "1080x2340",
    "sistema": "Android 14",
}

for nome_attr, valor in atributos_simples.items():
    net.add_node(valor, label=valor, shape="box", color="#ffffcc")
    net.add_edge(produto, valor, label=nome_attr)

# Tela com subatributos (tamanho e tipo)
tela_node = "tela_group"
net.add_node(tela_node, label="", shape="dot", color="#f0e68c", size=15)
net.add_edge(produto, tela_node, label="tela")

subatributos_tela = {"tamanho": '6.6"', "tipo": "Super AMOLED"}

for nome_sub, valor in subatributos_tela.items():
    net.add_node(valor, label=valor, shape="box", color="#ffe4e1")
    net.add_edge(tela_node, valor, label=nome_sub)

# Armazenamento (multiplos valores)
for arm in ["128GB", "256GB"]:
    net.add_node(arm, label=arm, shape="box", color="#F0FFF0")
    net.add_edge(produto, arm, label="armazenamento")

# Camera traseira (multiplas lentes)
for cam in ["50MP", "8MP", "5MP"]:
    net.add_node(f"cam_{cam}", label=cam, shape="box", color="#F0FFF0")
    net.add_edge(produto, f"cam_{cam}", label="camera_traseira")

net.set_options(
    """
var options = {
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -3000,
      "centralGravity": 0.3,
      "springLength": 150,
      "springConstant": 0.04,
      "damping": 0.09
    },
    "minVelocity": 0.75
  }
}
"""
)

net.show("pkg_samsung_a35.html")
