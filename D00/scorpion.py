import argparse
import os
from PIL import Image, ExifTags  # pour manipuler les images
import time


def is_image_file(path):
    """Check img extension is valid"""
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
    return os.path.splitext(path)[1].lower() in image_extensions


def get_file_creation_date(path):
    """Get the creation date of the file"""
    img_info = os.stat(path)
    creation_time = img_info.st_ctime
    # Date de création en secondes depuis l'époque
    print(f"    --> DateTimeCreation: {time.ctime(creation_time)}")


def print_img_info(img, path, DateTimeOriginal):
    """Print basic img attributes"""
    print("> Basic attributes")
    print(f"    --> Format: {img.format}\n    --> Mode: {img.mode}\n"
          f"    --> Size: {img.size}\n    --> Palette: {img.palette}")
    if not DateTimeOriginal:
        get_file_creation_date(path)


def print_img_exif(img):
    """Print EXIF data for img"""
    # EXIF (Exchangeable Image File Format)
    exif_data = img._getexif()
    DateTimeOriginal = False
    if exif_data:
        print("> EXIF data")
        for tag, value in exif_data.items():
            # Convertir le tag en nom lisible
            tag_name = ExifTags.TAGS.get(tag, tag)
            print(f"    --> {tag_name}: {value}")
            if tag_name == "DateTimeOriginal":
                DateTimeOriginal = True
    else:
        print("> No EXIF data found")
    return DateTimeOriginal


def get_img_data(path):
    """Get the data from an img"""
    if not is_image_file(path):
        print(f"*** ! '{path}' not a valid image (check extension) ***")
        return
    try:
        img = Image.open(path)
        print(f"*** Data for '{path}' ***")
        DateTimeOriginal = print_img_exif(img)
        print_img_info(img, path, DateTimeOriginal)
        print("\n")

    except Exception:
        print(f"*** ! Error opening '{path} (check path) ***")


def main():
    try:
        parser = argparse.ArgumentParser(description="Scorpion")
        parser.add_argument('file', type=str, nargs="+", help="Path to file")
        args = parser.parse_args()
        for arg in args.file:
            get_img_data(arg)

    except Exception as e:
        print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()
