#!/usr/bin/env python3

import os
import sys
import time
import hmac
import hashlib
import argparse

KEY_FILE = "ft_otp.key"

def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		usage="ft_otp [-g hexkey | file.hex] [-k]"
	)
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-g", metavar="HEXKEY|FILE.hex", help="hexadecimal master key (≥64 chars) or path to .hex file")
	group.add_argument("-k", action="store_true", help="generate current 6-digit TOTP code")
	return parser.parse_args()

def read_hex_from_file(filename: str) -> str:
	if not os.path.isfile(filename):
		print(f"error: file not found: {filename}", file=sys.stderr)
		sys.exit(1)

	try:
		with open(filename, "r") as f:
			content = f.read().strip()
		content = content.replace("0x", "").replace(" ", "").replace("\n", "").replace("\r", "")
		return content
	except Exception as e:
		print(f"error reading file {filename}: {e}", file=sys.stderr)
		sys.exit(1)

def is_valid_hex_key(s: str) -> bool:
	return len(s) >= 64 and all(c in "0123456789abcdefABCDEF" for c in s)

def hotp(secret: bytes, counter: int, digits: int = 6) -> str:
	msg = counter.to_bytes(8, byteorder='big')
	h = hmac.new(secret, msg, hashlib.sha1).digest()

	offset = h[19] & 0x0F
	binary = (
		((h[offset]	 & 0x7F) << 24) |
		((h[offset + 1] & 0xFF) << 16) |
		((h[offset + 2] & 0xFF) <<  8) |
		( h[offset + 3] & 0xFF)
	)

	return f"{binary % (10 ** digits):0{digits}d}"

def totp(secret: bytes, time_step: int = 30, digits: int = 6) -> str:
	counter = int(time.time()) // time_step
	return hotp(secret, counter, digits)

def save_key(input_arg: str):
	if input_arg.lower().endswith(".hex"):
		hex_str = read_hex_from_file(input_arg)
	else:
		hex_str = input_arg
	hex_str = hex_str.lower()
	if not is_valid_hex_key(hex_str):
		print("error: key must be a valid hexadecimal string of at least 64 characters", file=sys.stderr)
		print(f"	(got {len(hex_str)} characters)", file=sys.stderr)
		sys.exit(1)

	try:
		with open(KEY_FILE, "w") as f:
			f.write(hex_str)
		# Make file readable/writable only by owner
		os.chmod(KEY_FILE, 0o600)
		print(f"key successfully stored to {KEY_FILE}")
	except PermissionError:
		print(f"error: permission denied when writing {KEY_FILE}", file=sys.stderr)
		sys.exit(1)
	except Exception as e:
		print(f"error writing {KEY_FILE}: {e}", file=sys.stderr)
		sys.exit(1)

def load_key() -> bytes:
	try:
		with open(KEY_FILE, "r") as f:
			hex_str = f.read().strip()

		if not is_valid_hex_key(hex_str):
			print(f"error: invalid key format in {KEY_FILE}", file=sys.stderr)
			sys.exit(1)

		return bytes.fromhex(hex_str)

	except FileNotFoundError:
		print(f"error: {KEY_FILE} not found. Use -g first.", file=sys.stderr)
		sys.exit(1)
	except Exception as e:
		print(f"error reading {KEY_FILE}: {e}", file=sys.stderr)
		sys.exit(1)

if __name__ == "__main__":
	args = parse_args()

	if args.g:
		save_key(args.g)

	elif args.k:
		secret = load_key()
		code = totp(secret)
		print(code)
