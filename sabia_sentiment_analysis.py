# Analise de Sentimentos Baseada em Aspectos - SABIA-3

import pandas as pd
import json
import os
import re
import requests
from typing import Dict, List
import logging


class SabiaSentimentAnalyzer:
    def __init__(self):
        """Inicializa o analisador com modelo SABIA-3 via API Maritaca"""
        self.api_url = "https://chat.maritaca.ai/api/chat/inference"
        self.api_key = "YOUR_API-KEY-HERE"

        # Especificacoes tecnicas dos celulares
        self.phone_specs = {
            "Samsung Galaxy A35 5G": {
                "processador": "Exynos 1380",
                "ram": "8GB",
                "tela": '6.6" Super AMOLED',
                "resolucao": "1080x2340",
                "camera_traseira": "50MP+8MP+5MP",
                "camera_frontal": "13MP",
                "bateria": "5000mAh",
                "sistema": "Android 13",
            },
            "Samsung Galaxy A54 5G": {
                "processador": "Exynos 1380",
                "ram": "8GB",
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
                "tela": '6.67" AMOLED',
                "resolucao": "1220x2712",
                "camera_traseira": "64MP+8MP+2MP",
                "camera_frontal": "16MP",
                "bateria": "5000mAh",
                "sistema": "Android 14",
            },
        }

    def create_structured_prompt(self, review: str, phone_model: str) -> str:
        """Cria prompt estruturado para analise de aspectos"""
        specs = self.phone_specs.get(phone_model, {})

        prompt = f"""Voce e um especialista em analise de sentimentos para avaliacoes de smartphones.

PRODUTO: {phone_model}
ESPECIFICACOES TECNICAS:
- Processador: {specs.get('processador', 'N/A')}
- RAM: {specs.get('ram', 'N/A')} 
- Tela: {specs.get('tela', 'N/A')}
- Resolucao: {specs.get('resolucao', 'N/A')}
- Camera Traseira: {specs.get('camera_traseira', 'N/A')}
- Camera Frontal: {specs.get('camera_frontal', 'N/A')}
- Bateria: {specs.get('bateria', 'N/A')}
- Sistema: {specs.get('sistema', 'N/A')}

ASPECTOS PARA ANALISE:
1. processador: desempenho, velocidade, lag, travamentos, CPU, chip
2. ram: memoria, multitarefa, velocidade, travamento por falta de memoria
3. tela: display, brilho, cores, qualidade visual, screen, visor
4. resolucao: nitidez, definicao, pixels, qualidade de imagem
5. camera_traseira: camera principal, fotos, qualidade fotografica, zoom
6. camera_frontal: selfie, camera frontal, videochamada
7. bateria: duracao, autonomia, carregamento, tempo de uso
8. sistema: Android, interface, software, apps, atualizacoes

AVALIACAO A ANALISAR:
"{review}"

INSTRUCOES:
1. Leia a avaliacao cuidadosamente
2. Identifique menoens diretas ou indiretas aos aspectos tecnicos
3. Determine se a opiniao e positiva, negativa ou neutra
4. Extraia a evidencia textual que justifica a classificacao
5. Responda APENAS com um JSON valido no formato especificado

FORMATO DE RESPOSTA (JSON apenas):
{{
    "analise": [
        {{
            "aspecto": "nome_do_aspecto",
            "opiniao": "positiva/negativa/neutra",
            "evidencia": "trecho exato do texto",
            "confianca": "alta/media/baixa"
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
                "model": "sabia-3",
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
            # Procura por JSON na resposta
            json_patterns = [
                r'\{[^{}]*"análise"[^{}]*\[[^\]]*\][^{}]*\}',
                r'\{.*?"análise".*?\}',
                r"\{.*\}",
            ]

            for pattern in json_patterns:
                match = re.search(pattern, response, re.DOTALL)
                if match:
                    try:
                        json_str = match.group(0)
                        parsed_json = json.loads(json_str)
                        if "análise" in parsed_json:
                            return parsed_json
                    except:
                        continue

            return {"análise": []}

        except Exception as e:
            logging.warning(f"Erro ao extrair JSON: {e}")
            return {"análise": []}

    def analyze_review(self, review: str, phone_model: str) -> Dict:
        """Analisa uma avaliacao especifica"""
        try:
            prompt = self.create_structured_prompt(review, phone_model)
            response = self.call_sabia_api(prompt)

            if response:
                return self.extract_json_from_response(response)
            else:
                return {"análise": []}

        except Exception as e:
            logging.error(f"Erro na análise: {e}")
            return {"análise": []}

    def process_csv(self, csv_path: str, output_path: str = None) -> pd.DataFrame:
        """Processa arquivo CSV com avaliações"""
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

            results = []

            for index, row in df.iterrows():
                print(f"Processando avaliacao {index + 1}/{len(df)}")

                # Identifica o produto
                csv_filename = csv_path.split("/")[-1].replace(".csv", "")
                phone_model = csv_to_product.get(csv_filename, csv_filename)

                # Obtém o texto da avaliação
                review_text = str(row.get("Comentário", ""))

                if len(review_text.strip()) > 10:
                    analysis = self.analyze_review(review_text, phone_model)

                    # Prepara resultado
                    result_row = row.to_dict()
                    result_row["produto"] = phone_model
                    result_row["análise_sabia"] = json.dumps(
                        analysis, ensure_ascii=False
                    )

                    # Inicializa colunas para aspectos
                    aspectos = [
                        "processador",
                        "ram",
                        "tela",
                        "resolucao",
                        "camera_traseira",
                        "camera_frontal",
                        "bateria",
                        "sistema",
                    ]

                    for aspecto in aspectos:
                        result_row[f"{aspecto}_opinião"] = "nao_mencionado"
                        result_row[f"{aspecto}_evidencia"] = ""
                        result_row[f"{aspecto}_confianca"] = ""

                    # Preenche com resultados da analise
                    for item in analysis.get("analise", []):
                        aspecto = item.get("aspecto", "")
                        if aspecto in aspectos:
                            result_row[f"{aspecto}_opinião"] = item.get("opinião", "")
                            result_row[f"{aspecto}_evidencia"] = item.get(
                                "evidencia", ""
                            )
                            result_row[f"{aspecto}_confianca"] = item.get(
                                "confianca", ""
                            )

                    results.append(result_row)

            # Cria DataFrame de resultados
            result_df = pd.DataFrame(results)

            # Salva se especificado
            if output_path:
                result_df.to_csv(output_path, index=False, encoding="utf-8")
                print(f"Resultados salvos em: {output_path}")

            return result_df

        except Exception as e:
            logging.error(f"Erro no processamento: {e}")
            return pd.DataFrame()

    def generate_summary_report(self, df: pd.DataFrame) -> Dict:
        """Gera relatorio resumido da analise"""
        try:
            aspectos = [
                "processador",
                "ram",
                "tela",
                "resolucao",
                "camera_traseira",
                "camera_frontal",
                "bateria",
                "sistema",
            ]

            summary = {"total_avaliacoes": len(df), "aspectos_analisados": {}}

            for aspecto in aspectos:
                col_opiniao = f"{aspecto}_opinião"
                if col_opiniao in df.columns:
                    opinies = df[col_opiniao].value_counts()
                    summary["aspectos_analisados"][aspecto] = {
                        "positivas": opinies.get("positiva", 0),
                        "negativas": opinies.get("negativa", 0),
                        "neutras": opinies.get("neutra", 0),
                        "nao_mencionadas": opinies.get("nao_mencionado", 0),
                    }

            return summary

        except Exception as e:
            logging.error(f"Erro ao gerar relatorio: {e}")
            return {}


def main():
    """Função principal para processar analise completa de todos os celulares"""
    print("=" * 60)
    print("SISTEMA DE ANALISE DE SENTIMENTOS - CELULARES")
    print("Modelo: SABIA-3")
    print("=" * 60)

    # Inicializa analisador
    analyzer = SabiaSentimentAnalyzer()

    print("\nEscolha uma opcao:")
    print("1. Processar multiplos arquivos CSV")
    print("2. Processar arquivo CSV unico")
    print("3. Teste com exemplo de avaliacao")
    print("4. Sair")

    while True:
        opcao = input("\nDigite a opcao (1-4): ").strip()

        if opcao == "1":
            print("\n" + "-" * 50)
            print("PROCESSAMENTO DE MULTIPLOS ARQUIVOS")
            print("-" * 50)

            data_folder = input(
                "Digite o caminho da pasta com os CSVs (ou ENTER para usar pasta atual): "
            ).strip()
            if not data_folder:
                data_folder = os.getcwd()

            csv_files = []
            try:
                for file in os.listdir(data_folder):
                    if file.endswith(".csv"):
                        csv_files.append(os.path.join(data_folder, file))

                if not csv_files:
                    print(f"Nenhum arquivo CSV encontrado em {data_folder}")
                    continue

                print(f"\n{len(csv_files)} arquivos CSV encontrados")

                all_results = []
                output_folder = os.path.join(data_folder, "resultados_analise")
                os.makedirs(output_folder, exist_ok=True)

                for i, csv_file in enumerate(csv_files, 1):
                    filename = os.path.basename(csv_file)
                    print(f"\n[{i}/{len(csv_files)}] Processando: {filename}")

                    try:
                        df_result = analyzer.process_csv(csv_file)

                        if not df_result.empty:
                            # Salva resultado individual
                            output_file = os.path.join(
                                output_folder, f"resultado_{filename}"
                            )
                            df_result.to_csv(output_file, index=False, encoding="utf-8")
                            all_results.append(df_result)
                            print(f"  Processado: {len(df_result)} avaliacoes")
                        else:
                            print(f"  Erro ao processar")

                    except Exception as e:
                        print(f"  Erro: {e}")

                # Consolida resultados
                if all_results:
                    consolidated_df = pd.concat(all_results, ignore_index=True)
                    consolidated_file = os.path.join(
                        output_folder, "analise_completa_todos_celulares.csv"
                    )
                    consolidated_df.to_csv(
                        consolidated_file, index=False, encoding="utf-8"
                    )

                    # Gera relatório consolidado
                    summary = analyzer.generate_summary_report(consolidated_df)

                    # Salva relatório
                    report_file = os.path.join(output_folder, "relatorio_completo.json")
                    with open(report_file, "w", encoding="utf-8") as f:
                        json.dump(summary, f, indent=2, ensure_ascii=False)

                    print(f"\n{'='*60}")
                    print("PROCESSAMENTO CONCLUIDO!")
                    print(f"{'='*60}")
                    print(f"Total de avaliações: {len(consolidated_df)}")
                    print(f"Resultados salvos em: {output_folder}")
                    print(f"- Dados consolidados: analise_completa_todos_celulares.csv")
                    print(f"- Relatório: relatorio_completo.json")

                    # Mostra resumo por produto
                    if "produto" in consolidated_df.columns:
                        print(f"\nDistribuicao por produto:")
                        for produto, count in (
                            consolidated_df["produto"].value_counts().items()
                        ):
                            print(f"  - {produto}: {count} avaliacoes")

            except Exception as e:
                print(f"Erro ao processar pasta: {e}")

        elif opcao == "2":
            # Processa arquivo unico
            print("\n" + "-" * 50)
            print("PROCESSAMENTO DE ARQUIVO UNICO")
            print("-" * 50)

            csv_file = input("Digite o caminho completo do arquivo CSV: ").strip()
            if not csv_file or not os.path.exists(csv_file):
                print("Arquivo nao encontrado!")
                continue

            output_file = input(
                "Nome do arquivo de saída (opcional, ENTER para automático): "
            ).strip()
            if not output_file:
                output_file = f"resultado_{os.path.basename(csv_file)}"

            try:
                print(f"\nProcessando: {os.path.basename(csv_file)}")
                df_result = analyzer.process_csv(csv_file, output_file)

                if not df_result.empty:
                    summary = analyzer.generate_summary_report(df_result)

                    print(f"\nProcessamento concluido!")
                    print(f"Total de avaliacoes: {len(df_result)}")
                    print(f"Arquivo salvo: {output_file}")

                    print(f"\nResumo da analise:")
                    print(json.dumps(summary, indent=2, ensure_ascii=False))
                else:
                    print("Nenhum resultado valido gerado")

            except Exception as e:
                print(f"Erro ao processar arquivo: {e}")

        elif opcao == "3":
            # Teste com exemplo
            print("\n" + "-" * 50)
            print("TESTE COM EXEMPLO")
            print("-" * 50)

            print("Produtos disponiveis:")
            for i, produto in enumerate(analyzer.phone_specs.keys(), 1):
                print(f"  {i}. {produto}")

            produto_escolhido = list(analyzer.phone_specs.keys())[
                0
            ]  # Samsung Galaxy A35 5G como padrao

            example_review = """Esse celular e incrivel! A bateria dura mais de um dia inteiro 
            de uso pesado, e a camera tira fotos muito nitidas. O unico problema e que as vezes 
            trava um pouco quando uso muitos apps ao mesmo tempo. A tela tem cores muito vivas 
            e o processador e bem rapido na maioria das tarefas."""

            print(f"\nAnalisando exemplo para: {produto_escolhido}")
            print(f"Avaliacao: {example_review}")

            result = analyzer.analyze_review(example_review, produto_escolhido)

            print(f"\nResultado da analise:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif opcao == "4":
            print("\nEncerrando sistema...")
            break

        else:
            print("Opcao invalida")


if __name__ == "__main__":
    main()
