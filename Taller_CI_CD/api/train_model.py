# train_model.py
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Cargar dataset
df = pd.read_csv("app/data/penguins_size.csv")

# Eliminar filas con valores nulos
df.dropna(inplace=True)

# Variables predictoras y objetivo
X = df[['Culmen Length (mm)', 'Culmen Depth (mm)', 'Flipper Length (mm)', 'Body Mass (g)']]
y = df['Species']

# Codificar la variable objetivo
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Entrenamiento del modelo
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Guardar modelo y codificador
joblib.dump(model, "app/model.pkl")
joblib.dump(le, "app/label_encoder.pkl")

