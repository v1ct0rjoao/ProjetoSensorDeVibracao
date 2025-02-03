import os
import serial
import time
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# Configuração do serial e porta
arduino_port = 'COM3'  # Substitua com a porta correta do seu Arduino
baud_rate = 115200  # Ajuste a taxa de transmissão conforme necessário
ser = serial.Serial(arduino_port, baud_rate)
time.sleep(2)

# Inicializa o scaler e o modelo
scaler = StandardScaler()
model_rf = RandomForestClassifier(n_estimators=100, random_state=42)

# Função para processar dados em tempo real
def processar_linha(linha):
    valores = {}
    partes = linha.strip().split(" | ")
    for parte in partes:
        if "=" in parte:
            chave, valor = parte.split("=")
            valores[chave.strip()] = float(valor.strip())
    return valores

# Função para treinar o modelo com os dados históricos
def treinar_modelo():
    # Verifica se o arquivo CSV já existe, se não cria um
    if not os.path.exists("dados_vibracao.csv"):
        # Criar um DataFrame vazio e salvar como CSV
        df_empty = pd.DataFrame(columns=["GAcX", "GAcY", "GAcZ", "classe"])
        df_empty.to_csv("dados_vibracao.csv", index=False)
        print("Arquivo CSV criado.")

    # Carregar os dados de treinamento para criar o modelo
    df = pd.read_csv("dados_vibracao.csv")

    if not df.empty:
        X = df[['GAcX', 'GAcY', 'GAcZ']]  # Características (dados de aceleração)
        y = df['classe']  # Rótulo (classe)

        # Normaliza os dados históricos
        X_normalized = scaler.fit_transform(X)

        # Treina o modelo Random Forest
        model_rf.fit(X_normalized, y)
        print("Modelo treinado com dados históricos.")
    else:
        print("Nenhum dado disponível no arquivo CSV para treinamento.")

# Função para ler dados em tempo real do Arduino e classificar
def read_arduino_data():
    with open("dados_vibracao.csv", "a") as file:
        while True:
            if ser.in_waiting > 0:  # Verifica se há dados na porta serial
                line = ser.readline()  # Lê a linha de dados
                try:
                    decoded_line = line.decode('utf-8', errors='ignore').strip()  # Decodifica os dados recebidos
                    if decoded_line:
                        print(f"Dados recebidos: {decoded_line}")
                        
                        # Processa a linha para extrair os valores de GAcX, GAcY, GAcZ
                        dados_processados = processar_linha(decoded_line)
                        
                        # Extrai os valores de GAcX, GAcY, GAcZ
                        GAcX = dados_processados.get("GAcX", 0)
                        GAcY = dados_processados.get("GAcY", 0)
                        GAcZ = dados_processados.get("GAcZ", 0)

                        # Normaliza os dados de vibração em tempo real
                        dados_normalizados = scaler.transform([[GAcX, GAcY, GAcZ]])

                        # Classifica os dados usando o modelo Random Forest
                        previsao = model_rf.predict(dados_normalizados)
                        print(f"Classe prevista: {previsao[0]}")

                        # Adiciona a classe ao dicionário
                        dados_processados["classe"] = previsao[0]

                        # Escreve os dados no CSV
                        pd.DataFrame([dados_processados]).to_csv(file, header=False, index=False)

                except Exception as e:
                    print(f"Erro ao processar a linha: {e}")

# Treina o modelo antes de começar a leitura em tempo real
treinar_modelo()

# Iniciar a leitura e classificação em tempo real
read_arduino_data()
