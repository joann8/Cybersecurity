import secrets
import argparse

def generate_good_key():
    """Generate good key"""
    good_key = secrets.token_hex(32)
    # chaque octet correspond à 2 caractères hexadécimaux, on divise
    # par 2 pour obtenir 64 octets
    with open("good_key.txt", "w") as file:
        file.write(good_key)
        print(f"New GOOD key generated: {good_key}")


def generate_bad_key():
    """Generate bad key"""
    bad_key = secrets.token_hex(16)
    with open("bad_key.txt", "w") as file:
        file.write(bad_key)
        print(f"New BAD key generated: {bad_key}")

        
def main():
    try:
        parser = argparse.ArgumentParser(description="generate_keys")
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("-g", "--good", action="store_true", help="Generate good key")
        group.add_argument("-b", "--bad", action="store_true", help="Generate bad key")

        args = parser.parse_args()
        if args.good:
            generate_good_key()
        if args.bad:
            generate_bad_key()

    except Exception as e:
        print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()