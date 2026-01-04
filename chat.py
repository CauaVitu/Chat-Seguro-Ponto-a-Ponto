import threading
import os
import sys
from block_modes import (
aes_decrypt_cbc, 
aes_encrypt_cbc, 
aes_decrypt_ctr, 
aes_encrypt_ctr
)    #Tudo menos o XOR

# Aqui a gente vai definir a thread que fica ouvindo mensagens
def receive_messages(sock, session_key, mode):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("[CONEXÃO ENCERRADA PELO OUTRO LADO]")
                os._exit(0)
            if mode == 'CBC':
                plaintext = aes_decrypt_cbc(session_key, data)
            elif mode == 'CTR':
                plaintext = aes_decrypt_ctr(session_key, data)
            else:
                print("[ERRO] Modo de operação desconhecido.")
                continue
            # Limpa a linha do prompt e imprime a mensagem
            print(f"\r\033[K[OUTRO]: {plaintext.decode('utf-8')}\n[VOCÊ]: ", end='', flush=True)
        except Exception as e:
            print(f"[ERRO AO RECEBER MENSAGEM]: {e}")
            os._exit(1)

def start_chat_loop(sock, session_key, mode='CBC'):
    """
    Função principal do chat. Inicia a thread de ouvir e gerencia o loop de envio.
    """
    print(f"\n{'='*40}")
    print("CHAT INICIADO (Digite 'sair' para encerrar)")
    print(f"{'='*40}")

    # 1. Inicia a thread de escuta (Receber)
    listener = threading.Thread(target=receive_messages, args=(sock, session_key, mode))
    listener.daemon = True  # A thread morre se o programa principal fechar
    listener.start()

    if mode == 'CBC':
        iv = os.urandom(16)  # Vetor de inicialização aleatório para CBC

    # 2. Loop principal (Enviar)
    while True:
        try:
            msg = input("[VOCÊ]: ")
            
            if msg.lower() == 'sair':
                print("Encerrando chat...")
                sock.close()
                break
            
            if msg:
                # Cifra usando o modo selecionado
                if mode == 'CBC':
                    encrypted_data = aes_encrypt_cbc(session_key, msg, iv)
                elif mode == 'CTR':
                    encrypted_data = aes_encrypt_ctr(session_key, msg, iv)
                else:
                    print("[ERRO] Modo inválido")
                    continue
                
                # Envia
                sock.send(encrypted_data)
                
        except KeyboardInterrupt:
            print("\nSaindo...")
            break
        except Exception as e:
            print(f"[ERRO NO ENVIO]: {e}")
            break
