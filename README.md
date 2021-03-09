# Download Windows ISO

Python script to download Windows from Microsoft's website

## Requirements

1. Python

2. Docker

No other dependencies.

## How to use

```sh
wget https://raw.githubusercontent.com/ms-jpq/download-windows-iso/bindows/download.py
python3 download.py
```

It will keep trying to download image until it succeeds.

If you are unlucky, it might take 2 or 3 runs.

## How do you know it still works?

[Look at the CI](https://github.com/ms-jpq/download-windows-iso/actions)

It has a simple test, if the script downloads `*.iso` over 1000MB, it's probably the Windows ISO.

I will try to update it whenever it breaks.

## Why are my fans so loud?

This script is designed to run on a CI, AKA not your hardware.

It will spin up `cpu_count()` instances of headless browsers in Docker at the same time.

This will help to cut down flakiness at cost of compute.

Since I am running this on Microsoft's dime, I don't really care about the resource usage.
