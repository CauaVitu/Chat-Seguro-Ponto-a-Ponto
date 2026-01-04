import os

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Gera um par de chaves RSA (pública e privada).
# O tamanho padrão é 2048 bits e o expoente público padrão é 65537.
# Você pode alterar esses valores se desejar, mas 2048 bits é geralmente seguro para a maioria dos usos.
# E o expoente 65537 é um valor comum que oferece um bom equilíbrio entre segurança e desempenho., mas outros valores podem ser usados.
def generate_rsa_keypair(exponent=65537, size=2048):
    private_key = rsa.generate_private_key(
        public_exponent=exponent,
        key_size=size,
    )
    public_key = private_key.public_key()
    return private_key, public_key



# Checa se a chave é privada ou pública e converte a chave em formato PEM (texto).
def serialize_key_rsa (key):
    if isinstance(key, rsa.RSAPrivateKey):
        pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
    else:
        pem = key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    return pem

def deserialize_public_key_rsa(pem_data):
    # Transforma o texto da chave pública de volta em objeto.
    return serialization.load_pem_public_key(pem_data)

def deserialize_private_key_rsa(pem_data):
    # Transforma o texto da chave privada de volta em objeto
    # Usamos NoEncryption(), então o password=None (não tem senha).
    return serialization.load_pem_private_key(pem_data, password=None)

def generate_aes_key(size = 256):
    # Gera uma chave AES de tamanho especificado (128, 192 ou 256 bits).
    if size not in [128, 192, 256]:
        raise ValueError("Tamanho da chave AES deve ser 128, 192 ou 256 bits.")
    #Função da biblioteca que gera uma chave segura e com entropia alta.
    key = AESGCM.generate_key(bit_length=size)
    return key






