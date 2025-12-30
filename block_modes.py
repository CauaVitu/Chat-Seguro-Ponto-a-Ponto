import os
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)

def xor_block(block1, block2):
    # Faz o XOR byte a byte entre dois blocos de 16 bytes
    return bytes(a ^ b for a, b in zip(block1, block2))

def aes_encrypt_cbc(key, plaintext, iv):
    if (isinstance(plaintext, str)):
        plaintext = plaintext.encode('utf-8')
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext) + padder.finalize()

    # Usamos o modo ECB para cifrar um bloco por vez
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    encryptor = cipher.encryptor()

    ciphertext = b""
    previous_block = iv

    for i in range(0, len(padded_data), 16):
        block = padded_data[i:i+16]
        block_to_encrypt = xor_block(block, previous_block)
        encrypted_block = encryptor.update(block_to_encrypt)
        ciphertext += encrypted_block
        previous_block = encrypted_block
    ciphertext += encryptor.finalize()
    return iv + ciphertext  # Mandamos o IV junto com o ciphertext

def aes_decrypt_cbc(key,iv_ciphertext):
    # Separamos o IV do ciphertext
    iv = iv_ciphertext[:16]
    ciphertext = iv_ciphertext[16:]
    # Criamos o objeto da cifra dos dados com AES em modo ECB.
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    decryptor = cipher.decryptor()
    padded_plaintext = b""
    previous_block = iv
    # Decriptamos bloco por bloco
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i+16]
        decrypted_block = decryptor.update(block)
        # XOR com o bloco anterior (ou IV para o primeiro bloco)
        plaintext_block = xor_block(decrypted_block, previous_block)
        padded_plaintext += plaintext_block
        previous_block = block
    padded_plaintext += decryptor.finalize()
    # Removemos o padding
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    return plaintext

def aes_encrypt_ctr(key, plaintext, nonce):
    if (isinstance(plaintext, str)):
        plaintext = plaintext.encode('utf-8')
    # Criamos o objeto da cifra dos dados com AES em modo ECB.
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    encryptor = cipher.encryptor()
    ciphertext = b""
    counter = int.from_bytes(nonce, byteorder='big')
    # Processamos bloco por bloco
    for i in range(0, len(plaintext),16):
        block = plaintext[i:i+16]
        current = counter.to_bytes(16, byteorder='big')
        keystream = encryptor.update(current)
        # Fazemos o XOR do bloco com o keystream gerado (:len(block) para o ultimo bloco e por isso não precisa de padding)
        encrypted_block = xor_block(block, keystream[:len(block)])
        ciphertext += encrypted_block
        counter += 1
    ciphertext += encryptor.finalize()
    return nonce + ciphertext  # Mandamos o nonce junto com o ciphertext


def aes_decrypt_ctr(key, nonce_ciphertext):
    # Separamos o nonce do ciphertext
    nonce = nonce_ciphertext[:16]
    ciphertext = nonce_ciphertext[16:]
    return aes_encrypt_ctr(key, ciphertext, nonce)[16:]  # A decriptação é igual à encriptação no modo CTR