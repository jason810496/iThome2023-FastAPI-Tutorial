import subprocess
from multiprocessing import Pool
import time

file_name = "sample1.mp4"
# url = "http://0.0.0.0:8001/stt/native"
url = "http://0.0.0.0:8001/stt/task"

urls = [url for _ in range(10)]

def upload(url):
    subprocess.call(['curl', '-H', 'Content-Type: multipart/form-data', '-X', 'POST', '-F', f"file=@{file_name};type=video/mp4", url])   

if __name__ == '__main__':
    start = time.time()

    agents = 5
    with Pool(processes=agents) as pool:
        result = pool.map(upload, urls )
    print(result)

    end = time.time()
    print(f"\nTime taken: {end - start}")