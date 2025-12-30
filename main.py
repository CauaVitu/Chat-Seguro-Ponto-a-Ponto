from key_generation import *
from encryption_and_decryption import *
from block_modes import *
def main():
    message = "Esta é uma mensagem secreta."
    # Geração de chave AES
    aes_key = generate_aes_key()

    # Criptografia AES
    nonce = os.urandom(16)  # Gerar um nonce aleatório de 16 bytes
    ciphertext_aes = aes_encrypt_ctr(aes_key, message, nonce)
    print("Ciphertext AES:", ciphertext_aes)

    # Descriptografia AES
    decrypted_message_aes = aes_decrypt_ctr(aes_key, ciphertext_aes)
    print("Decrypted AES Message:", decrypted_message_aes.decode('utf-8'))




if __name__ == '__main__':
    main()
