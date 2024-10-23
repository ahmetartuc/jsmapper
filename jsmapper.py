import os
import json
import argparse
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class SourceMapTool:
    def __init__(self, target, output_dir, local=False, detect=False, ssl_verify=True):
        self.target = target
        self.output_dir = os.path.abspath(output_dir)
        self.local = local
        self.detect = detect
        self.ssl_verify = ssl_verify
        self._create_output_directory()

    def _create_output_directory(self):
        if not os.path.exists(self.output_dir):
            print(f"Creating output directory: {self.output_dir}")
            os.makedirs(self.output_dir, exist_ok=True)

    def run(self):
        if self.local:
            self._extract_from_local_file()
        elif self.detect:
            self._detect_and_extract_from_html()
        else:
            self._extract_from_remote_url(self.target)

    def _extract_from_local_file(self):
        if os.path.isfile(self.target):
            print(f"Extracting from local file: {self.target}")
            self._process_sourcemap(self.target)
        else:
            print("Error: Local file not found!")

    def _detect_and_extract_from_html(self):
        html_data = self._get_remote_data(self.target)
        soup = BeautifulSoup(html_data, "html.parser")
        scripts = soup.find_all("script", src=True)

        for script in scripts:
            script_url = urljoin(self.target, script['src'])
            print(f"Checking JS file: {script_url}")
            self._check_for_sourcemap(script_url)

    def _check_for_sourcemap(self, js_url):
        js_content = self._get_remote_data(js_url)
        if "sourceMappingURL" in js_content:
            sourcemap_url = self._extract_sourcemap_url(js_content, js_url)
            print(f"Found sourcemap: {sourcemap_url}")
            self._extract_from_remote_url(sourcemap_url)

    def _extract_sourcemap_url(self, js_content, base_url):
        last_line = js_content.strip().split("\n")[-1]
        if "sourceMappingURL=" in last_line:
            url = last_line.split("sourceMappingURL=")[-1].strip()
            return urljoin(base_url, url)
        return None

    def _extract_from_remote_url(self, url):
        print(f"Downloading sourcemap: {url}")
        data = self._get_remote_data(url)
        self._process_sourcemap_content(data)

    def _process_sourcemap(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self._process_sourcemap_content(content)

    def _process_sourcemap_content(self, content):
        try:
            sourcemap = json.loads(content)
            self._extract_files_from_sourcemap(sourcemap)
        except json.JSONDecodeError:
            print("Error: Failed to decode the sourcemap.")

    def _extract_files_from_sourcemap(self, sourcemap):
        if "sources" not in sourcemap or "sourcesContent" not in sourcemap:
            print("Error: Sourcemap is missing required fields.")
            return

        for source, content in zip(sourcemap["sources"], sourcemap["sourcesContent"]):
            filename = os.path.basename(source)
            filepath = os.path.join(self.output_dir, filename)

            print(f"Writing file: {filepath}")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

    def _get_remote_data(self, url):
        try:
            response = requests.get(url, verify=self.ssl_verify)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return ""

def main():
    parser = argparse.ArgumentParser(description="Extract source code from Webpack source maps.")
    parser.add_argument("target", help="The target URL or local file.")
    parser.add_argument("output_dir", help="Directory to save extracted files.")
    parser.add_argument("--local", action="store_true", help="Use a local source map file.")
    parser.add_argument("--detect", action="store_true", help="Detect sourcemaps from HTML.")
    parser.add_argument("--no-ssl-verify", action="store_true", help="Disable SSL verification.")

    args = parser.parse_args()

    tool = SourceMapTool(
        target=args.target,
        output_dir=args.output_dir,
        local=args.local,
        detect=args.detect,
        ssl_verify=not args.no_ssl_verify
    )
    tool.run()

if __name__ == "__main__":
    main()
