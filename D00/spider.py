import os  # creer le dossier sur notre ordi
import argparse  # parser les arguments en ligne de commande
import requests  # gerer les requetes HTTP --> html
from bs4 import BeautifulSoup  # analyser la page html et reperer les balises
from urllib.parse import urljoin  # transformer les url relatif -> absolu
from urllib.parse import urlparse  # décomposer l'URL en composants


class Scrapper:

    def __init__(self, url_main, recursive, level_max, path):
        self.url_main = urlparse(url_main).netloc  # url root
        self.recursive = recursive
        self.level_max = level_max
        self.path = path
        self.visited_url = set()  # set car evite les valeurs doublons
        self.images_urls = set()  # set car evite les valeurs doublons
        self.valid_extensions = {"jpg", "jpeg", "png", "gif", "bmp"}

    def is_valid_image(self, url):
        """ Verifier l'extension du fichier"""
        extension = url.lower().split('.')[-1]
        return extension in self.valid_extensions

    def get_images(self, soup, url):
        """Recupere les img d'une page html a partir des balises img"""
        images = soup.find_all("img", src=True)  # que les img qui ont une src
        # src pour les sites statiques (data-* pour les non statiques)
        for img in images:
            # Convertir les URLs relatives (/images/pics.jpg) -> absolues
            img_url = urljoin(url, img["src"])
            if img_url not in self.images_urls and \
               self.is_valid_image(img_url):
                self.download_img(img_url)

    def download_img(self, img_url):
        """Download images and save them in a folder"""

        os.makedirs(self.path, exist_ok=True)
        # on creer le dossier si besoin

        img_name = os.path.basename(urlparse(img_url).path)
        # on creer le nom de l'image a enregistrer (avec chemin pour eviter
        # les doublons)
        # img_name = str(img_url)
        # invalid_chars = '<>:"/\\|?* '
        # for char in invalid_chars: # Remplace les caractères invalides
        #    img_name = img_name.replace(char, '_')

        img_path = os.path.join(self.path, img_name)
        # Résultat : "path/img_name"

        # Sauvegarder l'image
        img_response = requests.get(img_url, stream=True)
        if img_response.status_code == 200:
            with open(img_path, 'wb') as file:
                for chunk in img_response.iter_content(1024):
                    file.write(chunk)
            self.images_urls.add(img_url)

    def get_links(self, soup, url, current_level):
        """Explore all links from a page"""

        # Recupere les balises a href=True (hyperlink) d'une page html
        links = soup.find_all('a', href=True)
        for link in links:
            full_url = urljoin(url, link['href'])
            # Convertir les liens relatifs en liens absolus
            parsed_link = urlparse(full_url)
            if self.url_main == parsed_link.netloc or \
               'www.' + self.url_main == parsed_link.netloc:
                if full_url not in self.visited_url:
                    self.scrap_page(full_url, current_level + 1)

    def scrap_page(self, url, current_level):
        """Scrape the url given"""

        response = requests.get(url, timeout=5)
        # Timeout : Limite le temps d'attente de la réponse pour éviter
        # que le programme reste bloqué si le serveur ne répond pas.

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            self.get_images(soup, url)
            self.visited_url.add(url)
            if current_level + 1 <= self.level_max:
                self.get_links(soup, url, current_level)


def main():
    try:
        parser = argparse.ArgumentParser(description="Spider")
        parser.add_argument('-r', '--recursive', action='store_true',
                            help="recursive")
        parser.add_argument('-l', '--level', type=int, choices=[1, 2, 3, 4, 5],
                            default=5, help="level (int between 1 and 5)")
        parser.add_argument('-p', '--path', type=str, default='./data/',
                            help="path to store the images")
        parser.add_argument('url', type=str, help="url to scrap")
        # Analyser les arguments
        args = parser.parse_args()
        scrapping = Scrapper(args.url, args.recursive, args.level, args.path)
        scrapping.scrap_page(args.url, 1)
        # print(f"Images prises = {len(scrapping.images_urls)}")
        # print(f"Url visite = {len(scrapping.visited_url)}")

    except Exception as e:

        print(type(e).__name__ + ":", e)


if __name__ == "__main__":
    main()
