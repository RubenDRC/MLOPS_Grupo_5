import time
import requests
from datetime import date

URL = "http://10.43.101.188:30190/predict"

example = {
    "brokered_by": "51868.0",
    "status": "for_sale",
    "bed": 5,
    "bath": 3,
    "acre_lot": 0.12,
    "street": "1499905.0",
    "city": "Enfield",
    "state": "Connecticut",
    "zip_code": "6082.0",
    "house_size": 3117,
    "prev_sold_date": date(2014, 7, 1).isoformat()
}

def load_test(n_requests: int = 100, interval: float = 0.5):
    for i in range(n_requests):
        try:
            response = requests.post(f"{URL}?model_name=RandomForestModel_Move", json=example)
            print(f"Request {i+1}: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"Request {i+1}: Error - {e}")
        time.sleep(interval)

if __name__ == "__main__":
    load_test()


