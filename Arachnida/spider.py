#!/usr/bin/env python3

import os
import sys
import requests
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

def parseArgs() -> argparse.Namespace:
	spiderParser = argparse.ArgumentParser(
		usage="./spider.py [-r] [-l N] [-p PATH] URL"
	)
	spiderParser.add_argument("url")
	spiderParser.add_argument("-r", "--recursive", action="store_true")
	spiderParser.add_argument("-l", "--level", type=int, default=5)
	spiderParser.add_argument("-p", "--path", type=str, default="./data/")

	return spiderParser.parse_args()

def fetchSoup(url: str):
	try:
		r = requests.get(url, timeout=5)
		r.raise_for_status()
	except Exception as e:
		print(f"Cannot fetch {url}: {e}")
		return None

	try:
		return BeautifulSoup(r.text, "html.parser")
	except Exception as e:
		print(f"Cannot parse HTML from {url}: {e}")
		return None

def getImageUrls(url: str, soup: BeautifulSoup | None) -> list:
	images = []
	if soup is None:
		return images

	for img in soup.find_all("img"):
		src = img.get("src")
		if not src:
			continue

		img_url = urljoin(url, src)
		if any(img_url.lower().endswith(ext) for ext in exts):
			images.append(img_url)

	return images

def downloadImage(img_url: str, path: str) -> None:
	try:
		r = requests.get(img_url, timeout=5)
		r.raise_for_status()
	except Exception as e:
		print(f"Failed to download {img_url}: {e}")
		return

	filename = os.path.basename(urlparse(img_url).path)
	filepath = os.path.join(path, filename)

	if os.path.exists(filepath):
		return

	try:
		with open(filepath, 'wb') as f:
			for chunk in r.iter_content(1024):
				if chunk:
					f.write(chunk)
		print(f"Downloaded: {img_url}")
	except Exception as e:
		print(f"Failed to save {img_url}: {e}")

def spider(url: str, path: str, level: int, current_level: int = 0) -> None:
	if current_level > level:
		return

	soup = fetchSoup(url)
	if soup is None:
		return

	images = getImageUrls(url, soup)

	if images:
		for img_url in images:
			downloadImage(img_url, path)

	for a_tag in soup.find_all('a', href=True):
		next_url = urljoin(url, a_tag['href'])
		if next_url.startswith(url):
			spider(next_url, path, level, current_level + 1)

def main() -> None:
	args = parseArgs()

	url = args.url
	recursive = args.recursive
	level = args.level
	path = args.path

	print("---------------------------------------------------------------------")
	print("URL:", url)
	print("Recursive:", recursive)
	print("Level:", level)
	print("Path:", path)
	print("---------------------------------------------------------------------")

	if path != './data':
		if path[-1] != '/':
			path += '/'

	if not os.path.exists(path):
		os.makedirs(path)

	if not recursive:
		level = 0

	try:
		spider(url, path, level)
	except KeyboardInterrupt:
		print("Spider stopped by user!")
		sys.exit(0)

if __name__ == '__main__':
	main()
