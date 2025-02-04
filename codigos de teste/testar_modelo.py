import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler

# Carregar o modelo treinado
with open("modelo_vibracao.pkl", "rb") as file:
    model_rf, scaler = pickle.load(file)  # Carrega modelo e scaler

# Função para testar o modelo com novos dados
def prever_estado(novos_dados):
    # Converter os dados para um formato adequado (numpy array)
    novos_dados = np.array(novos_dados).reshape(1, -1)  # Redimensiona para 1 amostra

    # Normalizar os dados usando o mesmo scaler do treinamento
    novos_dados = scaler.transform(novos_dados)

    # Fazer a previsão
    estado_previsto = model_rf.predict(novos_dados)
    
    return estado_previsto[0]  # Retorna o estado previsto

# --- Exemplo de uso ---

# Simulando uma nova leitura do sensor (substitua pelos valores reais)
nova_leitura = [0.01, -0.01, 0.00]  # [GAcX, GAcY, GAcZ]

# Prever o estado da máquina
estado_predito = prever_estado(nova_leitura)
print(f"Estado previsto: {estado_predito}")
