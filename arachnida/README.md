# Arachnida

## Overview

This project contains two Python programs developed as part of the **Arachnida - 42 Cybersecurity Piscine**:

1. **Spider** – Recursively downloads images from web pages.
2. **Scorpion** – Parses image files for EXIF and other metadata, displaying it on the screen.

The focus of the project is on web crawling, HTTP requests, file handling, and image metadata analysis, while implementing all core logic manually.

## Getting Started

It is recommended to run this project inside a virtual environment to avoid conflicts between Python packages.

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
```

Once the virtual environment is activated, install the required packages:

```bash
pip install -r requirements.txt
```

## Spider

**Spider** is a command-line web crawler that downloads images from a given URL, optionally following links recursively.

### Features

* Downloads images with the following extensions: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`.
* Recursive crawling with configurable depth (default: 5).
* Custom download path for storing images (default: `./data/`).
* Prevents revisiting the same URLs.

### Usage

```bash
./spider.py [-r] [-l N] [-p PATH] URL
```

**Options:**

| Option    | Description                                          |
| --------- | ---------------------------------------------------- |
| `-r`      | Recursively download images.                         |
| `-l N`    | Maximum recursion depth (default: 5).                |
| `-p PATH` | Path to save downloaded images (default: `./data/`). |

**Examples:**

```bash
./spider.py https://example.com
./spider.py -r https://example.com
./spider.py -r -l 3 https://example.com
./spider.py -r -l 2 -p ./downloads https://example.com
```

## Scorpion

**Scorpion** analyzes image files and displays metadata including EXIF information.

### Features

* Supports `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp` files.
* Displays creation date, camera info, and other EXIF data.
* Accepts multiple files as input:

```bash
./scorpion.py [-d] FILE1 [FILE2 ...]
```

**Bonus features (optional):**

* Delete metadata from images.

## Requirements

* Python 3.8+
* `requests`
* `beautifulsoup4`
* `pillow`
* `piexif`

## Project Structure

```
Arachnida/
├─ spider.py       # Web spider program
├─ data/           # Default folder for downloads
├─ scorpion.py     # Image metadata parser
└─ README.md       # Project documentation
```
