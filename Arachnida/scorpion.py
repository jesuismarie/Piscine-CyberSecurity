#!/usr/bin/env python3

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from PIL import Image, ExifTags

exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

def parseArgs() -> argparse.Namespace:
	scorpionParser = argparse.ArgumentParser(
		usage="./scorpion.py [-d] FILE1 [FILE2 ...]",
	)
	scorpionParser.add_argument('file', nargs='*', help="One or more image files (supports .jpg/.jpeg/.png/.gif/.bmp)")
	return scorpionParser.parse_args()

def isSupportedFile(filepath: str) -> bool:
	if not os.path.isfile(filepath):
		print(f"File not found: {filepath}", file=sys.stderr)
		return False

	if not any(filepath.lower().endswith(ext) for ext in exts):
		print(f"Unsupported format (supported: {', '.join(exts)}): {filepath}", file=sys.stderr)
		return False
	return True

def getAllMetadata(img: Image.Image) -> dict | None:
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
		print(f"Error extracting metadata from {img.filename}: {e}", file=sys.stderr)

	return metadata if metadata else None

def formatMetadataValue(value):
	if isinstance(value, bytes):
		try:
			decoded = value.decode('utf-8', errors='ignore').strip()
			return decoded if decoded else f"<binary: {len(value)} bytes>"
		except:
			return f"<binary: {len(value)} bytes>"
	elif isinstance(value, tuple):
		return f"({', '.join(map(str, value))})"
	elif isinstance(value, list):
		return f"[{', '.join(map(str, value))}]"
	else:
		return str(value)

def printMetadata(files: list[str]) -> None:
	for file in files:
		filepath = Path(file).resolve()

		print(f"{'─' * 70}")
		print(f"FILE: {filepath.name}")
		print(f"PATH: {filepath.resolve()}")
		print(f"{'─' * 70}")

		try:
			with Image.open(file) as img:
				stat = filepath.stat()
				modified_time = datetime.fromtimestamp(stat.st_mtime)
				created_time = datetime.fromtimestamp(stat.st_ctime)

				basic_info = [
					("Type", img.format or "Unknown"),
					("Size", f"{os.path.getsize(file):,} bytes"),
					("Dimensions", f"{img.width}×{img.height} pixels"),
					("Mode", img.mode),
					("Modified", modified_time.strftime('%Y-%m-%d %H:%M:%S')),
					("Created", created_time.strftime('%Y-%m-%d %H:%M:%S')),
				]

				print("FILE INFORMATION")
				print('-' * 50)
				for key, value in basic_info:
					print(f"{key: <20}: {value}")
				print('-' * 50)

				metadata = getAllMetadata(img)
				if metadata:
					print(f"METADATA ({len(metadata)} entries)")
					print('-' * 50)
					for key, value in sorted(metadata.items()):
						print(f"{key: <20}: {formatMetadataValue(value)}")
				else:
					print("No readable metadata found.")

		except Exception as e:
			print(f"Cannot open/process image: {e}")

		print(f"{'─' * 70}\n")

if __name__ == '__main__':
	args = parseArgs()

	valid_files = [f for f in args.file if isSupportedFile(f)]

	if not valid_files:
		print("No valid image files provided.", file=sys.stderr)
		sys.exit(1)

	printMetadata(valid_files)
