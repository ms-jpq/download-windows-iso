# Download Windows ISO

Bash script to download Windows ISO from Microsoft's website using Docker and Playwright.

## Requirements

1. Have `docker`
2. Have `bash`
3. Have `wget`

## Installation

### On Windows

1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop
2. Run the installer and follow the setup wizard
3. Once installed, open Docker Desktop from the Start menu
4. Create a Docker account or sign in if you already have one
5. Docker will start automatically and you'll see the whale icon in your system tray
6. Verify installation by running `docker --version` in PowerShell or Command Prompt

### On Linux (Ubuntu/Debian)

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
sudo docker run --rm hello-world
```

### On Linux (Other Distributions)

Refer to the official Docker documentation for your specific distribution:
https://docs.docker.com/engine/install/

## Usage

### Step 1

```
# Default to `Windows 11, English International`
./download.sh [-l LANGUAGE] [-w WINDOWS_VERSION]

# Download Windows 10, English International
./download.sh -l "English International" -w 10

# Download Windows 11, Spanish
./download.sh -l "Español" -w 11
```

### Step 2

Check `./tmp/` for the downloaded ISO.

### Step 3

The script will:
1. Build a Docker image with Playwright installed
2. Run a browser to navigate to the Microsoft Windows {10/11} download page
3. Show support end-of-life warnings
4. Select the product edition and language
5. Output the direct download page URL
6. Note: Microsoft's website may require manual completion of the download
   due to anti-bot measures. The URL output below can be used with wget or a browser.

### Important Warnings

When downloading Windows 10:

- **Mainstream support ended**: October 14, 2025
- **ESU (Extended Support Updates) ends**: October 12, 2027
  (3-year paid program to receive critical and important security updates)
- **Microsoft can withdraw ISO downloads at any time** - the download link may become unavailable without notice
- Consider using Windows 11 for continued security updates and support

### Step 4

The script outputs a download page URL. You can use this URL with wget or a browser:

```bash
# Using wget (may require additional options for Microsoft's site):
wget --content-disposition "URL_OUTPUT"

# Or simply open the URL in a browser and click the download button:
# The URL will be displayed after the script runs
```
