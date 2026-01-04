from key_generation import *
from encryption_and_decryption import *
from block_modes import *
from connection import iniciar_troca_segura
from chat import start_chat_loop

def main():
    # Estabelece conexão segura e troca chaves
    resultado = iniciar_troca_segura()
    
    if resultado is None:
        print("Falha ao estabelecer conexão segura.")
        return
    
    sock, session_key = resultado
    
    # Seleciona o modo de criptografia
    print("\nEscolha o modo de criptografia:")
    print("1. CBC (Cipher Block Chaining)")
    print("2. CTR (Counter Mode)")
    
    while True:
        escolha = input("Digite 1 ou 2: ").strip()
        if escolha == '1':
            mode = 'CBC'
            break
        elif escolha == '2':
            mode = 'CTR'
            break
        else:
            print("Opção inválida. Tente novamente.")
    
    print(f"Modo selecionado: {mode}")
    
    # Inicia o chat com o modo escolhido
    start_chat_loop(sock, session_key, mode)

if __name__ == '__main__':
    main()
