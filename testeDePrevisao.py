import os 
import serial
import time
import csv
import joblib
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import numpy as np

# 🔹 Configuração da porta serial
arduino_port = 'COM3'  # Altere conforme necessário
baud_rate = 115200
ser = serial.Serial(arduino_port, baud_rate)
time.sleep(2)

# 🔹 Caminhos dos arquivos
pasta_referencia = r'C:\Users\joaov\Documents\Programação\Python\ProjetoSensorDeVibracao\arquivos_txt'
modelo_path = "modelo_vibracao.pkl"
scaler_path = "scaler.pkl"
dados_csv_path = "dados_vibracao.csv"
dados_fft_csv_path = "dados_fft.csv"

# 🔹 Inicializa contador de leituras
contador_leituras = 0

# Buffer de dados para armazenar as leituras
BUFFER_SIZE = 100  # Tamanho do buffer para armazenar as leituras temporais
buffer_x, buffer_y, buffer_z = [], [], []

# 🔹 Função para processar uma linha recebida do sensor
def processar_linha(linha):
    valores = {}
    partes = linha.strip().split("|")
    for parte in partes:
        if "=" in parte:
            chave, valor = parte.split("=")
            valores[chave.strip()] = float(valor.strip())
    return valores

# 🔹 Carregar dados de referência para treinamento
def carregar_dados_referencia():
    X, y = [], []
    for arquivo in os.listdir(pasta_referencia):
        if arquivo.endswith(".txt"):
            caminho = os.path.join(pasta_referencia, arquivo)
            estado_maquina = arquivo.replace(".txt", "")
            with open(caminho, "r") as f:
                linhas = f.readlines()
                for linha in linhas:
                    if linha.strip():
                        valores = processar_linha(linha)
                        if 'GAcX' in valores and 'GAcY' in valores and 'GAcZ' in valores:
                            X.append([valores['GAcX'], valores['GAcY'], valores['GAcZ']])
                            y.append(estado_maquina)
    return X, y

# 🔹 Criar janelas temporais (para a previsão com base em múltiplas leituras)
def criar_janelas_temporais(dados, janela_tamanho=10):
    X, y = [], []
    for i in range(len(dados) - janela_tamanho):
        janela = dados[i:i+janela_tamanho]
        # Características agregadas: média e desvio padrão
        media = np.mean(janela, axis=0)  # Média das últimas "janela_tamanho" leituras
        desvio_padrao = np.std(janela, axis=0)  # Desvio padrão
        X.append(np.concatenate([media, desvio_padrao]))  # Adiciona a média e o desvio
        y.append(dados[i + janela_tamanho][0])  # Estado da máquina após a janela
    return np.array(X), np.array(y)

# 🔹 Treinar o modelo de Machine Learning
def treinar_modelo():
    X, y = carregar_dados_referencia()
    
    if not X or not y:
        print("Nenhum dado de referência encontrado! O treinamento não pode ser feito.")
        return None, None

    X, y = criar_janelas_temporais(X, janela_tamanho=3)  # Criar janelas temporais

    scaler = StandardScaler()
    X_normalized = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.2, random_state=42)

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    # Salvar modelo e scaler
    joblib.dump(modelo, modelo_path)
    joblib.dump(scaler, scaler_path)
    print("✅ Modelo treinado e salvo com sucesso!")

    return modelo, scaler

# 🔹 Carregar modelo treinado (ou treinar se não existir)
def carregar_modelo():
    if os.path.exists(modelo_path) and os.path.exists(scaler_path):
        try:
            modelo = joblib.load(modelo_path)
            scaler = joblib.load(scaler_path)
            print("✅ Modelo carregado do arquivo!")
            return modelo, scaler
        except Exception as e:
            print(f"⚠️ Erro ao carregar o modelo: {e}. Treinando novamente...")

    return treinar_modelo()

# 🔹 Função para calcular a FFT
def transformar_fourier(dados):
    try:
        dados_array = np.array(dados)
        fft_resultado = np.fft.fft(dados_array)
        fft_amplitude = np.abs(fft_resultado)
        return fft_amplitude.tolist()
    except Exception as e:
        print(f"⚠️ Erro ao aplicar FFT: {e}")
        return []

# 🔹 Função para salvar os dados FFT no CSV
def salvar_dados_fft(fft_x, fft_y, fft_z, estado_maquina):
    with open(dados_fft_csv_path, "a", newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(['Timestamp', 'FFT_GAcX', 'FFT_GAcY', 'FFT_GAcZ', 'Estado_Maquina'])

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([timestamp, fft_x, fft_y, fft_z, estado_maquina])

# 🔹 Ler dados do Arduino e prever estado da máquina
def read_arduino_data():
    global contador_leituras
    modelo, scaler = carregar_modelo()

    with open(dados_csv_path, "a", newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(['Timestamp', 'GAcX', 'GAcY', 'GAcZ'])

        while True:
            if ser.in_waiting > 0:
                line = ser.readline()
                try:
                    decoded_line = line.decode('utf-8', errors='ignore').strip()
                    if decoded_line:
                        valores = processar_linha(decoded_line)
                        if 'GAcX' in valores and 'GAcY' in valores and 'GAcZ' in valores:
                            # Adiciona os dados ao buffer
                            buffer_x.append(valores['GAcX'])
                            buffer_y.append(valores['GAcY'])
                            buffer_z.append(valores['GAcZ'])

                            # Quando o buffer estiver cheio, aplica a FFT
                            if len(buffer_x) >= BUFFER_SIZE:
                                fft_x = transformar_fourier(buffer_x)
                                fft_y = transformar_fourier(buffer_y)
                                fft_z = transformar_fourier(buffer_z)

                                # Limpa o buffer após aplicar a FFT
                                buffer_x.clear()
                                buffer_y.clear()
                                buffer_z.clear()

                                # Salva os dados de FFT no CSV
                                estado_maquina = "bom_estado"  # Ajuste conforme a lógica de estado
                                salvar_dados_fft(fft_x, fft_y, fft_z, estado_maquina)

                            # Grava os dados no arquivo CSV
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            writer.writerow([timestamp, valores['GAcX'], valores['GAcY'], valores['GAcZ']])
                            contador_leituras += 1

                            # 🔹 A cada 1000 leituras, treina o modelo novamente
                            if contador_leituras % 1000 == 0:
                                print("🔄 Treinando modelo com novas leituras...")
                                modelo, scaler = treinar_modelo()

                            # 🔹 Normaliza os dados e prevê estado da máquina
                            dados_normalizados = scaler.transform([[valores['GAcX'], valores['GAcY'], valores['GAcZ']]])
                            estado_previsto = modelo.predict(dados_normalizados)[0]

                            # Atualizando o estado da máquina em tempo real
                            print(f"🟢 Estado previsto da máquina: {estado_previsto}")
                except Exception as e:
                    print(f"⚠️ Erro ao processar a linha: {e}")

# 🔹 Executar leitura contínua dos dados
if __name__ == "__main__":
    read_arduino_data()

ser.close()
