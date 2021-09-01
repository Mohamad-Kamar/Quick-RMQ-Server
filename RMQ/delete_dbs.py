
import requests

payload={}
headers = {}

response_service = requests.request("DELETE", "http://localhost:9200/l3vpn-ingestion-engine-services", headers=headers)
response_requests = requests.request("DELETE", "http://localhost:9200/l3vpn-ingestion-engine-requests", headers=headers)

print(response_service.text)
print(response_requests.text)
