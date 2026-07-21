# Analise de Sentimentos Baseada em Aspectos - Sabia-3.1 (Maritaca AI)
#
# Configuracao utilizada no experimento para reprodutibilidade:
#   Modelo: sabia-3.1 (Maritaca AI, Abonizio et al. 2024)
#   Endpoint: https://chat.maritaca.ai/api/chat/inference
#   Temperature: 0.1
#   Top_p: 1.0 (padrao da API)
#   Max_tokens: 1000
#   Data da coleta: setembro-novembro 2025

import pandas as pd
import json
import os
import re
import requests
from typing import Dict, List
import logging


class SabiaSentimentAnalyzer:
    def __init__(self):
        """Inicializa o analisador com modelo Sabia-3.1 via API Maritaca"""
        self.api_url = "https://chat.maritaca.ai/api/chat/inference"
        self.api_key = os.environ.get("MARITACA_API_KEY", "")

        # Especificacoes tecnicas dos celulares (fonte: GSMArena)
        self.phone_specs = {
            "Samsung Galaxy A35 5G": {
                "processador": "Exynos 1380",
                "ram": "8GB",
                "armazenamento": "128GB/256GB",
                "tela": '6.6" Super AMOLED',
                "resolucao": "1080x2340",
                "camera_traseira": "50MP+8MP+5MP",
                "camera_frontal": "13MP",
                "bateria": "5000mAh",
                "sistema": "Android 14",
            },
            "Samsung Galaxy A54 5G": {
                "processador": "Exynos 1380",
                "ram": "8GB",
                "armazenamento": "128GB/256GB",
                "tela": '6.4" Super AMOLED',
                "resolucao": "1080x2340",
                "camera_traseira": "50MP+12MP+5MP",
                "camera_frontal": "32MP",
                "bateria": "5000mAh",
                "sistema": "Android 13",
            },
            "Xiaomi Redmi Note 13 Pro 5G": {
                "processador": "Snapdragon 7s Gen 2",
                "ram": "8GB",
                "armazenamento": "128GB/256GB",
                "tela": '6.67" AMOLED',
                "resolucao": "1220x2712",
                "camera_traseira": "200MP+8MP+2MP",
                "camera_frontal": "16MP",
                "bateria": "5100mAh",
                "sistema": "Android 13",
            },
            "Motorola Moto G84": {
                "processador": "Snapdragon 695",
                "ram": "8GB",
                "armazenamento": "128GB/256GB",
                "tela": '6.55" P-OLED',
                "resolucao": "1080x2400",
                "camera_traseira": "50MP+8MP",
                "camera_frontal": "16MP",
                "bateria": "5000mAh",
                "sistema": "Android 13",
            },
            "Infinix Note 40 5G": {
                "processador": "Dimensity 7020",
                "ram": "8GB",
                "armazenamento": "256GB",
                "tela": '6.78" AMOLED',
                "resolucao": "1080x2436",
                "camera_traseira": "108MP+2MP+2MP",
                "camera_frontal": "32MP",
                "bateria": "5000mAh",
                "sistema": "Android 14",
            },
            "Poco X6 Pro": {
                "processador": "Dimensity 8300 Ultra",
                "ram": "12GB",
                "armazenamento": "256GB/512GB",
                "tela": '6.67" AMOLED',
                "resolucao": "1220x2712",
                "camera_traseira": "64MP+8MP+2MP",
                "camera_frontal": "16MP",
                "bateria": "5000mAh",
                "sistema": "Android 14",
            },
        }

    def create_structured_prompt(self, review: str, phone_model: str) -> str:
        """Cria prompt hierarquico para extracao de opiniao baseada em aspectos

        Estrutura hierarquica seguindo Li et al. (2025):
        1. Mensagem do sistema (papel do modelo)
        2. Descricao da atividade e categorias
        3. Formato de saida em JSON
        4. Entrada com o comentario a ser analisado
        """
        specs = self.phone_specs.get(phone_model, {})

        prompt = f"""Voce e um especialista em analise de sentimentos para avaliacoes de smartphones.

PRODUTO: {phone_model}
ESPECIFICACOES TECNICAS:
- Processador: {specs.get('processador', 'N/A')}
- RAM: {specs.get('ram', 'N/A')}
- Armazenamento: {specs.get('armazenamento', 'N/A')}
- Tela: {specs.get('tela', 'N/A')}
- Resolucao: {specs.get('resolucao', 'N/A')}
- Camera Traseira: {specs.get('camera_traseira', 'N/A')}
- Camera Frontal: {specs.get('camera_frontal', 'N/A')}
- Bateria: {specs.get('bateria', 'N/A')}
- Sistema: {specs.get('sistema', 'N/A')}

CATEGORIAS DE ASPECTOS (9 categorias):
1. armazenamento: espaco, memoria interna, capacidade, GB
2. processador: desempenho, velocidade, lag, travamentos, CPU, chip
3. ram: memoria RAM, multitarefa, velocidade
4. tela: display, brilho, cores, qualidade visual, visor
5. resolucao: nitidez, definicao, pixels, qualidade de imagem da tela
6. camera_traseira: camera principal, fotos, qualidade fotografica, zoom
7. camera_frontal: selfie, camera frontal, videochamada
8. bateria: duracao, autonomia, carregamento, tempo de uso
9. sistema_operacional: Android, interface, software, apps, atualizacoes

AVALIACAO A ANALISAR:
"{review}"

INSTRUCOES:
1. Leia a avaliacao cuidadosamente
2. Identifique mencoes diretas ou indiretas aos aspectos tecnicos
3. Para cada aspecto, atribua uma polaridade numerica de -1.0 a +1.0:
   -1.0 = muito negativo, -0.8 = negativo, -0.5 = moderadamente negativo,
   -0.2 = levemente negativo, 0.0 = neutro, +0.2 = levemente positivo,
   +0.5 = moderadamente positivo, +0.8 = positivo, +1.0 = muito positivo
4. Extraia a evidencia textual que justifica a classificacao
5. Identifique a sentenca original do comentario
6. Responda APENAS com um JSON valido no formato abaixo

FORMATO DE RESPOSTA (JSON):
{{
    "analise": [
        {{
            "aspecto": "descricao do aspecto mencionado",
            "polaridade": valor_numerico_entre_-1_e_1,
            "evidencia": "trecho do texto que justifica",
            "categoria": "uma_das_9_categorias_acima",
            "sentenca": "sentenca original completa"
        }}
    ]
}}

Resposta:"""

        return prompt

    def call_sabia_api(self, prompt: str) -> str:
        """Chama a API do SABIA-3"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": "sabia-3.1",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 1000,
            }

            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=30
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                logging.error(f"Erro na API: {response.status_code}")
                return ""

        except Exception as e:
            logging.error(f"Erro na chamada da API: {e}")
            return ""

    def extract_json_from_response(self, response: str) -> Dict:
        """Extrai e valida JSON da resposta"""
        try:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                try:
                    parsed_json = json.loads(match.group(0))
                    if "analise" in parsed_json:
                        return parsed_json
                except json.JSONDecodeError:
                    pass

            return {"analise": []}

        except Exception as e:
            logging.warning(f"Erro ao extrair JSON: {e}")
            return {"analise": []}

    def analyze_review(self, review: str, phone_model: str) -> Dict:
        """Analisa uma avaliacao e retorna tuplas de opiniao com polaridade numerica"""
        try:
            prompt = self.create_structured_prompt(review, phone_model)
            response = self.call_sabia_api(prompt)

            if response:
                return self.extract_json_from_response(response)
            else:
                return {"analise": []}

        except Exception as e:
            logging.error(f"Erro na analise: {e}")
            return {"analise": []}

    def process_csv(self, csv_path: str, output_path: str = None) -> pd.DataFrame:
        """Processa arquivo CSV com avaliacoes e extrai tuplas de opiniao.

        Cada tupla extraida tem o formato:
            <aspecto, polaridade, evidencia, categoria, sentenca>
        onde polaridade e numerica de -1.0 a +1.0.

        Gera uma linha por tupla de opiniao (nao por avaliacao).
        """
        try:
            df = pd.read_csv(csv_path)

            # Mapeamento de arquivos CSV para produtos
            csv_to_product = {
                "Infinix Note 40 5G_1": "Infinix Note 40 5G",
                "Infinix Note 40 5G_2": "Infinix Note 40 5G",
                "Motorola Moto G84": "Motorola Moto G84",
                "Motorola Moto G84_2": "Motorola Moto G84",
                "Poco X6 ProPoco X6 Pro": "Poco X6 Pro",
                "Poco X6 ProPoco X6 Pro_2": "Poco X6 Pro",
                "samsung a35 8gb": "Samsung Galaxy A35 5G",
                "samsung a54": "Samsung Galaxy A54 5G",
                "samsung a54_2": "Samsung Galaxy A54 5G",
                "Xiaomi Redmi Note 13 Pro 5g": "Xiaomi Redmi Note 13 Pro 5G",
                "Xiaomi Redmi Note 13 Pro 5g_2": "Xiaomi Redmi Note 13 Pro 5G",
            }

            # 9 categorias de aspectos
            categorias_validas = [
                "armazenamento",
                "processador",
                "ram",
                "tela",
                "resolucao",
                "camera_traseira",
                "camera_frontal",
                "bateria",
                "sistema_operacional",
            ]

            results = []

            csv_filename = csv_path.split("/")[-1].replace(".csv", "")
            phone_model = csv_to_product.get(csv_filename, csv_filename)

            for index, row in df.iterrows():
                if (index + 1) % 50 == 0:
                    print(f"Processando avaliacao {index + 1}/{len(df)}")

                review_text = str(row.get("Comentário", ""))

                if len(review_text.strip()) > 10:
                    analysis = self.analyze_review(review_text, phone_model)

                    for item in analysis.get("analise", []):
                        categoria = item.get("categoria", "")
                        if categoria in categorias_validas:
                            polaridade = item.get("polaridade", 0)
                            try:
                                polaridade = float(polaridade)
                                polaridade = max(-1.0, min(1.0, polaridade))
                            except (ValueError, TypeError):
                                continue

                            results.append({
                                "comentario_id": row.get("ID", index),
                                "celular": phone_model,
                                "rating": row.get("Rating", 0),
                                "titulo": row.get("Título", ""),
                                "comentario": review_text,
                                "aspecto": item.get("aspecto", ""),
                                "polaridade": polaridade,
                                "evidencia": item.get("evidencia", ""),
                                "categoria": categoria,
                                "sentenca": item.get("sentenca", ""),
                            })

            result_df = pd.DataFrame(results)

            if output_path and not result_df.empty:
                result_df.to_excel(output_path, index=False)
                print(f"Resultados salvos em: {output_path}")

            return result_df

        except Exception as e:
            logging.error(f"Erro no processamento: {e}")
            return pd.DataFrame()

    def generate_summary_report(self, df: pd.DataFrame) -> Dict:
        """Gera relatorio resumido da analise por categoria e celular"""
        try:
            summary = {
                "total_tuplas": len(df),
                "categorias": {},
            }

            if "categoria" in df.columns and "polaridade" in df.columns:
                for cat in sorted(df["categoria"].unique()):
                    cat_df = df[df["categoria"] == cat]
                    summary["categorias"][cat] = {
                        "total": len(cat_df),
                        "polaridade_media": round(cat_df["polaridade"].mean(), 3),
                        "positivas": int((cat_df["polaridade"] > 0).sum()),
                        "negativas": int((cat_df["polaridade"] < 0).sum()),
                        "neutras": int((cat_df["polaridade"] == 0).sum()),
                    }

            return summary

        except Exception as e:
            logging.error(f"Erro ao gerar relatorio: {e}")
            return {}


def main():
    """Processa avaliacoes de todos os CSVs e extrai tuplas de opiniao"""
    print("=" * 60)
    print("EXTRACAO DE OPINIOES BASEADA EM ASPECTOS")
    print("Modelo: Sabia-3.1 (Maritaca AI)")
    print("9 categorias | Polaridade numerica [-1, +1]")
    print("=" * 60)

    if not os.environ.get("MARITACA_API_KEY"):
        print("\nATENCAO: Defina a variavel de ambiente MARITACA_API_KEY")
        print("  export MARITACA_API_KEY='sua_chave_aqui'")
        return

    analyzer = SabiaSentimentAnalyzer()

    data_folder = "data/reviews"
    if not os.path.isdir(data_folder):
        print(f"Pasta {data_folder} nao encontrada")
        return

    csv_files = [
        os.path.join(data_folder, f)
        for f in os.listdir(data_folder)
        if f.endswith(".csv") and f != "resultado_unificado.csv"
    ]

    if not csv_files:
        print("Nenhum arquivo CSV encontrado")
        return

    print(f"\n{len(csv_files)} arquivos CSV encontrados")

    all_results = []
    for i, csv_file in enumerate(csv_files, 1):
        filename = os.path.basename(csv_file)
        print(f"\n[{i}/{len(csv_files)}] Processando: {filename}")

        df_result = analyzer.process_csv(csv_file)
        if not df_result.empty:
            all_results.append(df_result)
            print(f"  {len(df_result)} tuplas extraidas")

    if all_results:
        consolidated_df = pd.concat(all_results, ignore_index=True)
        output_file = "avaliacoes_opinioes.xlsx"
        consolidated_df.to_excel(output_file, index=False)

        summary = analyzer.generate_summary_report(consolidated_df)

        print(f"\n{'='*60}")
        print("EXTRACAO CONCLUIDA")
        print(f"{'='*60}")
        print(f"Total de tuplas de opiniao: {len(consolidated_df)}")
        print(f"Arquivo salvo: {output_file}")
        print(f"\nResumo por categoria:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
