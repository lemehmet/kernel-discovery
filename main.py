import argparse
import logging
import os
import re
import platform
from distutils.version import LooseVersion

import requests

from bs4 import BeautifulSoup

vers = re.split('[.-]', platform.release())
current_kernel_version = "0.0.0"
if len(vers) >= 3:
    current_kernel_version = f"{vers[0]}.{vers[1]}.{vers[2]}"

logging.basicConfig(level=logging.DEBUG)
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-r", "--repository", action="store",
                    help="The url for the custom kernel repository",
                    default="https://kernel.ubuntu.com/~kernel-ppa/mainline/")
parser.add_argument("--min-version", action="store",
                    help="Ignore earlier versions",
                    default=current_kernel_version)
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
            logging.info("Folder: %s Parsed: %s Comps: %s", href, v, v.version)
            if selected[0] is None or selected[1] < v:
                selected = (folder, v)
        except TypeError as e:
            logging.warning("TypeError: %s  %s Err: %s", href, v, e)
        except:
            logging.warning("Failed while working on link %s", href)
    return selected


def extract_urls(folder: str) -> []:
    req = requests.get(f"{args.repository}{folder}{args.arch}")
    soup = BeautifulSoup(req.content, 'html.parser')
    kernel_type = "lowlatency" if args.low_latency else "generic"
    urls = []
    links = soup.find_all('a')
    if not links:
        logging.error("The document has no links: %s", req.content)
    for link in links:
        logging.debug("Processing link: %s", link)
        url = link.get('href')
        if kernel_type in url or 'all' in url:
            urls.append(url)
    return urls


def download_files(folder: str, files: []):
    output_path = os.path.join(args.output, folder)
    try:
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        else:
            logging.error("Output folder already exist, to re-download please delete: %s", output_path)
    except OSError:
        logging.error("Unable to create output folder %s", output_path)
        return
    for filename in files:
        url = f"{args.repository}{folder}{args.arch}/{filename}"
        logging.info("Downloading %s", url)
        r = requests.get(url)
        logging.info("Downloaded %s in %s", len(r.content), r.elapsed)
        with open(f"{output_path}/{filename}", 'wb') as f:
            f.write(r.content)


def main():
    logging.info("Starting kernel downloader")
    latest_version = find_latest()
    logging.info("Found latest version: %s", latest_version[1])
    folder = latest_version[0]
    if folder is not None:
        files = extract_urls(folder)
        logging.info("Got the list %s", files)
        if len(files) > 0:
            download_files(folder, files)


if __name__ == '__main__':
    main()
