import requests
import time
import json

def run_test():
    url = "http://127.0.0.1:8085/api/signals"
    # we don't have a direct endpoint to inject raw signals, but we can check if the API is alive
    print("O backend não tem endpoint pra injetar array na queue direto.")
    print("Vamos observar o log ao vivo.")

if __name__ == "__main__":
    run_test()
