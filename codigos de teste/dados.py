import serial
import time
import csv
from datetime import datetime

# Configuração da porta serial
arduino_port = 'COM3'  
baud_rate = 115200      

ser = serial.Serial(arduino_port, baud_rate)
time.sleep(2)  # Aguarda a conexão estabilizar

# Função para ler e armazenar os dados
def read_arduino_data():
    with open("dados_vibracao.csv", "a", newline='') as file:  
        writer = csv.writer(file)
        
        # Adiciona cabeçalho, caso o arquivo esteja vazio
        if file.tell() == 0:
            writer.writerow(['Timestamp', 'Gravidade X', 'Gravidade Y', 'Gravidade Z'])
        
        while True:
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

# Inicia a leitura dos dados
read_arduino_data()

ser.close()
