import pickle

# Supondo que você treinou o modelo e normalizou os dados
with open("modelo_vibracao.pkl", "wb") as file:
    pickle.dump((model_rf, scaler), file)  # Salva o modelo e o scaler juntos
