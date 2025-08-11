import os
import requests
import pandas as pd
from dotenv import load_dotenv
import time

# --- Configurações e variaveis --- #
load_dotenv()  # Carrega a chave do arquivo .env
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://dadosabertos.camara.leg.br/api/v2/deputados"
df_despesas = pd.DataFrame(columns=['id', 'nome', 'ano','partido', 'uf', 'valor_liquido', 'valor_glosa'])
anos = [2022,2023,2024]

# --- Função para buscar deputados --- #
def fetch_deputados():
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        print(f"Erro na requisição: {response.status_code} - {response.text}")
        return []
    try:
        data = response.json()
        return data["dados"]
    except Exception as e:
        print(f"Erro ao processar JSON: {e}")
        return []

# --- Loop para buscar todos os deputados --- #
deputados = fetch_deputados()
if not deputados:
    print("Nenhum dado encontrado ou erro na requisição.")
else:
    df_deputados = pd.json_normalize(
        data=deputados['dados']
    )
    print(df_deputados.head())
    ids_deputados = df_deputados["id"].tolist()
    nomes_deputados = df_deputados["nome"].tolist()

# --- Função para buscar despesas --- #
def fetch_despesas_deputado(id_deputado, ano):
    url = f"{BASE_URL}/{id_deputado}/despesas?ano={ano}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica erros HTTP
        return response.json()
    except Exception as e:
        print(f"Erro ao buscar despesas do deputado {id_deputado}: {e}")
        return None

# --- Loop principal: busca despesas para cada deputado --- #
for ano in anos:
    print(f"Buscando despesas para o ano {ano}...")
    for index, row in df_deputados.iterrows():
        print(f"Buscando despesas do deputado {row['nome']}...")
        despesas = fetch_despesas_deputado(row['id'], ano)
        if despesas:
            df_agrupado = pd.json_normalize(data=despesas['dados'])
            despesa_anual = {
                'id': row['id'],
                'nome': row['nome'], 
                'ano': ano,
                'partido': row['partido'],
                'uf': row['uf'],
                'valor_liquido': df_agrupado['valorLiquido'].sum() if not df_agrupado.empty else 0,
                'valor_glosa': df_agrupado['valorGlosa'].sum() if not df_agrupado.empty else 0
            }
            #df_despesas.insert(despesa_anual)
            df_despesas = pd.concat([df_despesas, pd.DataFrame([despesa_anual])], ignore_index=True)
            print(df_agrupado.head())

    time.sleep(1)  # Evita sobrecarregar o servidor

# Salva o resultado final
df_despesas.to_csv("despesas_deputados.csv", index=False, encoding="utf-8-sig")
print("Dados salvos em 'despesas_deputados.csv'!")