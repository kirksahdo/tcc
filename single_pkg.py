from pyvis.network import Network

net = Network(height="600px", width="100%", directed=True, notebook=True)

produto = "Samsung Galaxy S24"
net.add_node(produto, label=produto, shape="ellipse", color="#add8e6")

atributos_simples = {
    "Marca": "Samsung",
    "Processador": "Snapdragon 8 Gen 3",
    "RAM": "8GB",
    "Armazenamento": "128GB",
    "Bateria": "4000mAh",
    "Câmera": "50MP + 12MP + 10MP",
    "Sistema": "Android 14",
}

for nome_attr, valor in atributos_simples.items():
    net.add_node(valor, label=valor, shape="box", color="#ffffcc")
    net.add_edge(produto, valor, label=nome_attr)

tela_node = " "
net.add_node(tela_node, label="", shape="circle", color="#f0e68c")
net.add_edge(produto, tela_node, label="Tela")

subatributos_tela = {"Tamanho": "6.2''", "Tipo": "Dynamic AMOLED 2X"}

for nome_sub, valor in subatributos_tela.items():
    net.add_node(valor, label=valor, shape="box", color="#ffe4e1")
    net.add_edge(tela_node, valor, label=nome_sub)

# Aumenta o espaçamento entre os nós
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

net.show("pkg_samsung_s24.html")
