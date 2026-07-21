import requests
import time
import random
import json
import os
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging


class MercadoLivreReviewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.setup_logging()

    def setup_logging(self):
        """Configura logging para monitorar o processo"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("mercadolivre_scraper.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def setup_session(self):
        """Configura a sessão para simular um navegador real"""
        # User agents realistas
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ]

        # Headers padrão para simular navegador
        self.session.headers.update(
            {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            }
        )

        # Configurar retry strategy
        retry_strategy = Retry(
            total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def simulate_human_behavior(self):
        """Simula comportamento humano com delays aleatórios"""
        delay = random.uniform(2.0, 5.0)
        self.logger.info(f"Aguardando {delay:.2f} segundos...")
        time.sleep(delay)

    def visit_homepage(self):
        """Visita a homepage do Mercado Livre para estabelecer sessão"""
        try:
            self.logger.info("Visitando homepage do Mercado Livre...")
            response = self.session.get("https://www.mercadolivre.com.br/")
            response.raise_for_status()
            self.simulate_human_behavior()
            return True
        except Exception as e:
            self.logger.error(f"Erro ao visitar homepage: {e}")
            return False

    def login(self, email, password):
        """Faz login no Mercado Livre"""
        try:
            self.logger.info("Iniciando processo de login...")

            # Primeiro, obter a página de login
            login_url = "https://www.mercadolivre.com/jms/mlb/lgz/login?platform_id=ML&go=https%3A%2F%2Fwww.mercadolivre.com.br%2F&loginType=explicit#nav-header"
            response = self.session.get(login_url)
            response.raise_for_status()

            self.simulate_human_behavior()

            # Atualizar headers para o login
            self.session.headers.update(
                {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://www.mercadolivre.com.br",
                    "Referer": login_url,
                }
            )

            # Dados do login
            login_data = {
                "user_id": email,
                "password": password,
                "two_factor_auth_token": "",
                "loginTimeZone": "-180",
                "keep_me": "true",
            }

            # Fazer POST do login
            login_response = self.session.post(
                "https://www.mercadolivre.com.br/jms/mlb/lgn/loginservice",
                data=login_data,
                allow_redirects=True,
            )

            # Verificar se o login foi bem-sucedido
            if (
                "user-nav" in login_response.text
                or "account-nav" in login_response.text
            ):
                self.logger.info("Login realizado com sucesso!")
                self.save_cookies()
                return True
            else:
                self.logger.error("Falha no login - credenciais podem estar incorretas")
                return False

        except Exception as e:
            self.logger.error(f"Erro durante o login: {e}")
            return False

    def save_cookies(self):
        """Salva cookies da sessão"""
        try:
            cookies_dict = dict(self.session.cookies)
            with open("mercadolivre_cookies.json", "w") as f:
                json.dump(cookies_dict, f, indent=2)
            self.logger.info("Cookies salvos com sucesso!")
        except Exception as e:
            self.logger.error(f"Erro ao salvar cookies: {e}")

    def load_cookies(self):
        """Carrega cookies salvos"""
        try:
            if os.path.exists("mercadolivre_cookies.json"):
                with open("mercadolivre_cookies.json", "r") as f:
                    cookies_dict = json.load(f)
                    self.session.cookies.update(cookies_dict)
                self.logger.info("Cookies carregados com sucesso!")
                return True
        except Exception as e:
            self.logger.error(f"Erro ao carregar cookies: {e}")
        return False

    def get_reviews(self, product_id, offset=0, limit=30):
        """Obtém avaliações de um produto específico"""
        try:
            # Atualizar headers para API
            api_headers = {
                "Accept": "application/json, text/plain, */*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"https://www.mercadolivre.com.br/{product_id}",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            }

            # URL da API com parâmetros
            api_url = f"https://www.mercadolivre.com.br/noindex/catalog/reviews/{product_id}/search"
            params = {
                "objectId": product_id,
                "siteId": "MLB",
                "isItem": "false",
                "offset": offset,
                "limit": limit,
                "x-is-webview": "false",
            }

            self.logger.info(f"Coletando avaliações - offset: {offset}, limit: {limit}")

            response = self.session.get(
                api_url, params=params, headers=api_headers, timeout=30
            )
            response.raise_for_status()

            return response.json()

        except Exception as e:
            self.logger.error(f"Erro ao obter avaliações: {e}")
            return None

    def collect_all_reviews(self, product_id, max_reviews=None):
        """Coleta todas as avaliações de um produto"""
        all_reviews = []
        offset = 0
        limit = 30
        collected = 0

        self.logger.info(f"Iniciando coleta de avaliações para produto: {product_id}")

        while True:
            # Verificar limite máximo
            if max_reviews and collected >= max_reviews:
                break

            # Simular comportamento humano
            self.simulate_human_behavior()

            # Rotacionar User-Agent ocasionalmente
            if random.random() < 0.1:  # 10% de chance
                self.session.headers["User-Agent"] = random.choice(self.user_agents)

            # Obter avaliações
            data = self.get_reviews(product_id, offset, limit)

            if not data or "reviews" not in data:
                self.logger.warning("Não foi possível obter mais avaliações")
                break

            reviews = data["reviews"]

            if not reviews:
                self.logger.info("Não há mais avaliações para coletar")
                break

            all_reviews.extend(reviews)
            collected += len(reviews)
            offset += limit

            self.logger.info(f"Coletadas {len(reviews)} avaliações. Total: {collected}")

            # Delay mais longo ocasionalmente
            if random.random() < 0.15:  # 15% de chance
                extra_delay = random.uniform(10.0, 20.0)
                self.logger.info(f"Delay extra de {extra_delay:.2f} segundos...")
                time.sleep(extra_delay)

        return all_reviews

    def save_reviews(self, reviews, product_id):
        """Salva as avaliações coletadas"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reviews_{product_id}_{timestamp}.json"

            # Processar dados para salvar apenas o essencial
            processed_reviews = []
            for review in reviews:
                processed_review = {
                    "id": review.get("id"),
                    "rating": review.get("rating"),
                    "title": review.get("title", {}).get("text", ""),
                    "comment": review.get("comment", {})
                    .get("content", {})
                    .get("text", ""),
                    "date": review.get("date", ""),
                    "helpful_votes": (
                        review.get("actions", [{}])[0].get("value", 0)
                        if review.get("actions")
                        else 0
                    ),
                    "official_store": bool(review.get("official_store")),
                    "has_media": bool(review.get("media")),
                }
                processed_reviews.append(processed_review)

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "product_id": product_id,
                        "collection_date": timestamp,
                        "total_reviews": len(processed_reviews),
                        "reviews": processed_reviews,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            self.logger.info(f"Avaliações salvas em: {filename}")

            # Salvar também um CSV simples
            csv_filename = f"reviews_{product_id}_{timestamp}.csv"
            self.save_reviews_csv(processed_reviews, csv_filename)

        except Exception as e:
            self.logger.error(f"Erro ao salvar avaliações: {e}")

    def save_reviews_csv(self, reviews, filename):
        """Salva avaliações em formato CSV"""
        try:
            import csv

            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
                    "id",
                    "rating",
                    "title",
                    "comment",
                    "date",
                    "helpful_votes",
                    "official_store",
                    "has_media",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for review in reviews:
                    writer.writerow(review)

            self.logger.info(f"CSV salvo: {filename}")

        except Exception as e:
            self.logger.error(f"Erro ao salvar CSV: {e}")


