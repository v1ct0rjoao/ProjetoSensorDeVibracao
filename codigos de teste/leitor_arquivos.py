import os
import pandas as pd

# Caminho para a pasta dos arquivos de dados
pasta_dados = "C:/Users/joaov/Documents/Programação/Python/ProjetoSensorDeVibracao/arquivos_txt"

# Lista para armazenar todos os dados que vão para o DataFrame
dados_lista = []

def processar_linha(linha):
    valores = {}
    partes = linha.strip().split("|")  # Divide os valores pelo separador '|'

    for parte in partes:
        if "=" in parte:  # Verifica se a linha contém "=" para evitar erro
            chave, valor = parte.split("=")
            valores[chave.strip()] = float(valor.strip())  # Convertendo para float
    return valores

# Ler cada arquivo e armazenar os dados no DataFrame
for arquivo in os.listdir(pasta_dados):
    if arquivo.endswith(".txt"):  # Garante que só pegue arquivos TXT
        caminho = os.path.join(pasta_dados, arquivo)
        nome_classe = arquivo.replace(".txt", "")  # Nome do estado do motor

        with open(caminho, "r") as f:
            linhas = f.readlines()
            # Processa cada linha do arquivo e adiciona ao DataFrame
            for linha in linhas:
                if linha.strip():  # Ignora linhas vazias
                    valores = processar_linha(linha)
                    # Adiciona o estado (nome_classe) como a coluna 'Estado'
                    valores['Estado'] = nome_classe
                    dados_lista.append(valores)

# Cria o DataFrame com todos os dados coletados
df = pd.DataFrame(dados_lista)

# Exibe os primeiros registros para verificação
print(df.head())

# Agora o DataFrame 'df' está pronto para ser utilizado para o treinamento do modelo
