import requests
import pandas as pd
import time

# --- Configurações e variáveis --- #
BASE_URL = "https://dadosabertos.camara.leg.br/api/v2/deputados"
df_despesas = pd.DataFrame(columns=['id', 'nome', 'ano', 'partido', 'uf', 'valor_liquido', 'valor_glosa'])
anos = [2023, 2024, 2025]

# --- Função para buscar deputados --- #
def fetch_deputados():
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        print(f"Erro na requisição: {response.status_code} - {response.text}")
        return []
    try:
        data = response.json()
        return data['dados']
    except Exception as e:
        print(f"Erro ao processar JSON: {e}")
        return []

# --- Função para buscar despesas por deputado e ano --- #
def fetch_despesas_deputado(id_deputado, ano):
    url = f"{BASE_URL}/{id_deputado}/despesas?ano={ano}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao buscar despesas do deputado {id_deputado}: {e}")
        return None

# --- Loop para buscar todas as despesas dos deputados --- #
deputados = fetch_deputados()
if not deputados:
    print("Nenhum dado encontrado ou erro na requisição.")
else:
    df_deputados = pd.json_normalize(deputados)
    print(df_deputados.head())

    for ano in anos:
        print(f"Buscando despesas para o ano {ano}...")
        for index, row in df_deputados.iterrows():
            print(f"Buscando despesas do deputado {row['nome']}...")
            despesas = fetch_despesas_deputado(row['id'], ano)
            if despesas and 'dados' in despesas:
                df_agrupado = pd.json_normalize(data=despesas['dados'])
                despesa_anual = {
                    'id': row['id'],
                    'nome': row['nome'],
                    'ano': ano,
                    'partido': row['siglaPartido'] if 'siglaPartido' in row else row.get('partido', ''),
                    'uf': row['siglaUf'] if 'siglaUf' in row else row.get('uf', ''),
                    'valor_liquido': df_agrupado['valorLiquido'].sum() if not df_agrupado.empty else 0,
                    'valor_glosa': df_agrupado['valorGlosa'].sum() if not df_agrupado.empty else 0
                }
                df_despesas = pd.concat([df_despesas, pd.DataFrame([despesa_anual])], ignore_index=True)
                print(df_agrupado.head())
            else:
                print(f"Nenhuma despesa encontrada para o deputado {row['nome']} no ano {ano}.")
        time.sleep(1)  # Evita sobrecarregar o servidor

    # Salva o resultado final
    df_despesas.to_csv("despesas_deputados.csv", index=False, encoding="utf-8-sig")
    print("Dados salvos em 'despesas_deputados.csv'!")