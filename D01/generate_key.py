import secrets

try:
    good_key = secrets.token_hex(32)
    # chaque octet correspond à 2 caractères hexadécimaux, on divise
    # par 2 pour obtenir 64 octets
    with open("good_key", "w") as file:
        file.write(good_key)
        print(f"New GOOD key generated: {good_key}")

    bad_key = secrets.token_hex(16)
    with open("bad_key", "w") as file:
        file.write(bad_key)
        print(f"New BAD key generated: {bad_key}")

        
except Exception as e:
    print(type(e).__name__ + ":", e)

