import pandas as pd  

''' --- TODO --- #
- Implementar a lógica para buscar e processar os dados dos deputados
- Adicionar tratamento de erros e logs
- Testar a aplicação com dados reais'''
# Carregar dados das despesas dos deputados
df = pd.read_csv("despesas_deputados.csv")
print(df.head())