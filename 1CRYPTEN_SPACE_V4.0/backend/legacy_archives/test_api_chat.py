import httpx
import json

def test_chat():
    url = "http://127.0.0.1:8085/api/chat"
    payload = {"message": "Olá JARVIS, você está me ouvindo?"}
    headers = {"Content-Type": "application/json"}
    
    print(f"Enviando mensagem para {url}...")
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
        print(f"Status Code: {response.status_code}")
        print("Resposta do Servidor:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erro ao conectar: {e}")

if __name__ == "__main__":
    test_chat()
