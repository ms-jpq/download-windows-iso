# Didactic Guide: download-windows-iso Script

## Overview

The `download-windows-iso` script automates the navigation of the Microsoft Windows 10/11 download page using Docker and Playwright. It selects the desired product edition and language, and outputs the download page URL. Note: Microsoft's website layout changes and anti-bot measures may require manual completion of the download.

1. Build a Docker image with Playwright installed.
2. Launch a headless browser to visit the Microsoft Windows 10/11 download page.
3. Select the desired product edition (e.g., Windows 10 or Windows 11) and language.
4. Output the download page URL.
5. Note: Microsoft's website layout changes and anti-bot measures may require manual download completion.

## How It Works

### Step 1: Docker Image Build

The script begins by building a Docker image named `download-windows-iso-2026-bindows` using the project's `Dockerfile`. The Dockerfile:

- Starts from the official `mcr.microsoft.com/playwright/python:latest` image, which includes Playwright and Chromium.
- Copies `requirements.txt` and installs Python dependencies (currently `playwright`).
- Runs `playwright install` to download the Chromium browser executable.
- Copies the local `scripts/` directory into the image.
- Sets the entry point to run the Python module `srv` with the `--language` and `--windows-version` arguments.

### Step 2: Run the Python Application

The script runs `docker compose build` and `docker run` to start the container. The container executes a Python application (`scripts/play.py`) that:

- Launches Chromium in headless mode.
- Navigates to `https://www.microsoft.com/software-download/windows{10/11}` (depends on the `-w` argument).
- Dismisses any cookie consent banner if present.
- Selects the product edition based on the Windows version selected.
- Clicks the "Submit" button to proceed.
- Waits for the language selector to become visible.
- Selects the language specified via the `-l` or `--language` argument (default: "English International").
- Clicks "Submit" again to proceed to the download page.
- Gets the final page URL after all selections.
- The Bash script captures this URL from the container's stdout.

### Step 3: Download the ISO

Once the direct download page URL is obtained from the script:

- Creates a `tmp/` directory if it doesn't exist.
- Changes to the `tmp/` directory.
- The user can run `wget --content-disposition <URL>` to download the ISO file, preserving the original filename.
- Note: Microsoft's website may require manual interaction to complete the download due to anti-bot measures.

### Step 4: Usage

```bash
# Default: Windows 11, English International
./download.sh

# Download Windows 10, English International
./download.sh -l "English International" -w 10

# Download Windows 11, Spanish
./download.sh -l "Spanish" -w 11

# Available languages depend on Microsoft's website; common values include:
# - "English International"
# - "Spanish"
# - "French"
# - etc.
```

### Important Warnings for Windows 10

When downloading Windows 10:

- **Mainstream support ended**: October 14, 2025
- **ESU (Extended Support Updates) ends**: October 12, 2027
  (3-year paid program to receive critical and important security updates)
- **Microsoft can withdraw ISO downloads at any time** - the download link may become unavailable without notice
- Consider using Windows 11 for continued security updates and support

## Recent Fixes

- Added `playwright install` to the Dockerfile to ensure the Chromium executable is available.
- Added `wait_for_load_state("networkidle")` after page navigation to ensure resources are loaded.
- Added cookie consent dismissal logic.
- Added explicit waits for element visibility to improve reliability.
- Added Windows 10/11 version selection support.
- Updated to output download page URL due to Microsoft website layout changes.

## Troubleshooting

If the script fails:

- Ensure Docker is running and accessible.
- Check that the language argument matches exactly what Microsoft displays (case-sensitive).
- Verify the Windows version argument is either "10" or "11".
- The script may fail if Microsoft changes their website layout; in such cases, the Playwright selectors may need updating.
- The output URL can be used with wget or a browser; Microsoft's site may require additional interaction.