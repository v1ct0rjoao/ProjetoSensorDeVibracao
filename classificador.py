from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import pandas as pd

# Carregar os dados
df = pd.read_csv("dados_vibracao.csv")

# Separar as características (X) e o rótulo (y)
X = df[['GAcX', 'GAcY', 'GAcZ']]  # Características
y = df['classe']  # Rótulo (classe)

# Normalizar os dados (importante para SVM e Redes Neurais, mas no caso do Random Forest não é necessário)
scaler = StandardScaler()
X_normalized = scaler.fit_transform(X)

# Separar os dados em treinamento (80%) e teste (20%)
X_train, X_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.2, random_state=42)

# Modelo RandomForest
model_rf = RandomForestClassifier(n_estimators=100, random_state=42)

# Treinamento e avaliação do modelo RandomForest
model_rf.fit(X_train, y_train)
y_pred_rf = model_rf.predict(X_test)

# Resultados
print("Random Forest:")
print(f"Acurácia: {accuracy_score(y_test, y_pred_rf)}")
print(f"Matriz de Confusão:\n{confusion_matrix(y_test, y_pred_rf)}\n")
