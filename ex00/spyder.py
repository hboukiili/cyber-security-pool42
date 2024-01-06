import os
import requests
from bs4 import BeautifulSoup
import re
import argparse
import urllib.parse

def download_image(url, path):
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def extract_images_from_page(url, path, extensions):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'html.parser')
            img_tags = soup.find_all('img')
            for img in img_tags:
                img_url = img.get('src')
                img_name = os.path.basename(urllib.parse.urlsplit(img_url)[2])
                img_ext = os.path.splitext(img_name)[1]
                if img_ext.lower() in extensions:
                    img_path = os.path.join(path, img_name)
                    download_image(img_url, img_path)
        else :
            print(f"failed to get response from {url} : status {r.status_code}")
    except Exception as e:
        print(f"Failed to extract images from {url}: {e}")

def spider(url, recursive=False, maxdepth=5, path='./data/', extensions=['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
    if not os.path.exists(path):
        os.makedirs(path)
    extract_images_from_page(url, path, extensions)
    if recursive and maxdepth > 0:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, 'html.parser')
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href')
                    full_url = urllib.parse.urljoin(url, href)
                    spider(full_url, recursive, maxdepth-1, path, extensions)
        except Exception as e:
            print(f"Failed to spider {url}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("URL", help="The URL to scrape images from")
    parser.add_argument("-r", "--recursive", action="store_true", help="Enable recursive download")
    parser.add_argument("-l", "--maxdepth", type=int, default=5, help="Maximum depth level of recursive download")
    parser.add_argument("-p", "--path", default="./data/", help="Path to save downloaded files")
    args = parser.parse_args()
  
    spider(args.URL, args.recursive, args.maxdepth, args.path)