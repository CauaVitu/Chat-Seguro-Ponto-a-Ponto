from key_generation import *
def main():
    private_key, public_key = generate_rsa_keypair(size=2048)
    public_key_pem = serialize_key(public_key)
    private_key_pem = serialize_key(private_key)
    print(public_key_pem.decode())
    print(private_key_pem.decode())




if __name__ == '__main__':
    main()
