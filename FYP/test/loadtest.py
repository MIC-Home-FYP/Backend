import requests
import time

URL = "http://192.168.0.155:8000/new"
DATA = {"query": "Hello world"}
NUM_REQUESTS = 10

response_times = []

for _ in range(NUM_REQUESTS):
    start_time = time.time()
    response = requests.post(URL, json=DATA)
    end_time = time.time()
    
    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
    response_times.append(response_time)
    
    print(f"Response Time: {response_time:.2f} ms, Status Code: {response.status_code}")

mean_response_time = sum(response_times) / NUM_REQUESTS
max_response_time = max(response_times)

print(f"\nMean Response Time: {mean_response_time:.2f} ms")
print(f"Max Response Time: {max_response_time:.2f} ms")
