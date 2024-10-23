# Source Map Extractor Tool

This project provides a simple tool to extract and analyze JavaScript source maps. It helps developers or bug hunters to retrieve uncompiled source code embedded in Webpack bundles or `.map` files, allowing further inspection for vulnerabilities or hidden code.

---

## Features
- **Local and Remote Source Map Extraction**: Extracts source code from local `.map` files or remote URLs.
- **HTML Sourcemap Detection**: Detects sourcemaps linked in HTML `<script>` tags automatically.
- **SSL Verification Option**: Supports disabling SSL verification for debugging on untrusted sources.
- **Easy Directory Management**: Automatically saves extracted files to a specified output directory.

---

## Installation
   ```bash
   git clone https://github.com/ahmetartuc/jsmapper.git
   cd jsmapper
   pip install -r requirements.txt