def main():
    """Função principal"""
    scraper = MercadoLivreReviewsScraper()

    # Carregar cookies se existirem
    if scraper.load_cookies():
        print("Cookies carregados. Tentando usar sessão existente...")
    else:
        print("Nenhum cookie encontrado. Será necessário fazer login.")

        # Solicitar credenciais
        email = input("Digite seu email do Mercado Livre: ")
        password = input("Digite sua senha: ")

        # Visitar homepage primeiro
        if not scraper.visit_homepage():
            print("Erro ao acessar o site. Verifique sua conexão.")
            return

        # Fazer login
        if not scraper.login(email, password):
            print("Falha no login. Verifique suas credenciais.")
            return

    # ID do produto (exemplo: MLB22514940)
    product_id = input("Digite o ID do produto (ex: MLB22514940): ").strip()

    if not product_id:
        product_id = "MLB22514940"  # Produto do exemplo

    # Coletar avaliações
    try:
        max_reviews = input("Número máximo de avaliações (Enter para todas): ").strip()
        max_reviews = int(max_reviews) if max_reviews else None

        reviews = scraper.collect_all_reviews(product_id, max_reviews)

        if reviews:
            print(f"\nColetadas {len(reviews)} avaliações!")
            scraper.save_reviews(reviews, product_id)

            # Estatísticas básicas
            ratings = [r.get("rating", 0) for r in reviews]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            print(f"Avaliação média: {avg_rating:.2f}")

        else:
            print("Nenhuma avaliação foi coletada.")

    except KeyboardInterrupt:
        print("\nColeta interrompida pelo usuário.")
    except Exception as e:
        print(f"Erro durante a coleta: {e}")


if __name__ == "__main__":
    main()
