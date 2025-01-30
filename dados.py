import serial
import time

# Configuração da porta serial
arduino_port = 'COM3' 
baud_rate = 115200      


ser = serial.Serial(arduino_port, baud_rate)
time.sleep(2)  


def read_arduino_data():
    with open("dados_vibracao.txt", "a") as file:  
        while True:
            if ser.in_waiting > 0:  
                line = ser.readline()
                try:
                    
                    decoded_line = line.decode('utf-8', errors='ignore').strip() 
                    if decoded_line:  
                        print(f"Dados recebidos: {decoded_line}")  
                        file.write(decoded_line + "\n")  
                        process_data(decoded_line)
                except Exception as e:
                    print(f"Erro ao processar a linha: {e}")


def process_data(data):
    try:

        values = data.split(" | ")
        GAcX = float(values[0].split('= ')[1])
        GAcY = float(values[1].split('= ')[1])
        GAcZ = float(values[2].split('= ')[1])

        print(f"Gravidade X: {GAcX} | Gravidade Y: {GAcY} | Gravidade Z: {GAcZ}")
        
    except ValueError:
        print("Erro ao processar os dados recebidos!")


read_arduino_data()

ser.close()
