import time
import requests
from datetime import date

URL = "http://api:8000/predict"

example = {
    "brokered_by": "RE/MAX",
    "status": "for_sale",
    "bed": 3,
    "bath": 2,
    "acre_lot": 0.25,
    "street": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "zip_code": "62704",
    "house_size": 1500,
    "prev_sold_date": date(2020, 1, 1).isoformat()
}

def load_test(n_requests: int = 100, interval: float = 0.5):
    for i in range(n_requests):
        try:
            response = requests.post(f"{URL}?model_name=RandomForestModel", json=example)
            print(f"Request {i+1}: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"Request {i+1}: Error - {e}")
        time.sleep(interval)

if __name__ == "__main__":
    load_test()

