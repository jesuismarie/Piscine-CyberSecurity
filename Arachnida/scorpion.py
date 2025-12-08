#!/usr/bin/env python3

import os
import piexif
import argparse
from pathlib import Path
from datetime import datetime
from PIL import Image, ExifTags

exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

def parseArgs() -> argparse.Namespace:
	scorpionParser = argparse.ArgumentParser(
		usage="./scorpion.py [-d] FILE1 [FILE2 ...]",
	)
	mode_group = scorpionParser.add_mutually_exclusive_group()
	mode_group.add_argument('-d', '--delete', action='store_true', help="Delete metadata from the given image(s).")
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
		path = Path(file)

		try:
			if path.suffix.lower() in (".jpg", ".jpeg"):
				piexif.remove(str(path))
				img = Image.open(file)
				img.save(file, exif=b"")
			else:
				img = Image.open(file)
				img.info.clear()
				img.save(file)
			print(f"Metadata removed from: {file}")
		except Exception as e:
			print(f"Error removing metadata from {file}: {e}")

def getAllMetadata(img: Image) -> dict | None:
	metadata = {}

	try:
		exif_data = img.getexif()
		if exif_data:
			for tag_id, value in exif_data.items():
				tag_name = ExifTags.TAGS.get(tag_id, tag_id)
				metadata[tag_name] = value

		if hasattr(img, 'info') and img.info:
			for key, value in img.info.items():
				k = key.decode(errors='ignore') if isinstance(key, bytes) else str(key)
				if any(bad in k.lower() for bad in ['icc', 'jfif', 'xml', 'adobe', 'photoshop']):
					continue
				if isinstance(value, (bytes, bytearray)):
					try:
						v = value.decode('utf-8', errors='replace').strip()
						if v and len(v) < 500:
							metadata[k] = v
					except:
						pass
				else:
					metadata[k] = value

	except Exception as e:
		print(f"Error extracting metadata: {e}")

	return metadata if metadata else None

def formatMetadataValue(value):
	if isinstance(value, bytes):
		try:
			decoded = value.decode('utf-8', errors='ignore').strip()
			return decoded if decoded else f"<binary data: {len(value)} bytes>"
		except:
			return f"<binary data: {len(value)} bytes>"
	elif isinstance(value, tuple):
		return f"({', '.join(map(str, value))})"
	elif isinstance(value, list):
		return f"[{', '.join(map(str, value))}]"
	else:
		return str(value)

def printMetadata(files: list) -> None:
	for file in files:
		filepath = Path(file)

		print(f"{'-'*70}")
		print(f"FILE: {filepath.name}")
		print(f"PATH: {filepath.resolve()}")
		print(f"{'-'*70}")

		try:
			img = Image.open(file)
			stat = filepath.stat()
			modified_time = datetime.fromtimestamp(stat.st_mtime)
			created_time = datetime.fromtimestamp(stat.st_ctime)

			print(f"Type       : {img.format or 'Unknown'}")
			print(f"Size       : {os.path.getsize(file):,} bytes")
			print(f"Dimensions : {img.width}x{img.height} pixels")
			print(f"Mode       : {img.mode}")
			print(f"Modified   : {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
			print(f"Created    : {created_time.strftime('%Y-%m-%d %H:%M:%S')}")
			print("-" * 50)

			metadata = getAllMetadata(img)

			if metadata:
				print(f"METADATA FOUND ({len(metadata)} entries)")
				print("-" * 50)

				for key, value in metadata.items():
					formatted_value = formatMetadataValue(value)
					print(f"{key}: {formatted_value}")
			else:
				print(f"No metadata found for {img.format} format")

		except Exception as e:
			print(f"Error processing image: {e}")

		print(f"{'-'*70}\n")

def main() -> None:
	args = parseArgs()

	valid_files = [f for f in args.file if isSupportedFile(f)]

	if not valid_files:
		print("No valid files to process.")
		return

	if args.delete:
		deleteMetadata(valid_files)
	else:
		printMetadata(valid_files)

if __name__ == '__main__':
	main()
