"""
Construcao do PKG basico com PyVis.
Grafo direcionado G = <V, E, LV, LE> com 6 smartphones e seus atributos tecnicos.
Dados carregados do banco SQLite (db/tcc.db).
"""

import sqlite3
from pyvis.network import Network


def carregar_smartphones(db_path="db/tcc.db"):
    """Carrega smartphones e atributos do banco de dados SQLite"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Buscar smartphones com tela (JOIN)
    cursor.execute("""
        SELECT s.id, s.nome, s.processador, s.ram, s.resolucao,
               s.camera_frontal, s.bateria, s.sistema_operacional,
               t.tamanho, t.tipo
        FROM Smartphones s
        JOIN Smartphones_Telas st ON s.id = st.smartphone
        JOIN Telas t ON st.tela = t.id
        ORDER BY s.id
    """)
    rows = cursor.fetchall()

    smartphones = []
    for row in rows:
        sid, nome, proc, ram, res, cam_f, bat, so, tela_tam, tela_tipo = row

        # Buscar armazenamentos
        cursor.execute("""
            SELECT a.tamanho FROM Armazenamentos a
            JOIN Smartphones_Armazenamentos sa ON a.id = sa.armazenamento
            WHERE sa.smartphone = ?
            ORDER BY a.tamanho
        """, (sid,))
        armazenamentos = [f"{r[0]}GB" for r in cursor.fetchall()]

        # Buscar cameras traseiras
        cursor.execute("""
            SELECT c.valor FROM Cameras c
            JOIN Smartphones_Cameras sc ON c.id = sc.camera
            WHERE sc.smartphone = ? AND c.tipo = 'traseira'
            ORDER BY c.valor DESC
        """, (sid,))
        cameras = [f"{r[0]}MP" for r in cursor.fetchall()]

        smartphones.append({
            "nome": nome,
            "processador": proc,
            "ram": f"{ram}GB",
            "armazenamento": armazenamentos,
            "tela": {
                "tamanho": f'{tela_tam}"',
                "tipo": tela_tipo,
            },
            "resolucao": res,
            "camera_traseira": cameras,
            "camera_frontal": f"{cam_f}MP",
            "bateria": f"{bat}mAh",
            "sistema": so,
        })

    conn.close()
    return smartphones


def construir_pkg(smartphones):
    """Constroi o PKG basico e retorna o objeto Network"""
    net = Network(height="3000px", width="100%", directed=True, notebook=True)
    empty_node = 0

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
            if key == "nome":
                continue

            if isinstance(value, list):
                for item in value:
                    net.add_node(
                        item, label=item, shape="box", color="#F0FFF0", shadow=True
                    )
                    net.add_edge(phone["nome"], item, label=key)

            elif isinstance(value, dict):
                net.add_node(
                    n_id=empty_node, label="", shape="box", color="#F0FFF0", shadow=True
                )
                net.add_edge(phone["nome"], empty_node, label=key)
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

            else:
                net.add_node(
                    value, label=value, shape="box", color="#ffffcc", shadow=True
                )
                net.add_edge(phone["nome"], value, label=key)

    net.set_options("""
var options = {
  "nodes": {
    "font": {"size": 20, "face": "Arial", "color": "#2B2B2B"},
    "shadow": {"enabled": true, "color": "rgba(0,0,0,0.2)", "size": 10, "x": 5, "y": 5}
  },
  "edges": {
    "font": {
      "size": 18, "face": "Verdana", "color": "#1a237e",
      "background": "#ffffff", "strokeWidth": 3, "strokeColor": "#e3e3e3", "align": "middle"
    }
  },
  "physics": {
    "enabled": true,
    "forceAtlas2Based": {
      "gravitationalConstant": -150, "springLength": 250,
      "springConstant": 0.02, "damping": 0.4
    },
    "maxVelocity": 30, "minVelocity": 0.75,
    "solver": "forceAtlas2Based",
    "stabilization": {"enabled": true, "iterations": 200, "fit": true}
  }
}
""")

    return net


if __name__ == "__main__":
    smartphones = carregar_smartphones()
    print(f"Smartphones carregados do banco: {len(smartphones)}")
    for s in smartphones:
        print(f"  - {s['nome']}")

    net = construir_pkg(smartphones)
    net.show("pkg_celulares.html")
    print("PKG basico gerado: pkg_celulares.html")
