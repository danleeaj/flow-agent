import requests

url = 'https://jzyhllxxkkwfryebzvdn.supabase.co/functions/v1/get_record_test'

headers = {
    'Authorization': 'Bearer sb_publishable_XLSGi6ODTjNGv09KuveIAw_f8AED19R',
    'apikey': 'sb_publishable_XLSGi6ODTjNGv09KuveIAw_f8AED19R',
    'Content-Type': 'application/json'
}

data = {
    "patient_id": "6f5ace3b-fc16-4a32-9b35-1b936af758eb",
    # "order_id": 1,

}

response = requests.post(url, headers=headers, json=data)

# Check if request was successful
response.raise_for_status()

# Get response data
result = response.json()
print(result)