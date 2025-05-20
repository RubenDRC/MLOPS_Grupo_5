import time
import requests

URL = "http://api:8000/predict"

example = {
    "island": "Torgersen",
    "culmen_length_mm": 39.1,
    "culmen_depth_mm": 18.7,
    "flipper_length_mm": 181.0,
    "body_mass_g": 3750.0,
    "sex": "MALE"
}

def load_test(n_requests: int = 100, interval: float = 0.1):
    for i in range(n_requests):
        try:
            response = requests.post(URL, json=example)
            print(f"Request {i+1}: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"Request {i+1}: Error - {e}")
        time.sleep(interval)

if __name__ == "__main__":
    load_test()

