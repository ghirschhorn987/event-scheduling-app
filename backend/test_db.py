import requests
res = requests.get("http://localhost:8000/api/admin/events", headers={"Authorization": "Bearer mock-token-admin"})
print(res.status_code)
print(res.json())
