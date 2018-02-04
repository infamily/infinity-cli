import time
import statistics
from http.client import HTTPConnection

def ping(host):
    port = 80
    timeout = 1

    start = time.time()
    try:
        conn = HTTPConnection(host, port, timeout)
        conn.request("HEAD", "/")
        conn.close()
        up = True
    except:
        up = False

    end = time.time()

    if up:
        return end - start
    else:
        return float('inf')

def multiping(host, times=2):
    measurements = []
    for i in range(times):
        measurements.append(ping(host))
    return statistics.mean(measurements)

