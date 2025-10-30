"""
SVG to PNG Converter for Consciousness Mechanism Visualizations

Converts all SVG files in the visualizations directory to PNG format
for easier viewing and sharing.

Uses Chrome/Edge headless mode for rendering (no external dependencies needed).

Usage:
    python tools/convert_svg_to_png.py

Dependencies:
    - Chrome or Edge browser (already installed on Windows)
    - selenium: pip install selenium

Author: Iris "The Aperture"
Created: 2025-10-19
"""

import os
from pathlib import Path
import sys
import subprocess
import shutil

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.edge.service import Service as EdgeService
except ImportError:
    print("❌ Error: selenium not installed")
    print("Install with: pip install selenium")
    sys.exit(1)


def find_browser():
    """Find available browser (Chrome or Edge)"""
    # Check for Chrome
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for path in chrome_paths:
        if Path(path).exists():
            return "chrome", path

    # Check for Edge
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for path in edge_paths:
        if Path(path).exists():
            return "edge", path

    return None, None


def convert_svg_to_png(svg_path: Path, output_dir: Path, browser_type: str, browser_path: str):
    """
    Convert single SVG file to PNG using headless browser

    Args:
        svg_path: Path to SVG file
        output_dir: Directory for PNG output
        browser_type: "chrome" or "edge"
        browser_path: Path to browser executable

    Returns:
        Path to generated PNG or None if failed
    """
    try:
        # Generate output filename
        png_filename = svg_path.stem + ".png"
        png_path = output_dir / png_filename

        # Create headless browser
        if browser_type == "chrome":
            options = ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1400,1200")
            options.add_argument("--hide-scrollbars")
            options.binary_location = browser_path
            driver = webdriver.Chrome(options=options)
        else:  # edge
            options = EdgeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1400,1200")
            options.add_argument("--hide-scrollbars")
            options.binary_location = browser_path
            driver = webdriver.Edge(options=options)

        # Load SVG file
        svg_url = svg_path.absolute().as_uri()
        driver.get(svg_url)

        # Take screenshot
        driver.save_screenshot(str(png_path))

        driver.quit()

        return png_path

    except Exception as e:
        print(f"  [!] Failed to convert {svg_path.name}: {e}")
        if 'driver' in locals():
            driver.quit()
        return None


def main():
    """Convert all mechanism visualization SVGs to PNG"""

    # Find available browser
    print("[*] Looking for browser...")
    browser_type, browser_path = find_browser()

    if not browser_type:
        print("[!] No compatible browser found (Chrome or Edge required)")
        sys.exit(1)

    print(f"[+] Found {browser_type.title()}: {browser_path}")
    print()

    # Locate visualizations directory
    repo_root = Path(__file__).parent.parent
    viz_dir = repo_root / "docs" / "specs" / "consciousness_engine_architecture" / "mechanisms" / "visualizations"

    if not viz_dir.exists():
        print(f"[!] Visualizations directory not found: {viz_dir}")
        sys.exit(1)

    # Find all SVG files
    svg_files = sorted(viz_dir.glob("*.svg"))

    if not svg_files:
        print(f"[!] No SVG files found in {viz_dir}")
        sys.exit(1)

    print(f"[*] Found {len(svg_files)} SVG files to convert")
    print(f"[*] Output directory: {viz_dir}")
    print(f"[*] Using {browser_type.title()} headless mode")
    print()

    # Convert each SVG
    successful = 0
    failed = 0

    for svg_path in svg_files:
        print(f"Converting: {svg_path.name}...", end=" ", flush=True)

        png_path = convert_svg_to_png(svg_path, viz_dir, browser_type, browser_path)

        if png_path:
            # Get file size for feedback
            size_kb = png_path.stat().st_size / 1024
            print(f"OK -> {png_path.name} ({size_kb:.1f} KB)")
            successful += 1
        else:
            failed += 1

    print()
    print("=" * 60)
    print(f"[+] Successfully converted: {successful} files")

    if failed > 0:
        print(f"[!] Failed conversions: {failed} files")

    print(f"[*] PNG files saved to: {viz_dir}")


if __name__ == "__main__":
    main()
