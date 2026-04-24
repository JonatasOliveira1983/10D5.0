import os.path
import logging
from google_auth_oauthlib.flow import InstalledAppFlow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GoogleAuth")

# Escopos necessários
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    """
    Realiza o fluxo de autenticação e salva o token.json.
    """
    creds_path = 'client_secret.json'
    token_path = 'token.json'
    
    if not os.path.exists(creds_path):
        logger.error(f"❌ Arquivo {creds_path} não encontrado!")
        return

    logger.info("🚀 Iniciando fluxo de autenticação (MODO DESKTOP)...")
    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    
    # O Google Desktop Flow gerencia a porta automaticamente.
    # Se o Almirante criou como "App de área de trabalho", isso deve funcionar sem configurar URIs.
    creds = flow.run_local_server(port=0, open_browser=False)
    
    # Salva o token para uso futuro
    with open(token_path, 'w') as token:
        token.write(creds.to_json())
    
    logger.info("✅ Autenticação concluída! O arquivo token.json foi gerado com sucesso.")

if __name__ == '__main__':
    main()
