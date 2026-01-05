# Chat Seguro Ponto-a-Ponto com Criptografia Híbrida

Um sistema de chat em tempo real que implementa criptografia híbrida (RSA + AES) com suporte para dois modos de operação simétrica: **CBC** (Cipher Block Chaining) e **CTR** (Counter Mode).

## � Como Compilar e Executar

### Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

### Instalação Rápida

```bash
# 1. Clonar ou extrair o projeto
cd Chat-Seguro-Ponto-a-Ponto

# 2. Instalar dependências
pip install -r requirements.txt
```

### Executar o Chat

O sistema usa **dois processos**: um servidor e um cliente.

**Terminal 1 (Servidor):**
```bash
python main.py
# Digite: s
# Escolha modo: 1 (CBC) ou 2 (CTR)
```

**Terminal 2 (Cliente):**
```bash
python main.py
# Digite: c
# Escolha modo: 1 (CBC) ou 2 (CTR)
```

**Usar o Chat:**
```
[VOCÊ]: Olá mundo!
[OUTRO]: Oi, tudo bem?
[VOCÊ]: sair
```

---

## �📋 Arquitetura do Sistema

### Visão Geral

O sistema é dividido em **duas fases de segurança**:

1. **Fase 1: Troca de Chaves Assimétricas (RSA)**
   - Cada participante gera um par de chaves RSA (2048 bits)
   - As chaves públicas são trocadas via socket TCP
   - Estabelece um canal autenticado

2. **Fase 2: Criptografia de Sessão (AES)**
   - Um participante (cliente) gera uma chave AES-256
   - Criptografa a chave com a RSA pública do outro
   - Ambos possuem a mesma chave simétrica para comunicação
   - Mensagens são criptografadas em um dos dois modos escolhido

### Arquitetura de Arquivos

```
main.py                          # Ponto de entrada, controla fluxo geral
├── key_generation.py            # Gera chaves RSA e AES
├── encryption_and_decryption.py # Operações RSA e AES-ECB base
├── block_modes.py               # Implementação de CBC e CTR
├── connection.py                # Troca de chaves e estabelece socket
└── chat.py                       # Loop de chat com threads
```

### Fluxo de Execução

```
INICIALIZAÇÃO
     ↓
1. Escolher papel (servidor ou cliente)
     ↓
2. Conectar via TCP
     ↓
3. Trocar chaves públicas RSA
     ↓
4. Cliente gera chave AES-256
     ↓
5. Cliente criptografa com RSA pública do servidor
     ↓
6. Servidor descriptografa com RSA privada
     ↓
7. Ambos possuem mesma chave AES
     ↓
8. Escolher modo (CBC ou CTR)
     ↓
9. Trocar mensagens criptografadas
     ↓
CHAT EM ANDAMENTO
```

##  Decisões de Projeto

### 1. Algoritmo Assimétrico: RSA-2048

**Por que RSA?**
- Amplamente testado e confiável
- Suporta troca de chaves segura
- Implementação disponível em bibliotecas confiáveis (cryptography)

**Por que 2048 bits?**
- Oferece ~112 bits de segurança (equivalente a chave de 112 bits simétrica)
- Suportado por praticamente todos os sistemas
- Balanceamento entre segurança e performance

**Alternativas consideradas:**
- ECDH (Elliptic Curve Diffie-Hellman): Mais rápido, requer sincronização de curva
- Decisão: RSA é simples e direto para este caso

### 2. Padding RSA: OAEP (Optimal Asymmetric Encryption Padding)

**Implementado em:** `encryption_and_decryption.py`

```python
asym_padding.OAEP(
    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None
)
```

**Características:**
- **Randomizado**: A mesma mensagem produz cifras diferentes (não-determinístico)
- **Resistente a ataques**: OAEP protege contra ataques de oráculo
- **Hash**: SHA-256 para 256 bits de segurança
- **MGF1**: Mask Generation Function padrão

**Por que não PKCS#1 v1.5?**
- Vulnerável a ataques de padding oracle
- OAEP é o padrão moderno recomendado

