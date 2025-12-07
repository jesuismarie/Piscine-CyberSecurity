#!/usr/bin/env python3

import os
import argparse
from pathlib import Path
from datetime import datetime
from PIL import Image, ExifTags

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
	for file in files:
		try:
			img = Image.open(file)
			data = list(img.getdata())
			image_without_exif = Image.new(img.mode, img.size)
			image_without_exif.putdata(data)
			image_without_exif.save(file)
			print(f"Metadata removed from: {file}")
		except Exception as e:
			print(f"Error removing metadata from {file}: {e}")

def getExifData(img: Image) -> dict:
	try:
		exif_data = img.getexif()

		if exif_data:
			exif = {}
			for tag_id, value in exif_data.items():
				tag_name = ExifTags.TAGS.get(tag_id, tag_id)
				exif[tag_name] = value
			return exif
		else:
			return None
	except Exception as e:
		print(f"Error reading EXIF data: {e}")
		return None

def printMetadata(files: list) -> None:
	for file in files:
		filepath = Path(file)

		print(f"{'-'*70}")
		print(f"FILE: {filepath.name}")
		print(f"PATH: {filepath.resolve()}")
		print(f"{'-'*70}")

		try:
			img = Image.open(file)
			exif_info = getExifData(img)
			stat = filepath.stat()
			modified_time = datetime.fromtimestamp(stat.st_mtime)
			created_time = datetime.fromtimestamp(stat.st_ctime)

			print(f"Type       : {img.format or 'Unknown'}")
			print(f"Size       : {os.path.getsize(file):,} bytes")
			print(f"Dimensions : {img.width} × {img.height} pixels")
			print(f"Mode       : {img.mode}")
			print(f"Modified   : {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
			print(f"Created    : {created_time.strftime('%Y-%m-%d %H:%M:%S')}")
			print("-" * 50)
			if not exif_info:
				print("No EXIF metadata found (common for PNG/GIF/BMP or stripped images)")
				print(f"{'-'*70}")
				continue
			print(f"EXIF METADATA FOUND ({len(exif_info)} tags)")
			print("-" * 50)
			for tag, value in exif_info.items():
				print(f"{tag}: {value}")
		except Exception as e:
			print(f"Error processing image: {e}")

		print(f"{'-'*70}")

def launchScorpionGUI() -> None:
	print("Open GUI")

def main() -> None:
	args = parseArgs()
	if args.gui and args.file:
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
		deleteMetadata(valid_files)
	# elif args.modify:
		# modifyMetadata(valid_files)
	else:
		printMetadata(valid_files)

if __name__ == '__main__':
	main()
