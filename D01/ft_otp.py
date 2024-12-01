import argparse                          # parsing arguments
import re                                # expression matching (check 64hex)
from cryptography.fernet import Fernet   # chiffrement method
import time                              # timestamp
import struct                            # implementation RFC 4226 --> 8 octets big endian
import hmac                              # manipulation des Hash Msg Athentification code
import hashlib                           # manipulation des hash
import binascii                          # convertir cipher en bytes
import os                                # creation/enregisterment des fichiers
import subprocess                        # comparaison avec oathtool
import pyotp                             # comparaison avec pyotp
import base64                            # conversion 64-32 pour pyotp
import qrcode                            # bonus QR code

# __________ GENERATION et CONSREVATION DE LA CLEF ENCRYPTAGE __________

KEY_FILE = "fernet.key"

def load_key_from_file():
    """Fonction pour charger la clé depuis un fichier"""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as file:
            return file.read()
    return None

def load_fernet_key():
    """Fonction pour générer ou recupérer la clé depuis un fichier"""
    fernet_key = load_key_from_file()
    if fernet_key is None:
        fernet_key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as file:
            file.write(fernet_key)
    return fernet_key


# __________ GESTION DES ERREURS PERSONNALISEES __________

class ErrorHex(Exception):
    """Exception personnalisée Hex"""
    def __init__(self, message="/ft_otp: error: key must be 64 hexadecimal characters."):
        self.message = message
        super().__init__(self.message)

class ErrorFernet(Exception):
    """Exception personnalisée Fernet"""
    def __init__(self, message="Mutual secret lost (no fernet.key file)"):
        self.message = message
        super().__init__(self.message)


# _______ First program _______
# -g: The program receives as argument a hexadecimal key of at least 64 characters.
# The program stores this key safely in a file called ft_otp.key, which is encrypted.


def is_valid_hexadecimal_64(key_str: str):
    """Check hexadecimal key format"""
    pattern = r'^[0-9a-fA-F]{64}$'
    return bool(re.fullmatch(pattern, key_str))


def crypt_the_key(key_str: str):
    """Crypt the key"""
    fernet_key = load_fernet_key()
    cipher = Fernet(fernet_key)
    key_bytes = key_str.encode()  # Nécessaire pour la fonction cypher
    encrypted_data = cipher.encrypt(key_bytes)
    return encrypted_data


def generate_encrypted_key_file(file):
    """Generate encrypted key"""
    key_str = file.read()
    if not is_valid_hexadecimal_64(key_str):
        raise ErrorHex()
    encrypted_data = crypt_the_key(key_str)
    with open("ft_otp.key", "wb") as key_file:
        key_file.write(encrypted_data)
        print("Key was successfully saved in ft_otp.key.")
    return

                   
# _______ Second program _______
# -k: The program generates a new temporary password based on the key given
# as argument and prints it on the standard output.
# on recupere notre secret et on s'identifie via le hash


def decrypt_the_key(file):
    """Decrypt the key"""
    encrypted_data = file.read()
    fernet_key = load_key_from_file()
    if fernet_key is None:
        raise ErrorFernet()
    cipher = Fernet(fernet_key)
    decrypted_key = cipher.decrypt(encrypted_data)
    decrypted_key_bytes = binascii.unhexlify(decrypted_key)
    return decrypted_key_bytes


def generate_my_totp(decrypted_key_bytes, time_step=30, digits=6, algorithm=hashlib.sha512):
    """Generate my TOTP code with HOTP protocol RFC 4226"""
    timestamp = int(time.time())
    counter = timestamp // time_step 
    counter_bytes = struct.pack(">Q", counter)      # Counter en 8 octets (big-endian)
    hmac_hash = hmac.new(decrypted_key_bytes, counter_bytes, algorithm).digest()    # Calculer le HMAC avec SHA-512
    # Troncation dynamique
    offset = hmac_hash[-1] & 0x0F
    truncated_hash = hmac_hash[offset:offset + 4]
    code = struct.unpack(">I", truncated_hash)[0] & 0x7FFFFFFF  # Retirer le bit de signe
    final_code = str(code % (10 ** digits)).zfill(digits)  # pour 6 chiffres 
    return final_code


# ________ Bonnus & testing _________

def generate_py_totp(decrypted_key_bytes, algorithm=hashlib.sha512):
    """Comparer l'OTP généré avec python"""
    py_totp = pyotp.TOTP(base64.b32encode(decrypted_key_bytes), digest=algorithm)
    py_code = py_totp.now()  # divisé par 30 par défault
    return py_code


def generate_qr(decrypted_key_bytes):
    uri = pyotp.TOTP(base64.b32encode(decrypted_key_bytes), digest=hashlib.sha512).provisioning_uri(name="jacher", issuer_name="jacher_ft_otp")
    qrcode.make(uri).save("QR_ft_otp.png")

# _______ Main _______


def main():
    try:
        parser = argparse.ArgumentParser(description="ft_otp")
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("-g", dest="g_key_file", type=argparse.FileType("r"), help="Encrypt a key")
        group.add_argument("-k", dest="k_key_file", type=argparse.FileType("rb"), help="Generate a temporary paswword given a key")
        args = parser.parse_args()

        if args.g_key_file:  # First program
            generate_encrypted_key_file(args.g_key_file)

        if args.k_key_file:  # Second program
            decrypted_key_bytes = decrypt_the_key(args.k_key_file)
            
            my_code = generate_my_totp(decrypted_key_bytes)
            print(f'{"--> Mycode    :":<12} {my_code}')

            # comparaison avec un autre outil 
            py_code = generate_py_totp(decrypted_key_bytes)          
            print(f'{"--> PyOTP     :":<12} {py_code}')
            
            # Bonus QR code
            generate_qr(decrypted_key_bytes)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
