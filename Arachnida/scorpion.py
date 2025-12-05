#!/usr/bin/env python3

import os
import argparse

exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

def parseArgs() -> argparse.Namespace:
	scorpionParser = argparse.ArgumentParser(
		usage="./scorpion.py -g   OR   ./scorpion.py [-d | -m] FILE1 [FILE2 ...]",
	)
	mode_group = scorpionParser.add_mutually_exclusive_group()
	mode_group.add_argument('-g', '--gui', action='store_true', help="Launch a simple graphical interface for metadata viewing/modification.")
	mode_group.add_argument('-d', '--delete', action='store_true', help="Delete metadata from the given image(s).")
	mode_group.add_argument('-m', '--modify', action='store_true', help="Modify metadata on the given image(s).")
	scorpionParser.add_argument('file', nargs='*', help="One or more image files (required unless -g is used) (supports .jpg/.jpeg/.png/.gif/.bmp).")

	return scorpionParser.parse_args()

def isSupportedFile(filepath: str) -> bool:
	if not os.path.isfile(filepath):
		print(f"File not found: {filepath}")
		return False

	if not any(filepath.lower().endswith(ext) for ext in exts):
		print(f"Unsupported format (supported: {', '.join(exts)}): {filepath}")
		return False
	
	return True

def deleteMetadata(files: list) -> None:
	print("Delete Metadata")

def modifyMetadata(files: list) -> None:
	print("Modify Metadata")

def printMetadata(files: list) -> None:
	print("Print Metadata")

def launchScorpionGUI() -> None:
	print("Open GUI")

def main() -> None:
	args = parseArgs()
	if args.gui and len(args.file) != 0:
		print("GUI mode (-g) does not accept file arguments.")
		return

	if args.gui:
		launchScorpionGUI()
		return

	valid_files = [f for f in args.file if isSupportedFile(f)]

	if not valid_files:
		print("No valid files to process.")
		return

	if args.delete:
		deleteMetadata(args.file)
	elif args.modify:
		modifyMetadata(args.file)
	else:
		printMetadata(args.file)

if __name__ == '__main__':
	main()
