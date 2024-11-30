import argparse
import re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os


# Vecteur d'initialisation (IV) 
# Indispensable au chiffrage / dechiffrage
# pour l"exemple on le prend un en dur mais normalement aléatoire et stocké qq part
# (iv = os.urandom(16)) aléatoire de 16 octets
iv = b'iDh;X\x8a=m\xee\xb2y\x10\xc7(\x02\xf0'

# Clé de chifferement AES (Advanced Encryption Standard)
# Indispensable au chiffrage / dechiffrage
# pour l"exemple on le  prend un en dur mais normalement aléatoire et stocké qq part
aes_key = b'[\xfe\x02\x05\x8e\x8fk\xbe\x1e\xa2\xd1\xc5o\xa0\xef\xea\xcb\xca\xa7y`\x87\x1c\xc06\x17\x99U\x0b5\xcd\x9a'


# _______ First program _______
# -g: The program receives as argument a hexadecimal key of at least 64 characters.
# The program stores this key safely in a file called ft_otp.key, which is encrypted.

def is_valid_hexadecimal_64(key_str: str):
    """Check hexadecimal key format"""
    pattern = r'^[0-9a-fA-F]{64}$'
    return bool(re.fullmatch(pattern, key_str))


def crypt_the_key(key_bytes: str):
    """Crypt the key : AES (Advanced Encryption Standard) en mode CBC (Cipher block chaining)"""

    # Créer un objet de chiffrement AES 
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())

    # Padding : Le mode CBC exige que le texte clair soit un multiple de la taille du bloc (128 bits = 16 octets).
    # Le padding est ajouté pour atteindre cette longueur à l'aide d'un padder
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(key_bytes) + padder.finalize()

    # Chiffrer les données
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return encrypted_data

def generate_encrypted_key_file(file):
    """Generate encrypted key"""
    key_str = file.read()
    if not is_valid_hexadecimal_64(key_str):
        raise TypeError("not an Hexadecimal 64 key")
    key_bytes = bytes.fromhex(key_str)  # Convertir la clé hexadécimale en bytes
    encrypted_data = crypt_the_key(key_bytes)
    with open("ft_otp.key", "wb") as key_file:
        key_file.write(encrypted_data) 
        print("Clé chiffrée:", encrypted_data)
    return

                   
# _______ Second program _______
# -k: The program generates a new temporary password based on the key given
# as argument and prints it on the standard output.


def decrypt_the_key(encrypted_data: str):
    """Decrypt the key : AES (Advanced Encryption Standard) en mode CBC (Cipher block chaining)"""

    # Créer un objet de déchiffrement AES en mode CBC (avec le meme aes_key et iv)
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())

    # Déchiffrer les données
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Enlever le padding
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

    # La clé déchiffrée
    print("Clé déchiffrée:", unpadded_data.hex())
    return unpadded_data

def generate_totp(file):
    """Generate TOTP key"""

    encrypted_data = file.read()
    key = decrypt_the_key(encrypted_data)
    


# _______ Main _______

def main():
    try:
        parser = argparse.ArgumentParser(description="ft_otp")
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("-g", dest="g_key_file", type=argparse.FileType("r"), help="Encrypt a key")
        group.add_argument("-k", dest="k_key_file", type=argparse.FileType("rb"), help="Generate a temporary paswword given a key")

        args = parser.parse_args()
        if args.g_key_file:
            generate_encrypted_key_file(args.g_key_file)
        if args.k_key_file:
            generate_totp(args.k_key_file)

    except Exception as e:
        print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()