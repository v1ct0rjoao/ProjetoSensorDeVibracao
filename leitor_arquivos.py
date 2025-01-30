import os

pasta_dados = (
    "C:/Users/joaov/Documents/Programação/Python/ProjetoSensorDeVibracao/arquivos_txt"
)


dados_referencia = {}



def processar_linha(linha):
    valores = {}
    partes = linha.strip().split("|")  # Divide os valores pelo separador '|'

    for parte in partes:
        if "=" in parte:  # Verifica se a linha contém "=" para evitar erro
            chave, valor = parte.split("=")
            valores[chave.strip()] = float(valor.strip())  # Convertendo para float
    return valores


# Ler cada arquivo e armazenar os dados no dicionário
for arquivo in os.listdir(pasta_dados):
    if arquivo.endswith(".txt"):  # Garante que só pegue arquivos TXT
        caminho = os.path.join(pasta_dados, arquivo)
        nome_classe = arquivo.replace(".txt", "")  # Nome do estado do motor

        with open(caminho, "r") as f:
            linhas = f.readlines()
            # Armazena os valores processados no dicionário, ignorando linhas vazias
            dados_referencia[nome_classe] = [
                processar_linha(linha) for linha in linhas if linha.strip()
            ]

# Exibir os dados carregados (para teste)
for estado, valores in dados_referencia.items():
    print(f"\nEstado: {estado}")
    for v in valores[:5]:  # Exibir apenas os 5 primeiros para evitar poluir o terminal
        print(v)
