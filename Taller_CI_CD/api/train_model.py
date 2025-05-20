import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib


# Prueba cambios 3

# Leer el dataset desde la carpeta local
df = pd.read_csv("data/penguins_size.csv")

# Eliminar filas con valores faltantes
df = df.dropna()

# Seleccionar características y variable objetivo
X = df[['culmen_length_mm', 'culmen_depth_mm', 'flipper_length_mm', 'body_mass_g']]
y = df['species']

# Codificar la variable objetivo
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Entrenar modelo
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y_encoded)

# Guardar el modelo y el codificador
joblib.dump(model, "app/model.pkl")
joblib.dump(le, "app/label_encoder.pkl")

print("Modelo entrenado y guardado correctamente.")

