#!/usr/bin/env python3
"""
backend/generate_qrcodes.py
Zero-dependency QR Code Generator for Open EMF Camper (V2) Dashboards.
Fetches high-contrast black and white QR code PNG images
and saves them locally to web/qrcodes/.
"""

import os
import urllib.request
import urllib.parse

# Brand configurations
PORTAL_BASE_URL = "https://emf.harvinderatwal.com/index.html"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "web", "qrcodes")

# High-contrast black and white color palette for universal scan compatibility
QR_SIZE = "300x300"
COLOR_FOREGROUND = "000000"   # Black foreground
COLOR_BACKGROUND = "ffffff"   # White background

CAMPERS = {
    "hvy": "Harvy",
    "cha": "Charlotte",
    "ash": "Ash",
    "tin": "Tina",
    "combined": "Combined Camper Stats"
}

# ANSI Colors for beautiful terminal output
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def main():
    print(f"{BLUE}=== EMF Camper Dashboard QR Code Generator ==={RESET}")
    print(f"Target Base: {PORTAL_BASE_URL}")
    print(f"Output Directory: {os.path.abspath(OUTPUT_DIR)}\n")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for shortcode, name in CAMPERS.items():
        # Construct target URL
        dashboard_url = f"{PORTAL_BASE_URL}?u={shortcode}"
        
        # Build styled QR Server API endpoint query parameters
        encoded_data = urllib.parse.quote(dashboard_url)
        qr_api_url = (
            f"https://api.qrserver.com/v1/create-qr-code/"
            f"?size={QR_SIZE}&data={encoded_data}"
            f"&color={COLOR_FOREGROUND}&bgcolor={COLOR_BACKGROUND}"
        )
        
        output_file = os.path.join(OUTPUT_DIR, f"{shortcode}.png")
        print(f"Generating QR for {name} ({shortcode}) ... ", end="")
        
        try:
            req = urllib.request.Request(
                qr_api_url,
                headers={"User-Agent": "EMF-Camper-QR-Generator/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                image_data = response.read()
                
            with open(output_file, "wb") as fh:
                fh.write(image_data)
                
            print(f"{GREEN}[SUCCESS]{RESET} Saved to qrcodes/{shortcode}.png")
        except Exception as e:
            print(f"\033[91m[FAILED]\033[0m -> Error: {e}")

    print(f"\n{GREEN}✓ QR codes successfully generated inside web/qrcodes/!{RESET}")

if __name__ == "__main__":
    main()