### 3. Criptografia Simétrica: AES-256

**Tamanho da chave: 256 bits**
- Máxima segurança prática
- Suportado em hardware moderno (AES-NI)
- Seguro contra ataques quânticos teóricos

**Geração da chave:**
```python
AESGCM.generate_key(bit_length=256)  # Criptograficamente segura
```

### 4. Padding Simétrico: PKCS7

**Implementado em:** `encryption_and_decryption.py` e `block_modes.py`

```python
padder = padding.PKCS7(128).padder()  # 128 bits = 16 bytes
padded_data = padder.update(plaintext) + padder.finalize()
```

**Como funciona:**
- Bloco tem 16 bytes (128 bits)
- Se mensagem tem 10 bytes, adiciona 6 bytes com valor 6
- Se mensagem tem múltiplo de 16, adiciona 16 bytes com valor 16
- Na descriptografia, remove os últimos N bytes com valor N

**Exemplo:**
```
Mensagem:    "Olá" (3 bytes)
Em hex:      4F 6C C3 A1
PKCS7:       4F 6C C3 A1 0D 0D 0D 0D 0D 0D 0D 0D 0D 0D 0D 0D
             ↑ original ↑              ↑ 13 bytes de padding ↑
```

---

## 🔄 Modos de Operação: CBC vs CTR

### CBC (Cipher Block Chaining)

**Localização:** `block_modes.py` - `aes_encrypt_cbc()` e `aes_decrypt_cbc()`

#### Como Funciona

```
ENCRIPTAÇÃO:
Bloco 1:   IV ⊕ Plaintext[0] → AES → Ciphertext[0]
Bloco 2:   Ciphertext[0] ⊕ Plaintext[1] → AES → Ciphertext[1]
Bloco 3:   Ciphertext[1] ⊕ Plaintext[2] → AES → Ciphertext[2]

DESCRIPTOGRAFIA:
Bloco 1:   AES⁻¹(Ciphertext[0]) ⊕ IV → Plaintext[0]
Bloco 2:   AES⁻¹(Ciphertext[1]) ⊕ Ciphertext[0] → Plaintext[1]
Bloco 3:   AES⁻¹(Ciphertext[2]) ⊕ Ciphertext[1] → Plaintext[2]
```

#### Código-Chave

```python
def aes_encrypt_cbc(key, plaintext, iv):
    # ... padding com PKCS7 ...
    ciphertext = b""
    previous_block = iv  # Primeiro "bloco anterior" é o IV
    
    for i in range(0, len(padded_data), 16):
        block = padded_data[i:i+16]
        block_to_encrypt = xor_block(block, previous_block)  # ⊕ com anterior
        encrypted_block = encryptor.update(block_to_encrypt)  # AES
        ciphertext += encrypted_block
        previous_block = encrypted_block  # Próximo anterior é este cifrado
    
    return iv + ciphertext  # IV é transmitido junto
```

#### IV (Initialization Vector)

**Tamanho:** 16 bytes (128 bits)

**Gerenciamento:**
```python
# Em chat.py
iv = os.urandom(16)  # Um IV aleatório por sessão
```

**Características:**
- Gerado uma vez quando o chat inicia
- **REUTILIZADO** em todas as mensagens da sessão
- Transmitido junto com o ciphertext (não é segredo)

**Por que reutilizar?**
- Simplifica implementação (não precisa gerar novo a cada mensagem)
- Em chat, geralmente aceitável (mesma sessão)

**Risco:**
- Se o IV for reutilizado com mesma chave em **múltiplas sessões**, há vulnerabilidade
- Recomendação: Usar nonce/IV único por mensagem em produção

#### Características

| Aspecto | CBC |
|---------|-----|
| **Padding** | Necessário |
| **IV Obrigatório** | Sim (1 por mensagem ou sessão) |
| **Parallelização** | Descripto: Sim / Encripto: Não |
| **Tamanho Output** | Aumentado pelo IV (16 bytes extras) |
| **Implementação** | Sequencial, cada bloco depende do anterior |
| **Autenticação** | Não (apenas confidencialidade) |

