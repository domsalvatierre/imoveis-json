import pandas as pd
import json
import os
import re

ARQUIVO_EXCEL = 'imoveis.xlsx'
PASTA_SAIDA = 'json_saida'

def limpar_nome_arquivo(nome):
    nome = str(nome).strip()
    nome = re.sub(r'[\\/*?:"<>|]', "_", nome)
    nome = nome.replace(" ", "_")
    return nome

# Criar pasta
os.makedirs(PASTA_SAIDA, exist_ok=True)

# Ler Excel
df = pd.read_excel(ARQUIVO_EXCEL)

# 🔥 PADRONIZAÇÃO FORTE (resolve tudo)
df.columns = df.columns.str.strip().str.upper()

COLUNA_FILTRO = 'SUG'

# Verificação segura
if COLUNA_FILTRO not in df.columns:
    print("❌ Coluna não encontrada!")
    print("Colunas disponíveis:")
    print(df.columns.tolist())
    exit()

# Remover linhas vazias
df = df.dropna(subset=[COLUNA_FILTRO])

# Agrupar
grupos = df.groupby(COLUNA_FILTRO)

# Gerar JSONs
for unidade, grupo in grupos:
    nome_arquivo = limpar_nome_arquivo(unidade)

    dados = grupo.to_dict(orient='records')

    caminho = os.path.join(PASTA_SAIDA, f"{nome_arquivo}.json")

    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

    print(f"✔ Gerado: {caminho}")

print("\n✅ Finalizado com sucesso!")