from locust import HttpUser, task, between

class UsuarioDeCarga(HttpUser):
    wait_time = between(1, 2.5)

    @task
    def hacer_inferencia(self):
        payload = {
            "island": "Biscoe",
            "culmen_length_mm": 50.0,
            "culmen_depth_mm": 18.5,
            "flipper_length_mm": 200.0,
            "body_mass_g": 4000.0,
            "sex": "MALE"
        }
        # Enviar una petición POST al endpoint /predict
        response = self.client.post("/predict", json=payload)
        # Opcional: validación de respuesta
        if response.status_code != 200:
            print("❌ Error en la inferencia:", response.text)