---

### CTR (Counter Mode)

**Localização:** `block_modes.py` - `aes_encrypt_ctr()` e `aes_decrypt_ctr()`

#### Como Funciona

```
ENCRIPTAÇÃO e DESCRIPTOGRAFIA (idênticas):
Counter[0] → AES → Keystream[0]   ⊕   Plaintext[0]   → Ciphertext[0]
Counter[1] → AES → Keystream[1]   ⊕   Plaintext[1]   → Ciphertext[1]
Counter[2] → AES → Keystream[2]   ⊕   Plaintext[2]   → Ciphertext[2]
```

#### Código-Chave

```python
def aes_encrypt_ctr(key, plaintext, nonce):
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    encryptor = cipher.encryptor()
    ciphertext = b""
    counter = int.from_bytes(nonce, byteorder='big')  # Nonce é o contador inicial
    
    for i in range(0, len(plaintext), 16):
        block = plaintext[i:i+16]
        current = counter.to_bytes(16, byteorder='big')
        keystream = encryptor.update(current)  # AES(counter)
        encrypted_block = xor_block(block, keystream[:len(block)])
        ciphertext += encrypted_block
        counter += 1  # Incrementa o contador
    
    return nonce + ciphertext  # Nonce é transmitido junto
```

#### Nonce (Number Used Once)

**Tamanho:** 16 bytes (128 bits)

**Gerenciamento:**
```python
# Em chat.py
iv = os.urandom(16)  # "nonce" em CTR também é aleatório
```

**Características:**
- Usado como valor inicial do contador
- Não precisa ser secreto, só único (mesmo com mesma chave)
- Transmitido junto com ciphertext

**Diferença de IV:**
| Propriedade | IV (CBC) | Nonce (CTR) |
|------------|----------|-----------|
| Papel | Alimenta primeiro bloco | Inicializa contador |
| Determinístico? | Aleatório por mensagem/sessão | Deve ser único |
| Risco de reutilização | Alto (reduz segurança) | Catastrófico (quebra segurança) |

#### Características

| Aspecto | CTR |
|---------|-----|
| **Padding** | NÃO necessário |
| **Nonce Obrigatório** | Sim (deve ser único) |
| **Parallelização** | Sim (blocos independentes) |
| **Tamanho Output** | Igual ao input (nenhum overhead) |
| **Implementação** | Parallelizável completamente |
| **Autenticação** | Não (apenas confidencialidade) |

---

## 📊 Comparação CBC vs CTR

### Facilidade de Implementação

| Critério | CBC | CTR |
|----------|-----|-----|
| **Complexidade** | Média | Simples |
| **Dependências** | Blocos anteriores | Apenas contador |
| **Linha de código** | ~20 para implementação | ~15 para implementação |
| **Bugs comum** | IV incorreto | Nonce reutilizado |
| **Debugging** | Mais difícil (efeito cascata) | Mais fácil (blocos independentes) |

### Requisitos de IV/Nonce

| Propriedade | CBC | CTR |
|-------------|-----|-----|
| **Tamanho** | 16 bytes | 16 bytes |
| **Geração** | Aleatória por mensagem/sessão | Aleatória (deve ser única) |
| **Secreto?** | Não | Não |
| **Reutilização segura** | Evitar (reduz segurança) | Proibida (quebra segurança) |
| **Transmissão** | Junto com ciphertext | Junto com ciphertext |

### Necessidade de Padding

| Modo | Padding | Razão |
|------|---------|-------|
| **CBC** | Sim (PKCS7) | Bloco deve ter exatamente 16 bytes |
| **CTR** | Não | Gera keystream de qualquer tamanho |

**Impacto:**
- CBC: Adiciona 1-16 bytes ao ciphertext
- CTR: Tamanho exato = tamanho plaintext


## 📁 Descrição dos Arquivos

### `main.py`
Ponto de entrada do programa. Coordena:
- Estabelecimento da conexão segura
- Escolha do modo de criptografia
- Inicialização do chat

