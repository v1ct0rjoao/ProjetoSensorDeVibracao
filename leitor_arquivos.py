import os 

pasta_dados = "C:/Users/joaov/Documents/Programação/Python/ProjetoSensorDeVibracao/arquivos_txt"

dados_referencia = {}

def processar_linha(linha):
    valores = {}
    partes = linha.strip().split('|')
    for parte in partes:
        chave, valor = parte.split('=')
        valores[chave.strip()] = float(valor.strip())
    return valores

for arquivo in os.listdir(pasta_dados):
    if arquivo.endswith(".txt"):
        caminho = os.path.join(pasta_dados,arquivo)
        nome_classe = arquivo.replace(".txt", "")
        
     
        with open(caminho, "r") as f:
            linhas = f.readlines()
            # Armazena os valores processados no dicionário
            dados_referencia[nome_classe] = [processar_linha(linha) for linha in linhas]

# Exibir os dados carregados (para teste)
for estado, valores in dados_referencia.items():
    print(f"\nEstado: {estado}")
    for v in valores[:5]:  # Exibir apenas os 5 primeiros para não poluir o terminal
        print(v)