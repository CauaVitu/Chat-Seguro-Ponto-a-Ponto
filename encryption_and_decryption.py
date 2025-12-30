from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)
def rsa_encrypt(public_key, plaintext):
    ciphertext = public_key.encrypt(
        plaintext,
        # Usando OAEP com SHA-256 para melhor segurança.
        # Garantimos que mensagens iguais tenham cifras diferentes a cada vez que são criptografadas.
        # MGF = Mask Generation Function, MGF1 é o único suportado atualmente.
        # algorithm = algoritmo de hash usado no OAEP. 
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def rsa_decrypt(private_key, ciphertext):
    # Usando OAEP com SHA-256 para descriptografar. (Afinal foi assim que criptografamos)
    # Usamos os mesmos esquemas de padding e hash.
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext

def aes_encrypt(aes_key, plaintext):
    # Certifica que o plaintext está em bytes.
    if (isinstance(plaintext, str)):
        plaintext = plaintext.encode('utf-8')
    # Usamos PKCS7 para fazer o padding do plaintext em blocos de 128 bits.
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext) + padder.finalize()
    # Usamos AES em modo ECB (Electronic Codebook)
    # Assim podemos tratar os blocos de forma independente.
    # Criamos o objeto que vai encriptar os dados.
    cipher = Cipher(algorithms.AES(aes_key), modes.ECB())
    encryptor = cipher.encryptor()
    # Efetivamente encriptamos os dados.
    # .update() processa os dados, .finalize() finaliza a encriptação.
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return ciphertext

def aes_decrypt(aes_key, ciphertext):
    # Usamos o mesmo esquema de padding PKCS7 para remover o padding após a decriptação.
    unpadder = padding.PKCS7(128).unpadder()
    # Criamos o objeto da cifra dos dados com AES em modo ECB.
    cipher = Cipher(algorithms.AES(aes_key), modes.ECB())
    # Criamos o objeto que vai descriptografar os dados.
    decryptor = cipher.decryptor()
    # Efetivamente descriptografamos os dados.
    # .update() processa os dados, .finalize() finaliza a decriptação.
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    # E por ultimo removemos o padding.
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    return plaintext

