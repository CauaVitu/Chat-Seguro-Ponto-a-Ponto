import socket
# Seus módulos
from key_generation import (
    generate_rsa_keypair, 
    serialize_key_rsa, 
    deserialize_public_key_rsa,
    generate_aes_key
)
from encryption_and_decryption import rsa_encrypt, rsa_decrypt

# Configurações de conexão
HOST = '127.0.0.1'
PORT = 5556

def iniciar_troca_segura():
    print ("Bem-vindo ao Chat Seguro Ponto-a-Ponto!")
    print ("Digite 'sair' a qualquer momento para encerrar a conexão.")
    tipo = input("Digite 's' para ser servidor ou 'c' para ser cliente: ").lower()
    
    sock = None

    # CONEXÃO 
    if tipo == 's': # SERVIDOR 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            #Aguardamos conexão
            s.bind((HOST, PORT))
            s.listen(1)
            print(f"[AGUARDANDO] Esperando conexão na porta {PORT}...")
            # Aceita a conexão
            sock, addr = s.accept()
            print(f"[CONECTADO] Aceitou conexão de {addr}")
        # Printa qualquer erro e sai
        except Exception as e:
            print(f"Erro: {e}")
            return
    
    elif tipo == 'c': # CLIENTE 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Tenta conectar ao servidor
        try:    
            sock.connect((HOST, PORT))
            print("[CONECTADO] Conexão estabelecida!")
        except:
            print("[ERRO] Falha ao conectar.")
            return

    # Troca de chaves públicas
    print("\n--- FASE 1: TROCA DE CHAVES PÚBLICAS ---")
    
    # Gera meu par de chaves (Um dos pares será usado para descriptografar a chave AES)
    my_private, my_public = generate_rsa_keypair()
    my_pub_bytes = serialize_key_rsa(my_public)
    
    # Envia minha pública e recebe a do outro
    sock.send(my_pub_bytes)
    peer_pub_bytes = sock.recv(4096)
    peer_public_key = deserialize_public_key_rsa(peer_pub_bytes)
    print(" -> Chaves Públicas trocadas com sucesso.")

    # TROCA DA CHAVE DE SESSÃO (A Mágica acontece aqui)
    print("\n--- FASE 2: DEFININDO A CHAVE AES ---")
    
    session_key = None

    if tipo == 'c': 
        # SOU O CLIENTE 'A': Eu gero a chave e envio
        print("[A] Gerando chave AES de 256 bits...")
        session_key = generate_aes_key(256)
        
        print("[A] Criptografando chave AES com a RSA Pública de B...")
        encrypted_key = rsa_encrypt(peer_public_key, session_key)
        
        print(f"[A] Enviando chave cifrada ({len(encrypted_key)} bytes)...")
        sock.send(encrypted_key)
        
    elif tipo == 's':
        # SOU O CLIENTE 'B': Eu aguardo a chave chegar
        print("[B] Aguardando chave de sessão criptografada...")
        encrypted_key = sock.recv(4096)
        
        print("[B] Chave recebida! Descriptografando com minha RSA Privada...")
        try:
            session_key = rsa_decrypt(my_private, encrypted_key)
            print(" -> SUCESSO! Chave AES recuperada.")
        except Exception as e:
            print(f" -> ERRO FATAL: Não consegui decifrar a chave. {e}")
            return

    # --- 4. VALIDAÇÃO ---
    print("\n" + "="*40)
    print(">>> CANAL SEGURO ESTABELECIDO <<<")
    # Mostramos os primeiros bytes da chave AES (em hex) só para confirmar que são IGUAIS
    # Num sistema real, nunca imprima a chave!
    print(f"Minha chave AES: {session_key.hex()[:10]}... (secreto)")
    print("Agora ambos têm a MESMA chave simétrica.")
    print("="*40)
    
    # --- 5. MANTER CANAL ABERTO ---
    print("\nCanal aberto. Digite 'sair' para encerrar.\n")
    
    # Retorna o socket e a chave para uso externo
    return sock, session_key

if __name__ == "__main__":
    iniciar_troca_segura()