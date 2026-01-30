#!/usr/bin/env python3

import os
import sys
import time
import hmac
import base64
import hashlib
import getpass
import argparse
from cryptography.fernet import Fernet, InvalidToken

KEY_FILE = "ft_otp.key"

def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		usage="ft_otp [-g hexkey | file.hex] [-k keyfile]"
	)
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-g", metavar="HEXKEY|FILE.hex", help="hexadecimal master key (≥64 chars) or path to .hex file")
	group.add_argument("-k", metavar="KEYFILE", help="path to the encrypted key file")
	return parser.parse_args()

def read_hex_from_file(filename: str) -> str:
	if not os.path.isfile(filename):
		print(f"error: file not found: {filename}", file=sys.stderr)
		sys.exit(1)

	try:
		with open(filename, "r") as f:
			content = f.read().strip()
		content = content.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
		return content
	except Exception as e:
		print(f"error reading file {filename}: {e}", file=sys.stderr)
		sys.exit(1)

def is_valid_hex_key(s: str) -> bool:
	return len(s) >= 64 and all(c in "0123456789abcdefABCDEF" for c in s)

def protect_key_password() -> str:
	password = getpass.getpass("Enter password to protect ft_otp.key: ").strip()
	if not password:
		print("error: password cannot be empty", file=sys.stderr)
		sys.exit(1)

	password_confirm = getpass.getpass("Confirm password: ").strip()
	if password != password_confirm:
		print("error: passwords do not match", file=sys.stderr)
		sys.exit(1)
	return password

def unlock_key_password() -> str:
	password = getpass.getpass("Enter password to unlock ft_otp.key: ").strip()
	if not password:
		print("error: password cannot be empty", file=sys.stderr)
		sys.exit(1)
	return password

def password_to_fernet_key(password: str) -> bytes:
	key_material = hashlib.sha256(password.encode('utf-8')).digest()
	return base64.urlsafe_b64encode(key_material)

def encrypt_secret(secret_hex: str, password: str) -> bytes:
	fernet_key = password_to_fernet_key(password)
	f = Fernet(fernet_key)
	return f.encrypt(secret_hex.encode('utf-8'))

def decrypt_secret(encrypted_data: bytes, password: str) -> str:
	fernet_key = password_to_fernet_key(password)
	f = Fernet(fernet_key)
	try:
		decrypted = f.decrypt(encrypted_data)
		return decrypted.decode('utf-8')
	except InvalidToken:
		print("error: incorrect password or corrupted file", file=sys.stderr)
		sys.exit(1)

def hotp(secret: bytes, counter: int, digits: int = 6) -> str:
	msg = counter.to_bytes(8, byteorder='big')
	h = hmac.new(secret, msg, hashlib.sha1).digest()

	offset = h[19] & 0x0F
	binary = (
		((h[offset]	 & 0x7F) << 24) |
		((h[offset + 1] & 0xFF) << 16) |
		((h[offset + 2] & 0xFF) << 8) |
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

	password = protect_key_password()
	encrypted = encrypt_secret(hex_str, password)

	try:
		with open(KEY_FILE, "wb") as f:
			f.write(encrypted)
		os.chmod(KEY_FILE, 0o600)
		print(f"key successfully stored (encrypted) to {KEY_FILE}")
	except PermissionError:
		print(f"error: permission denied when writing {KEY_FILE}", file=sys.stderr)
		sys.exit(1)
	except Exception as e:
		print(f"error writing {KEY_FILE}: {e}", file=sys.stderr)
		sys.exit(1)

def load_key() -> bytes:
	if not os.path.exists(KEY_FILE):
		print(f"error: {KEY_FILE} not found. Use -g first.", file=sys.stderr)
		sys.exit(1)

	try:
		with open(KEY_FILE, "rb") as f:
			encrypted_data = f.read()
	except Exception as e:
		print(f"error reading {KEY_FILE}: {e}", file=sys.stderr)
		sys.exit(1)

	password = unlock_key_password()
	hex_str = decrypt_secret(encrypted_data, password)

	if not is_valid_hex_key(hex_str):
		print(f"error: decrypted content is not a valid hex key", file=sys.stderr)
		sys.exit(1)

	return bytes.fromhex(hex_str)

if __name__ == "__main__":
	args = parse_args()

	if args.g:
		save_key(args.g)

	elif args.k:
		secret = load_key()
		code = totp(secret)
		print(code)
