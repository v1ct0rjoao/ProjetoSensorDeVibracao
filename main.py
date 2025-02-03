import serial
import time
import csv
from datetime import datetime
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

# Configuração da porta serial
arduino_port = 'COM3'  
baud_rate = 115200
ser = serial.Serial(arduino_port, baud_rate)
time.sleep(2)  # Aguarda a conexão estabilizar

# Função para ler e armazenar os dados
def read_arduino_data(tempo_maximo=10):
    with open("dados_vibracao.csv", "a", newline='') as file:  
        writer = csv.writer(file)
        
        # Adiciona cabeçalho, caso o arquivo esteja vazio
        if file.tell() == 0:
            writer.writerow(['Timestamp', 'Gravidade X', 'Gravidade Y', 'Gravidade Z'])

        start_time = time.time()
        while time.time() - start_time < tempo_maximo:  # Define tempo máximo de coleta de dados
            if ser.in_waiting > 0:
                line = ser.readline()
                try:
                    decoded_line = line.decode('utf-8', errors='ignore').strip()
                    if decoded_line:
                        print(f"Dados recebidos: {decoded_line}")  
                        # Processa e escreve os dados no CSV
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        GAcX, GAcY, GAcZ = process_data(decoded_line)
                        writer.writerow([timestamp, GAcX, GAcY, GAcZ])
                except Exception as e:
                    print(f"Erro ao processar a linha: {e}")

# Função para processar os dados do sensor
def process_data(data):
    try:
        values = data.split(" | ")
        GAcX = float(values[0].split('= ')[1])
        GAcY = float(values[1].split('= ')[1])
        GAcZ = float(values[2].split('= ')[1])

        print(f"Gravidade X: {GAcX} | Gravidade Y: {GAcY} | Gravidade Z: {GAcZ}")
        return GAcX, GAcY, GAcZ
        
    except ValueError:
        print("Erro ao processar os dados recebidos!")
        return 0, 0, 0

# Função para carregar os dados do CSV e treinar o modelo
def treinar_modelo():
    # Carregar os dados do CSV
    df = pd.read_csv('dados_vibracao.csv')
    print(df.head())

    # Separar as características (X) e o rótulo (y)
    X = df[['Gravidade X', 'Gravidade Y', 'Gravidade Z']]  # Características
    y = df['Timestamp']  # Pode ser qualquer rótulo que você tenha (nesse caso, 'Timestamp')

    # Normalizar os dados (não é estritamente necessário para RandomForest, mas ajuda em outros modelos)
    scaler = StandardScaler()
    X_normalized = scaler.fit_transform(X)

    # Separar os dados em treinamento (80%) e teste (20%)
    X_train, X_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.2, random_state=42)

    # Modelo RandomForest
    model_rf = RandomForestClassifier(n_estimators=100, random_state=42)

    # Treinamento e avaliação do modelo RandomForest
    model_rf.fit(X_train, y_train)
    y_pred_rf = model_rf.predict(X_test)



# Função principal para executar o código
def main():
    # Passo 1: Coletar e armazenar os dados do Arduino
    print("Coletando dados do Arduino por 10 segundos...")
    read_arduino_data(tempo_maximo=10)  # Defina o tempo máximo de coleta aqui

    # Passo 2: Treinar o modelo Random Forest com os dados coletados
    print("Treinando o modelo Random Forest...")
    treinar_modelo()

# Executar o programa
if __name__ == "__main__":
    main()

ser.close()