### `key_generation.py`
Geração de chaves:
- `generate_rsa_keypair()`: Cria par RSA-2048
- `serialize_key_rsa()`: Converte para PEM
- `deserialize_public_key_rsa()`: Carrega chave pública
- `deserialize_private_key_rsa()`: Carrega chave privada
- `generate_aes_key()`: Cria chave AES-256

### `encryption_and_decryption.py`
Operações criptográficas:
- `rsa_encrypt()`: RSA com OAEP
- `rsa_decrypt()`: Descriptografia RSA
- `aes_encrypt()`: AES-ECB (base)
- `aes_decrypt()`: Descriptografia AES-ECB

### `block_modes.py`
Modos de operação:
- `aes_encrypt_cbc()`: Encriptação CBC
- `aes_decrypt_cbc()`: Descriptografia CBC
- `aes_encrypt_ctr()`: Encriptação CTR
- `aes_decrypt_ctr()`: Descriptografia CTR
- `xor_block()`: XOR byte-a-byte

### `connection.py`
Gerenciamento de conexão:
- `iniciar_troca_segura()`: Fluxo completo de autenticação e troca de chaves

### `chat.py`
Interface de chat:
- `receive_messages()`: Thread para escutar mensagens
- `start_chat_loop()`: Loop principal de envio

---

## 📋 Requisitos

```
cffi==2.0.0
cryptography==46.0.3
pycparser==2.23
```

---

## 📝 Exemplo de Uso

```
Terminal 1:
$ python main.py
Bem-vindo ao Chat Seguro Ponto-a-Ponto!
Digite 's' para ser servidor ou 'c' para ser cliente: s
[AGUARDANDO] Esperando conexão na porta 5556...
[CONECTADO] Aceitou conexão de ('127.0.0.1', 54321)

--- FASE 1: TROCA DE CHAVES PÚBLICAS ---
 -> Chaves Públicas trocadas com sucesso.

--- FASE 2: DEFININDO A CHAVE AES ---
[B] Aguardando chave de sessão criptografada...
[B] Chave recebida! Descriptografando com minha RSA Privada...
 -> SUCESSO! Chave AES recuperada.

========================================
>>> CANAL SEGURO ESTABELECIDO <<<
Minha chave AES: 3f7a2e1d... (secreto)
Agora ambos têm a MESMA chave simétrica.
========================================

Escolha o modo de criptografia:
1. CBC (Cipher Block Chaining)
2. CTR (Counter Mode)
Digite 1 ou 2: 1
Modo selecionado: CBC

========================================
CHAT INICIADO (Digite 'sair' para encerrar)
========================================
[VOCÊ]: Olá!
[OUTRO]: Oi, tudo bem?
[VOCÊ]: Tudo ótimo! Como você está?
[OUTRO]: Feliz demais!
[VOCÊ]: sair
Encerrando chat...
```

---

## 🔬 Testes

Para testar a segurança:

```bash
# Terminal 1: Servidor com CBC
python main.py
# s, 1

# Terminal 2: Cliente com CBC
python main.py
# c, 1

# Trocar mensagens, depois Ctrl+C em ambos
```

---

## 📚 Referências

- [NIST SP 800-38A: Recommendation for Block Cipher Modes](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38a.pdf)
- [RFC 3394: AES Key Wrap Algorithm](https://tools.ietf.org/html/rfc3394)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [Cryptography.io Documentation](https://cryptography.io/)

---

## ✅ Checklist de Funcionalidades

- [x] Chat bidirecional em tempo real
- [x] Troca de chaves RSA-2048
- [x] Encriptação de chave com RSA OAEP
- [x] Suporte a CBC com PKCS7
- [x] Suporte a CTR sem padding
- [x] Gerenciamento de IV/Nonce
- [x] Comunicação via TCP
- [x] Threading para recepção simultânea
- [x] Interface amigável

---

**Autor:** Cauã Victor Pinheiro da Silva 
**Data:** Janeiro 2026  

