import argparse
import logging
import os
from distutils.version import LooseVersion

import requests

from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG)
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--repository", action="store",
                    help="The url for the custom kernel repository",
                    default="https://kernel.ubuntu.com/~kernel-ppa/mainline/")
parser.add_argument("--min-version", action="store",
                    help="Ignore earlier versions",
                    default="5.10.4")
parser.add_argument("--arch", action="store",
                    help="Use architecture",
                    default="amd64")
parser.add_argument("--output", action="store",
                    help="Output folder",
                    default="")
parser.add_argument("--include-rc", action="store_true",
                    help="Include release candidate versions")
parser.add_argument("--low-latency", action="store_true",
                    help="Use low latency kernel instead")

args = parser.parse_args()


def find_latest() -> (str, LooseVersion):
    logging.info(f"Scraping {args.repository}")
    req = requests.get(args.repository)
    soup = BeautifulSoup(req.content, 'html.parser')
    min_version = LooseVersion(args.min_version)
    selected = (None, None)
    for link in soup.find_all('a'):
        folder = link.get('href')
        href = folder.rstrip('/')
        try:
            if not href.startswith('v'):
                continue
            href = href.lstrip('v')
            v = LooseVersion(href)
            if not args.include_rc and 'rc' in v.version:
                continue
            if v < min_version:
                continue
            logging.info(f"Folder: {href} Parsed: {v} Comps: {v.version}")
            if selected[0] is None or selected[1] < v:
                selected = (folder, v)
        except TypeError as e:
            logging.warning(f"TypeError: '{href}' {v} {min_version} Err: {e}")
        except:
            logging.warning(f"Failed while working on link '{href}'")
    return selected


def extract_urls(folder: str) -> []:
    req = requests.get(f"{args.repository}{folder}/{args.arch}")
    soup = BeautifulSoup(req.content, 'html.parser')
    kernel_type = "lowlatency" if args.low_latency else "generic"
    urls = []
    for link in soup.find_all('a'):
        url = link.get('href')
        if kernel_type in url or 'all' in url:
            urls.append(url)
    return urls


def download_files(folder: str, files: []):
    output_path = os.path.join(args.output, folder)
    try:
        if not os.path.exists(output_path):
            os.mkdir(output_path)
    except OSError:
        logging.error(f"Unable to create output folder {output_path}")
        return
    for filename in files:
        url = f"{args.repository}{folder}/{args.arch}/{filename}"
        logging.info(f"Downloading {url}")
        r = requests.get(url)
        logging.info(f"Downloaded {len(r.content)} in {r.elapsed}")
        with open(f"{output_path}/{filename}", 'wb') as f:
            f.write(r.content)


def main():
    logging.info("Starting kernel downloader")
    latest_version = find_latest()
    logging.info(f"Found latest version: {latest_version[1]}")
    folder = latest_version[0]
    if folder is not None:
        files = extract_urls(folder)
        logging.info(f"Got the list {files}")
        if len(files) > 0:
            download_files(folder, files)

if __name__ == '__main__':
    main()
