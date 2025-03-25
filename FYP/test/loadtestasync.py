import aiohttp
import asyncio
import time

URL = "http://127.0.0.1:8000/new"
DATA = {"query": "Hello world"}
NUM_REQUESTS = 5

async def send_request(session):
    start_time = time.time()
    async with session.post(URL, json=DATA) as response:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"Response Time: {response_time:.2f} ms, Status Code: {response.status}")
        return response_time

async def main():
    response_times = []
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session) for _ in range(NUM_REQUESTS)]
        response_times = await asyncio.gather(*tasks)
    
    mean_response_time = sum(response_times) / NUM_REQUESTS
    max_response_time = max(response_times)
    
    print(f"\nMean Response Time: {mean_response_time:.2f} ms")
    print(f"Max Response Time: {max_response_time:.2f} ms")

asyncio.run(main())
