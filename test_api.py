import requests
import json

# Test the /api/v1/search/similar endpoint
url = "http://localhost:8000/api/v1/search/similar"

payload = {
    "client_data": {
        "archetype": "market_vendor",
        "employment_type": "informal",
        "debt_ratio": 0.45,
        "years_active": 15,
        "income_stability": 0.85,
        "payment_regularity": 0.88,
        "monthly_income": 2500
    },
    "top_k": 50
}

headers = {
    "Content-Type": "application/json"
}

try:
    print(f"Sending request to {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"Error: {e}")
