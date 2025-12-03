#!/usr/bin/env python3

import argparse

exts = [".jpg", "jpeg", ".png", ".gif", ".bmp"]

def parseArgs() -> argparse.Namespace:
	spiderParser = argparse.ArgumentParser(
		usage="./spider.py[-r] [-l N] [-p PATH] URL"
	)
	spiderParser.add_argument("url")
	spiderParser.add_argument("-r", "--recursive", action="store_true")
	spiderParser.add_argument("-l", "--level", type=int, default=5)
	spiderParser.add_argument("-p", "--path", type=str, default="./data/")

	return spiderParser.parse_args()

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

if __name__ == '__main__':
	main()
